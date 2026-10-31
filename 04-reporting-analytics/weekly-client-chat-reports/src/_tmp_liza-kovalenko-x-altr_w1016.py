import json
from datetime import datetime
from collections import Counter

PATH = "data/chats/liza-kovalenko-x-altr.jsonl"
S = datetime.fromisoformat("2026-10-09T09:05:57-04:00")
E = datetime.fromisoformat("2026-10-16T09:06:40-04:00")
msgs = [json.loads(l) for l in open(PATH)]
print("keys:", sorted(msgs[-1].keys()))
c = Counter()
for m in msgs:
    ts = datetime.fromisoformat(m["ts"])
    if ts.tzinfo is None:
        print("naive ts", m["ts"]); break
    if not (S < ts <= E):
        continue
    if m.get("service"):
        print(m["id"], m["ts"], "[SERVICE]", m.get("event"), {k: v for k, v in m.items() if k not in ("id", "ts", "service", "event")})
        continue
    c[m.get("sender")] += 1
    print("----", m["id"], m["ts"], m.get("sender"), "reply_to", m.get("reply_to"), m.get("media") or "")
    print(m.get("text"))
print(c, sum(c.values()))
print("LAST", msgs[-1]["id"], msgs[-1]["ts"])
# last post by sender
last = {}
for m in msgs:
    if not m.get("service"):
        last[m.get("sender")] = m["ts"][:10]
for k, v in sorted(last.items(), key=lambda x: x[1]):
    print(v, k)
