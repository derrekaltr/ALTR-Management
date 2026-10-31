import json, sys, datetime as dt

PATH = 'data/chats/sarah-x-altr.jsonl'
rows = [json.loads(l) for l in open(PATH)]

mode = sys.argv[1]
if mode == 'since':
    since = sys.argv[2]
    for r in rows:
        if r['ts'][:10] >= since:
            t = (r.get('text') or '').replace('\n', ' ⏎ ')
            print(f"{r['ts'][:16]} [{r.get('sender') or 'SERVICE:' + str(r.get('event'))}] {t[:400]}")
elif mode == 'grep':
    needles = [n.lower() for n in sys.argv[2:]]
    for i, r in enumerate(rows):
        t = (r.get('text') or '')
        if any(n in t.lower() for n in needles):
            print(f"{r['ts'][:16]} [{r.get('sender')}] {t[:400]}".replace('\n', ' ⏎ '))
elif mode == 'range':
    a, b = sys.argv[2], sys.argv[3]
    for r in rows:
        if a <= r['ts'][:10] <= b:
            t = (r.get('text') or '').replace('\n', ' ⏎ ')
            print(f"{r['ts'][:16]} [{r.get('sender') or 'SERVICE:' + str(r.get('event'))}] {t[:400]}")
