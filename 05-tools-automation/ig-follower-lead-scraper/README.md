# client-ig-scraper

Finds qualified DM leads — female influencers/creators (including OnlyFans models) — among the followers of a client's Instagram account. Scraping runs through paid Apify actors (no Instagram login or session cookies, so the client's account is never at risk); a rubric then filters the list down to leads.

## Rubric

A follower qualifies when ALL of these hold (thresholds and keyword lists live in `rubric.yaml`):

1. **Female** — she/her pronouns, feminine bio terms, or female first name
2. **≥ 25,000 followers**
3. **Public** account
4. **Link in bio** OR bio pointing to **story highlights** ("link in highlights" etc.)
5. **At least one creator signal** — link-hub/OF domains, Snapchat/TikTok/YouTube mentions, creator/collab/booking language

Profiles passing gates 2–4 but with unresolved gender or zero creator signals go to `needs_review.csv` instead of being rejected; approve/reject them in `review_decisions.csv`.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your APIFY_TOKEN (apify.com → Settings → Integrations)
```

An Apify **Starter plan (~$39/mo)** is recommended — free-tier caps block large follower exports.

## Run order (per client account)

```bash
# 1. PILOT first — verifies the actor works and shows real data (~$0.60)
python -m pipeline scrape-followers --target CLIENT_HANDLE --limit 1000 --yes
python -m pipeline prefilter        --target CLIENT_HANDLE
python -m pipeline scrape-profiles  --target CLIENT_HANDLE --limit 50 --yes
python -m pipeline qualify          --target CLIENT_HANDLE
python -m pipeline status           --target CLIENT_HANDLE

# 2. Full run (delete data/CLIENT_HANDLE/ first to restart clean, or let it resume)
python -m pipeline scrape-followers --target CLIENT_HANDLE --yes   # ≈$120–150 per 200k
python -m pipeline prefilter        --target CLIENT_HANDLE          # free; prints profile-scrape cost estimate
python -m pipeline scrape-profiles  --target CLIENT_HANDLE --yes   # ≈$1.60 per 1k candidates
python -m pipeline qualify          --target CLIENT_HANDLE
# → review data/CLIENT_HANDLE/needs_review.csv, write review_decisions.csv
python -m pipeline export           --target CLIENT_HANDLE
```

Deliverables land in `data/CLIENT_HANDLE/`: **`qualified_leads.csv`** (handle, profile URL, name, followers, bio, link, qualification reasons — sorted by followers) and **`handles.txt`**.

Both paid stages checkpoint after every batch and resume where they left off; both refuse to run without `--yes` after printing a cost estimate.

## Things to verify during the pilot

- **Follower actor input/cursor fields** (`pipeline/followers.py`): the chunking input (`username`, `resultsLimit`, `type`) and continuation-cursor key names are best-effort against `scraping_solutions/instagram-scraper-followers-following-no-cookies` docs — confirm against the actor's input schema on its Apify page and adjust the constants at the top of the file if needed. Fallback actor: `thenetaji/instagram-followers-followings-scraper` (set `APIFY_FOLLOWERS_ACTOR` in `.env`).
- **Real yield**: Instagram sometimes caps follower pagination on very large accounts (~10–20k per some reports) even when actors claim unlimited. If the full run exhausts early, the checkpoint will say so — try the fallback actor before assuming the list is complete.
- **Pricing**: re-check both actors' current per-1k pricing on their Apify pages; the estimates in code are from Aug 2026.

## Tests

```bash
pytest tests/
```
