#!/usr/bin/env python3
"""Render the weekly client dashboard from findings JSON.

Usage:
    python3 src/render.py 2026-08-08
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[\s_-]+", "-", name)

REPO_ROOT = Path(__file__).resolve().parent.parent
WEEKS_DIR = REPO_ROOT / "data" / "weeks"
CHATS_DIR = REPO_ROOT / "data" / "chats"


def health_status(score):
    if score >= 80:
        return "good", "Healthy"
    if score >= 60:
        return "warning", "Watch"
    if score >= 40:
        return "serious", "At risk"
    return "critical", "Critical"


def sparkline_points(values, width=120, height=32, pad=4):
    """Map a series of health scores (0-100) to SVG polyline points."""
    if not values:
        return ""
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + (width - 2 * pad) * (i / (n - 1) if n > 1 else 0.5)
        y = pad + (height - 2 * pad) * (1 - v / 100)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def load_week(week: str):
    week_dir = WEEKS_DIR / week
    if not week_dir.is_dir():
        sys.exit(f"no findings for week {week} in {WEEKS_DIR}")
    clients, employees = [], None
    for path in sorted(week_dir.glob("*.json")):
        obj = json.loads(path.read_text())
        if path.name == "_employees.json":
            employees = obj
        else:
            clients.append(obj)
    return clients, employees


def load_history():
    """slug -> [(week, health score)] across all week dirs, oldest first."""
    history = {}
    for week_dir in sorted(WEEKS_DIR.iterdir()):
        if not week_dir.is_dir():
            continue
        for path in week_dir.glob("*.json"):
            if path.name == "_employees.json":
                continue
            obj = json.loads(path.read_text())
            history.setdefault(obj["slug"], []).append((week_dir.name, obj["health"]["score"]))
    return history


def load_warnings():
    warnings = []
    for meta_path in sorted(CHATS_DIR.glob("*.meta.json")):
        meta = json.loads(meta_path.read_text())
        for w in meta.get("warnings", []):
            warnings.append(f"{meta['chat']}: {w}")
    return warnings


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    week = sys.argv[1]
    clients, employees = load_week(week)
    history = load_history()

    clients.sort(key=lambda c: c["health"]["score"])
    for c in clients:
        # Analysts store dated evidence under "evidence"; the template renders
        # "quotes". Expose both so the evidence actually shows on the card.
        for field in ("reminders", "complaints", "commitments", "payments"):
            for item in c.get(field) or []:
                if isinstance(item, dict) and not item.get("quotes") and item.get("evidence"):
                    item["quotes"] = item["evidence"]
        status, label = health_status(c["health"]["score"])
        c["status"] = status
        c["status_label"] = label
        scores = [s for _, s in history.get(c["slug"], [])]
        c["spark"] = sparkline_points(scores)
        c["spark_n"] = len(scores)
        c["open_complaints"] = sum(1 for x in c["complaints"] if x["status"] in ("new", "in_progress", "recurring"))
        c["overdue"] = sum(1 for x in c["commitments"] if x["status"] == "overdue")
        c["payment_flag"] = any(p.get("late") for p in c["payments"])

    totals = {
        "clients": len(clients),
        "avg_health": round(sum(c["health"]["score"] for c in clients) / len(clients)) if clients else 0,
        "open_complaints": sum(c["open_complaints"] for c in clients),
        "overdue": sum(c["overdue"] for c in clients),
        "payment_flags": sum(1 for c in clients if c["payment_flag"]),
        "messages": sum(c.get("week_stats", {}).get("messages", 0) for c in clients),
    }

    emp_list = (employees or {}).get("employees", [])
    for e in emp_list:
        e["file"] = f"employees/{slugify(e['name'])}.html"

    env = Environment(loader=FileSystemLoader(REPO_ROOT / "src" / "templates"), autoescape=True)
    env.globals["health_status"] = health_status
    html = env.get_template("dashboard.html.j2").render(
        week=week,
        clients=clients,
        employees=emp_list,
        totals=totals,
        warnings=load_warnings(),
    )

    out = REPO_ROOT / "reports" / week / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(out)

    emp_tpl = env.get_template("employee.html.j2")
    emp_dir = out.parent / "employees"
    emp_dir.mkdir(exist_ok=True)
    for e in emp_list:
        (out.parent / e["file"]).write_text(emp_tpl.render(e=e, week=week))
    if emp_list:
        print(f"{emp_dir} ({len(emp_list)} employee reports)")


if __name__ == "__main__":
    main()
