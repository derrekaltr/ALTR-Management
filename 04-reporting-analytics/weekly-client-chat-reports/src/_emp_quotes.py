#!/usr/bin/env python3
"""Pull verbatim evidence quotes attributable to one employee across a week's findings,
so the _employees.json rollup quotes real messages instead of paraphrases.

Usage: python3 src/_emp_quotes.py 2026-09-18 "Mayson" [max_per_client]
"""
import glob
import json
import sys

WEEK = sys.argv[1]
WHO = sys.argv[2]
MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 4


def quotes_of(item):
    """Evidence lives under 'evidence' or 'quotes'; items are dicts or bare strings."""
    out = []
    for key in ("evidence", "quotes"):
        for q in item.get(key) or []:
            if isinstance(q, dict) and q.get("quote"):
                out.append((q.get("date", "?"), q.get("who", "?"), q["quote"]))
            elif isinstance(q, str):
                out.append(("?", "?", q))
    return out


for path in sorted(glob.glob(f"data/weeks/{WEEK}/*.json")):
    if path.endswith("_employees.json"):
        continue
    d = json.load(open(path))
    hits = []
    for field, owner_key in (("reminders", "employee"), ("complaints", "owner"), ("commitments", "who")):
        for item in d.get(field, []):
            owner = str(item.get(owner_key) or "")
            if WHO.lower() in owner.lower():
                hits.extend(quotes_of(item))
    if not hits:
        continue
    print(f"\n### {d['client']}")
    seen = set()
    shown = 0
    for date, who, quote in hits:
        if quote in seen:
            continue
        seen.add(quote)
        print(f"  [{date}] {who}: {quote[:190]}")
        shown += 1
        if shown >= MAX:
            break
