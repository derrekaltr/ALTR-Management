"""Scratch helper for the 2026-10-30 CS gap pass on shayna-x-altr.

Usage:
  python3 src/_tmp_shayna-x-altr_w1030.py dump [YYYY-MM-DD]   # print messages from date (default 2026-10-16)
  python3 src/_tmp_shayna-x-altr_w1030.py metrics             # sender counts, '?' counts, team silence gaps
  python3 src/_tmp_shayna-x-altr_w1030.py grep <regex>        # case-insensitive search over text
"""
import json
import re
import sys
from datetime import datetime

PATH = "data/chats/shayna-x-altr.jsonl"
CLIENT = {"Shayna Holt"}
TEST = {"Antonio Veritrade"}


def load():
    rows = []
    for line in open(PATH):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def ts(r):
    return datetime.fromisoformat(r["ts"])


def fmt(r):
    t = (r.get("text") or "").replace("\n", " / ")
    extra = ""
    if r.get("media"):
        extra += f" [media:{r['media']}]"
    if r.get("reply_to"):
        extra += f" [re:{r['reply_to']}]"
    if r.get("service"):
        extra += f" [service:{r.get('event')}]"
    return f"{r['id']} {r['ts'][:16]} {r['sender']}: {t}{extra}"


def dump(rows, since):
    for r in rows:
        if r["ts"][:10] >= since:
            print(fmt(r))


def metrics(rows):
    msgs = [r for r in rows if not r.get("service") and r["sender"] not in TEST]
    print("total non-service (excl test acct):", len(msgs))
    print("first", msgs[0]["ts"], "last", msgs[-1]["ts"])
    from collections import Counter
    c = Counter(r["sender"] for r in msgs)
    for k, v in c.most_common():
        print(f"  {k}: {v}")
    client = [r for r in msgs if r["sender"] in CLIENT]
    team = [r for r in msgs if r["sender"] not in CLIENT]
    print("client msgs", len(client), "team msgs", len(team))
    print("client msgs with '?':", sum(1 for r in client if "?" in (r.get("text") or "")))
    # new window
    new = [r for r in msgs if r["ts"][:10] >= "2026-10-16"]
    print("since 10/16:", len(new), "client", sum(1 for r in new if r["sender"] in CLIENT),
          "team", sum(1 for r in new if r["sender"] not in CLIENT))
    cn = Counter(r["sender"] for r in new)
    print("  ", dict(cn))
    print("client '?' since 10/16:", sum(1 for r in new if r["sender"] in CLIENT and "?" in (r.get("text") or "")))
    # team silence gaps
    gaps = []
    prev = None
    for r in team:
        if prev is not None:
            d = (ts(r) - ts(prev)).total_seconds() / 86400
            gaps.append((d, prev["ts"], r["ts"]))
        prev = r
    gaps.sort(reverse=True)
    print("top team silence gaps (days):")
    for g in gaps[:8]:
        print(f"  {g[0]:.1f}  {g[1]} -> {g[2]}")
    last_team = team[-1]
    print("last team msg", last_team["ts"], last_team["sender"])
    print("last client msg", client[-1]["ts"])
    # per-person last message
    last = {}
    for r in msgs:
        last[r["sender"]] = r["ts"]
    print("last message per sender:")
    for k, v in sorted(last.items(), key=lambda x: x[1]):
        print(f"  {k}: {v}")
    # client questions unanswered >24h (next team message after a client '?')
    unans = []
    for i, r in enumerate(msgs):
        if r["sender"] in CLIENT and "?" in (r.get("text") or ""):
            nxt = next((x for x in msgs[i + 1:] if x["sender"] not in CLIENT), None)
            if nxt is None or (ts(nxt) - ts(r)).total_seconds() > 86400:
                unans.append((r["ts"][:16], (r.get("text") or "")[:90]))
    print("client '?' msgs with no team message within 24h:", len(unans))
    for u in unans:
        print("  ", u)


def grep(rows, pat):
    rx = re.compile(pat, re.I)
    for r in rows:
        if rx.search(r.get("text") or ""):
            print(fmt(r))


if __name__ == "__main__":
    rows = load()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dump"
    if cmd == "dump":
        dump(rows, sys.argv[2] if len(sys.argv) > 2 else "2026-10-16")
    elif cmd == "metrics":
        metrics(rows)
    elif cmd == "grep":
        grep(rows, sys.argv[2])
