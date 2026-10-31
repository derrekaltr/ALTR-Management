"""Scratch: CS-gap metric checks for sarah-lloyd-x-altr (2026-10-30 run)."""
import json
from collections import Counter
from datetime import datetime

PATH = "data/chats/sarah-lloyd-x-altr.jsonl"
CLIENT = "Sarah Lloyd"
WINDOW_CLOSE = datetime.fromisoformat("2026-10-30T09:05:30-04:00")
PREV_EXPORT = datetime.fromisoformat("2026-10-16T09:06:40-04:00")

rows = [json.loads(l) for l in open(PATH)]
msgs = [r for r in rows if not r.get("service")]
dt = lambda s: datetime.fromisoformat(s)
cli = [m for m in msgs if m["sender"] == CLIENT]
ours = [m for m in msgs if m["sender"] != CLIENT]

print("total msgs", len(msgs), "client", len(cli), "ours", len(ours))
print("client msgs containing '?':", sum(1 for m in cli if "?" in (m.get("text") or "")))
new = [m for m in msgs if dt(m["ts"]) > PREV_EXPORT]
print("new since prev export:", len(new), [(m["id"], m["sender"], m["ts"][:16]) for m in new])

ts = [dt(m["ts"]) for m in ours] + [WINDOW_CLOSE]
gaps = sorted(((b - a).total_seconds() / 86400, a.isoformat()[:16], b.isoformat()[:16])
              for a, b in zip(ts, ts[1:]))[::-1]
print("top team silences incl. trailing gap:", [(round(g[0], 2), g[1], g[2]) for g in gaps[:4]])

last = {}
for m in ours:
    last[m["sender"]] = m["ts"][:10]
for s, d in sorted(last.items(), key=lambda x: x[1]):
    print(f"  last post {s:28s} {d}  ({(WINDOW_CLOSE.date() - dt(d + 'T00:00:00-04:00').date()).days}d)")
print("client last:", cli[-1]["ts"], "client last self-initiated ask: 2026-10-12 (hand)")
print("client msgs by month:", Counter(m["ts"][:7] for m in cli))
