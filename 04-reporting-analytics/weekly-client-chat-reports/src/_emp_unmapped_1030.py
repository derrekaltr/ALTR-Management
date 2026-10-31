#!/usr/bin/env python3
"""List owner strings in this week's findings that map to no roster name."""
import glob
import json
import sys
from collections import Counter

sys.argv = ["x", "2026-10-30"]
ns = {}
src = open("src/_emp_rollup_build.py").read()
exec(src.split("def owners")[0].split("WEEK = sys.argv[1]")[1], ns)
ROSTER = ns["ROSTER"]


def owners(raw):
    s = str(raw or "").lower()
    return [n for n, (_r, k) in ROSTER.items() if any(x in s for x in k)]


un = Counter()
for f in glob.glob("data/weeks/2026-10-30/*.json"):
    if "_emp" in f:
        continue
    d = json.load(open(f))
    for r in d["reminders"]:
        if not owners(r.get("employee")):
            un[r.get("employee")] += 1
    for c in d["complaints"]:
        if not owners(c.get("owner")):
            un[c.get("owner")] += 1
    for c in d["commitments"]:
        if not owners(c.get("who")):
            un[c.get("who")] += 1
for k, v in un.most_common():
    print(v, repr(k))
