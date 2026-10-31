import json, statistics
from datetime import datetime

rows = [json.loads(l) for l in open('data/chats/sarah-x-altr.jsonl')]
ts = lambda m: datetime.fromisoformat(m['ts'])
C = {'Sarah H'}
msgs = [m for m in rows if not m.get('service') and not m.get('event') and m.get('sender')]
cl = [m for m in msgs if m['sender'] in C]
tm = [m for m in msgs if m['sender'] not in C]
print('rows', len(rows), 'client', len(cl), 'team', len(tm), 'senders', len({m['sender'] for m in tm}),
      'span', rows[0]['ts'][:10], rows[-1]['ts'][:10])
qs = [m for m in cl if '?' in (m.get('text') or '')]
tts = [ts(m) for m in tm]
lags, un = [], []
end = ts(rows[-1])
for q in qs:
    t = ts(q)
    nxt = [x for x in tts if x > t]
    if nxt:
        lags.append((nxt[0] - t).total_seconds() / 3600)
    if (not nxt or (nxt[0] - t).total_seconds() > 86400) and (end - t).total_seconds() > 86400:
        un.append(q)
print('questions', len(qs), 'unans>24h', len(un))
lags.sort()
print('median', round(statistics.median(lags), 2), 'mean', round(statistics.mean(lags), 2),
      'p90', round(lags[int(len(lags) * .9)], 1))
g = max(((tts[i + 1] - tts[i]).total_seconds() / 86400, tts[i], tts[i + 1]) for i in range(len(tts) - 1))
print('max team gap', round(g[0], 2), g[1].date(), g[2].date())
ct = [ts(m) for m in cl]
g = max(((ct[i + 1] - ct[i]).total_seconds() / 86400, ct[i], ct[i + 1]) for i in range(len(ct) - 1))
print('max client gap', round(g[0], 2), g[1].date(), g[2].date())
for q in un[-6:]:
    print(' UN', q['ts'][:16], (q.get('text') or '')[:120])
