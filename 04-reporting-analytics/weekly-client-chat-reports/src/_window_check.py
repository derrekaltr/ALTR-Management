"""One-off helper: in-window message counts + roster gaps for the weekly run."""
import json, glob, sys, yaml, datetime

WS = datetime.datetime.fromisoformat(sys.argv[1])

team = yaml.safe_load(open('config/team.yaml'))
clients = yaml.safe_load(open('config/clients.yaml'))
known = set()
for m in team.get('team', []):
    known.update(m.get('aliases', [])); known.add(m['name'])
for v in team.get('vendors', []):
    known.update(v.get('aliases', [])); known.add(v['name'])
for c in clients['clients']:
    known.update(c.get('client_aliases', [])); known.add(c['name'])

unknown, rows, allwarn = {}, [], []
for f in sorted(glob.glob('data/chats/*.meta.json')):
    d = json.load(open(f))
    slug = d['slug']
    for nm, cnt in d['senders'].items():
        if nm not in known:
            unknown.setdefault(nm, []).append((slug, cnt))
    if d.get('warnings'):
        allwarn.append((slug, d['warnings']))
    n = 0
    for line in open(f.replace('.meta.json', '.jsonl')):
        m = json.loads(line)
        ts = m.get('date') or m.get('ts') or m.get('timestamp')
        if ts and datetime.datetime.fromisoformat(ts) > WS:
            n += 1
    rows.append((slug, d['messages'], n, d['last_ts'][:10]))

print("=== IN-WINDOW COUNTS ===")
for s, t, n, l in sorted(rows, key=lambda r: -r[2]):
    print(f"{s:32} total={t:5} window={n:4} last={l}")
print("\n=== UNKNOWN SENDERS ===")
print(json.dumps(unknown, indent=1) if unknown else "none")
print("\n=== WARNINGS ===")
print(allwarn if allwarn else "none")
