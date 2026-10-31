import json, collections
P = 'data/chats/sarah-lloyd-x-altr.jsonl'
rows = [json.loads(l) for l in open(P)]
START, END = '2026-10-09T09:05:57-04:00', '2026-10-16T09:06:40-04:00'
last = {}
for r in rows:
    if not r.get('service'):
        last[r.get('sender')] = r['ts']
for s, t in sorted(last.items(), key=lambda x: x[1]):
    print('LAST', t[:16], s)
win = [r for r in rows if START <= r['ts'] <= END]
ids = [r['id'] for r in win]
print('window ids', ids[0], ids[-1], 'missing', sorted(set(range(ids[0], ids[-1] + 1)) - set(ids)))
c = collections.Counter(r.get('sender') for r in win if not r.get('service'))
print('svc', [r for r in win if r.get('service')])
print(c, sum(c.values()))
print('--- Melissa posts (reply_to topic)')
for r in rows:
    if r.get('sender') == 'Melissa Userfacing':
        print(r['id'], r['ts'][:16], r.get('reply_to'), (r.get('text') or '')[:90].replace('\n', ' '), r.get('media'))
