"""Scratch: CS-gap metrics for amber-haze-x-altr (2026-09-18 run)."""
import datetime as dt
import json

CL = "Kirsten (amber Haze)"
PATH = "data/chats/amber-haze-x-altr.jsonl"
TODAY = dt.date(2026, 9, 18)


def p(s):
    return dt.datetime.fromisoformat(s)


rows = [json.loads(l) for l in open(PATH)]
msgs = [r for r in rows if r.get("sender")]
client = [r for r in msgs if r["sender"] == CL]

people = {}
for r in msgs:
    people.setdefault(r["sender"], []).append(r)

print("per-person last message and days since:")
for who, rs in sorted(people.items(), key=lambda kv: kv[1][-1]["ts"]):
    d = (TODAY - p(rs[-1]["ts"]).date()).days
    print(f"  {who:24s} n={len(rs):4d} last={rs[-1]['ts'][:10]} ({d}d ago)")

print()
print("Derrek gaps over 7d:")
dk = people["Derrek"]
for a, b in zip(dk, dk[1:]):
    g = (p(b["ts"]) - p(a["ts"])).days
    if g >= 7:
        print("  ", g, "days", a["ts"][:10], b["ts"][:10])

print()
print("client message count by month:")
by = {}
for r in client:
    by[r["ts"][:7]] = by.get(r["ts"][:7], 0) + 1
for k in sorted(by):
    print("  ", k, by[k])

print()
print("client questions (msgs containing '?'):", sum(1 for r in client if "?" in (r.get("text") or "")))
print("client messages total:", len(client))
