import json
L = [json.loads(l) for l in open("data/chats/haileigh-cox-x-altr.jsonl")]
F = json.load(open("data/weeks/2026-10-16/haileigh-cox-x-altr.json"))
bad = 0
for sec in ("reminders", "complaints", "commitments", "payments"):
    for item in F[sec]:
        for ev in item.get("evidence", []):
            hits = [m for m in L if m.get("sender") == ev["sender"] and m["ts"][:10] == ev["date"]
                    and ev["quote"] in (m.get("text") or "")]
            if not hits:
                bad += 1
                print("MISS", sec, ev["date"], ev["sender"], ev["quote"][:70])
print("misses:", bad)
