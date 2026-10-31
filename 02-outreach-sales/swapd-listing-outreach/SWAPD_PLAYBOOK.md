# SWAPD Operation — Playbook

The runbook the assistant follows on every scan. Read this at the start of each run.
All swapd access happens through **your logged-in Chrome** (Claude-in-Chrome extension);
swapd blocks anonymous access, so nothing works without your authenticated session.

## Files
- `catalog.json` — services you already sell (input you maintain).
- `data/listings.json` — canonical listing store, keyed by swapd topic id.
- `data/services.json` — analysis output (grouped, ranked, recommendations).
- `data/outreach.json` — per (seller+service) message + status + captured prices.
- `data/runs/<ts>.json` — per-run snapshot/log.
- `dashboard/index.html` — regenerated each run; open via the local server (below).
- `scripts/analyze.py`, `scripts/generate_dashboard.py` — stdlib only.
- `fixtures/sample_listings.json` — demo data for re-verifying the scripts offline.

## Weekly run — steps
1. **Login check.** Open `https://swapd.co`; confirm the logged-in state (avatar/username
   visible). If logged out, stop and tell the user to log in.
2. **Discover listings.** For each services category, pull the topic list. swapd is
   **Discourse** — prefer authenticated JSON via `javascript_tool` `fetch()` in the page
   context so cookies apply:
   - Categories: `GET /categories.json`
   - Category topics: `GET /c/<slug>/<id>.json?page=N`
   - Listing detail: `GET /t/<topic_id>.json`
   - Your PM inbox: `GET /topics/private-messages/<you>.json`
   Fall back to DOM (`get_page_text`/`read_page`) if JSON is blocked.
3. **Extract per listing:** title, category, seller + profile url, price (`price` numeric +
   `price_raw`), requirements, turnaround, post date, listing url, recent replies/reviews
   with dates (`last_review_date`), raw body excerpt.
4. **Upsert** into `data/listings.json` (set `first_seen` once, refresh `last_seen`);
   snapshot to `data/runs/`.
5. **Analyze:** `python3 scripts/analyze.py` → normalizes each listing to a canonical
   `<platform>_<action>` service id, groups providers, scores activity, ranks price,
   emits recommendations.
