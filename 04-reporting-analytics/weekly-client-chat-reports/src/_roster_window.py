#!/usr/bin/env python3
"""Pre-analysis check: in-window message counts per chat + senders missing from rosters.

Usage: python3 src/_roster_window.py <window_start_iso>
"""
import datetime
import glob
import json
import sys

import yaml

team = yaml.safe_load(open("config/team.yaml"))
clients = yaml.safe_load(open("config/clients.yaml"))

known = set()
for m in team.get("team", []):
    known.update(m.get("aliases", []))
    known.add(m["name"])
for v in team.get("vendors", []):
    known.update(v.get("aliases", []))
    known.add(v["name"])
for c in clients["clients"]:
    known.update(c.get("client_aliases", []))
    known.add(c["name"])

ws = datetime.datetime.fromisoformat(sys.argv[1])
unknown = {}

print(f"{'chat':30} {'total':>6} {'in-window':>10}  warnings")
for path in sorted(glob.glob("data/chats/*.meta.json")):
    meta = json.load(open(path))
    n = 0
    for line in open(path.replace(".meta.json", ".jsonl")):
        msg = json.loads(line)
        if msg.get("service"):
            continue
        if datetime.datetime.fromisoformat(msg["ts"]) > ws:
            n += 1
    print(f"{meta['chat']:30} {meta['messages']:>6} {n:>10}  {meta['warnings'] or ''}")
    for sender, count in meta["senders"].items():
        if sender not in known:
            unknown.setdefault(sender, []).append((meta["chat"], count))

print("\n=== SENDERS NOT IN ROSTERS ===")
for sender, hits in sorted(unknown.items(), key=lambda kv: -sum(c for _, c in kv[1])):
    print(f"  {sender!r}: {hits}")
if not unknown:
    print("  (none)")
