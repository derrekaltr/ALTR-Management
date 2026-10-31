"""One-off: dump every finding attributed to / mentioning one person for the narrative layer."""
import json, glob, sys, re
name = sys.argv[1]
full = len(sys.argv) > 2
pat = re.compile(re.escape(name), re.I)
for f in sorted(glob.glob('data/weeks/2026-10-09/*.json')):
    d = json.load(open(f))
    out = []
    for kind, lst, key in (('REM', 'reminders', 'employee'), ('CMP', 'complaints', 'owner'), ('COM', 'commitments', 'who')):
        for r in d.get(lst, []):
            if pat.search(str(r.get(key, ''))):
                txt = r.get('topic') or r.get('issue') or r.get('what')
                extra = f" st={r.get('status')} n={r.get('count', r.get('escalation_count'))}"
                out.append(f"  {kind} [{r.get(key)}]{extra}: {txt}")
                if full:
                    for e in r.get('evidence', []):
                        out.append(f"      ev {e.get('date')} {e.get('sender')}: {e.get('quote')}")
    for w in d.get('wins', []):
        if pat.search(w):
            out.append(f"  WIN: {w}")
    for s in d.get('suggestions', []):
        if pat.search(s):
            out.append(f"  SUG: {s[:400]}")
    for sent in re.split(r'(?<=[.!?])\s+', d.get('summary', '') + ' ' + d.get('health', {}).get('rationale', '')):
        if pat.search(sent):
            out.append(f"  SUM: {sent}")
    if out:
        print(f"## {d['client']}")
        print("\n".join(out))
