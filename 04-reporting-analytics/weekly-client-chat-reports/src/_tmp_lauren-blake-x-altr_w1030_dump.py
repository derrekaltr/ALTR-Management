"""Dump Lauren Blake chat for the 10/30 CS gap analysis.

Usage: python3 src/_tmp_lauren-blake-x-altr_w1030_dump.py [since_date] [redact=1]
Prints id / ts / sender / text. Credential-looking lines are masked.
"""
import json
import re
import sys

SLUG = "lauren-blake-x-altr"
since = sys.argv[1] if len(sys.argv) > 1 else "2026-07-03"
until = sys.argv[2] if len(sys.argv) > 2 else "2099-01-01"

CRED_RE = re.compile(
    r"(password|passw|pw\b|pass:|login|user(name)?\s*[:\-]|2fa|code\s*[:\-]?\s*\d{4,}|\b\d{6}\b|backup code)",
    re.I,
)

rows = [json.loads(l) for l in open(f"data/chats/{SLUG}.jsonl", encoding="utf-8")]
print("total", len(rows), "first", rows[0]["ts"], "last", rows[-1]["ts"])
for r in rows:
    d = r["ts"][:10]
    if d < since or d > until:
        continue
    if r.get("service"):
        print(f"#{r['id']} {r['ts'][:16]} [SERVICE] {r.get('event')}")
        continue
    t = (r.get("text") or "").replace("\n", " / ")
    if CRED_RE.search(t):
        t = "[CREDENTIAL-LIKE CONTENT MASKED; len=%d] " % len(t) + t[:40].split(":")[0]
    m = " [media:%s]" % r.get("media") if r.get("media") else ""
    rp = f" (re #{r['reply_to']})" if r.get("reply_to") else ""
    print(f"#{r['id']} {r['ts'][:16]} {r['sender']}{rp}: {t}{m}")
