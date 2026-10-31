"""Print every string in a run dir that sits in credential-flavoured context, so
secrets the shape-based _cred_scan.py misses (all-lowercase passwords, phone
logins, bank numbers) can be spotted by eye.

Usage: python3 src/_cred_context_dump.py <run_dir> [slug ...]
"""
import glob
import json
import os
import re
import sys

RUN = sys.argv[1]
ONLY = set(sys.argv[2:])
CONTEXT = re.compile(
    r"(?i)pass\s?word|\bpw\b|passcode|\bpwd\b|\b2fa\b|\botp\b|backup code|login|"
    r"routing|account (number|no)|acct|\biban\b|bsb|swift|phone|mobile|\+\d{6,}|\d{3}[- ]\d{3}[- ]\d{4}"
)


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


for f in sorted(glob.glob(os.path.join(RUN, "*.json"))):
    slug = os.path.basename(f)[:-5]
    if slug.startswith("_") or (ONLY and slug not in ONLY):
        continue
    for path, text in walk(json.load(open(f))):
        if path.endswith(".quote") and CONTEXT.search(text):
            print(f"{slug} {path}\n   {text[:300]}\n")
