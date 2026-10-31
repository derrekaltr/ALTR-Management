#!/usr/bin/env python3
"""Show context for secret-shaped strings found in data/state on the 2026-10-30 run."""
import glob
import re

NEEDLES = ["Bobbettek11@gmail.com", "R0d1905", "AbundantLauren444", "Kirs10xx", "Vickymerm"]
files = sorted(glob.glob("reports/*/index.html")) + sorted(glob.glob("data/state/*.json"))
for s in NEEDLES:
    print("===", s)
    shown = 0
    for f in files:
        t = open(f, errors="ignore").read()
        for m in re.finditer(re.escape(s), t):
            a, b = max(0, m.start() - 160), min(len(t), m.end() + 60)
            print(f"  [{f}] …{t[a:b]!r}")
            shown += 1
            if shown >= 2:
                break
        if shown >= 2:
            break
