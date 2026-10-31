"""One-off: list a team member's in-window messages (2026-09-25..2026-10-09) across the 12 active chats,
for picking verbatim narrative quotes. Usage: python3 src/_narr_msgs.py "Alias1|Alias2" [maxlen]"""
import json, glob, sys, os
aliases = set(sys.argv[1].split('|'))
maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 220
slugs = [os.path.basename(f)[:-5] for f in glob.glob('data/weeks/2026-10-09/*.json')]
for slug in sorted(slugs):
    meta_client = json.load(open(f'data/weeks/2026-10-09/{slug}.json'))['client']
    rows = []
    for line in open(f'data/chats/{slug}.jsonl'):
        m = json.loads(line)
        if m.get('service') or m.get('sender') not in aliases:
            continue
        d = m['ts'][:10]
        if not ('2026-09-25' <= d <= '2026-10-09'):
            continue
        t = m.get('text') or ''
        if isinstance(t, list):
            t = ''.join(x if isinstance(x, str) else x.get('text', '') for x in t)
        if t.strip():
            rows.append(f"  {d} {t[:maxlen]!r}")
    if rows:
        print(f"## {meta_client} ({len(rows)})")
        print("\n".join(rows))
