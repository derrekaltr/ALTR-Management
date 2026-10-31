#!/usr/bin/env python3
"""Build data/weeks/<week>/_employees.json.

Per-client counts are derived mechanically from the client findings files so the
numbers cannot drift from the evidence. The narrative fields (summary, trend,
strengths, coaching_flags, quotes) are authored in NARRATIVE below.

Owner strings in findings are often compound ("Mayson / Derrek", "Michelle
(Promo team)"); ALIASES maps the substrings we care about onto canonical names.

Usage: python3 src/_emp_rollup_build.py 2026-09-18
"""
import glob
import json
import re
import sys
from collections import defaultdict

WEEK = sys.argv[1]

# Never appear in the Team tab (Derrek's request, 2026-08-08). Owner-level items
# for these people go in the private message to Derrek instead.
EXCLUDED = {"Derrek", "Nick (DMCA)", "Noah"}

# canonical name -> (role, [substrings that identify them in an owner string])
ROSTER = {
    "Mayson":             ("Chatter (queue account)", ["mayson"]),
    "Stephski":           ("Invoicing", ["stephski"]),
    "Ollie Mckinlay":     ("Account lead", ["ollie"]),
    "Fred":               ("OFM", ["fred"]),
    "Michelle":           ("Promo / DMCA (queue account)", ["michelle"]),
    "Melissa":            ("Client-facing account (leak updates, intake)", ["melissa"]),
    "Vivek":              ("Platform & Meta support", ["vivek", "fonta"]),
    "Mica Vecco":         ("Social / reels", ["mica"]),
    "Ronnie":             ("Chatter (queue account)", ["ronnie"]),
    "Olivia":             ("Team", ["olivia"]),
    "Eric":               ("Team", ["eric"]),
    "Aroosha":            ("Customs / content organization", ["aroosha"]),
    "Jeremy Tarr":        ("Account manager", ["jeremy"]),
    "Spencer P":          ("Customs / content uploads", ["spencer"]),
    "Alex Camus":         ("Team", ["alex camus"]),
    "Lauren (Biz Assistant)": ("Business assistant", ["biz assistant"]),
    "IG farm vendor":     ("Vendor (IG growth)", ["ig farm vendor"]),
    "Sarah Lloyd chat team": ("Vendor chat team", ["sarah lloyd chat team"]),
    "Lauryn chat team":   ("Vendor chat team", ["lauryn chat team"]),
    "Amber Haze chat team": ("Vendor chat team", ["amber haze chat team"]),
}


def owners(raw):
    """Map a findings owner string onto every canonical roster name it mentions."""
    s = str(raw or "").lower()
    hits = []
    for name, (_role, keys) in ROSTER.items():
        if any(k in s for k in keys):
            # "Michelle" must not swallow "Mica"; substrings are distinct enough here.
            hits.append(name)
    return hits


agg = defaultdict(lambda: defaultdict(lambda: {
    "reminders": 0, "complaints_owned": 0, "commitments_kept": 0,
    "commitments_overdue": 0, "commitments_pending": 0, "notes": []}))

for path in sorted(glob.glob(f"data/weeks/{WEEK}/*.json")):
    if path.split("/")[-1].startswith("_"):
        continue
    d = json.load(open(path))
    client = d["client"]
    for r in d.get("reminders", []):
        for name in owners(r.get("employee")):
            agg[name][client]["reminders"] += int(r.get("count") or 1)
            if r.get("topic"):
                agg[name][client]["notes"].append(f"reminded: {r['topic']}")
    for c in d.get("complaints", []):
        for name in owners(c.get("owner")):
            agg[name][client]["complaints_owned"] += 1
            if c.get("issue"):
                agg[name][client]["notes"].append(f"[{c.get('status')}] {c['issue']}")
    for c in d.get("commitments", []):
        for name in owners(c.get("who")):
            st = c.get("status")
            key = {"done": "commitments_kept", "overdue": "commitments_overdue",
                   "pending": "commitments_pending"}.get(st)
            if key:
                agg[name][client][key] += 1
            if c.get("what"):
                agg[name][client]["notes"].append(f"[{st}] {c['what']}")


# Notes are copied from findings text, which names excluded people freely.
# Keep them off the Team tab entirely, including inside other people's notes.
_EXCLUDED_RE = re.compile(r"Nick \(DMCA\)|Nick \| DMCA|\b(?:Derrek|Noah|Nate)\b")


def scrub(text):
    return _EXCLUDED_RE.sub("leadership", text)


NARRATIVE = json.load(open(f"data/state/_narrative-{WEEK}.json"))

employees = []
for name, (role, _keys) in ROSTER.items():
    if name in EXCLUDED or name not in agg:
        continue
    nar = NARRATIVE.get(name, {})
    clients = []
    for client, v in sorted(agg[name].items()):
        notes = scrub(" | ".join(v.pop("notes")[:6]))
        clients.append({"client": client, **v, "notes": notes[:1200]})
    open_issues = sum(
        c["complaints_owned"] + c["commitments_overdue"] + c["commitments_pending"]
        for c in clients
    )
    employees.append({
        "name": name,
        "role": role,
        "summary": nar.get("summary", ""),
        "open_issues": open_issues,
        "trend": nar.get("trend", "flat"),
        "clients": clients,
        "strengths": nar.get("strengths", []),
        "coaching_flags": nar.get("coaching_flags", []),
        "quotes": nar.get("quotes", []),
    })

employees.sort(key=lambda e: -e["open_issues"])
out = {"week_ending": WEEK, "employees": employees}
path = f"data/weeks/{WEEK}/_employees.json"
with open(path, "w") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print(f"wrote {path}: {len(employees)} employees")
for e in employees:
    print(f"  {e['name']:24} open_issues={e['open_issues']:<4} clients={len(e['clients'])}")
