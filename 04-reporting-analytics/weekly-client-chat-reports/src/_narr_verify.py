"""One-off: verify every narrative quote is a verbatim substring of a message by that person
in that client's chat on that date, and scan all fields for credential-like strings."""
import json, glob, re, sys, yaml
path = sys.argv[1]
nar = json.load(open(path))
team = yaml.safe_load(open('config/team.yaml'))
alias = {p['name']: set(p['aliases']) for p in team['team'] + team['vendors']}
slug_by_client = {}
for f in glob.glob('data/weeks/2026-10-09/*.json'):
    d = json.load(open(f))
    slug_by_client[d['client']] = d['slug']
ok = True
for name, e in nar.items():
    for q in e['quotes']:
        slug = slug_by_client[q['client']]
        hit = False
        for line in open(f'data/chats/{slug}.jsonl'):
            m = json.loads(line)
            if m.get('sender') not in alias[name] or not m['ts'].startswith(q['date']):
                continue
            t = m.get('text') or ''
            if isinstance(t, list):
                t = ''.join(x if isinstance(x, str) else x.get('text', '') for x in t)
            if q['quote'] in t:
                hit = True
                break
        if not hit:
            ok = False
            print('MISS', name, q)
blob = json.dumps(nar, ensure_ascii=False)
for pat in [r'\b\d{6}\b', r'[\w.+-]+@[\w-]+\.[\w.]+', r'[Pp]assword\s*[:=]', r'\d{4}[A-Z][a-z]+\d+']:
    for m in re.finditer(pat, blob):
        print('CRED?', pat, blob[max(0, m.start()-40):m.end()+20])
print('all quotes verified' if ok else 'quote failures above', '| keys:', list(nar))
