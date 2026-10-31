import json

rows = [json.loads(l) for l in open("data/chats/sarah-x-altr.jsonl")]
texts = {}
for r in rows:
    if not r.get("service"):
        texts.setdefault((r["sender"], r["ts"][:10]), []).append(r.get("text", ""))
f = json.load(open("data/weeks/2026-10-16/sarah-x-altr.json"))


def walk(o):
    if isinstance(o, dict):
        if "quote" in o and "who" in o:
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


bad = 0
for ev in walk(f):
    cands = texts.get((ev["who"], ev["date"]), [])
    if not any(ev["quote"] in t for t in cands):
        bad += 1
        print("MISS", ev["who"], ev["date"], ev["quote"][:80])
        for r in rows:
            if r.get("id") == 1785:
                print(repr(r["sender"]), repr(r["ts"]), repr(r["text"][:200]))
print("misses", bad)
