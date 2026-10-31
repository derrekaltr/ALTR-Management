import json
from collections import Counter

P = "data/chats/shayna-x-altr.jsonl"
msgs = [json.loads(l) for l in open(P)]
S, E = "2026-10-09T09:05:57", "2026-10-16T09:06:40"

print("== full text of selected ids ==")
for m in msgs:
    if m["id"] in (1016, 1045, 1051) or 1000 <= m["id"] <= 1015 or m["id"] == 1029:
        print(m["id"], m["ts"], m.get("sender"), m.get("service"), m.get("event"), repr(m.get("text")), m.get("media"))

print("== window stats ==")
win = [m for m in msgs if S <= m["ts"][:19] <= E]
real = [m for m in win if not m.get("service") and m.get("sender")]
svc = [m for m in win if m.get("service")]
print("total in window", len(win), "service", len(svc), "real", len(real))
c = Counter(m["sender"] for m in real)
print(c)

print("== last msg per sender (full history) ==")
last = {}
for m in msgs:
    if not m.get("service") and m.get("sender"):
        last[m["sender"]] = (m["ts"], (m.get("text") or "")[:100])
for k, v in sorted(last.items(), key=lambda x: x[1][0]):
    print(k, v)

print("== keyword search full history ==")
for kw in ["shaynasworld", "link in bio", "linktree", "link.me", "xli.ink", "domain", "flag", "leak", "sent!", "received", "zelle", "@fonta", "Vivek"]:
    hits = [(m["id"], m["ts"][:10], m.get("sender")) for m in msgs if kw.lower() in (m.get("text") or "").lower()]
    print(kw, len(hits), hits[-6:])
