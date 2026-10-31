"""One-off helper: report which payment entries carry the `late` flag render.py keys off."""
import json, glob

for f in sorted(glob.glob('data/weeks/2026-09-04/*.json')):
    if f.endswith('_employees.json'):
        continue
    d = json.load(open(f))
    pays = d.get('payments', [])
    if not pays:
        continue
    print(f"\n{d['slug']}  ({len(pays)} payment entries)")
    for p in pays:
        has = 'late' in p
        print(f"   late={p.get('late')!r:8} {'' if has else '[MISSING] '}note={p.get('note','')[:110]}")
