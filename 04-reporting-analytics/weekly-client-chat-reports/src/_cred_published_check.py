#!/usr/bin/env python3
"""Pre-publish check: does any known leaked secret appear in reports/ or the
weekly findings/state JSON? Secrets are the PASSWORDS list in _cred_redact.py.

Usage: python3 src/_cred_published_check.py
"""
import glob
import re

src = open("src/_cred_redact.py").read()
block = src.split("PASSWORDS = [", 1)[1].split("]", 1)[0]
secrets = re.findall(r'"([^"]+)"', block)
print(f"{len(secrets)} known secrets")

paths = (glob.glob("reports/**/*", recursive=True)
         + glob.glob("data/weeks/**/*.json", recursive=True)
         + glob.glob("data/state/*.json"))
for f in sorted(paths):
    try:
        t = open(f, errors="ignore").read()
    except IsADirectoryError:
        continue
    hits = [s for s in secrets if s in t]
    if hits:
        print(f"{f}: {len(hits)} secret(s)")
