import json, sys, collections, datetime
P = 'data/chats/sarah-lloyd-x-altr.jsonl'
since = sys.argv[1] if len(sys.argv) > 1 else '2026-09-20'
rows = [json.loads(l) for l in open(P)]
print('total', len(rows), 'first', rows[0]['ts'], 'last', rows[-1]['ts'])
for r in rows:
    if r['ts'][:10] >= since:
        t = (r.get('text') or '').replace('\n', ' ')
        print(r['id'], r['ts'][:16], r.get('sender'), '|', t[:400], '| media' if r.get('media') else '', '| svc' if r.get('service') else '')
