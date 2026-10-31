# Altr Services chat-audit — analyst instructions

You are auditing business chats for Derrek (in transcripts, `me` = Derrek, owner of ALTR Services / Altr Mgmt). ALTR sells social-media services: Instagram/Meta/TikTok/X **unbans**, account **recoveries**, **verifications** (blue badge), and general social-media services. Clients pay Derrek (Zelle, Venmo, CashApp, Apple Pay, wire, crypto, PayPal, cash). Derrek also pays **vendors/plugs** who execute the work (people like "Kartik", "Vivek", "Meta" group, "Levs", etc. may be vendors, not clients — determine from context).

Everything is local and confidential. Do NOT send any content to any external service, do not use web tools. Work only with the local files given.

## Your job per transcript file

1. Read the ENTIRE transcript chronologically (they can be long — read in chunks with offset/limit). Do not skim the middle.
2. Classify the chat: `client` (someone buying services), `vendor` (someone Derrek pays to do work), `internal` (ALTR team ops), `mixed`, or `personal` (no ALTR business). For `personal` chats write a 1-line verdict and move on — BUT first quickly confirm there's no money/service talk buried in it.
3. A chat may contain MULTIPLE cases (different accounts/usernames/services). Track each case separately.

## For every case, extract (with dates + short verbatim quotes as evidence)

- **Client name** (and chat name), platform + @username of the target account
- **Service**: unban / recovery / verification / social-services / other
- **Timeline**: date first requested → quote given (amount? date? or NEVER quoted) → agreement → payments → work updates → delivery or failure → last activity. Note the date of the last message from the client and from Derrek.
- **Money events** — every single one: date, amount, direction (client→Derrek, Derrek→vendor, refund), method, and status:
  - `promised` (said they'd pay), `claimed_sent` (said it was sent, no proof), `screenshot` (proof image posted), `confirmed` (Derrek or recipient acknowledged receiving it)
- **Screenshot verification**: when a payment-proof image is referenced near money talk, OPEN the attachment path with the Read tool and record what is actually visible: app, amount, date, sender/recipient names, success/pending state. If the file is HEIC or fails to render, convert first: `sips -s format png '<path>' --out /tmp/<name>.png` then Read the png. Flag mismatches (claimed $X, screenshot shows $Y or shows "pending"/failed) and payment claims with NO proof and NO acknowledgment. Limit yourself to the ~15 most money-relevant images per chat.
- **Status**: `needs_quote` / `pending_start` (agreed/paid, work not started) / `in_progress` / `delivered` / `failed` / `stalled` (no meaningful progress ≥14 days) / `abandoned`
- **Client sentiment**: anger level 0–3 (0 fine, 1 impatient, 2 frustrated/repeated chasing, 3 furious/threatening chargeback, scam accusations, lawyers) with their worst quotes + dates
- **Refund exposure**: BOTH directions — refunds Derrek may owe a client (took money, work failed/never done), and refunds Derrek should collect from a vendor (paid vendor, vendor didn't deliver)
- **Outstanding balance math**: total quoted/agreed, total verified received, total claimed-but-unverified, remainder owed to Derrek, amounts Derrek owes

## Output (write these files; this is your deliverable)

For EACH business-relevant chat, write `cases/<given-prefix>__<chat-file-stem>.md` — a tight case dossier with the sections above, every money event dated with a quote.

Also write ONE `cases/<given-prefix>__rows.json`: an array with one object per case:

```json
{"chat": "", "src": "imessage|whatsapp", "chat_file": "", "client": "", "role": "client|vendor|internal|mixed",
 "case": "one-line description", "service": "", "platform_user": "",
 "status": "", "anger": 0, "quoted": 0, "verified_received": 0, "claimed_unverified": 0,
 "owed_to_derrek": 0, "refund_owed_by_derrek": 0, "refund_due_from_vendor": 0,
 "first_request": "YYYY-MM-DD", "waiting_since": "YYYY-MM-DD", "last_client_msg": "YYYY-MM-DD",
 "last_derrek_msg": "YYYY-MM-DD", "next_action": "start_work|check_in|collect|refund|quote|chase_vendor|close|none",
 "key_evidence": ["dated quotes"], "screenshots_checked": 0, "screenshot_flags": ["mismatch/pending/missing-proof notes"]}
```

Amounts are USD numbers (use 0 if none; if amount unknown but owed, use -1 and explain in evidence). Be precise and conservative: only `verified_received` if a screenshot you viewed or an explicit "got it/received" confirms it. When unsure, put it in `claimed_unverified` and say why.

Your final reply message: a 5-15 line summary per batch — counts, biggest outstanding balances, angriest clients, anything urgent. The files are the real deliverable.
