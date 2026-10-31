#!/usr/bin/env python3
"""Objective customer-success metrics computed from message timestamps.

Usage: python3 src/cs_metrics.py [days]   (default: 30-day window + full history)
Writes data/analysis/cs_metrics.json and prints a table.
"""
import json, sys, statistics
from datetime import datetime, timedelta
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
clients = yaml.safe_load((ROOT / "config/clients.yaml").read_text())["clients"]

def slug(folder): return folder.lower().replace(" ", "-")
def parse(ts): return datetime.fromisoformat(ts)

def analyze(msgs, client_side, since=None):
    msgs = [m for m in msgs if not m.get("service") and m.get("ts")]
    msgs.sort(key=lambda m: m["ts"])
    if since:
        msgs = [m for m in msgs if parse(m["ts"]).replace(tzinfo=None) >= since]
    if not msgs:
        return None
    is_client = lambda m: m["sender"] in client_side
    lags, unanswered, questions = [], 0, 0
    # response lag: client message -> next team message (only measured at the START of a client burst)
    i = 0
    while i < len(msgs):
        m = msgs[i]
        if is_client(m):
            burst_start = parse(m["ts"])
            j = i
            while j + 1 < len(msgs) and is_client(msgs[j + 1]): j += 1
            burst_has_q = any("?" in x.get("text", "") for x in msgs[i:j + 1])
            if burst_has_q: questions += 1
            nxt = next((x for x in msgs[j + 1:] if not is_client(x)), None)
            if nxt:
                lag = (parse(nxt["ts"]) - burst_start).total_seconds() / 3600
                lags.append(lag)
                if burst_has_q and lag > 24: unanswered += 1
            else:
                if burst_has_q: unanswered += 1  # never answered
            i = j + 1
        else:
            i += 1
    # initiative: who starts a conversation after >12h quiet
    team_starts = client_starts = 0
    for a, b in zip(msgs, msgs[1:]):
        if (parse(b["ts"]) - parse(a["ts"])).total_seconds() > 12 * 3600:
            if is_client(b): client_starts += 1
            else: team_starts += 1
    # longest gap with no team message
    team_ts = [parse(m["ts"]) for m in msgs if not is_client(m)]
    max_silence = 0.0
    if team_ts:
        bounds = [parse(msgs[0]["ts"])] + team_ts + [parse(msgs[-1]["ts"])]
        max_silence = max((b - a).total_seconds() / 86400 for a, b in zip(bounds, bounds[1:]))
    return {
        "messages": len(msgs),
        "client_messages": sum(1 for m in msgs if is_client(m)),
        "median_response_h": round(statistics.median(lags), 1) if lags else None,
        "p90_response_h": round(sorted(lags)[int(len(lags) * 0.9) - 1], 1) if len(lags) >= 10 else None,
        "pct_over_24h": round(100 * sum(1 for l in lags if l > 24) / len(lags)) if lags else None,
        "client_question_bursts": questions,
        "questions_unanswered_24h": unanswered,
        "team_initiated_pct": round(100 * team_starts / (team_starts + client_starts)) if (team_starts + client_starts) else None,
        "max_team_silence_days": round(max_silence, 1),
        "last_client_msg": max((m["ts"][:10] for m in msgs if is_client(m)), default=None),
    }

since = datetime(2026, 8, 26) - timedelta(days=DAYS)
out = {}
for c in clients:
    p = ROOT / "data/chats" / f"{slug(c['folder'])}.jsonl"
    if not p.exists(): continue
    msgs = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    side = set(c.get("client_aliases") or [])
    out[c["name"]] = {"full": analyze(msgs, side), f"last_{DAYS}d": analyze(msgs, side, since)}

(ROOT / "data/analysis/cs_metrics.json").write_text(json.dumps(out, indent=2))
hdr = f"{'CLIENT':<17}{'MSGS':>6}{'MEDIAN h':>10}{'P90 h':>8}{'>24h%':>7}{'Q?':>5}{'UNANS':>7}{'TEAM-INIT%':>12}{'MAXSILENCE d':>14}  LAST CLIENT MSG"
for label in ("full", f"last_{DAYS}d"):
    print(f"\n=== {label.upper()} ===\n{hdr}")
    for name, d in sorted(out.items(), key=lambda kv: -((kv[1][label] or {}).get("pct_over_24h") or 0)):
        m = d[label]
        if not m: print(f"{name:<17}   (no messages)"); continue
        f = lambda v: "-" if v is None else v
        print(f"{name:<17}{m['messages']:>6}{f(m['median_response_h']):>10}{f(m['p90_response_h']):>8}{f(m['pct_over_24h']):>7}{m['client_question_bursts']:>5}{m['questions_unanswered_24h']:>7}{f(m['team_initiated_pct']):>12}{m['max_team_silence_days']:>14}  {m['last_client_msg']}")
