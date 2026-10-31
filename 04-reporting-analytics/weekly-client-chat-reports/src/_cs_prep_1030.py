"""One-off prep for the 2026-10-30 CS gap run: write the dated brief, create the
output dir, and print prior statuses + chat recency so clients can be assigned
to analyst agents."""
import glob
import json
import os

DATE = "2026-10-30"
PREV = "data/analysis/cs-gaps-2026-10-16"

src = open(".claude/skills/cs-gap-analysis/analyst-brief.md").read().replace("{{DATE}}", DATE)
os.makedirs(".context", exist_ok=True)
open(".context/cs-gap-brief.md", "w").write(src)
os.makedirs(f"data/analysis/cs-gaps-{DATE}", exist_ok=True)
print("brief written; DATE occurrences:", src.count(DATE))

print("\n--- prior run statuses ---")
for f in sorted(glob.glob(PREV + "/*.json")):
    if os.path.basename(f).startswith("_"):
        continue
    d = json.load(open(f))
    print(f"{d.get('slug'):28} {d.get('status'):9} last_client={d.get('last_client_message')}  {str(d.get('status_reason',''))[:100]}")

print("\n--- chat recency ---")
for f in sorted(glob.glob("data/chats/*.jsonl")):
    lines = open(f).read().splitlines()
    msgs = [json.loads(l) for l in lines]
    last = msgs[-1] if msgs else {}
    since = [m for m in msgs if m.get("ts", "") >= "2026-10-16"]
    print(f"{os.path.basename(f):32} n={len(msgs):5} since_1016={len(since):4} last={last.get('ts','')[:16]} by={last.get('sender','')}")
