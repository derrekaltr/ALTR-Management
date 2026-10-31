# Monthly Content Drop Automation (Content Snare + AI ideas)

Automates your agency's monthly content workflow:

1. **AI-generated shoot ideas per client**, tailored to their comfort level
   (Non Nude / Topless / Full Nude) and niche.
2. **A Content Snare request per client**, created + published from a template,
   with a due date and Content Snare's **automatic reminders** doing the chasing.
3. **A ready-to-send message per client** (in `outbox/`) containing their ideas
   and their upload link.

## How the pieces fit

| Piece | Role |
|---|---|
| `clients.csv` | Your roster: name, email, comfort level, niche, notes |
| Claude API | Generates fresh, comfort-level-appropriate ideas each month |
| GPTease (optional) | No public API — paste its output into `ideas_override/` and the script uses that instead of Claude |
| Content Snare | Collects the actual content uploads and sends automated reminders |

**Important Content Snare limitation:** the API can only create requests from
pre-built *templates* — you can't inject fresh AI text into the request body per
client. So the fresh ideas travel in the message you send (from `outbox/`), and
the Content Snare request handles upload collection + reminders.

## One-time setup

### 1. In Content Snare

1. **Create 3 request templates** (Templates → New), one per tier — the names
   must match `.env`:
   - `Content Drop — Non Nude`
   - `Content Drop — Topless`
   - `Content Drop — Full Nude`

   Suggested template structure: an instructions section ("check your ideas
   message from us"), then sections like *Idea 1–8* each with a file-upload
   field, plus a "bonus/extra content" upload field.
2. **Set up your reminder schedule** (Settings → Reminders). The default
   schedule already nags politely; customize timing/wording if you want. The
   script assigns the schedule named in `CS_COMMUNICATION_TEMPLATE`.
3. **Create an API application**: avatar menu → Integrations → API → new app.
   - Redirect URL: `http://localhost:8484/callback`
   - Scopes: read + write
   - Copy the client ID/secret into `.env`.
   - Note: API access may require one of Content Snare's higher plans — check
     your plan if the Integrations → API option isn't visible.

### 2. Locally

```bash
cd content-drop-automation
cp .env.example .env      # fill in CS_CLIENT_ID, CS_CLIENT_SECRET, ANTHROPIC_API_KEY
pip install anthropic     # only needed if using Claude for idea generation
python3 cs_auth.py        # one-time browser authorization; saves .tokens.json
```

Fill in `clients.csv` with your real roster. `comfort_level` must be
`non_nude`, `topless`, or `full_nude`.

## Monthly run

```bash
python3 monthly_drop.py            # generates ideas + creates/publishes requests
python3 monthly_drop.py --dry-run  # preview ideas only, no Content Snare calls
```

Per client this:
- generates 8 seasonal shoot concepts within their comfort tier,
- creates + **publishes** a Content Snare request from their tier's template
  (publish = the invite email goes out; reminders then run automatically until
  they finish, per your schedule),
- sets the due date to the last day of the month,
- writes `outbox/YYYY-MM/<client>.md` — the ideas + upload link, ready to paste
  into email/Telegram/your CRM.

## Using GPTease instead of Claude

GPTease has no API, so it can't be fully automated — but you can use it as the
idea source: ask it for the month's ideas per client, then save the output to

```
ideas_override/YYYY-MM/<email-with-dashes>.md   e.g. ideas_override/2026-07/ava-example-com.md
```

The script prefers an override file when it exists and never calls Claude for
that client. (Tip: the same tier prompts in `monthly_drop.py` work well pasted
into GPTease.)

## Scheduling it monthly

Run it on the 1st of each month at 9am with cron:

```bash
crontab -e
# add:
0 9 1 * * cd "/Users/locklyjailbreak/conductor/workspaces/Starter project/delhi/content-drop-automation" && /usr/bin/python3 monthly_drop.py >> run.log 2>&1
```

Reminders after that point are Content Snare's job — no extra scheduling needed.

## Files

- `cs_common.py` — env/token handling + Content Snare API client (OAuth refresh built in)
- `cs_auth.py` — one-time OAuth authorization
- `monthly_drop.py` — the monthly job
- `.tokens.json` — created by `cs_auth.py`; keep private (never commit)
- `outbox/` — generated messages per client per month
- `ideas_override/` — optional hand-written/GPTease ideas that take precedence
