#!/usr/bin/env python3
"""
generate_dashboard.py — build a self-contained dashboard/index.html from the JSON data.

Reads:  data/listings.json, data/services.json, data/outreach.json
Writes: dashboard/index.html   (open directly in a browser; no server needed)

Run:  python3 scripts/generate_dashboard.py   (run analyze.py first)
"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "dashboard" / "index.html"

STATUS_LABELS = {
    "pending_approval": ("Pending approval", "#b45309"),
    "approved": ("Approved", "#0369a1"),
    "sent": ("Message sent", "#6d28d9"),
    "replied_yes": ("Replied: YES (bulk)", "#15803d"),
    "replied_no": ("Replied: no", "#b91c1c"),
    "no_response": ("No response", "#6b7280"),
    "skipped": ("Skipped", "#9ca3af"),
}
ACTIVITY_BADGE = {
    "active": ("#dcfce7", "#166534", "active"),
    "stale": ("#fef9c3", "#854d0e", "stale"),
    "cold": ("#fee2e2", "#991b1b", "cold"),
    "unknown": ("#f1f5f9", "#475569", "no reviews"),
}


def load(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def esc(v):
    return html.escape("" if v is None else str(v))


def money(v):
    if v is None:
        return "—"
    try:
        return f"${float(v):,.0f}"
    except (TypeError, ValueError):
        return esc(v)


def badge(text, bg, fg):
    return (f'<span style="background:{bg};color:{fg};padding:2px 8px;'
            f'border-radius:10px;font-size:12px;font-weight:600;white-space:nowrap">'
            f'{esc(text)}</span>')


def activity_badge(activity):
    bg, fg, label = ACTIVITY_BADGE.get(activity, ACTIVITY_BADGE["unknown"])
    return badge(label, bg, fg)


def success_cell(p):
    """Success rate + review count; badge colored by the >60% quality gate."""
    sr = p.get("success_rate")
    reviews = p.get("review_count") or 0
    if not isinstance(sr, (int, float)):
        return badge("no score", "#f1f5f9", "#64748b")
    qualified = p.get("qualified")
    bg, fg = ("#dcfce7", "#166534") if qualified else ("#fee2e2", "#991b1b")
    label = f"{sr:.1f}%"
    suffix = f" · {reviews}★" if reviews else ""
    gate = "" if qualified else " ✗"
    return badge(label + suffix + gate, bg, fg)


def build():
    listings = load(DATA / "listings.json", {"listings": {}, "meta": {}})
    services = load(DATA / "services.json", {"services": {}})
    outreach = load(DATA / "outreach.json", {"contacts": {}})

    all_listings = listings.get("listings", {})
    svc = services.get("services", {})
    contacts = outreach.get("contacts", {})

    # --- Summary stats ---
    n_listings = len(all_listings)
    n_services = len(svc)
    n_new = sum(1 for l in all_listings.values()
                if l.get("first_seen") == l.get("last_seen") and l.get("first_seen"))
    status_counts = {}
    for c in contacts.values():
        status_counts[c.get("status")] = status_counts.get(c.get("status"), 0) + 1
    deals = status_counts.get("replied_yes", 0)
    savings = 0.0
    for s in svc.values():
        yp, bp = s.get("your_price"), s.get("best_price")
        if isinstance(yp, (int, float)) and isinstance(bp, (int, float)) and bp < yp:
            savings += yp - bp

    cards = [
        ("Services tracked", n_services),
        ("Listings tracked", n_listings),
        ("New this run", n_new),
        ("Outreach pending", status_counts.get("pending_approval", 0)),
        ("Messages sent", status_counts.get("sent", 0) + deals + status_counts.get("replied_no", 0) + status_counts.get("no_response", 0)),
        ("Bulk deals (yes)", deals),
        ("Est. potential savings", money(savings)),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="card-val">{esc(v)}</div>'
        f'<div class="card-lbl">{esc(l)}</div></div>' for l, v in cards
    )

    # --- Recommendations ---
    recs = [(cid, s) for cid, s in svc.items() if s.get("recommendation")]
    if recs:
        rec_rows = "".join(
            f'<li><strong>{esc(s["display"])}:</strong> {esc(s["recommendation"])}</li>'
            for _, s in recs
        )
        rec_html = f'<div class="panel rec"><h2>⚡ Recommendations</h2><ul>{rec_rows}</ul></div>'
    else:
        rec_html = ('<div class="panel"><h2>⚡ Recommendations</h2>'
                    '<p class="muted">None yet — add <code>your_price</code> to catalog.json '
                    'and run a scan to surface cheaper alternatives.</p></div>')

    # --- Competitive view (by service) ---
    comp_blocks = []
    for cid, s in sorted(svc.items(), key=lambda kv: kv[1]["display"].lower()):
        rows = []
        for p in s.get("providers", []):
            star = " ⭐" if p.get("is_best_price") else ""
            seller = (f'<a href="{esc(p.get("listing_url"))}" target="_blank">'
                      f'{esc(p.get("seller"))}</a>' if p.get("listing_url")
                      else esc(p.get("seller")))
            dim = "" if p.get("qualified") else ' style="opacity:.5"'
            rows.append(
                f"<tr{dim}><td>{seller}{star}</td><td>{money(p.get('price'))}</td>"
                f"<td>{success_cell(p)}</td>"
                f"<td>{esc(p.get('turnaround'))}</td>"
                f"<td>{activity_badge(p.get('activity'))}</td>"
                f"<td class='muted'>{esc(p.get('last_review_date') or '—')}</td></tr>"
            )
        tag = badge("you sell this", "#e0e7ff", "#3730a3") if s.get("in_catalog") \
            else badge("NEW to you", "#fde68a", "#92400e")
        yp = f' · your cost {money(s.get("your_price"))}' if s.get("your_price") else ""
        qc = s.get("qualified_count", 0)
        qc_txt = f' · {qc} trusted (>60%)' if s.get("providers") else ""
        comp_blocks.append(
            f'<div class="svc"><h3>{esc(s["display"])} {tag}'
            f'<span class="muted">{yp}{qc_txt}</span></h3>'
            f'<table class="tbl"><thead><tr><th>Provider</th><th>Price</th>'
            f'<th>Success</th><th>Turnaround</th><th>Activity</th><th>Last review</th>'
            f'</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
        )
    comp_html = ('<div class="panel"><h2>📊 Competitive view (by service)</h2>'
                 + ("".join(comp_blocks) or '<p class="muted">No listings yet.</p>')
                 + '</div>')

    # --- Outreach table ---
    o_rows = []
    for c in sorted(contacts.values(), key=lambda c: c.get("drafted_at") or ""):
        label, color = STATUS_LABELS.get(c.get("status"), (c.get("status"), "#374151"))
        o_rows.append(
            f"<tr><td>{esc(c.get('seller'))}</td>"
            f"<td>{esc(c.get('service_type'))}</td>"
            f"<td>{badge(label, '#f3f4f6', color)}</td>"
            f"<td>{money(c.get('regular_price'))}</td>"
            f"<td>{money(c.get('bulk_price'))}</td>"
            f"<td class='muted'>{esc(c.get('sent_at') or '—')}</td></tr>"
        )
    outreach_html = (
        '<div class="panel"><h2>✉️ Outreach & pricing</h2>'
        '<table class="tbl"><thead><tr><th>Seller</th><th>Service</th><th>Status</th>'
        '<th>Regular price</th><th>Bulk price</th><th>Sent</th></tr></thead><tbody>'
        + ("".join(o_rows) or '<tr><td colspan="6" class="muted">No outreach yet.</td></tr>')
        + '</tbody></table></div>'
    )

    # --- All listings table ---
    l_rows = []
    for l in sorted(all_listings.values(), key=lambda l: l.get("last_seen") or "", reverse=True):
        link = (f'<a href="{esc(l.get("url"))}" target="_blank">{esc(l.get("title"))}</a>'
                if l.get("url") else esc(l.get("title")))
        new = " 🆕" if (l.get("first_seen") and l.get("first_seen") == l.get("last_seen")) else ""
        l_rows.append(
            f"<tr><td>{link}{new}</td><td>{esc(l.get('seller'))}</td>"
            f"<td>{money(l.get('price'))}</td><td>{esc(l.get('turnaround'))}</td>"
            f"<td>{esc((l.get('requirements') or '')[:120])}</td>"
            f"<td class='muted'>{esc(l.get('last_seen') or '—')}</td></tr>"
        )
    listings_html = (
        '<div class="panel"><h2>🗂️ All listings</h2>'
        '<table class="tbl"><thead><tr><th>Listing</th><th>Seller</th><th>Price</th>'
        '<th>Turnaround</th><th>Requirements</th><th>Last seen</th></tr></thead><tbody>'
        + ("".join(l_rows) or '<tr><td colspan="6" class="muted">No listings yet.</td></tr>')
        + '</tbody></table></div>'
    )

    last_run = listings.get("meta", {}).get("last_run") or "never"
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SWAPD Marketplace Dashboard</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0; background: #f8fafc; color: #0f172a; }}
  header {{ background: #0f172a; color: #fff; padding: 20px 28px; }}
  header h1 {{ margin: 0; font-size: 20px; }}
  header .sub {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr));
    gap: 12px; margin-bottom: 20px; }}
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; }}
  .card-val {{ font-size: 24px; font-weight: 700; }}
  .card-lbl {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  .panel {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 20px; }}
  .panel h2 {{ margin: 0 0 12px; font-size: 16px; }}
  .rec {{ border-left: 4px solid #f59e0b; }}
  .rec ul {{ margin: 0; padding-left: 20px; line-height: 1.7; }}
  .svc {{ margin-bottom: 18px; }}
  .svc h3 {{ font-size: 14px; margin: 0 0 6px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
  table.tbl {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  table.tbl th {{ text-align: left; color: #64748b; font-weight: 600;
    border-bottom: 2px solid #e2e8f0; padding: 6px 8px; }}
  table.tbl td {{ border-bottom: 1px solid #f1f5f9; padding: 6px 8px; vertical-align: top; }}
  a {{ color: #2563eb; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .muted {{ color: #94a3b8; }}
  code {{ background: #f1f5f9; padding: 1px 5px; border-radius: 4px; }}
</style></head>
<body>
<header>
  <h1>SWAPD Marketplace Dashboard</h1>
  <div class="sub">Last scan: {esc(last_run)} · Page generated: {esc(generated)}</div>
</header>
<main>
  <div class="cards">{cards_html}</div>
  {rec_html}
  {comp_html}
  {outreach_html}
  {listings_html}
</main>
<script id="raw-data" type="application/json">{json.dumps({
    "listings": listings, "services": services, "outreach": outreach
})}</script>
</body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"dashboard: wrote {OUT} ({n_services} services, {n_listings} listings)")


if __name__ == "__main__":
    build()
