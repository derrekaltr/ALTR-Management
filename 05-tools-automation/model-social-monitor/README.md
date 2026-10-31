# Model Social Monitor

Keeps your chatters in sync with the models' real lives — automatically.

Every 15 minutes it checks each model's **Instagram posts** and **TikTok**
(plus **Instagram Stories** on a separate ~30-minute interval), has Claude
look at each new post (photo + caption) and write a short plain-English
update, and drops that update — with the photo — into that model's dedicated
**Telegram channel**. Chatters join the channel(s) for the model(s) they're
assigned to.

**Only relevant updates get through.** Claude judges every post before
sending: things that tell chatters about the model's real life (location,
activity, outfit, mood, travel, life events) are announced; noise that doesn't
help a chatter — sponsored posts, brand ads, giveaways, promo codes, meme
reposts, cross-promotion of other creators — is silently skipped (you can see
skips in the log).

Example of what lands in a channel:

> 🆕 Amber Hayes — Instagram
>
> Amber just posted a beach photo — she's in a red bikini at what looks like a
> tropical beach, sunny and relaxed vibes.
> Conversation hook: mention loving beach days or ask fans if they'd join her
> for a swim.
>
> https://www.instagram.com/p/...

## How it works

```
Apify scrapers (IG posts + IG stories + TikTok)  →  new-post detection (SQLite)
→  Claude (reads caption + image, judges relevance)  →  Telegram bot posts
   to the model's channel
```

- **No model logins needed** — Apify scrapes public profiles; the models'
  accounts are never touched or put at risk.
- **No history spam** — the first time an account is seen, its existing posts
  are recorded silently. Only posts made *after* that get announced. Adding a
  new model later behaves the same way.
- **Resilient** — one platform or one post failing never blocks the rest;
  failed sends retry on the next cycle (up to 3 attempts).

## Quick start

Full step-by-step instructions (including creating the Telegram bot and
channels) are in **[SETUP.md](SETUP.md)**. Short version:

```bash
python3 -m venv venv
venv/bin/pip install -e .
cp .env.example .env                              # fill in your 3 API keys
cp config/models.example.yaml config/models.yaml  # fill in your models
venv/bin/python -m model_monitor send-test        # verify Telegram wiring
venv/bin/python -m model_monitor check --dry-run  # verify scraping + AI, sends nothing
```

Then install the launchd job (SETUP.md step 7) so it runs every 15 minutes.

## Commands

| Command | What it does |
|---|---|
| `check` | The scheduled command: fetch, detect new posts, send updates |
| `check --dry-run` | Full pipeline but prints updates to the terminal instead of sending; writes no state |
| `check --force --model "Amber Hayes"` | Treats her latest post as new and really sends it — end-to-end test for one channel |
| `seed` | Record all current posts silently (happens automatically for new accounts) |
| `send-test` | Posts "✅ Monitor connected" to every channel — verifies bot + channel IDs |

## What it costs (approximate)

| Service | Rough cost |
|---|---|
| Apify Instagram Post Scraper | listed from ~$1 per 1,000 posts fetched |
| Apify Instagram Stories Scraper | listed ~$2.50 per 1,000 story rows |
| Apify TikTok Scraper | listed from ~$1.70 per 1,000 results |
| Claude (claude-haiku-4-5) | well under 1¢ per new post analyzed |
| Telegram | free |

With 3 models polled every 15 min at 8 posts/account, expect roughly
1,500–3,000 Apify results per day per platform — check current pricing on the
actor pages ([Instagram posts](https://apify.com/apify/instagram-post-scraper),
[Instagram stories](https://apify.com/dami_studio/instagram-stories-scraper),
[TikTok](https://apify.com/clockworks/tiktok-scraper)) and set a spending
limit in your Apify console. Raising the poll interval to 30 min halves it.

Stories are the expensive one: every *active* story is billed again on every
fetch until it expires (~24h). That's why stories poll on their own interval
(`poll.stories_min_interval_minutes`, default 30). At 30 min, a model who
keeps ~5 stories up all day costs roughly $0.60/day in story scraping; set
`include_stories: false` to turn stories off entirely.

## Monitoring it

```bash
tail -f logs/monitor.log                    # one summary line per cycle
launchctl list | grep model-monitor         # is the schedule loaded?
```

## Limitations

- Story *highlights* aren't monitored — only currently-active stories.
- Videos are understood via their cover image + caption, not the full video.
- Public profiles only. If a model goes private, her posts stop appearing
  (you'll see warnings in the log).
