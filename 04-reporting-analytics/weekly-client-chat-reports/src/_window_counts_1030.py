#!/usr/bin/env python3
"""Per-chat in-window counts, senders, unknown names for the 2026-10-30 run."""
import datetime
import glob
import json
import os

import yaml

WS = datetime.datetime.fromisoformat("2026-10-16T09:06:40-04:00")
print("now:", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
team = yaml.safe_load(open("config/team.yaml"))
clients = yaml.safe_load(open("config/clients.yaml"))["clients"]
known = set()
for t in team["team"]:
    known |= set(t["aliases"])
for v in team["vendors"]:
    known |= set(v["aliases"])
cl_alias = {}
for c in clients:
    for a in c["client_aliases"]:
        cl_alias[a] = c["name"]
known |= set(cl_alias)
print("window start", WS)
for f in sorted(glob.glob("data/chats/*.jsonl")):
    slug = os.path.basename(f)[:-6]
    msgs = [json.loads(l) for l in open(f)]
    msgs = [m for m in msgs if not m.get("service")]
    inw = [m for m in msgs if datetime.datetime.fromisoformat(m["ts"]) > WS]
    last = msgs[-1]["ts"][:16] if msgs else "-"
    senders = {}
    for m in inw:
        senders[m["sender"]] = senders.get(m["sender"], 0) + 1
    unknown = {s: n for s, n in senders.items() if s not in known}
    cli = sum(n for s, n in senders.items() if s in cl_alias)
    print(f"{slug:28} total={len(msgs):5} inwin={len(inw):4} client={cli:3} last={last} unknown={unknown}")
    if inw:
        print("     senders:", dict(sorted(senders.items(), key=lambda x: -x[1])))
