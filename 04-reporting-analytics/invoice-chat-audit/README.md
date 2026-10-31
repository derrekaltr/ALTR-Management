# ALTR Invoicing Communication Audit

Re-runnable pipeline that parses Telegram Desktop **HTML** exports of the
`<Model> x ALTR` group chats, extracts all invoicing-related conversation,
reconstructs invoice cycles (issued → follow-ups → escalation → payment
signal), and produces the audit report in `report/invoicing-audit.md`.

## Run

```sh
./run.sh "/path/to/Telegram Export"
```

The export dir must contain one folder per chat, each with `messages.html`
(+ `messages2.html`, … if paginated). Stages:

1. `scripts/parse_export.py` — HTML → `data/parsed/<chat>.jsonl` (stdlib only,
   no dependencies). Handles joined-message sender carry-forward, forum-topic
   resolution via the reply graph, media, reactions, forwards.
2. `scripts/extract_invoicing.py` — keyword + context-window extraction →
   `data/invoicing/<chat>.jsonl` and a **redacted** readable transcript
   `data/invoicing/<chat>.md`. Keyword sets live in `config/keywords.py`.
3. `scripts/build_cycles.py` — event classification → `data/cycles/cycles.csv`
   (one row per invoice cycle, every number traceable to message ids).
4. `scripts/verify.py` — invariants: parse counts vs raw HTML, extraction
   recall, PII-redaction leak check, `data/` never tracked by git.

The final report is written by reading `data/invoicing/*.md` +
`data/cycles/cycles.csv` (LLM/human analysis pass) — payment detection is an
evidence flag, not a verdict: wire/Zelle payments can complete with no chat
trace.

## Privacy

Raw exports are referenced in place and never copied into the repo. All of
`data/` is gitignored. Anything committed (this report) passes through
`config/redact.py`, which strips bank account/routing numbers, phone numbers,
and non-agency emails. Sender→role mapping is in `config/roles.py`.
