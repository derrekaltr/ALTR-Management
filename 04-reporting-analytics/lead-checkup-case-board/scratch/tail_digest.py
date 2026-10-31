#!/usr/bin/env python3
"""Digest all not-yet-deep-read micro briefs into a compact tail digest."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
READ = {  # chats already deep-read (src, chat_id)
    ("imessage", 18), ("imessage", 13878), ("imessage", 13609), ("whatsapp", 1431),
    ("imessage", 126), ("imessage", 188), ("imessage", 112), ("whatsapp", 1494),
    ("imessage", 59), ("whatsapp", 888), ("imessage", 227), ("imessage", 12),
    ("imessage", 31), ("imessage", 13673), ("imessage", 14151), ("imessage", 13681),
    ("imessage", 22), ("whatsapp", 894), ("imessage", 14384), ("imessage", 2010),
    ("imessage", 67), ("imessage", 98), ("imessage", 13880), ("imessage", 13700),
    ("whatsapp", 1567), ("whatsapp", 1533), ("imessage", 45), ("imessage", 119),
    ("imessage", 32), ("whatsapp", 1415),
}
idx = json.load(open(os.path.join(HERE, "micro_index.json")))
DOLLAR = re.compile(r"\$\s?\d")
out = []
skipped = 0
for e in sorted(idx, key=lambda x: -x["score"]):
    if (e["src"], e["chat_id"]) in READ:
        continue
    path = os.path.join(HERE, e["micro"])
    lines = open(path).read().splitlines()
    header = lines[0] if lines else ""
    body = [l for l in lines[1:] if l.strip() and l != "..." and not l.strip().startswith("<IMG")]
    # score lines: prefer $ + ANGRY + PAY, and later dates
    def lscore(l):
        s = 0
        if DOLLAR.search(l): s += 3
        if "ANGRY" in l[:40]: s += 2
        if "PAY" in l[:40]: s += 2
        if "OUTCOME" in l[:40]: s += 1
        if l[1:8] >= "2026-08": s += 2
        elif l[1:8] >= "2026-07": s += 1
        return s
    scored = sorted(body, key=lscore, reverse=True)[:12]
    keep = sorted(scored, key=lambda l: l[:17])
    blob = header + "\n" + "\n".join(l[:230] for l in keep)
    out.append(blob)

full = "\n\n".join(out)
n = 4
size = len(full)
parts = []
chunk = []
csz = 0
for blob in out:
    if csz + len(blob) > size // n + 2000 and chunk:
        parts.append("\n\n".join(chunk)); chunk, csz = [], 0
    chunk.append(blob); csz += len(blob)
if chunk: parts.append("\n\n".join(chunk))
for i, p in enumerate(parts, 1):
    open(os.path.join(HERE, f"tail_digest_{i}.md"), "w").write(p)
    print(f"tail_digest_{i}.md {len(p)//1024}KB")
print("chats:", len(out))
