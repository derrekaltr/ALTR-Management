import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in sorted(glob.glob(os.path.join(ROOT, "data/chats/*.jsonl"))):
    rows = [json.loads(l) for l in open(p) if l.strip()]
    hits = []
    for r in rows:
        t = r.get("text") or ""
        if ("Content folder" in t or "Social Media Director" in t or r.get("event") in ("ChannelMigrateFrom", "ChatDeleteUser", "ChatAddUser")):
            hits.append((r.get("ts", "")[:10], r.get("sender"), r.get("event"), t[:70].replace("\n", " ")))
    hits = [h for h in hits if h[0] >= "2026-08-25"]
    if hits:
        print("==", os.path.basename(p), "last:", rows[-1].get("ts", "")[:10])
        for h in hits:
            print("  ", h)
# raw kaitlynn rows
print(open(os.path.join(ROOT, "data/chats/kaitlynn-x-altr.jsonl")).read()[:400])
print(open(os.path.join(ROOT, "data/chats/kaitlynn-x-altr.jsonl")).read().splitlines()[-1])
print(open(os.path.join(ROOT, "data/state/_last_run.json")).read())
