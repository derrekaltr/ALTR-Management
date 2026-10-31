import json, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slugs = sys.argv[2:] or ["amber-haze-x-altr","alex-paige-moore-x-altr","vicky-x-altr","paige-x-altr","chey-mai-x-altr","kaitlynn-x-altr"]
since = sys.argv[1] if len(sys.argv) > 1 else "2026-10-02"
for s in slugs:
    p = os.path.join(ROOT, "data/chats", s + ".jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    print("=" * 20, s, "n=", len(rows), "first", rows[0].get("ts"), "last", rows[-1].get("ts"))
    new = [r for r in rows if str(r.get("ts", "")) >= since]
    print("since", since, ":", len(new))
    show = new if new else rows[-5:]
    for r in show:
        t = (r.get("text") or "").replace("\n", " / ")
        extra = " ".join(f"{k}={r[k]}" for k in ("service", "event", "media") if r.get(k))
        print(r.get("id"), r.get("ts"), "|", r.get("sender"), "|", t[:600], extra)
