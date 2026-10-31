# Contact Enricher

Reads your iMessage history, works out who each unsaved person is, and creates
macOS Contacts (which sync to iPhone) with AI-written notes you can edit.

**It only ever creates new contacts.** Anyone already in Contacts is excluded at
extraction time and re-checked again at write time. Nothing existing is modified.

## Business categories

Each new contact gets its business line in the **Company** field:

| Category | Signals in conversation |
|---|---|
| `ALTR Media Group` | Music/track promotion, driving traffic to a brand, business, or creator |
| `ALTR MGMT` | OnlyFans management — earnings screenshots, revenue percentage splits, account management |
| `ALTR Services` | IG unbans, recoveries, shadow-ban removal, IG restrictions, TikTok verifications/unbans |
| `Personal` | No business context (no Company set) |

Details go in the contact's Notes under an `═══ Auto-notes (Claude) ═══` marker.
Anything you type **above** that marker is preserved on future runs.

## Requirements

- Terminal needs **Full Disk Access** (to read `~/Library/Messages/chat.db`)
- Terminal needs **Automation → Contacts** permission (macOS prompts once on first write)
- `claude` CLI on PATH (uses your existing subscription — no API key)

## Usage

```bash
# 1. Extract conversations for unsaved handles (default: 20+ msgs, 3+ each way)
python3 extract.py

# 2. Classify them with Claude
python3 analyze.py --parallel 4

# 3. Dry run — writes data/review.md, touches nothing
python3 write_contacts.py

# 4. Review data/review.md, then create the contacts
python3 write_contacts.py --apply
```

Or the whole pipeline: `./run.sh` (dry run) / `./run.sh --apply`.

### Capturing names from short conversations

For threads too small for full analysis, but where the person gave their name:

```bash
python3 namescan.py              # dry run → data/name_candidates.json
python3 namescan.py --from-file --apply
```

Creates minimal name + number contacts.

### Scheduling

```bash
./install-schedule.sh            # daily at 4:30am
launchctl start com.altr.contact-enricher   # run once now
```

Runs are incremental: only conversations with new messages are re-analyzed, and
only the auto-notes block is refreshed.

## Useful flags

- `extract.py --min-messages N --min-each-way N` — change the qualifying threshold
- `extract.py --handles "+15551234567"` — target specific people
- `extract.py --force` — re-extract everything
- `write_contacts.py --limit N` — create only the first N (good for a test batch)
- `write_contacts.py --include-personal` — also create Personal/Unknown contacts

## Files

| Path | Purpose |
|---|---|
| `common.py` | DB snapshots, AddressBook matching, phone normalization, `attributedBody` decoder |
| `extract.py` | chat.db → `data/dossiers/*.json` |
| `analyze.py` | dossiers → `data/analyses/*.json` via `claude -p` |
| `write_contacts.py` | analyses → `data/review.md` and macOS Contacts |
| `namescan.py` | name capture from low-volume threads |
| `data/` | gitignored — message content never gets committed |

## Privacy

`data/` holds message excerpts and personal details and is gitignored. Conversation
content is sent to Claude for classification. Databases are snapshotted to a temp
directory before reading, so the live Messages/Contacts databases are never locked
or written to.
