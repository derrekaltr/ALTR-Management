#!/usr/bin/env python3
"""Render the internal CS command-center dashboard.

Usage: python3 src/cs_render.py 2026-09-03 [--prev 2026-08-28]
Reads  data/analysis/cs-gaps-<date>/*.json      (analyst findings)
       data/analysis/cs-gaps-<prev>/*.json      (optional, for deltas)
       data/analysis/reports/cs-gaps-<date>-highlights.json (curated triage/drafts)
       data/weeks/*/                            (weekly health history -> trend)
       config/clients.yaml                      (optional monthly_revenue field)
Writes data/analysis/reports/cs-gaps-<date>.html  (self-contained, INTERNAL)
"""
import json, sys, glob
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["responsiveness","follow_through","proactive_communication","onboarding_handoff","chatter_conduct",
        "platform_health","billing_ops","ownership_escalation","disengagement_detection","security_hygiene"]
DIM_LABELS = {"responsiveness":"Responsiveness","follow_through":"Follow-through","proactive_communication":"Proactive comms",
    "onboarding_handoff":"Onboarding","chatter_conduct":"Chatter conduct","platform_health":"Platform health",
    "billing_ops":"Billing ops","ownership_escalation":"Ownership","disengagement_detection":"Quiet-client detection",
    "security_hygiene":"Security"}

def load_run(date):
    d = ROOT / "data/analysis" / f"cs-gaps-{date}"
    if not d.is_dir(): return None
    out = {}
    for f in sorted(glob.glob(str(d / "*.json"))):
        if Path(f).name.startswith("_"): continue
        r = json.loads(Path(f).read_text())
        out[r["client"]] = r
    return out

def load_weekly_health():
    """-> (weeks list, avg per week, per-client score history)"""
    weeks, avgs, per_client = [], [], {}
    for wd in sorted((ROOT / "data/weeks").iterdir()):
        if not wd.is_dir(): continue
        scores = {}
        for f in wd.glob("*.json"):
            if f.name == "_employees.json": continue
            o = json.loads(f.read_text())
            scores[o["client"]] = o["health"]["score"]
        if not scores: continue
        weeks.append(wd.name)
        avgs.append(round(sum(scores.values()) / len(scores)))
        for c, s in scores.items(): per_client.setdefault(c, []).append((wd.name, s))
    return weeks, avgs, per_client

def spark(values, w=120, h=30, pad=3, lo=0, hi=100):
    if not values: return ""
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + (w - 2*pad) * (i / (n - 1) if n > 1 else 0.5)
        y = pad + (h - 2*pad) * (1 - (v - lo) / (hi - lo))
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)

def sev_total(r): return sum((r["dimensions"].get(k) or {}).get("severity", 0) for k in DIMS)

def main():
    date = sys.argv[1]
    prev_date = sys.argv[sys.argv.index("--prev") + 1] if "--prev" in sys.argv else None
    cur = load_run(date); prev = load_run(prev_date) if prev_date else None
    if not cur: sys.exit(f"no run found for {date}")
    hl_path = ROOT / "data/analysis/reports" / f"cs-gaps-{date}-highlights.json"
    hl = json.loads(hl_path.read_text()) if hl_path.exists() else {}
    weeks, avgs, per_client = load_weekly_health()
    revenue = {}
    for c in yaml.safe_load((ROOT / "config/clients.yaml").read_text())["clients"]:
        if c.get("monthly_revenue"): revenue[c["name"]] = c["monthly_revenue"]

    clients = []
    for name, r in cur.items():
        total = sev_total(r)
        ptotal = sev_total(prev[name]) if prev and name in prev else None
        hist = [s for _, s in per_client.get(name, [])]
        dims = []
        for k in DIMS:
            x = r["dimensions"].get(k) or {}
            psev = (prev[name]["dimensions"].get(k) or {}).get("severity") if prev and name in prev else None
            dims.append({"key": k, "label": DIM_LABELS[k], "severity": x.get("severity", 0),
                         "delta": None if psev is None else x.get("severity", 0) - psev,
                         "failure": x.get("internal_failure"), "evidence": (x.get("evidence") or [])[:2]})
        clients.append({"name": name, "status": r["status"], "status_reason": r.get("status_reason", ""),
            "prev_status": prev[name]["status"] if prev and name in prev else None,
            "last_msg": r.get("last_client_message"), "total": total,
            "delta": None if ptotal is None else total - ptotal,
            "dims": dims, "top_fix": r.get("top_fix", ""),
            "wanted": r.get("what_client_wanted") or [], "worked": r.get("what_worked") or [],
            "health_hist": hist, "health_spark": spark(hist), "health_now": hist[-1] if hist else None,
            "revenue": revenue.get(name)})
    order = {"churned": 0, "at_risk": 1, "active": 2}
    clients.sort(key=lambda c: (order.get(c["status"], 3), -c["total"]))
    cmap = {c["name"]: c for c in clients}

    # attach spark/health to triage entries
    for section in ("fires", "this_week", "monitor", "churned"):
        for item in hl.get(section, []):
            c = cmap.get(item.get("client"))
            if c:
                item["spark"] = c["health_spark"]; item["health_now"] = c["health_now"]
                item["revenue"] = c["revenue"]; item["last_msg"] = c["last_msg"]

    dim_rank = []
    for k in DIMS:
        avg = sum((cur[c]["dimensions"].get(k) or {}).get("severity", 0) for c in cur) / len(cur)
        pavg = (sum((prev[c]["dimensions"].get(k) or {}).get("severity", 0) for c in prev) / len(prev)) if prev else None
        n3 = sum(1 for c in cur if (cur[c]["dimensions"].get(k) or {}).get("severity", 0) == 3)
        dim_rank.append({"key": k, "label": DIM_LABELS[k], "avg": round(avg, 2), "n3": n3,
                         "delta": None if pavg is None else round(avg - pavg, 2)})
    dim_rank.sort(key=lambda d: -d["avg"])

    made = sum((cur[c].get("metrics") or {}).get("promises_made") or 0 for c in cur)
    lapsed = sum((cur[c].get("metrics") or {}).get("promises_lapsed") or 0 for c in cur)
    q = sum((cur[c].get("metrics") or {}).get("client_questions_total") or 0 for c in cur)
    un = sum((cur[c].get("metrics") or {}).get("unanswered_over_24h") or 0 for c in cur)
    counts = {s: sum(1 for c in clients if c["status"] == s) for s in ("at_risk", "active", "churned")}
    totals = {"counts": counts, "promise_pct": round(100 * lapsed / made) if made else 0,
              "unanswered_pct": round(100 * un / q) if q else 0}

    trend = {"weeks": weeks, "avgs": avgs, "spark": spark(avgs, w=260, h=64, pad=6),
             "now": avgs[-1] if avgs else None,
             "delta_total": (avgs[-1] - avgs[0]) if len(avgs) > 1 else None,
             "per_week": round((avgs[-1] - avgs[0]) / (len(avgs) - 1), 1) if len(avgs) > 1 else None}

    env = Environment(loader=FileSystemLoader(ROOT / "src/templates"), autoescape=True)
    html = env.get_template("cs_dashboard.html.j2").render(
        date=date, prev_date=prev_date, clients=clients, dims=DIMS, dim_labels=DIM_LABELS,
        dim_rank=dim_rank, totals=totals, hl=hl, trend=trend)
    out = ROOT / "data/analysis/reports" / f"cs-gaps-{date}.html"
    out.write_text(html)
    print(out)

if __name__ == "__main__":
    main()
