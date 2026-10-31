import json, sys
from datetime import datetime

PATH = "data/chats/liza-kovalenko-x-altr.jsonl"
since = sys.argv[1] if len(sys.argv) > 1 else "2026-09-20"
msgs = [json.loads(l) for l in open(PATH)]
byid = {m["id"]: m for m in msgs}
for m in msgs:
    if m["ts"][:10] < since:
        continue
    if m.get("service"):
        print(f'{m["id"]} {m["ts"][:16]} [SERVICE] {m.get("event")}')
        continue
    t = (m.get("text") or "").replace("\n", " / ")
    rt = m.get("reply_to")
    rtxt = ""
    if rt and rt in byid:
        r = byid[rt]
        rtxt = f' (re #{rt} {r.get("sender","svc")}: {(r.get("text") or r.get("event") or "")[:50]!r})'
    media = f' <{m["media"]}>' if m.get("media") else ""
    print(f'{m["id"]} {m["ts"][:16]} {m.get("sender")}: {t[:400]}{media}{rtxt}')
