#!/usr/bin/env python3
"""Check whether an unknown sender is a rename of a known alias.

Prints current per-chat counts for each name given, plus first/last ts of that
sender's messages, so a zeroed-out old alias next to a new one with the same
history shape is easy to spot.

Usage: python3 src/_alias_check.py "Fredo" "FRED | OFM" "fred SPITFIRE"
"""
import glob
import json
import sys

names = sys.argv[1:]
for name in names:
    print(f"\n=== {name!r} ===")
    total = 0
    for path in sorted(glob.glob("data/chats/*.meta.json")):
        meta = json.load(open(path))
        count = meta["senders"].get(name)
        if not count:
            continue
        total += count
        stamps = []
        for line in open(path.replace(".meta.json", ".jsonl")):
            msg = json.loads(line)
            if msg.get("sender") == name:
                stamps.append(msg["ts"])
        span = f"{stamps[0][:10]} .. {stamps[-1][:10]}" if stamps else "?"
        print(f"  {meta['chat']:28} {count:>5}   {span}")
    print(f"  TOTAL {total}")
