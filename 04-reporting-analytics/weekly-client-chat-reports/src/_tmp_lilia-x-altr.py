import json, collections
from datetime import datetime
S = datetime.fromisoformat("2026-10-09T09:05:57-04:00")
E = datetime.fromisoformat("2026-10-16T09:06:40-04:00")
msgs = [json.loads(l) for l in open("data/chats/lilia-x-altr.jsonl")]
win = [m for m in msgs if S <= datetime.fromisoformat(m["ts"]) <= E]
svc = [m for m in win if m.get("service")]
ns = [m for m in win if not m.get("service")]
c = collections.Counter(m["sender"] for m in ns)
print("window non-service", len(ns), c, "service", [(m["event"], m["ts"]) for m in svc])
last = {}
for m in msgs:
    if not m.get("service"):
        last[m["sender"]] = m["ts"]
for k, v in sorted(last.items(), key=lambda x: x[1]):
    print(k, v)
for m in msgs:
    t = (m.get("text") or "").lower()
    if "earnings" in t or "performance report" in t:
        print("EARN", m["ts"], m["sender"], t[:100])
ids = [m["id"] for m in msgs]
print("id gaps late:", [i for i in range(1225, ids[-1]) if i not in ids])
