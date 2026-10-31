# Weekly client analyst brief — week ending 2026-10-30

You are one of 12 parallel analysts. Each of you owns ONE client chat. Work only from
the repo at `/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro`
(run all commands from there; do not cd elsewhere).

## Window

- **window_start:** `2026-10-16T09:06:40-04:00` (previous fetch)
- **window_end:**   `2026-10-30T09:05:30-04:00` (this fetch)
- **week_ending:**  `2026-10-30`
- This is a **TWO-WEEK window** (no run happened on 10/23). Do not call it "this week" in
  prose; say "this window" or "the last two weeks". When comparing counts to prior weeks,
  remember the denominator doubled.
- Prior findings exist for most clients in `data/weeks/2026-10-16/<slug>.json` (one-week
  window 10/09→10/16) and the carry-forward state in `data/state/<slug>.json` has
  `as_of: 2026-10-16`. Those are purely pre-window history this time; age carried items
  from their original `first_raised` / `date` fields.

## Inputs to read (all of them, fully)

1. `data/chats/<slug>.jsonl` — the FULL file. Each line is `{id, ts, sender, text, ...}` or a
   service event `{service: true, event, ts}`. Read every in-window row verbatim; skim full
   history for recurring patterns and for the first-raised dates of carried items.
2. `config/team.yaml` — employee + vendor aliases. Attribute by alias. Vendor chat-team
   members roll up to the vendor group name (e.g. "Lauryn chat team").
3. The client's entry in `config/clients.yaml` (client-side aliases).
4. `data/state/<slug>.json` if it exists — carry-forward memory: open complaints, pending/
   overdue commitments, payment history, priorities, health history, client-asks trend,
   churn watch, ALTR silence tracker.
5. `data/weeks/2026-10-16/<slug>.json` if it exists — last published findings (format example).
6. `src/schema.py` — required fields and enums.

## Noise to exclude

- **"Antonio Veritrade"** is a team/system test account. On 10/21 it posted
  "test message for new system (disregard)" 6–8 times in most chats, and Mayson posted a
  heads-up about it. **Exclude these test messages from team_messages, from the
  silence/response-time analysis, and from "ALTR message share" calculations.** Mention
  the count once in `week_stats.note`. Mayson's heads-up itself is a real team message.
- Service events (joins/leaves/pins/topic changes) are not messages, but DO report
  meaningful ones (member removed, client left the group) as findings.

## Security rule (non-negotiable)

Clients paste passwords, 2FA/backup codes, login emails, phone numbers used as logins,
and bank/routing numbers into these chats. The dashboard you are feeding is published on
the open web. **Never copy a secret into any field.** Describe it instead:
"client posted the IG password in the group (10/18, msg id 2031)". If an evidence quote
contains a secret, truncate the quote before the secret or replace just the secret with
`[REDACTED]`. Also flag every credential posted in-window as a complaint/commitment
(owner: whoever should rotate it or move it to a private channel).

## What to write

### A. `data/weeks/2026-10-30/<slug>.json` (create the dir if needed)

Follow `src/schema.py` exactly. Fields:

- `client`, `slug`, `week_ending: "2026-10-30"`.
- `summary` — dense narrative of the window: what happened, what closed, what broke,
  what is still open with ages, churn read, security. Plain prose, specific dates.
- `health` — `{score 0-100, trend up|down|flat|new, rationale}`. Compare to the last
  published score (in state `health_history`). The rationale must say what moved it.
- `reminders` — times the CLIENT had to nudge/re-ask ALTR. Items:
  `{employee, topic, count, first_date, last_date, days_outstanding, chased_this_week,
  note, evidence:[{quote, who, date}]}`. `employee` = the ALTR person/vendor who owns it
  (use canonical team.yaml names; compound owners like "Mayson / Vivek" are fine).
- `complaints` — `{issue, status new|in_progress|resolved|recurring, first_raised,
  days_open, owner, escalate_to?, severity low|medium|high|critical, evidence:[...]}`.
  Carry forward every still-open complaint from state (status `recurring` if raised again
  this window or `in_progress` if just still open); mark `resolved` only with evidence.
- `commitments` — things ALTR said it would do. `{what, who, date, due?, status
  done|pending|overdue, days_outstanding, escalate_to?, evidence:[...]}`. Carry forward open
  ones from state; a promise with no delivery proof after ~7 days (or past its stated due
  date) is `overdue`.
- `payments` — `{note, date, invoice_period?, late bool, paid bool, evidence:[...]}` for
  every invoice/payment event in-window plus the status of anything outstanding. Note
  heads-up timing, invoice timing vs the 1st/15th cadence, time-to-pay, errors, disputes.
  Remember: **fast payment is not a health signal on this book** — several clients paid
  instantly right before quitting.
- `client_priorities` — list of strings, what the client cares about, in their words where possible.
- `suggestions` — list of strings, concrete actions for named ALTR people.
- `wins` — list of strings with evidence (dates/quotes). Be honest; empty list is fine.
- `week_stats` — `{messages, client_messages, team_messages, client_asks, service_events,
  note}` for the window (test messages excluded; say so in note). `client_asks` = number of
  distinct things the client asked ALTR for this window. Put the asks trend
  (prior windows from state `client_asks`) and per-person ALTR message counts in `note`.

**Every reminder/complaint/commitment needs dated evidence quotes copied verbatim**
(`who` = exact sender display name, `date` = YYYY-MM-DD). Do not paraphrase inside
`quote`. Do not invent. If something has no evidence, leave it out.

### B. `data/state/<slug>.json` (overwrite with the updated version)

Keep the existing structure (see the current file). Update: `as_of: "2026-10-30"`,
`window_covered`, `open_complaints`, `resolved_last_window`, `open_commitments`,
`broken_commitments`, `completed_recently`, `payment_history` (append), `payment_risk`,
`client_priorities`, `health_history` (append), `week_stats_history` (append),
`engagement_trend` (append), `client_asks` (append), `churn_watch`, `altr_silence_tracker`
(last message date + days silent per ALTR person as of window_end, including Derrek),
`notes` (status paragraph + "predictions to check next week"). If no state file exists,
create one with those keys.

### C. Churn read (fold into summary / health rationale / churn_watch)

Known pre-exit signature on this book, check each explicitly:
1. Owner (Derrek) silent 30+ days in the chat.
2. A results/revenue question answered with a call offer instead of a written answer.
3. A long-promised deliverable with no written proof.
4. Most ALTR messages in the window are billing.
Plus: **client asks trending to zero** from a previously demanding client is the alarm;
zero asks + prompt payment = settling up to leave. Also note any request for exports,
logins back, data, or mention of other agencies/going solo.

## Final reply to the orchestrator (keep it under ~400 words)

Report: health score + trend + one-line why; top 3 open items with owner and age; any
commitments broken this window; payments status; credentials/secrets posted in-window
(described, not quoted) and whether you had to redact anything; per-ALTR-person notes for
the employee rollup (who did well, who dropped what — include Derrek/Nick/Noah items
separately under "owner-level"); 2–3 verbatim employee quotes with dates that illustrate
good or poor behaviour (for the Team tab); any sender you could not attribute; and confirm
both files were written and `python3 src/schema.py data/weeks/2026-10-30/<slug>.json` passed.
