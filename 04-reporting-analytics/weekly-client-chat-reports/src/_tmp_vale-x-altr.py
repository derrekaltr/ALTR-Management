import json, sys
SECRET_IDS = {10, 898, 903, 908}
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
for line in open('data/chats/vale-x-altr.jsonl'):
    m = json.loads(line)
    if not (lo <= m['id'] <= hi):
        continue
    if m.get('service'):
        print(m['id'], m['ts'][:16], 'SERVICE', m.get('event'))
        continue
    t = m.get('text', '') or ''
    if m['id'] in SECRET_IDS:
        t = '[REDACTED credential]'
    extra = ' [media]' if m.get('media') else ''
    rt = f" (re {m['reply_to']})" if m.get('reply_to') else ''
    print(m['id'], m['ts'][:16], m.get('sender'), rt, '|', t.replace('\n', ' / ')[:500] + extra)

if len(sys.argv) > 1 and sys.argv[1] == '0' and len(sys.argv) > 3:
    from datetime import datetime
    msgs = [json.loads(l) for l in open('data/chats/vale-x-altr.jsonl')]
    msgs = [m for m in msgs if not m.get('service')]
    q = [m for m in msgs if m.get('sender') == 'Vale' and '?' in (m.get('text') or '')]
    team = [m for m in msgs if m.get('sender') != 'Vale']
    gaps = []
    for a, b in zip(team, team[1:]):
        d = (datetime.fromisoformat(b['ts']) - datetime.fromisoformat(a['ts'])).total_seconds() / 86400
        gaps.append((round(d, 1), a['ts'][:10], b['ts'][:10]))
    print('total', len(msgs), 'vale', len(msgs) - len(team), 'team', len(team), 'q', len(q))
    print(sorted(gaps)[-4:])
