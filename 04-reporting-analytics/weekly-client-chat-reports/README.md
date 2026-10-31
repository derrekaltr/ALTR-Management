# ALTR Weekly Client Reports

Turns weekly Telegram group-chat exports into a single HTML dashboard: client
health, repeated reminders, unresolved complaints, commitments vs. delivery,
payment behavior, and a per-employee rollup.

## Weekly workflow

Open this project in Claude Code / Conductor and run **`/weekly-report`**.
That's it — chats are pulled straight from Telegram (no manual exports) and
you get `reports/<week>/index.html`, which opens in any browser.

### One-time Telegram API setup

1. Go to https://my.telegram.org → *API development tools* → create an app
   (any name) and copy the **api_id** and **api_hash**.
2. `cp config/telegram.example.ini config/telegram.ini` and paste them in.
3. Run `python3 src/fetch.py` in a terminal. The first run asks for your phone
   number and a login code (sent to your Telegram app). After that it's
   automatic. `python3 src/fetch.py --list` shows which groups matched.

New client? Add their group to `config/clients.yaml` (folder = exact group
title) and their handle to `client_aliases`.

Fallback: manual Telegram Desktop HTML exports still work —
`/weekly-report <path to export folder>` uses `src/ingest.py` instead.

## Pieces

- `src/ingest.py` — parses the Telegram HTML exports into `data/chats/*.jsonl`
- `.claude/skills/weekly-report/` — the analysis workflow (Claude reads each
  client's chat + prior state, writes findings JSON per `src/schema.py`)
- `src/render.py` + `src/templates/dashboard.html.j2` — renders the dashboard
- `config/team.yaml`, `config/clients.yaml` — who is team vs. client (edit these!)
- `data/state/` — carry-forward memory per client (open issues, payment history)

`data/` and `reports/` are gitignored — client chat content never leaves this
machine and never enters git.

## Setup

```
pip3 install --user -r requirements.txt
```
