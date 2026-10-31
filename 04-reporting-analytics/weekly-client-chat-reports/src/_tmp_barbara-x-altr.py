import json, sys, collections
since = sys.argv[1] if len(sys.argv) > 1 else "2026-10-09T09:05:57"
until = "2026-10-16T09:06:40"
client = {"Barb Brazil", "Barbara Silva"}
rows = [json.loads(l) for l in open("data/chats/barbara-x-altr.jsonl")]
print("keys sample", sorted(rows[-1].keys()))
n = 0
cnt = collections.Counter()
for m in rows:
    ts = m.get("ts", "")
    if ts < since or ts > until:
        continue
    n += 1
    svc = m.get("service") or m.get("event")
    if not svc:
        cnt[m.get("sender")] += 1
    tag = "C" if m.get("sender") in client else "T"
    extra = ""
    if m.get("media"): extra += f" [media:{m['media']}]"
    if svc: extra += f" [svc:{svc}]"
    if m.get("reply_to"): extra += f" [re:{m['reply_to']}]"
    if m.get("topic"): extra += f" [topic:{m.get('topic')}]"
    print(f"{m['id']} {ts[:19]} {tag} {m.get('sender')}: {(m.get('text') or '')}{extra}")
print("count", n, dict(cnt))
last = {}
for m in rows:
    if m.get("sender"):
        last[m["sender"]] = m["ts"]
print("last per sender", last)
print("last 3 rows", rows[-3:])
