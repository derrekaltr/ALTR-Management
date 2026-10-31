"""Redact live secrets that analysts quoted verbatim into a cs-gaps run.

The brief says describe, don't quote. Analysts sometimes quote anyway, and the
rendered dashboard embeds the evidence bank, so the secret would travel. This
rewrites the run's JSON in place, replacing the secret itself with a marker and
leaving the surrounding narrative intact.
"""
import glob
import json
import os
import re
import sys

RUN = sys.argv[1] if len(sys.argv) > 1 else "data/analysis/cs-gaps-2026-09-25"

# Exact secrets found by src/_cred_scan.py on the 2026-09-25 run.
PASSWORDS = [
    "hosjsjJaoo29.jaisb$",
    "BossMama261395$$",
    "Hilda0263$$30",
    "1122Perth33!!",
    "Maldives2025!",
    "Disney2233!",
    "Sydney2025!",
    "Find67xtree",
    # Added 2026-10-09 from src/_cred_scan_all.py over data/weeks + data/state.
    "Password1123",
    "Tylerthomas2014",
    "Wagamama123",
    "Jxstin03",
    "Cottonball21!",
    "Teigan1999!",
    "Teigan0011$",
    "Alissonbaby252217!!",
    "Alissonbaby252217!",
    "Nalasage172205!!",
    "Michelle2505!!",
    # Added 2026-10-09 — still plaintext in the 2026-09-25 run (analyst reports).
    "Hilda0263",
    "2027GetOfMyOF!?",
    "ojs4bYuuhl",
    "ALTRmgmt",
    "gpEMZJxm",
]
CODES = ["050430", "451019", "518844", "822833", "122868", "556659", "871482", "261395",
         "9354 0628"]
EMAILS = ["justinsarah22@icloud.com", "sarahxlloydphone@icloud.com",
          # Added 2026-10-30: personal / login emails still on published pages
          # (reports 08-08 .. 09-25). Order matters: "+1" variants before the base.
          "Vickymerm+1@gmail.com", "Vickymerm@gmail.com",
          "Lboultier@gmail.com", "shaynaholtonlyfans@gmail.com",
          "paigelgrogan4@icloud.com", "Hannahchamberss2022@gmail.com",
          "bookbarbsilva@gmail.com", "sotom225@gmail.com",
          "Bobbettek11@gmail.com"]
# Exact phrases where the secret is too short/generic to replace globally.
PHRASES = {"supercarcrashesonly - ALTR$1": "supercarcrashesonly - [REDACTED-PASSWORD]"}
# Personal phone numbers (one doubles as a TikTok login) and ALTR bank details.
NUMBERS = ["15303182647", "2136762479", "4079217561","898169904709", "063100277", "026009593",
           # Added 2026-10-30: client phone numbers (published 09-18 page; state file)
           "61432453716", "447429600251"]

PW_MARK = "[REDACTED-PASSWORD]"
CODE_MARK = "[REDACTED-2FA-CODE]"
EMAIL_MARK = "[REDACTED-RECOVERY-EMAIL]"
NUM_MARK = "[REDACTED-NUMBER]"


def redact(text):
    for k, v in PHRASES.items():
        text = text.replace(k, v)
    for p in sorted(PASSWORDS, key=len, reverse=True):
        text = text.replace(p, PW_MARK)
    for e in EMAILS:
        text = text.replace(e, EMAIL_MARK)
    for n in NUMBERS:
        text = re.sub(rf"(?<!\d){re.escape(n)}(?!\d)", NUM_MARK, text)
    for c in CODES:
        text = re.sub(rf"(?<!\d){re.escape(c)}(?!\d)", CODE_MARK, text)
    return text


def walk(obj):
    if isinstance(obj, dict):
        return {k: walk(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v) for v in obj]
    if isinstance(obj, str):
        return redact(obj)
    return obj


def main():
    for f in sorted(glob.glob(os.path.join(RUN, "*.json"))):
        before = open(f).read()
        after = json.dumps(walk(json.loads(before)), indent=2, ensure_ascii=False) + "\n"
        if redact(before) != before:
            with open(f, "w") as fh:
                fh.write(after)
            n = sum(before.count(s) for s in PASSWORDS + CODES + EMAILS + NUMBERS + list(PHRASES))
            print(f"redacted {n:2d} secret(s) in {os.path.basename(f)}")
    print("done")


if __name__ == "__main__":
    main()
