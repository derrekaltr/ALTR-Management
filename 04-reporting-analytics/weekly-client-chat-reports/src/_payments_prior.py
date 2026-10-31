"""One-off helper: how the `late` flag was used in prior weeks."""
import json, glob

for wk in ['2026-08-21', '2026-08-28']:
    print(f"===== {wk} =====")
    for f in sorted(glob.glob(f'data/weeks/{wk}/*.json')):
        if f.endswith('_employees.json'):
            continue
        d = json.load(open(f))
        for p in d.get('payments', []):
            print(f"{d['slug']:26} late={p.get('late')!r:8} {p.get('note','')[:150]}")
