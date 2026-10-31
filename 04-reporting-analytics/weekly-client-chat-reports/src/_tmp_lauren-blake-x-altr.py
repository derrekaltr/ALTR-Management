"""Dump Lauren Blake chat messages since a cutoff, with secret masking, plus gap metrics."""
import json
import re
import sys
from datetime import datetime

SLUG = "lauren-blake-x-altr"
CUTOFF = sys.argv[1] if len(sys.argv) > 1 else "2026-09-25"
CLIENT = {"Lauren Blake"}

msgs = [json.loads(l) for l in open(f"data/chats/{SLUG}.jsonl")]
msgs.sort(key=lambda m: m["ts"])


def mask(t):
    t = re.sub(r"\b\d{6,8}\b", "[CODE]", t or "")
    t = re.sub(r"(?i)(pass(word)?|pw)\s*[:=]?\s*\S+", r"\1 [REDACTED]", t)
    return t


if CUTOFF == "validate":
    for p in [f"data/analysis/cs-gaps-2026-10-09/{SLUG}.json", f"data/analysis/cs-gaps-2026-09-25/{SLUG}.json"]:
        raw = open(p).read()
        d = json.loads(raw)
        print(p, "valid", len(d["dimensions"]), "dims; secret hits:", raw.count("ALTRmgmt"), raw.lower().count("lboultier"))
    sys.exit()

if CUTOFF == "prior":
    d = json.load(open(f"data/analysis/cs-gaps-2026-09-25/{SLUG}.json"))
    for k, v in d["dimensions"].items():
        print("##", k, v["severity"])
        for e in v["evidence"]:
            print("  ", e["date"], e["who"], "|", e["quote"][:220])
    print(json.dumps(d["what_client_wanted"], indent=1)[:3000])
    print(json.dumps(d["what_worked"], indent=1)[:3000])
    sys.exit()

if CUTOFF == "vendor":
    for other in ["liza-kovalenko-x-altr", "haileigh-cox-x-altr", SLUG]:
        print("==", other)
        for l in open(f"data/chats/{other}.jsonl"):
            m = json.loads(l)
            if m.get("sender") in ("Stardust Nexus", "Theta SDX"):
                print(m["ts"][:16], m["sender"], re.sub(r"\b\d{4,8}\b", "[CODE]", m.get("text") or "")[:200])
    sys.exit()

if CUTOFF != "metrics":
    for m in msgs:
        if m["ts"][:10] < CUTOFF:
            continue
        txt = mask(m.get("text") or "")
        extra = ""
        if m.get("media"):
            extra += f" <media:{m['media']}>"
        if m.get("service") or m.get("event"):
            extra += f" <svc:{m.get('event') or m.get('service')}>"
        if m.get("reply_to"):
            extra += f" (re {m['reply_to']})"
        print(f"{m['id']} {m['ts'][:16]} {m.get('sender')}: {txt[:500]}{extra}")
else:
    def ts(m):
        return datetime.fromisoformat(m["ts"])
    team = [m for m in msgs if m.get("sender") and m["sender"] not in CLIENT and not (m.get("service") or m.get("event"))]
    client = [m for m in msgs if m.get("sender") in CLIENT]
    gaps = []
    for a, b in zip(team, team[1:]):
        gaps.append(((ts(b) - ts(a)).total_seconds() / 86400, a["ts"], b["ts"], b["sender"]))
    gaps.sort(reverse=True)
    print("top team gaps", gaps[:3])
    print("last client", client[-1]["ts"], "last team", team[-1]["ts"], team[-1]["sender"])
    print("total client", len(client), "team", len(team), "all", len(msgs))
    from collections import Counter
    print(Counter(m["sender"] for m in team if m["ts"][:10] >= "2026-09-25"))
