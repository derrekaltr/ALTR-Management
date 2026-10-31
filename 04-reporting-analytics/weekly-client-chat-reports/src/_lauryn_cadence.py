"""Cadence checks for the Lauryn CS gap analysis (2026-09-25)."""
import datetime
import json
import re

msgs = [json.loads(l) for l in open("data/chats/lauryn-x-altr.jsonl")]
msgs = [m for m in msgs if m.get("sender")]


def show(label, pat, senders=None):
    rx = re.compile(pat, re.I)
    hits = [m for m in msgs if rx.search(m.get("text") or "")
            and (senders is None or m["sender"] in senders)]
    print("\n== %s == %d" % (label, len(hits)))
    prev = None
    for m in hits:
        d = datetime.datetime.fromisoformat(m["ts"])
        gap = "" if prev is None else "  (+%.0fd)" % ((d - prev).total_seconds() / 86400)
        prev = d
        print("   %s | %-24s | %s%s" % (m["ts"][:10], m["sender"][:24],
                                        (m.get("text") or "")[:70].replace("\n", " "), gap))


show("DMCA / leak updates", r"(takedown update|leak scan report|leak removal|infringements removed)")
show("monthly content request", r"content ?(snare|request)")
show("facebook not recommended / recommend", r"(recommend|shadow ?ban|not recommended)")
show("calls", r"(meet\.google|calendly|zoom|weekly call|jump on a call|15.minute)")
show("reel inspo cadence", r"reel inspo")
