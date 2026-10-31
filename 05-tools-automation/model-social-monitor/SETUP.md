# Setup Guide

Follow these steps in order. You'll need about 30 minutes. Nothing here
requires coding — just copying keys into two text files.

---

## 1. Get your three API keys

### Apify (scrapes Instagram + TikTok)
1. Create an account at [apify.com](https://apify.com) (the free plan includes
   $5/month of credit — fine for testing; add a card for production use).
2. Go to **Settings → API & Integrations** and copy your **Personal API token**
   (starts with `apify_api_`).
3. Recommended: set a monthly spending limit in **Billing** so a bug can never
   run up a bill.

### Anthropic (Claude reads the posts)
1. Create an account at [console.anthropic.com](https://console.anthropic.com).
2. Go to **Settings → API keys → Create key** and copy it (starts with `sk-ant-`).
3. Add $5–10 of credit — each post costs a fraction of a cent to analyze.

### Telegram bot
1. In Telegram, message **@BotFather**, send `/newbot`, and follow the prompts
   (pick any name, e.g. "Agency Updates Bot").
2. BotFather replies with a **bot token** like `1234567890:AAxxx...`. Copy it.

## 2. Create one channel per model

### Option A — automatic (recommended, especially with many models)

After step 3 (install) and putting your bot token in `.env`, run:

```bash
venv/bin/pip install telethon
venv/bin/python scripts/setup_channels.py
```

It logs into **your** Telegram account (asks for your phone number and the
login code Telegram sends you — one time only), then for every model in
`config/models.yaml` that doesn't have a chat id yet it:

- creates a private channel named "*Model* — Updates",
- adds your bot as an admin that can post,
- writes the channel's `-100...` id into `config/models.yaml` for you,
- saves an invite link per channel to `config/channel_invites.md` — share
  each link with that model's chatters.

You'll first need a Telegram **api_id + api_hash** — free, 2 minutes at
[my.telegram.org](https://my.telegram.org) → "API development tools" (any app
name works). If Telegram rate-limits channel creation partway through (it
caps new channels per day), progress is saved — just re-run the script later.

### Option B — by hand

For each model:

1. In Telegram: **New Channel** → name it (e.g. "Amber Hayes — Updates") →
   set it to **Private**.
2. Open the channel → **Administrators → Add Admin** → search for your bot's
   username → add it, making sure **"Post messages"** is enabled.
3. Get the channel's chat ID (a negative number starting with `-100`):
   - Easiest: temporarily add **@getidsbot** to the channel — it posts the ID —
     then remove it. Or:
   - Post anything in the channel, then open
     `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a browser and
     find `"chat":{"id":-100...}`.
4. Invite the chatters assigned to that model to the channel.

## 3. Install the app

In Terminal, from this project's folder:

```bash
python3 -m venv venv
venv/bin/pip install -e .
```

(Requires Python 3.11+. Check with `python3 --version`; if it's older,
install from [python.org](https://www.python.org/downloads/) or `brew install python`.)

## 4. Configure

```bash
cp .env.example .env
cp config/models.example.yaml config/models.yaml
```

- Edit **`.env`** — paste in the three keys from step 1.
- Edit **`config/models.yaml`** — one entry per model with her Instagram
  username, TikTok username (omit a line if she's not on that platform), and
  the channel's `-100...` chat ID from step 2.

## 5. Verify the Telegram wiring

```bash
venv/bin/python -m model_monitor send-test
```

Every channel should receive "✅ Monitor connected". If one says `FAIL`,
the chat ID is wrong or the bot isn't an admin of that channel.

## 6. Verify scraping + AI (sends nothing)

```bash
venv/bin/python -m model_monitor check --dry-run
```

This really calls Apify and Claude, then **prints** the updates it would have
sent. Check that each model's latest posts show up and the summaries look right.

Then do one real end-to-end send to a single channel:

```bash
venv/bin/python -m model_monitor check --force --model "Amber Hayes"
```

Her channel should receive an update about her latest post.

> Note: the first normal `check` for any account silently records its existing
> posts without sending anything — channels only get posts made after setup.
> That's expected.

## 7. Schedule it (runs every 15 minutes, even after reboot)

```bash
# Fill in the absolute repo path automatically and install the schedule:
sed "s|__REPO_PATH__|$(pwd)|g" launchd/com.agency.model-monitor.plist \
  > ~/Library/LaunchAgents/com.agency.model-monitor.plist
launchctl load ~/Library/LaunchAgents/com.agency.model-monitor.plist
```

Check it's running:

```bash
launchctl list | grep model-monitor   # should print a line
tail -f logs/monitor.log              # one summary line per cycle
```

To change the interval, edit `StartInterval` (seconds) in
`~/Library/LaunchAgents/com.agency.model-monitor.plist`, then
`launchctl unload` + `launchctl load` it again.

To stop it: `launchctl unload ~/Library/LaunchAgents/com.agency.model-monitor.plist`

> The Mac must be awake for checks to run. If it's a laptop that sleeps,
> either keep it plugged in with `caffeinate` / Amphetamine, or run this on an
> always-on machine. Missed cycles are harmless — the next run picks up
> anything new (up to 48h old).

## Adding or removing a model later

Just edit `config/models.yaml` (create her channel + get its chat ID first,
as in step 2). The next cycle picks it up automatically; her existing posts
are seeded silently, so nothing floods the new channel.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Configuration problem: ...` on start | Missing/placeholder key in `.env`, or a model entry missing `telegram_chat_id` — the message says which |
| `send-test` FAIL: `chat not found` | Wrong chat ID (must be the `-100...` number) |
| `send-test` FAIL: `not enough rights` | Bot isn't an admin of that channel, or can't post |
| `fetch failed: ... HTTP 402/403` | Apify credit exhausted or token invalid |
| A model's posts stopped appearing | She went private/renamed her account — see warnings in `logs/monitor.log` |
| Nothing in `logs/monitor.log` | launchd job not loaded, or wrong paths in the plist |
