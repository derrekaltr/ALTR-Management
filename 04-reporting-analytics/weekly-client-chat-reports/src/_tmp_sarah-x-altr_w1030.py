#!/usr/bin/env python3
"""Dump in-window rows for sarah-x-altr (window ending 2026-10-30) plus
history slices used for first-raised dates. Read-only helper."""
import json
import sys
from datetime import datetime

ROWS = [json.loads(l) for l in open("data/chats/sarah-x-altr.jsonl")]
WS = datetime.fromisoformat("2026-10-16T09:06:40-04:00")
WE = datetime.fromisoformat("2026-10-30T09:05:30-04:00")


def ts(r):
    return datetime.fromisoformat(r["ts"])


mode = sys.argv[1] if len(sys.argv) > 1 else "window"

if mode == "window":
    W = [r for r in ROWS if WS < ts(r) <= WE]
    print(len(W), "in-window rows; file last ts", ROWS[-1]["ts"], "total rows", len(ROWS))
    for r in W:
        if r.get("service"):
            print(f"[SVC] {r['ts']} {r}")
        else:
            extra = {k: v for k, v in r.items() if k not in ("id", "ts", "sender", "text")}
            print(f"#{r['id']} {r['ts']} <{r['sender']}> {r.get('text')!r} {extra or ''}")
    # per-sender counts
    from collections import Counter
    c = Counter(r["sender"] for r in W if not r.get("service"))
    print("\nSENDER COUNTS:", dict(c))
    print("service events:", sum(1 for r in W if r.get("service")))
    # pre-window tail for context
    print("\n--- last 6 rows before window ---")
    for r in [r for r in ROWS if ts(r) <= WS][-6:]:
        print(f"#{r.get('id')} {r['ts']} <{r.get('sender')}> {str(r.get('text'))[:160]!r}")

elif mode == "grep":
    pat = sys.argv[2].lower()
    for r in ROWS:
        if r.get("service"):
            continue
        if pat in (r.get("text") or "").lower() or pat in (r.get("sender") or "").lower():
            print(f"#{r['id']} {r['ts']} <{r['sender']}> {str(r.get('text'))[:260]!r}")

elif mode == "last":
    # last message per sender across whole file
    last = {}
    for r in ROWS:
        if r.get("service"):
            continue
        last[r["sender"]] = r["ts"]
    for k, v in sorted(last.items(), key=lambda kv: kv[1], reverse=True):
        print(f"{v}  {k}")

elif mode == "statecheck":
    st = json.load(open("data/state/sarah-x-altr.json"))
    print("state parses; as_of", st["as_of"], "| keys", len(st),
          "| open_complaints", len(st["open_complaints"]),
          "| open_commitments", len(st["open_commitments"]),
          "| health_history last", st["health_history"][-1])

elif mode == "ids":
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for r in ROWS:
        if r.get("service"):
            continue
        if lo <= r["id"] <= hi:
            print(f"#{r['id']} {r['ts']} <{r['sender']}> {r.get('text')!r}")
