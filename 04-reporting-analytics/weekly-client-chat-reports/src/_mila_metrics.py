"""Scratch: validate CS-gap metrics for mila-x-altr (reply lags, silence gaps, cadence)."""
import json, datetime
from collections import Counter

rows = [json.loads(l) for l in open('data/chats/mila-x-altr.jsonl')]
msgs = [r for r in rows if not r.get('service')]
CL = 'Callie (Mila)'


def dt(s):
    return datetime.datetime.fromisoformat(s)


team = [m for m in msgs if m['sender'] != CL]
client = [m for m in msgs if m['sender'] == CL]
print('total msgs', len(msgs), 'client', len(client), 'team', len(team))
print('first', msgs[0]['ts'], 'last', msgs[-1]['ts'])

gaps = []
for a, b in zip(team, team[1:]):
    d = (dt(b['ts']) - dt(a['ts'])).total_seconds() / 86400
    gaps.append((round(d, 2), a['ts'][:10], b['ts'][:10], b['sender'], b['text'][:60]))
gaps.sort(reverse=True)
print('TOP TEAM SILENCE GAPS:')
for g in gaps[:8]:
    print(' ', g)

c = Counter()
for m in client:
    c[dt(m['ts']).strftime('%Y-W%V')] += 1
print('client weekly:', sorted(c.items()))

last, first, cnt = {}, {}, Counter()
for m in msgs:
    last[m['sender']] = m['ts'][:10]
    first.setdefault(m['sender'], m['ts'][:10])
    cnt[m['sender']] += 1
print('per sender first/last/count:')
for s in cnt:
    print('  ', s, first[s], '->', last[s], cnt[s])

lags = []
for m in client:
    nxt = [t for t in team if dt(t['ts']) > dt(m['ts'])]
    lags.append(((dt(nxt[0]['ts']) - dt(m['ts'])).total_seconds() / 3600 if nxt else None,
                 m['ts'][:16], m['text'][:60]))
over = [l for l in lags if l[0] is None or l[0] > 24]
print('client msgs with next-team-msg >24h or never:', len(over))
for l in over:
    print('  ', l)
med = sorted(x[0] for x in lags if x[0] is not None)
print('median lag h', round(med[len(med) // 2], 2), 'n', len(med))
