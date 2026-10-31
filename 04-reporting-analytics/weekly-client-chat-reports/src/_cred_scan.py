"""Scan a cs-gaps run directory for anything that looks like a live secret.

The analyst brief forbids reproducing credentials, but analysts sometimes quote
them verbatim as evidence. Run this before aggregating/rendering.
"""
import glob
import json
import os
import re
import sys

RUN = sys.argv[1] if len(sys.argv) > 1 else "data/analysis/cs-gaps-2026-09-25"

# a token with an uppercase, a digit and (usually) punctuation - password-shaped
PASSWORDISH = re.compile(
    r"(?<![\w@./-])(?=[A-Za-z0-9!@#$%^&*._-]{7,24}(?![\w@./-]))"
    r"(?=[^\s]*[A-Z])(?=[^\s]*[0-9])[A-Za-z0-9!@#$%^&*._-]+"
)
CODEISH = re.compile(r"(?<!\d)\d{6}(?!\d)")  # 2FA / OTP codes
CONTEXT = re.compile(r"(?i)pass\s?word|passcode|\bpwd\b|\b2fa\b|\botp\b|backup code|login code|verification code")

ALLOW = {
    "ALTR", "OnlyFans", "DMCA", "Telegram", "Instagram", "Facebook",
}


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def main():
    flagged = 0
    for f in sorted(glob.glob(os.path.join(RUN, "*.json"))):
        if os.path.basename(f).startswith("_"):
            continue
        data = json.load(open(f))
        for path, text in walk(data):
            hits = set()
            for m in PASSWORDISH.finditer(text):
                s = m.group(0)
                if s in ALLOW or s.isdigit():
                    continue
                # only care when the surrounding text is credential-flavoured
                if CONTEXT.search(text):
                    hits.add(s)
            if CONTEXT.search(text):
                hits.update(CODEISH.findall(text))
            if hits:
                flagged += 1
                print(f"{os.path.basename(f)} {path}")
                print(f"   candidates: {sorted(hits)}")
                print(f"   text: {text[:220]}")
                print()
    print(f"--- {flagged} suspicious field(s) ---")


if __name__ == "__main__":
    main()
