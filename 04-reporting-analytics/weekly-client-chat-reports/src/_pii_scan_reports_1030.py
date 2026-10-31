#!/usr/bin/env python3
"""List email addresses and phone-shaped numbers anywhere under reports/."""
import glob
import re
from collections import Counter

PAT = re.compile(
    r"[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"
    r"|\+?44 ?7\d{3} ?\d{6}"
    r"|\+1 ?\(?\d{3}\)? ?\d{3}[- ]\d{4}"
    r"|\+61 ?4\d{2} ?\d{3} ?\d{3}"
    r"|\+\d{10,13}"
)
c = Counter()
where = {}
for f in glob.glob("reports/**/*.html", recursive=True):
    t = open(f, errors="ignore").read()
    for m in PAT.findall(t):
        c[m] += 1
        where.setdefault(m, f)
for k, v in c.most_common(40):
    print(f"{v:3d}  {k:45s}  e.g. {where[k]}")
