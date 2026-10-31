#!/usr/bin/env python3
"""Redact known leaked secrets (the lists in _cred_redact.py) from everything
that feeds or forms the published site: reports/**, data/weeks/**/*.json and
data/state/*.json. Plain text replacement, so it works on HTML and JSON alike
(the markers contain no quotes or markup). Re-run publish.sh afterwards so the
live site picks up the redacted pages.

Usage: python3 src/_cred_redact_published.py
"""
import glob
import sys

sys.argv = sys.argv[:1]  # _cred_redact reads argv[1] as a run dir at import
from _cred_redact import CODES, EMAILS, PASSWORDS, redact

paths = (glob.glob("reports/**/*.html", recursive=True)
         + glob.glob("data/weeks/**/*.json", recursive=True)
         + glob.glob("data/state/*.json"))
for f in sorted(paths):
    before = open(f, encoding="utf-8").read()
    after = redact(before)
    if after != before:
        open(f, "w", encoding="utf-8").write(after)
        n = sum(before.count(s) for s in PASSWORDS + CODES + EMAILS)
        print(f"redacted {n:2d} secret(s) in {f}")
print("done")
