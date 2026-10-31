import json, datetime as dt, statistics

PATH = 'data/chats/sarah-x-altr.jsonl'
CLIENT = {'Sarah H'}

rows = [json.loads(l) for l in open(PATH)]
msgs = []
for r in rows:
    if not r.get('sender'):
        continue
    r['dt'] = dt.datetime.fromisoformat(r['ts'])
    r['side'] = 'client' if r['sender'] in CLIENT else 'altr'
    msgs.append(r)

cl = [r for r in msgs if r['side'] == 'client']
al = [r for r in msgs if r['side'] == 'altr']
print('rows', len(rows), 'client', len(cl), 'altr', len(al))
print('first', msgs[0]['ts'], 'last', msgs[-1]['ts'])

q = [r for r in cl if '?' in (r.get('text') or '')]
print('client_question_msgs', len(q))

un = 0
for r in q:
    nxt = [a for a in al if 0 < (a['dt'] - r['dt']).total_seconds() <= 86400]
    if not nxt:
        un += 1
print('unanswered_over_24h', un)

lags = []
for r in q:
    nxt = [a for a in al if a['dt'] > r['dt']]
    if nxt:
        lags.append((nxt[0]['dt'] - r['dt']).total_seconds() / 3600)
lags.sort()
print('lag median', round(statistics.median(lags), 2), 'mean', round(statistics.mean(lags), 2),
      'p90', round(lags[int(.9 * len(lags))], 2))

al.sort(key=lambda r: r['dt'])
gaps = sorted(((b['dt'] - a['dt']).total_seconds() / 86400, a['ts'], b['ts'])
              for a, b in zip(al, al[1:]))[::-1][:10]
print('--- longest ALTR silences (days) ---')
for g in gaps:
    print(round(g[0], 2), g[1], '->', g[2])

cl.sort(key=lambda r: r['dt'])
cgaps = sorted(((b['dt'] - a['dt']).total_seconds() / 86400, a['ts'], b['ts'])
               for a, b in zip(cl, cl[1:]))[::-1][:6]
print('--- longest CLIENT silences (days) ---')
for g in cgaps:
    print(round(g[0], 2), g[1], '->', g[2])
print('client silent since', cl[-1]['ts'])
