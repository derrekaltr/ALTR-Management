#!/usr/bin/env python3
"""Condense per-chat transcripts into case briefs: relevant excerpts + flow metrics."""
import json, re, os
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "briefs")
os.makedirs(OUT, exist_ok=True)
WA_MEDIA = os.path.expanduser("~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/")
TODAY = datetime(2026, 9, 18)

MONEY = re.compile(r"invoice|\bowe[sd]?\b|balance|deposit|\bpaid\b|payment|\bpay(?:ing|ment)?\b|zelle|venmo|cash ?app|apple ?pay|\bwire[d]?\b|crypto|\bbtc\b|\beth\b|usdt|paypal|refund|\bprice\b|quote|charge|\$\s?\d|\d+\s?k\b|sent (?:it|you|the|over)|received|\bfree\b|discount|comp(?:ed)?\b|invoice", re.I)
SERVICE = re.compile(r"unban|\bban(?:ned|s)?\b|recover(?:y|ed)?|verif(?:y|ied|ication)|blue (?:badge|check)|badge|appeal|disabled|suspend|restrict|shadowban|locked|hacked|reinstat|restor|delete[d]?|takedown|flood|\bqueue\b|submitted|escalat|approv|reject|denied|\bdone\b|fixed|back up|got it back|working on|update", re.I)
ANGER = re.compile(r"scam|fraud|lawyer|\bsue\b|report you|bullshit|\bwtf\b|pissed|ridiculous|ignor|no response|been waiting|still waiting|still nothing|any update|it'?s been|taking (?:so|too) long|forever|disappoint|unacceptable|chargeback|dispute|refund me|my money back|hello\?|\?\?\?|you there|answer me|fuck", re.I)
PROOF = re.compile(r"sent|proof|receipt|screenshot|confirm|here'?s? the|just (?:sent|paid)|payment", re.I)
DOLLAR = re.compile(r"\$\s?\d[\d,]*(?:\.\d\d)?|\b\d+(?:\.\d+)?\s?k\b", re.I)

REACT_PREFIX = re.compile(r"^\[reaction")

manifest = json.load(open(os.path.join(HERE, "manifest.json")))
raw = defaultdict(list)
for fn in ("imessage.jsonl", "whatsapp.jsonl"):
    with open(os.path.join(HERE, fn)) as f:
        for line in f:
            m = json.loads(line)
            raw[(m["src"], m["chat_id"])].append(m)

def days_ago(ts):
    return (TODAY - datetime.strptime(ts[:10], "%Y-%m-%d")).days

def clean(t, limit=260):
    t = " ".join((t or "").split())
    return t[:limit] + ("…" if len(t) > limit else "")

index = []
for entry in manifest:
    key = (entry["src"], entry["chat_id"])
    ms = raw.get(key, [])
    if not ms:
        continue
    # flow metrics
    last_in = last_out = None
    in_n = out_n = 0
    for m in ms:
        if m["from_me"]:
            out_n += 1; last_out = m["ts"]
        else:
            in_n += 1; last_in = m["ts"]
    last = ms[-1]
    unanswered = not last["from_me"]
    # score each message
    keep = set()
    tagged = []
    for i, m in enumerate(ms):
        t = m.get("text") or ""
        if REACT_PREFIX.match(t):
            continue
        tags = []
        if DOLLAR.search(t): tags.append("$")
        if MONEY.search(t): tags.append("money")
        if SERVICE.search(t): tags.append("svc")
        if ANGER.search(t): tags.append("anger")
        if m.get("atts"): tags.append("att")
        if tags and tags != ["svc"] or (tags == ["svc"] and len(ms) < 400):
            keep.add(i)
            if i > 0: keep.add(i - 1)
            if i + 1 < len(ms): keep.add(i + 1)
        tagged.append((i, tags))
    # always keep first 12 and last 30 messages for framing
    keep.update(range(0, min(12, len(ms))))
    keep.update(range(max(0, len(ms) - 30), len(ms)))

    slug = re.sub(r"[^A-Za-z0-9]+", "_", entry["chat"])[:40].strip("_") or "chat"
    fname = f"{entry['src']}_{entry['chat_id']}_{slug}.md"
    path = os.path.join(OUT, fname)
    gap_note = ""
    if last_in and last_out:
        gap_note = f"last_client={last_in[:10]} ({days_ago(last_in)}d ago), last_derrek={last_out[:10]} ({days_ago(last_out)}d ago)"
    elif last_in:
        gap_note = f"CLIENT-ONLY, last_client={last_in[:10]} ({days_ago(last_in)}d ago), DEREK NEVER REPLIED"
    elif last_out:
        gap_note = f"DEREK-ONLY, last_derrek={last_out[:10]}"

    lines = []
    lines.append(f"# {entry['chat']}  [{entry['src']} #{entry['chat_id']}{' GROUP' if entry['group'] else ''}]")
    lines.append(f"msgs={len(ms)} (in={in_n} out={out_n}) window={ms[0]['ts'][:10]}..{ms[-1]['ts'][:10]}")
    lines.append(f"{gap_note}")
    lines.append(f"LAST MESSAGE {'FROM CLIENT — UNANSWERED' if unanswered else 'from Derrek'}: {clean(last.get('text'),200)!r}")
    lines.append("")
    prev = -2
    for i in sorted(keep):
        m = ms[i]
        t = m.get("text") or ""
        if REACT_PREFIX.match(t) and not m.get("atts"):
            continue
        if i != prev + 1:
            lines.append("  ...")
        prev = i
        who = "DEREK" if m["from_me"] else (m["sender"] or "?")
        line = f"[{m['ts'][:16]}] {who}: {clean(t)}"
        for a in m.get("atts", []):
            p = a.get("path") or ""
            if p and not p.startswith(("/", "~")):
                p = WA_MEDIA + p
            p = os.path.expanduser(p)
            mime = a.get("mime") or ""
            isimg = p.lower().endswith((".png", ".jpg", ".jpeg", ".heic", ".webp")) or "image" in mime
            line += f"\n      <IMG {'OK' if os.path.exists(p) else 'MISSING'}{'' if isimg else ' non-image'}: {p}>"
        lines.append(line)
    open(path, "w").write("\n".join(lines) + "\n")
    index.append({"brief": f"briefs/{fname}", "chat": entry["chat"], "src": entry["src"], "chat_id": entry["chat_id"],
                  "group": entry["group"], "msgs": len(ms), "kb": round(os.path.getsize(path)/1024),
                  "last_in": last_in, "last_out": last_out, "unanswered": unanswered,
                  "days_since_client": days_ago(last_in) if last_in else None,
                  "days_since_derrek": days_ago(last_out) if last_out else None,
                  "anger": entry["anger"], "money": entry["money"], "score": entry["score"]})

index.sort(key=lambda x: -x["score"])
json.dump(index, open(os.path.join(HERE, "brief_index.json"), "w"), indent=1, ensure_ascii=False)
tot = sum(x["kb"] for x in index)
print(f"{len(index)} briefs, {tot/1024:.1f} MB total (was 14.9 MB)")
for x in index[:12]:
    print(f"  {x['kb']:>4}KB {x['chat'][:38]:<38} unanswered={int(x['unanswered'])} cli_d={x['days_since_client']}")