6. **Outreach candidates:** a listing qualifies for outreach only if ALL hold:
   - `service_type` is **NOT in `catalog.json`** (a NEW service ALTR doesn't sell), AND
   - the seller passes the **quality gate** (below), AND
   - (seller+service) is not already in `data/outreach.json`.
   Draft a message (below), store as `status: pending_approval`.
   NOTE: services ALTR ALREADY sells are never messaged, but their competitors are still
   scanned and ranked so the dashboard can flag cheaper/better trusted providers.
7. **Approval gate + 5/day cap:** each seller gets a UNIQUE message (built by
   `build_outreach.py`: varied phrasing + the seller's real success rate/reviews + their
   specific service). Show the queue; the user approves sellers. Sending is capped at
   **MAX_SENDS_PER_DAY = 5** — use `next_batch.py`:
   - `python3 scripts/next_batch.py approve <sellers…>` → mark approved
   - `python3 scripts/next_batch.py` → today's sendable batch (≤ 5 minus already sent today)
   - send each via browser PM, then `python3 scripts/next_batch.py sent <seller>` → `status: sent`
   Never exceed 5 sends per calendar day; never message the same seller twice.
8. **Reply tracking:** read PM inbox, match replies, classify `replied_yes`/`replied_no`,
   extract `bulk_price` (lowest offered) and `regular_price`. Non-repliers stay tracked
   (regular price still comes from the listing).
9. **Dashboard:** `python3 scripts/generate_dashboard.py`, then view it (below).

## Message style (generated per seller by build_outreach.py — unique, human, plain)
Each message is an INQUIRY, references ONE of the seller's services, and follows this arc:
1. Inquiring about your **[service]** I saw on swapd.
2. ALTR is a big **services marketplace** that could sell this.
3. If we bring **bulk clientele**, could you do a **better price down the line**?
4. We'll **show what we can do first**.
5. **What do you need to get started** so I can build it into our system?

No flattery, no reciting their stats, no "top providers" framing, no multi-service run-ons.
Six deterministic phrasings (varied by seller) live in `TEMPLATES` in `build_outreach.py`.

## Guardrails (why outreach is gated)
- **Every message needs explicit user approval** before it sends.
- **Dedup**: never message the same seller for the same service twice (outreach key).
- **Rate-limit / human pace**: small batches, spaced out — mass PMs risk swapd flags/bans.
- **No auto-accepting** terms, deals, or payments. Report prices; the user decides.

## Quality gate — seller success rate (required for outreach & recommendations)
Every seller must clear this before we contact or recommend them:
- **Success rate > 60%** AND has real feedback (reviews/transactions > 0).
- The number comes from swapd's **seller hover-card** (click a username in a thread):
  fields `SUCCESS RATE` (e.g. 78.6%), `N transactions`, `RECENT x/10 last deals`,
  `RATING ★ (M reviews)`, `MEMBER <year>`. Backed by the Discourse **user card**
  (`/u/<handle>/card.json`) — confirm the exact JSON field for success rate during scanner
  build; else read it off the rendered card.
- Capture per listing: `success_rate`, `transactions`, `recent_deals`, `rating`,
  `review_count`, `member_since`. `analyze.py` sets `qualified` and excludes sub-gate
  sellers from best-price, recommendations, and outreach. `MIN_SUCCESS_RATE = 60` there.

## Activity scoring (analyze.py)
- `active` ≤ 30 days since last review · `stale` ≤ 90 · `cold` older · `unknown` if none.
- Recommendations use ONLY qualified providers:
  - Existing service (you sell it): flag a qualified provider that undercuts your `your_cost`.
  - New service: surface the best qualified provider as an outreach/onboarding candidate.

## Viewing the dashboard (file:// is blocked by the extension)
```
cd <workspace> && python3 -m http.server 8747
# open http://127.0.0.1:8747/dashboard/index.html
```

## Offer-card bridge (ties into the "chiang-mai" card project)
`scripts/make_offer_cards.py` turns NEW + qualified social-media services into branded
marketplace offer cards in the sibling project
`sauce-the-brown-carpet-riders/chiang-mai/offers/` (files prefixed `swapd-`), then renders
PNGs via that project's `offers.mjs` → `output/offers/`.
- **Sell price = provider cost + inverse-scaled markup** (`pricing.json`): cheap services get
  a bigger multiple (≥2×), expensive ones a smaller % but healthy absolute margin
  (e.g. $2,000 cost → $3,000). Tune the cost bands or set a fixed price per service in
  `pricing.json` `overrides`.
- Run: `python3 scripts/make_offer_cards.py` (table only) or `--render` (build PNGs).
- Services with no provider price render as "Custom Quote". Cull off-target cards
  (delete their `offers/swapd-*.json`).

## Scheduling (session-only)
- In-session `CronCreate`: weekly full scan + daily reply-check.
- **Auto-expires after 7 days**; re-arm each week. Session must stay open. Manual trigger
  ("run the swapd scan") always works.

## Confirmed site specifics (recon 2026-09-29)
swapd runs **Discourse**; authenticated JSON API works in-page via `fetch()`.

- **Auth**: confirmed logged in (avatar/notifications visible). No re-login needed.
- **JSON endpoints (all 200 while authenticated):**
  - `/categories.json` → 29 categories with id/slug/name/topic_count.
  - `/c/<slug>/<id>.json?page=N` → topic list; each topic has `id, title, tags[],
    posts_count, views, created_at, last_posted_at, excerpt`.
  - `/t/<id>.json` → OP in `post_stream.posts[0].cooked` (HTML; strip tags); replies
    follow with `created_at` (activity signal).
- **Service categories to scan** (services, not account sales):
  Reputation Repair `reputation-repair/104`, PR Services `pr-services/75`,
  Services - Other `services-other/41`, Unique Services `unique-services/13` (has subs),
  Advertising `advertising/117` (has subs), Web & Content + SEO `developers/77`,
  Artificial Intelligence `ai/105`, Digital Intelligence `digital-intelligence/114`,
  Corporate `corporate/125`, Hire `hire/115`.
  NOTE: **Social Media `social-media/5` is mostly account SALES, not services** — skip for
  service scanning. Services also cross-cut categories via **tags**
  (`unban-service`, `removal-service`, `premium`, `featured`, `spotlight`, …), so also
  harvest by service tags, e.g. `/tag/unban-service.json`.
- **Price**: in BOTH title and OP body. Capture all `$` amounts (handle "FLAT $650",
  "$800 Per Link", "$100 per 1", ranges "$1500+", "$350 / Review Starting"); store the
  starting/min as `price` and the raw phrase as `price_raw`.
- **Turnaround (TAT)**: regex in title/body — `0-24hrs`, `24-48 Hours TAT`, `0-7 days TAT`,
  `0-72hrs Tat`, "same day", "instant".
- **Requirements**: freeform in OP; many listings use a `Service type: / Description: /
  Price:` template — parse those labels when present, else keep the body excerpt.
- **Activity**: use topic `last_posted_at` and the latest reply `created_at` as
  `last_review_date`.
- **Seller handle**: the JS tool **redacts usernames** in returned output (privacy). Capture
  the seller handle from the rendered topic page (`read_page`/screenshot) at scan time; use
  the **topic URL** as the stable listing/seller identifier and dedup key base.
- **Outreach flow (to finalize at build)**: on the seller's topic page use the post's
  **Message** action (Discourse PM) or `/new-message?username=<handle>`; alternatively a
  public reply on the listing thread. Approval-gated + rate-limited regardless.
