"""One-off: last N messages by a sender alias set (any date) across the active chats, for narrative quotes.
Usage: python3 src/_narr_last.py "Alias1|Alias2" [n] [since YYYY-MM-DD]"""
import json, glob, sys, os
aliases = set(sys.argv[1].split('|'))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
since = sys.argv[3] if len(sys.argv) > 3 else '0000'
slugs = [os.path.basename(f)[:-5] for f in glob.glob('data/weeks/2026-10-09/*.json')]
rows = []
for slug in sorted(slugs):
    client = json.load(open(f'data/weeks/2026-10-09/{slug}.json'))['client']
    for line in open(f'data/chats/{slug}.jsonl'):
        m = json.loads(line)
        if m.get('service') or m.get('sender') not in aliases:
            continue
        t = m.get('text') or ''
        if isinstance(t, list):
            t = ''.join(x if isinstance(x, str) else x.get('text', '') for x in t)
        if m['ts'][:10] >= since:
            rows.append((m['ts'], client, m.get('sender'), t[:260]))
rows.sort()
for r in rows[-n:]:
    print(r[0][:10], r[1], '|', r[2], '|', repr(r[3]))
