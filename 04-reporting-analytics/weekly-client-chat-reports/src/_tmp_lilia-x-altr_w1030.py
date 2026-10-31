#!/usr/bin/env python3
"""Dump in-window rows for lilia-x-altr, window 2026-10-16 09:06:40 -> 2026-10-30 09:05:30 (-04:00)."""
import json
import sys
from collections import Counter
from datetime import datetime

ROWS = [json.loads(l) for l in open('data/chats/lilia-x-altr.jsonl')]
WS = datetime.fromisoformat('2026-10-16T09:06:40-04:00')
WE = datetime.fromisoformat('2026-10-30T09:05:30-04:00')

mode = sys.argv[1] if len(sys.argv) > 1 else 'window'

if mode == 'window':
    inw = [r for r in ROWS if WS < datetime.fromisoformat(r['ts']) <= WE]
    print("keys sample:", sorted(ROWS[-1].keys()))
    print("in-window rows:", len(inw))
    c = Counter(r.get('sender', 'SERVICE:' + str(r.get('event'))) for r in inw)
    print(c)
    for r in inw:
        if r.get('service'):
            rest = {k: v for k, v in r.items() if k not in ('service', 'event', 'ts')}
            print(f"--- SERVICE {r['ts']} {r.get('event')} {json.dumps(rest, ensure_ascii=False)}")
        else:
            extra = {k: v for k, v in r.items() if k not in ('id', 'ts', 'sender', 'text')}
            print(f"[{r['id']}] {r['ts']} <{r['sender']}> {r.get('text')!r} {extra if extra else ''}")
elif mode == 'tail':
    # last N rows before window start for context
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    pre = [r for r in ROWS if datetime.fromisoformat(r['ts']) <= WS]
    for r in pre[-n:]:
        print(f"[{r.get('id')}] {r['ts']} <{r.get('sender')}> {r.get('text')!r}")
elif mode == 'grep':
    for pat in sys.argv[2:]:
        print(f"##### {pat}")
        pat = pat.lower()
        for r in ROWS:
            if pat in (r.get('text') or '').lower():
                print(f"[{r.get('id')}] {r['ts']} <{r.get('sender')}> {r.get('text')!r}"[:260])
elif mode == 'secrets':
    # Check output files for secrets taken from the chat rows by id (never printed).
    byid = {r.get('id'): r for r in ROWS}
    secrets = []
    for mid in (1315, 1321, 1325):
        t = (byid[mid].get('text') or '').strip()
        t = t.split(':', 1)[1].strip() if mid == 1315 else t
        secrets.append((mid, t))
    # historical OF password (msg 24) and fan handle in 1410
    secrets.append((24, (byid[24].get('text') or '').split(' ')[0]))
    fan = [ln for ln in (byid[1410].get('text') or '').splitlines() if ln.startswith('FAN:')]
    if fan:
        secrets.append((1410, fan[0].split(':', 1)[1].strip()))
    outs = ['data/weeks/2026-10-30/lilia-x-altr.json', 'data/state/lilia-x-altr.json']
    bad = False
    for o in outs:
        txt = open(o, encoding='utf-8').read()
        json.loads(txt)
        for mid, s in secrets:
            if s and s in txt:
                bad = True
                print(f"LEAK: secret from msg {mid} (len {len(s)}) found in {o}")
    print("secret scan:", "FAILED" if bad else "clean", "| files parse as JSON")
elif mode == 'last':
    # last message per sender overall
    last = {}
    for r in ROWS:
        if not r.get('service'):
            last[r['sender']] = r['ts']
    for s, t in sorted(last.items(), key=lambda x: x[1]):
        print(s, t, (WE - datetime.fromisoformat(t)).days, 'days silent at window end')
