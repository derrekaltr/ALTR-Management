import json, re
rows = [json.loads(l) for l in open("data/chats/barbara-x-altr.jsonl")]
f = json.load(open("data/weeks/2026-10-16/barbara-x-altr.json"))
bad = 0
for sec in ("reminders", "complaints", "commitments", "payments"):
    for it in f[sec]:
        for ev in it.get("evidence", []):
            q = ev["quote"]
            hits = [m for m in rows if m.get("sender") == ev["sender"] and q in (m.get("text") or "") and m["ts"][:10] == ev["date"]]
            if not hits:
                bad += 1
                print("MISS", sec, ev)
raw = open("data/weeks/2026-10-16/barbara-x-altr.json").read().lower()
st = json.load(open("data/state/barbara-x-altr.json"))
print("state ok", st["as_of"], "@gmail" in json.dumps(st), "@yahoo" in json.dumps(st))
print("bad", bad, "leak hits", [s for s in ["@gmail", "@yahoo", "password", "2fa"] if s in raw])
