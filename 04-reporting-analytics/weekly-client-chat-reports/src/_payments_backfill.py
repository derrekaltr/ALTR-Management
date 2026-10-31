"""One-off: backfill the `late` flag render.py keys off, for findings files whose
subagent omitted it. Values assigned from each entry's own note text, following the
convention in data/weeks/2026-08-21 and 2026-08-28 (true = real payment lateness,
arrears, or money at risk; false = on-time / not yet due / structural context)."""
import json
from pathlib import Path

WEEK = Path('data/weeks/2026-09-04')

# slug -> list of `late` values, one per payments[] entry, in order
DECISIONS = {
    'alex-paige-moore-x-altr': [False, False, True],
    'barbara-x-altr':          [False, True],
    'haileigh-cox-x-altr':     [False, True],
    'lauryn-x-altr':           [True, True, True, True],
    'lilia-x-altr':            [True],
    'liza-kovalenko-x-altr':   [False, False],
    'sarah-x-altr':            [False, False, False],
    'shayna-x-altr':           [False, True, False],
}

for slug, flags in DECISIONS.items():
    path = WEEK / f'{slug}.json'
    obj = json.loads(path.read_text())
    pays = obj['payments']
    assert len(pays) == len(flags), f'{slug}: {len(pays)} payments vs {len(flags)} flags'
    for p, flag in zip(pays, flags):
        assert 'late' not in p, f'{slug}: refusing to overwrite an existing late flag'
        p['late'] = flag
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
    print(f'{slug}: set late={flags}')
