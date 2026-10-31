"""One-off: aggregate per-employee attributions across this week's client findings,
so the rollup in _employees.json can be written from real counts rather than memory."""
import json, glob, sys
from collections import defaultdict

WEEK = sys.argv[1] if len(sys.argv) > 1 else '2026-09-11'

EXCLUDED = {'Derrek', 'Nick (DMCA)', 'Noah'}

agg = defaultdict(lambda: defaultdict(lambda: {
    'reminders': 0, 'reminder_topics': [], 'complaints': [], 'kept': 0,
    'overdue': 0, 'pending': 0, 'commitments': []}))

for f in sorted(glob.glob(f'data/weeks/{WEEK}/*.json')):
    if f.endswith('_employees.json'):
        continue
    d = json.load(open(f))
    client = d['client']
    for r in d.get('reminders', []):
        e = r.get('employee', '?')
        agg[e][client]['reminders'] += r.get('count', 1)
        agg[e][client]['reminder_topics'].append(r.get('topic', ''))
    for c in d.get('complaints', []):
        e = c.get('owner') or '?'
        agg[e][client]['complaints'].append(f"[{c.get('status')}] {c.get('issue','')}")
    for c in d.get('commitments', []):
        e = c.get('who', '?')
        st = c.get('status')
        key = {'done': 'kept', 'overdue': 'overdue', 'pending': 'pending'}.get(st)
        if key:
            agg[e][client][key] += 1
        agg[e][client]['commitments'].append(f"[{st}] {c.get('what','')}")

for emp in sorted(agg, key=lambda k: -sum(
        v['reminders'] + len(v['complaints']) + v['overdue'] for v in agg[k].values())):
    tot_r = sum(v['reminders'] for v in agg[emp].values())
    tot_c = sum(len(v['complaints']) for v in agg[emp].values())
    tot_o = sum(v['overdue'] for v in agg[emp].values())
    tot_k = sum(v['kept'] for v in agg[emp].values())
    tot_p = sum(v['pending'] for v in agg[emp].values())
    mark = '   [EXCLUDED FROM TEAM TAB]' if emp in EXCLUDED else ''
    print(f"\n===== {emp} ===== clients={len(agg[emp])} reminders={tot_r} "
          f"complaints={tot_c} kept={tot_k} pending={tot_p} overdue={tot_o}{mark}")
    for client, v in sorted(agg[emp].items()):
        print(f"  -- {client}: rem={v['reminders']} kept={v['kept']} pend={v['pending']} over={v['overdue']}")
        for t in v['reminder_topics']:
            print(f"       reminded: {t[:120]}")
        for c in v['complaints']:
            print(f"       complaint: {c[:150]}")
        for c in v['commitments']:
            print(f"       commit: {c[:150]}")
