#!/usr/bin/env python3
"""Scratch analysis for Vale, week ending 2026-10-30. Never prints credential text."""
import json, re, collections

rows = [json.loads(l) for l in open('data/chats/vale-x-altr.jsonl')]
byid = {r['id']: r for r in rows}
W0, W1 = '2026-10-16T09:06:40', '2026-10-30T09:05:30'
inw = [r for r in rows if W0 < r.get('ts', '') <= W1]

svc = [r for r in inw if r.get('service')]
msgs = [r for r in inw if not r.get('service')]
test = [r for r in msgs if r['sender'] == 'Antonio Veritrade']
real = [r for r in msgs if r['sender'] != 'Antonio Veritrade']
print('svc', len(svc), 'test', len(test), 'real', len(real))
print(collections.Counter(r['sender'] for r in real))

def pw(i):
    t = byid[i]['text']
    return t.strip().split('\n')[-1].strip()
for i in (898, 903, 908, 10):
    print(i, 'SAME-as-1011' if pw(i) == pw(1011) else 'different', '| sender', byid[i]['sender'],
          '| first line:', byid[i]['text'].split('\n')[0][:30])
print('1011 line count:', len(byid[1011]['text'].split('\n')))
print('id 980:', json.dumps(byid.get(980), ensure_ascii=False))
print('1029 exists:', 1029 in byid)
print('--- ids 974-998')
for i in range(974, 999):
    r = byid.get(i)
    if r:
        print(i, r['ts'][:16], r.get('sender'), '|', (r.get('text') or '')[:110].replace('\n', ' '),
              '| rt', r.get('reply_to'), '|', r.get('media', ''))

print('--- history keyword hits (pre-window)')
pat = re.compile(r'back ?up|theta|stardust|zeus|content house|twitch|repost|shoot|photograph|farm|halloween|amazon|grandma|louisiana|\bcall\b', re.I)
for r in rows:
    if r.get('service') or r['ts'] > W0:
        continue
    if pat.search(r.get('text') or ''):
        print(r['id'], r['ts'][:16], r['sender'], '|', (r['text'] or '')[:140].replace('\n', ' '), '| rt', r.get('reply_to'))

print('--- last msg per sender before window')
last = {}
for r in rows:
    if r.get('service') or r['ts'] > W0:
        continue
    last[r['sender']] = (r['id'], r['ts'][:16])
for k, v in sorted(last.items(), key=lambda x: x[1][1]):
    print(k, v)
print('--- all service events')
for r in rows:
    if r.get('service'):
        print(r['id'], r['ts'][:16], r['event'])
