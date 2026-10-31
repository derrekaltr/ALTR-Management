#!/usr/bin/env python3
"""Run _cred_scan.py over every weekly findings dir + data/state and print the
distinct secret-shaped candidates per dir, so new leaks can be added to the
PASSWORDS list in _cred_redact.py.

Usage: python3 src/_cred_scan_all.py
"""
import ast
import glob
import re
import subprocess

dirs = sorted(glob.glob("data/weeks/*")) + ["data/state"]
for d in dirs:
    out = subprocess.run(["python3", "src/_cred_scan.py", d],
                         capture_output=True, text=True).stdout
    found = set()
    for m in re.findall(r"candidates: (\[.*?\])", out):
        found |= set(ast.literal_eval(m))
    print(d, sorted(found))
