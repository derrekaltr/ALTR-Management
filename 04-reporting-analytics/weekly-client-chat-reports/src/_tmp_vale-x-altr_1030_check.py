#!/usr/bin/env python3
"""Confirm no credential text from the Vale chat appears in the 10-30 outputs. Prints nothing secret."""
import json, re

rows = {json.loads(l)['id']: json.loads(l) for l in open('data/chats/vale-x-altr.jsonl')}
secrets = set()
for i in (10, 898, 903, 908, 1011):
    for line in rows[i]['text'].split('\n'):
        line = line.strip()
        if not line:
            continue
        secrets.add(line)
        # also the token after 'Password is' style prefixes
        m = re.search(r'(?:password is|pass(?:word)?:)\s*(\S+)', line, re.I)
        if m:
            secrets.add(m.group(1))
# drop obviously public tokens (handles)
secrets = {s for s in secrets if not s.lower().startswith('@')}
# PII rows too
for i in (152, 397):
    for tok in re.findall(r'\S+@\S+|\+?\d[\d\-\s()]{7,}\d', rows[i]['text']):
        secrets.add(tok.strip())

files = ['data/weeks/2026-10-30/vale-x-altr.json', 'data/state/vale-x-altr.json']
ok = True
for f in files:
    txt = open(f).read()
    json.loads(txt)  # parse check
    hits = [s for s in secrets if s in txt]
    print(f, '| parses OK |', 'CLEAN' if not hits else f'LEAK x{len(hits)}')
    ok = ok and not hits
print('secret tokens checked:', len(secrets))
print('RESULT:', 'PASS' if ok else 'FAIL')
