"""Dump a readable Lauryn transcript + metrics for the 2026-09-25 CS gap run."""
import json
import os

PATH = "data/chats/lauryn-x-altr.jsonl"
OUT = "data/analysis/cs-gaps-2026-09-25/_transcript_lauryn.txt"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

rows = [json.loads(l) for l in open(PATH)]
print("rows", len(rows))
keys = set()
for r in rows:
    keys |= set(r)
print("keys", sorted(keys))

lines = []
for r in rows:
    ts = (r.get("ts") or "")[:16].replace("T", " ")
    who = r.get("sender") or "SERVICE"
    txt = (r.get("text") or "").replace("\n", " \\n ")
    if len(txt) > 420:
        txt = txt[:420] + " …[TRUNC %d chars]" % len(txt)
    extra = ""
    if r.get("service"):
        extra += " [SERVICE:%s]" % r.get("event")
    if r.get("media"):
        extra += " [media:%s]" % r.get("media")
    if r.get("reply_to"):
        extra += " [re:%s]" % r.get("reply_to")
    lines.append("%s | %s | %s%s | id=%s" % (ts, who, txt, extra, r.get("id")))

with open(OUT, "w") as fh:
    fh.write("\n".join(lines))
print("wrote", OUT, os.path.getsize(OUT), "bytes,", len(lines), "lines")
