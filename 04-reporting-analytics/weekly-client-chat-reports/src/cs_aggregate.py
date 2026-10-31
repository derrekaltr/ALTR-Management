#!/usr/bin/env python3
"""Aggregate per-client CS gap JSONs into a cross-client matrix + evidence bank.
Usage: python3 src/cs_aggregate.py data/analysis/cs-gaps-2026-08-26
"""
import json, sys, glob
from collections import defaultdict
from pathlib import Path

d = Path(sys.argv[1])
files = sorted(f for f in glob.glob(str(d / "*.json")) if not Path(f).name.startswith("_"))
rows = [json.loads(open(f).read()) for f in files]
dims = ["responsiveness","follow_through","proactive_communication","onboarding_handoff","chatter_conduct",
        "platform_health","billing_ops","ownership_escalation","disengagement_detection","security_hygiene"]

# matrix
print(f"{'CLIENT':<17}{'STATUS':<9}" + "".join(f"{x[:6]:>7}" for x in dims) + "   TOP FIX")
totals = defaultdict(list)
for r in rows:
    sev = {k: (r["dimensions"].get(k) or {}).get("severity", 0) for k in dims}
    for k, v in sev.items(): totals[k].append(v)
    print(f"{r['client'][:16]:<17}{r['status'][:8]:<9}" + "".join(f"{sev[k]:>7}" for k in dims) + f"   {r.get('top_fix','')[:70]}")
print("\nDIMENSION            AVG   #>=2  #==3")
for k in sorted(dims, key=lambda k: -sum(totals[k]) / max(1, len(totals[k]))):
    v = totals[k]
    print(f"{k:<20}{sum(v)/len(v):>5.2f}{sum(1 for x in v if x >= 2):>6}{sum(1 for x in v if x == 3):>6}")

print("\n=== STATUS ===")
for r in rows: print(f"{r['client']:<18} {r['status']:<9} last client msg {r.get('last_client_message')} — {r.get('status_reason','')[:120]}")

print("\n=== METRICS (analyst counts) ===")
for r in rows:
    m = r.get("metrics", {})
    print(f"{r['client']:<18} Q={m.get('client_questions_total')} unans24h={m.get('unanswered_over_24h')} maxSilence={m.get('max_team_silence_days')}d promises={m.get('promises_kept')}/{m.get('promises_made')} lapsed={m.get('promises_lapsed')}")

# evidence bank per dimension (severity >= 2 only)
bank = defaultdict(list)
for r in rows:
    for k in dims:
        x = r["dimensions"].get(k) or {}
        if x.get("severity", 0) >= 2:
            bank[k].append({"client": r["client"], "severity": x["severity"], "failure": x.get("internal_failure"), "evidence": (x.get("evidence") or [])[:2]})
(d / "_evidence_bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False))
wanted = {r["client"]: {"wanted": r.get("what_client_wanted"), "worked": r.get("what_worked"), "top_fix": r.get("top_fix")} for r in rows}
(d / "_wants_and_wins.json").write_text(json.dumps(wanted, indent=2, ensure_ascii=False))
# markdown scaffold for the narrative report
L = []
L.append(f"# CS gap scaffold — {d.name}\n")
made = sum((r.get("metrics") or {}).get("promises_made") or 0 for r in rows)
kept = sum((r.get("metrics") or {}).get("promises_kept") or 0 for r in rows)
lapsed = sum((r.get("metrics") or {}).get("promises_lapsed") or 0 for r in rows)
q = sum((r.get("metrics") or {}).get("client_questions_total") or 0 for r in rows)
un = sum((r.get("metrics") or {}).get("unanswered_over_24h") or 0 for r in rows)
st = defaultdict(int)
for r in rows: st[r["status"]] += 1
L.append(f"- Accounts: {len(rows)} — " + ", ".join(f"{v} {k}" for k, v in sorted(st.items())))
L.append(f"- Promises: {made} made / {kept} kept / {lapsed} lapsed ({(100*lapsed/made) if made else 0:.0f}% lapsed)")
L.append(f"- Client questions: {q} / {un} unanswered >24h ({(100*un/q) if q else 0:.0f}%)\n")
L.append("## Dimension averages\n")
for k in sorted(dims, key=lambda k: -sum(totals[k]) / max(1, len(totals[k]))):
    v = totals[k]; L.append(f"- {k}: avg {sum(v)/len(v):.2f}, {sum(1 for x in v if x >= 2)} clients >=2, {sum(1 for x in v if x == 3)} at 3")
L.append("\n## Status\n")
for r in rows: L.append(f"- **{r['client']}** — {r['status']} (last client msg {r.get('last_client_message')}): {r.get('status_reason','')}")
L.append("\n## Evidence by dimension (severity >= 2)\n")
for k in dims:
    L.append(f"### {k}")
    for it in sorted(bank.get(k, []), key=lambda x: -x["severity"]):
        L.append(f"- [{it['severity']}] {it['client']}: {it['failure']}")
        for e in it["evidence"][:2]:
            L.append(f"    - \"{e.get('quote','')}\" — {e.get('who','')}, {e.get('date','')}")
L.append("\n## Top fixes\n")
for r in rows: L.append(f"- {r['client']}: {r.get('top_fix','')}")
L.append("\n## What clients want / what worked\n")
for c, w in wanted.items():
    L.append(f"### {c}")
    for x in (w.get("wanted") or []): L.append(f"- want: {x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)}")
    for x in (w.get("worked") or []): L.append(f"- worked: {x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)}")
(d / "_scaffold.md").write_text("\n".join(L))
print(f"\nwrote {d/'_evidence_bank.json'}, {d/'_wants_and_wins.json'}, {d/'_scaffold.md'}")
