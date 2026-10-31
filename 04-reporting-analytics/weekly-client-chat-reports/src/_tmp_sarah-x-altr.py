import json
from collections import Counter
from datetime import datetime

S = datetime.fromisoformat("2026-10-09T09:05:57-04:00")
E = datetime.fromisoformat("2026-10-16T09:06:40-04:00")
rows = [json.loads(l) for l in open("data/chats/sarah-x-altr.jsonl")]
win = [r for r in rows if S <= datetime.fromisoformat(r["ts"]) <= E]
svc = [r for r in win if r.get("service")]
msgs = [r for r in win if not r.get("service")]
c = Counter(r["sender"] for r in msgs)
print("total", len(msgs), "service", len(svc), [s.get("event") for s in svc])
print(c)
client = sum(v for k, v in c.items() if k == "Sarah H")
print("client", client, "team", len(msgs) - client)
print("ids", msgs[0]["id"], msgs[-1]["id"], "len rows", len(rows))
ids = [r["id"] for r in rows]
print("missing ids in window range", [i for i in range(msgs[0]["id"], msgs[-1]["id"] + 1) if i not in ids])
last = {}
for r in rows:
    if not r.get("service"):
        last[r["sender"]] = r["ts"]
for k, v in sorted(last.items(), key=lambda x: x[1]):
    print(k, v)
