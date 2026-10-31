"""Verify evidence quotes in the 2026-10-16 lauryn findings appear verbatim in the chat."""
import json

msgs = [json.loads(l) for l in open("data/chats/lauryn-x-altr.jsonl")]
f = json.load(open("data/weeks/2026-10-16/lauryn-x-altr.json"))
bad = 0
for sec in ("reminders", "complaints", "commitments"):
    for item in f[sec]:
        for ev in item.get("evidence", []):
            q = ev["quote"]
            if "[REDACTED]" in q:
                continue
            hit = [m for m in msgs if q in (m.get("text") or "") and m.get("sender") == ev["sender"]
                   and m["ts"].startswith(ev["date"])]
            if not hit:
                bad += 1
                print("MISS", sec, ev)
print("misses:", bad)
for m in msgs:
    if m.get("id") == 1847:
        t = m["text"]
        i = t.find("topped")
        print(repr(t[i:i + 70]), m["sender"], m["ts"])
