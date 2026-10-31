import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
msgs = [json.loads(l) for l in (ROOT / "data/chats/mila-x-altr.jsonl").read_text().splitlines() if l.strip()]
texts = [(m.get("ts", "")[:10], m.get("text") or "") for m in msgs if not m.get("service")]
f = json.loads((ROOT / "data/weeks/2026-10-16/mila-x-altr.json").read_text())
bad = 0
for sec in ("reminders", "complaints", "commitments", "payments"):
    for item in f[sec]:
        for ev in item.get("evidence", []):
            q, d = ev["quote"], ev["date"]
            if not any(q in t and ts == d for ts, t in texts):
                bad += 1
                print("NOT FOUND:", sec, d, q[:80])
print("bad quotes:", bad)
json.loads((ROOT / "data/state/mila-x-altr.json").read_text())
print("state json ok")
