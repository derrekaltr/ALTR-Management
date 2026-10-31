#!/usr/bin/env python3
"""Tight money/case micro-briefs: only decision-relevant lines."""
import json, re, os
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "micro")
os.makedirs(OUT, exist_ok=True)
WA_MEDIA = os.path.expanduser("~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/")
TODAY = datetime(2026, 9, 18)

DOLLAR = re.compile(r"\$\s?\d[\d,]*(?:\.\d\d)?|\b\d{2,5}(?:\.\d+)?\s?k\b", re.I)
PAYFLOW = re.compile(r"\binvoice|\bowe[sd]?\b|balance|deposit(?:ed)?|\bpaid\b|payment|zelle|venmo|cash ?app|apple ?pay|\bwire[d]?\b|usdt|\bbtc\b|crypto|paypal|refund|\bquote\b|\bprice\b|charge|sent (?:it|you|the|over|now)|just sent|received|receipt|proof|\bpay you\b|\bpay me\b|half|upfront|\bfee\b|\bcost", re.I)
ASK = re.compile(r"how much|what.{0,12}(?:cost|price|charge)|can you (?:do|help|get|fix|unban|recover|verif)|need (?:help|to get|an? )|quote|possible to|do you (?:do|handle)|looking to|i want to|got banned|is banned|was banned|disabled|locked out|hacked|can.{0,8}get.{0,12}back", re.I)
ANGER = re.compile(r"scam|fraud|lawyer|\bsue\b|report you|bullshit|\bwtf\b|pissed|ridiculous|ignor(?:ing|ed)|no response|been waiting|still waiting|still nothing|any update|it'?s been|taking (?:so|too) long|forever|disappoint|unacceptable|chargeback|dispute|refund me|my money back|hello\?|\?\?\?|you there|answer me|what.s going on|following up|checking in", re.I)
DONE = re.compile(r"\bunbanned\b|\bback up\b|\bis back\b|got it back|\brecovered\b|\bverified\b|\bapproved\b|\bdone\b|\bcompleted?\b|\bfixed\b|went through|\bdenied\b|\brejected\b|didn'?t work|not working|failed|no luck|can'?t be|unable", re.I)

index = json.load(open(os.path.join(HERE, "brief_index.json")))
raw = defaultdict(list)
for fn in ("imessage.jsonl", "whatsapp.jsonl"):
    with open(os.path.join(HERE, fn)) as f:
        for line in f:
            m = json.loads(line)
            raw[(m["src"], m["chat_id"])].append(m)

def days_ago(ts):
    return (TODAY - datetime.strptime(ts[:10], "%Y-%m-%d")).days

def clean(t, limit=200):
    return " ".join((t or "").split())[:limit]

out_index = []
for e in index:
    key = (e["src"], e["chat_id"])
    ms = raw.get(key, [])
    if not ms:
        continue
    keep = {}
    for i, m in enumerate(ms):
        t = m.get("text") or ""
        if t.startswith("[reaction"):
            continue
        tags = []
        if DOLLAR.search(t): tags.append("$")
        if PAYFLOW.search(t): tags.append("PAY")
        if ASK.search(t): tags.append("ASK")
        if ANGER.search(t): tags.append("ANGRY")
        if DONE.search(t): tags.append("OUTCOME")
        if m.get("atts") and any(
            (a.get("path") or "").lower().endswith((".png", ".jpg", ".jpeg", ".heic", ".webp"))
            or "image" in (a.get("mime") or "") for a in m["atts"]):
            tags.append("IMG")
        if not tags:
            continue
        # IMG alone only matters near money talk
        if tags == ["IMG"]:
            near = any(DOLLAR.search(ms[j].get("text") or "") or PAYFLOW.search(ms[j].get("text") or "")
                       for j in range(max(0, i - 3), min(len(ms), i + 4)))
            if not near:
                continue
            tags = ["IMG-near-money"]
        keep[i] = tags
    # prune: if huge, keep highest-value tags only
    if len(keep) > 300:
        pri = {k: v for k, v in keep.items() if "$" in v or "ANGRY" in v or "IMG-near-money" in v or "IMG" in v}
        if len(pri) > 300:
            pri = dict(sorted(pri.items())[-300:])
        keep = pri
    slug = re.sub(r"[^A-Za-z0-9]+", "_", e["chat"])[:40].strip("_") or "chat"
    fname = f"{e['src']}_{e['chat_id']}_{slug}.md"
    L = [f"## {e['chat']} [{e['src']}#{e['chat_id']}{' GRP' if e['group'] else ''}] msgs={e['msgs']} "
         f"win={ms[0]['ts'][:10]}..{ms[-1]['ts'][:10]} "
         f"lastClient={e['last_in'][:10] if e['last_in'] else 'never'}({e['days_since_client']}d) "
         f"lastDerek={e['last_out'][:10] if e['last_out'] else 'never'}({e['days_since_derrek']}d) "
         f"{'UNANSWERED' if e['unanswered'] else ''}"]
    prev = -2
    for i in sorted(keep):
        m = ms[i]
        if i != prev + 1:
            L.append("...")
        prev = i
        who = "DEREK" if m["from_me"] else (m["sender"] or "?")[:18]
        L.append(f"[{m['ts'][:16]}]{'|'.join(keep[i])[:22]}| {who}: {clean(m.get('text'))}")
        for a in m.get("atts", []):
            p = a.get("path") or ""
            if p and not p.startswith(("/", "~")):
                p = WA_MEDIA + p
            p = os.path.expanduser(p)
            if p.lower().endswith((".png", ".jpg", ".jpeg", ".heic", ".webp")) or "image" in (a.get("mime") or ""):
                L.append(f"   <IMG {'OK' if os.path.exists(p) else 'MISSING'}: {p}>")
    open(os.path.join(OUT, fname), "w").write("\n".join(L) + "\n")
    out_index.append({**e, "micro": f"micro/{fname}", "mkb": round(os.path.getsize(os.path.join(OUT, fname))/1024, 1),
                      "hits": len(keep)})

json.dump(out_index, open(os.path.join(HERE, "micro_index.json"), "w"), indent=1, ensure_ascii=False)
print(f"{len(out_index)} micro-briefs, {sum(x['mkb'] for x in out_index)/1024:.2f} MB")
print("empty/near-empty:", sum(1 for x in out_index if x['hits'] < 3))
