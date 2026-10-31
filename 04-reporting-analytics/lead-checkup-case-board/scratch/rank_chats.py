#!/usr/bin/env python3
"""Rank chats by Altr Services business-signal density."""
import json, re, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

SERVICE = re.compile(r"unban|ban(?:ned)?\b|recover|verif|blue (?:badge|check)|badge|\bmeta\b|instagram|\big\b|\bfb\b|facebook|tiktok|snap(?:chat)?\b|twitter|\bx account|telegram|account|username|handle\b|followers|disabled|hacked|locked|suspend|appeal|restore|reinstat|altr", re.I)
MONEY = re.compile(r"invoice|\bowe[sd]?\b|balance|deposit|\bpaid\b|payment|\bpay\b|zelle|venmo|cash ?app|apple ?pay|\bwire\b|crypto|\bbtc\b|\beth\b|usdt|paypal|refund|price|quote|charge|\$\s?\d|\bk\b for|half now|half up", re.I)
ANGER = re.compile(r"scam|fraud|lawyer|sue\b|report you|bullshit|\bwtf\b|pissed|ridiculous|ignor|no response|been (?:waiting|a (?:week|month))|still nothing|any update|update\??$|it'?s been|taking (?:so|too) long|forever", re.I)
DOLLAR = re.compile(r"\$\s?\d[\d,]*")

stats = {}
for fn in ("imessage.jsonl", "whatsapp.jsonl"):
    with open(os.path.join(HERE, fn)) as f:
        for line in f:
            m = json.loads(line)
            key = (m["src"], m["chat_id"])
            s = stats.get(key)
            if s is None:
                s = stats[key] = {"chat": m["chat"], "group": m["group"], "n": 0, "svc": 0, "money": 0,
                                  "anger": 0, "dollars": [], "first": m["ts"], "last": m["ts"],
                                  "last_in": None, "last_out": None, "atts": 0,
                                  "in_n": 0, "out_n": 0}
            t = m.get("text", "")
            s["n"] += 1
            s["last"] = m["ts"]
            if m["from_me"]:
                s["out_n"] += 1; s["last_out"] = m["ts"]
            else:
                s["in_n"] += 1; s["last_in"] = m["ts"]
            if m.get("atts"):
                s["atts"] += len(m["atts"])
            if not t or m.get("react", 0) >= 2000:
                continue
            if SERVICE.search(t): s["svc"] += 1
            if MONEY.search(t): s["money"] += 1
            if ANGER.search(t): s["anger"] += 1
            s["dollars"].extend(DOLLAR.findall(t)[:3])

rows = []
for (src, cid), s in stats.items():
    # two-way conversation required; score service+money together
    score = s["svc"] * 1.0 + s["money"] * 2.0 + s["anger"] * 1.5 + min(len(s["dollars"]), 20) * 2
    if s["svc"] == 0 and s["money"] == 0:
        continue
    rows.append((score, src, cid, s))
rows.sort(key=lambda r: -r[0])

out = []
for score, src, cid, s in rows:
    out.append({"src": src, "chat_id": cid, "chat": s["chat"][:60], "group": s["group"],
                "score": round(score, 1), "msgs": s["n"], "in": s["in_n"], "out": s["out_n"],
                "svc": s["svc"], "money": s["money"], "anger": s["anger"],
                "dollar_samples": list(dict.fromkeys(s["dollars"]))[:8],
                "atts": s["atts"], "first": s["first"], "last": s["last"]})
with open(os.path.join(HERE, "chat_ranking.json"), "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

print(f"chats with signal: {len(out)}")
for r in out[:60]:
    print(f"{r['score']:>8} {r['src'][:2]} id={r['chat_id']:<6} grp={int(r['group'])} n={r['msgs']:<5} svc={r['svc']:<4} $={r['money']:<4} anger={r['anger']:<3} last={r['last'][:10]} | {r['chat']}")
