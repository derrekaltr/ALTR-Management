#!/usr/bin/env python3
"""Merge targets + live route sweep + live fan-overlap into dashboard/data.js.

ALL relationship signals are live-verified from @brown_derrek's own Instagram
session. data/ig-export/ is NOT used: that export belongs to a different account
(53,408 followers / 8,166 following vs the live account's 7,228 / 3,076) and
produced two false "follows you" flags on 2026-09-17.

A route = someone the CREATOR follows whom Derrek also follows (data/routes.json).
  friend tier = that route also follows Derrek back -> they can make the intro
                (verified against Derrek's own followers list, 2026-09-18)
  oneway tier = Derrek follows them but gets no follow-back -> warm them up first

Scoring (0-100), routes first:
  friend routes ... 22*log2(1+n), capped 70   (diminishing returns)
  one-way routes .. +4 each, capped 10
  they follow you . +25   (live-verified: currently nobody)
  you follow them . +5
  fan overlap ..... 2*ln(1+n), capped 8       (awareness only, not a path in)
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STATUSES = ["Have contact", "Have route", "Need access"]


def load(name, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


targets = load("targets.json", {"targets": []})["targets"]
mutuals = load("mutuals.json", {"profiles": {}})["profiles"]
routes_data = load("routes.json", {"profiles": {}})["profiles"]

rows = []
for t in targets:
    ig = (t.get("ig_handle") or "").lower()
    m = mutuals.get(ig, {})
    rt = routes_data.get(ig, {})

    swept = bool(m.get("swept"))
    you_follow = bool(m.get("you_follow", False))
    follows_you = bool(m.get("follows_you", False))
    mutual_count = m.get("mutual_count")
    if mutual_count is None and swept:
        mutual_count = len(m.get("mutual_usernames", []) or [])

    routes = rt.get("routes", [])
    friend_routes = [r["u"] for r in routes if r["tier"] == "friend"]
    oneway_routes = [r["u"] for r in routes if r["tier"] == "oneway"]
    verified = {r["u"] for r in routes if r.get("verified")}

    score = min(70, round(22 * math.log2(1 + len(friend_routes))))
    score += min(10, 4 * len(oneway_routes))
    if follows_you:
        score += 25
    if you_follow:
        score += 5
    score += min(8, round(2 * math.log(1 + (mutual_count or 0))))
    score = min(100, score)

    fee_low, fee_high = t.get("fee_low"), t.get("fee_high")
    rows.append({
        **t,
        "you_follow": you_follow,
        "follows_you": follows_you,
        "mutual_count": mutual_count,
        "mutual_usernames": m.get("mutual_usernames", []) or [],
        "friend_routes": friend_routes,
        "oneway_routes": oneway_routes,
        "verified_routes": sorted(verified),
        "route_count": len(routes),
        "routes_swept": bool(rt.get("swept")),
        "routes_note": rt.get("note") or ("IG confirms zero overlap" if rt.get("confirmed_empty") else None),
        "swept": swept,
        "sweep_note": m.get("note"),
        "score": score,
        "fee_mid": (fee_low + fee_high) / 2 if fee_low and fee_high else None,
        "opportunity": round(score * (fee_high or 0) / 1000),
    })

rows.sort(key=lambda r: (-r["score"], -(r["fee_high"] or 0)))

primary = [r for r in rows if not r["is_backup"]]
reachable = [r for r in rows if r["score"] >= 40]
summary = {
    "total": len(rows),
    "primary": len(primary),
    "backup": len(rows) - len(primary),
    "reachable_now": len(reachable),
    "reachable_fee_exposure": sum(r["fee_high"] or 0 for r in reachable if not r["is_backup"]),
    "total_fee_exposure": sum(r["fee_high"] or 0 for r in primary),
    "swept": sum(1 for r in rows if r["swept"]),
    "routes_swept": sum(1 for r in rows if r["routes_swept"]),
    "with_routes": sum(1 for r in rows if r["route_count"] > 0),
    "with_friend_routes": sum(1 for r in rows if r["friend_routes"]),
    "follows_you_count": sum(1 for r in rows if r["follows_you"]),
    "with_ig": sum(1 for r in rows if r.get("ig_handle")),
    "status_counts": {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES},
}

out = "const DATA = " + json.dumps({"summary": summary, "rows": rows}, indent=1) + ";\n"
(ROOT / "dashboard").mkdir(exist_ok=True)
(ROOT / "dashboard" / "data.js").write_text(out)
print(f"dashboard/data.js: {len(rows)} rows | {summary['with_routes']} with routes "
      f"| {summary['with_friend_routes']} with friend routes | follows_you={summary['follows_you_count']}")
