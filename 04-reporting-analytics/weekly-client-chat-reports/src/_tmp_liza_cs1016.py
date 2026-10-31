import json, re, sys
if sys.argv[1:2] == ['validate']:
    d = json.load(open('data/analysis/cs-gaps-2026-10-16/liza-kovalenko-x-altr.json'))
    print('ok', len(d['dimensions']), sorted(d['dimensions']))
    sys.exit()
since = sys.argv[1] if len(sys.argv) > 1 else '2026-10-08'
until = sys.argv[2] if len(sys.argv) > 2 else '9999'
for l in open('data/chats/liza-kovalenko-x-altr.jsonl'):
    m = json.loads(l)
    senders = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    if since <= m['ts'] < until and (not senders or (m.get('sender') or '') in senders):
        t = (m.get('text') or '')
        t = re.sub(r'\b\d{6}\b', '[6DIGIT]', t)
        t = re.sub(r'(?i)(pass(word)?|pw)\s*[:\-]?\s*\S+', r'\1 [REDACTED]', t)
        print(m['id'], m['ts'][:16], m.get('sender'), '|', t[:500].replace('\n', ' / '), '|',
              m.get('media') or '', m.get('event') or m.get('service') or '', m.get('reply_to') or '')
