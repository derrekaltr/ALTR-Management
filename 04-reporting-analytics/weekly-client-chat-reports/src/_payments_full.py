"""One-off helper: full payment notes for findings files missing the `late` flag."""
import json, glob

for f in sorted(glob.glob('data/weeks/2026-09-04/*.json')):
    if f.endswith('_employees.json'):
        continue
    d = json.load(open(f))
    pays = d.get('payments', [])
    if not any('late' not in p for p in pays):
        continue
    print(f"\n########## {d['slug']} ##########")
    for i, p in enumerate(pays):
        print(f"\n--- [{i}] late={p.get('late')!r} amount={p.get('amount')!r} date={p.get('date')!r}")
        print(p.get('note', ''))
