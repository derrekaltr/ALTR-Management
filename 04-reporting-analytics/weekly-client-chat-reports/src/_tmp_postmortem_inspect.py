"""Inspect churned-client chats: sizes, last messages, prior analysis + state files."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUGS = ["amber-haze", "alex-paige-moore", "vicky", "paige", "kaitlynn", "chey-mai"]

for s in SLUGS:
    slug = f"{s}-x-altr"
    p = os.path.join(ROOT, "data/chats", slug + ".jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    print(f"== {slug}: {len(rows)} msgs, first {rows[0].get('ts')}, last {rows[-1].get('ts')}")
    st = os.path.join(ROOT, "data/state", slug + ".json")
    print("   state:", os.path.exists(st), os.path.getsize(st) if os.path.exists(st) else "")
    pr = os.path.join(ROOT, "data/analysis/cs-gaps-2026-09-25", slug + ".json")
    print("   prior:", os.path.getsize(pr) if os.path.exists(pr) else "missing")
    senders = {}
    for r in rows:
        senders[r.get("sender")] = senders.get(r.get("sender"), 0) + 1
    print("   senders:", senders)
