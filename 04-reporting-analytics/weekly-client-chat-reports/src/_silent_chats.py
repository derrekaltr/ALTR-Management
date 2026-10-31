#!/usr/bin/env python3
"""Summarize chats with no in-window traffic: how long they have been quiet,
who spoke last, and what the last run's findings left open.

Usage: python3 src/_silent_chats.py <window_start_iso> <slug> [slug ...]
"""
import datetime
import json
import sys
from pathlib import Path

ws = datetime.datetime.fromisoformat(sys.argv[1])

for slug in sys.argv[2:]:
    meta = json.load(open(f"data/chats/{slug}.meta.json"))
    msgs = [
        json.loads(line)
        for line in open(f"data/chats/{slug}.jsonl")
        if not json.loads(line).get("service")
    ]
    last = msgs[-1]
    quiet_days = (ws - datetime.datetime.fromisoformat(last["ts"])).days
    print(f"\n=== {meta['chat']} ===")
    print(f"  {len(msgs)} msgs total; silent {quiet_days}d as of window start")
    print(f"  last: [{last['ts'][:16]}] {last['sender']}: {last['text'][:160]!r}")

    priors = sorted(Path("data/weeks").glob(f"*/{slug}.json"))
    if priors:
        prior = priors[-1]
        p = json.loads(prior.read_text())
        h = p.get("health", {})
        print(f"  last report ({prior.parent.name}): health {h.get('score')} ({h.get('trend')})")
        opens = [c for c in p.get("complaints", []) if c.get("status") != "resolved"]
        od = [c for c in p.get("commitments", []) if c.get("status") in ("pending", "overdue")]
        print(f"  left open: {len(opens)} complaint(s), {len(od)} pending/overdue commitment(s)")
        for c in opens[:3]:
            print(f"     ! {c.get('issue', '')[:120]}")
        for c in od[:3]:
            print(f"     > [{c.get('status')}] {c.get('who')}: {c.get('what', '')[:110]}")
    else:
        print("  last report: none (no findings file in any week)")
