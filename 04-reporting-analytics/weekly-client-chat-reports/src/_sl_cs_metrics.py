"""Scratch: CS-gap metrics for sarah-lloyd-x-altr (2026-09-18 run)."""
import json
import re
import statistics
from datetime import datetime

PATH = "data/chats/sarah-lloyd-x-altr.jsonl"
CLIENT = "Sarah Lloyd"
TEMPLATED = {"Michelle Queue", "Mica Vecco", "Stephski"}

rows = [json.loads(line) for line in open(PATH)]
msgs = [r for r in rows if not r.get("service")]
svc = [r for r in rows if r.get("service")]


def dt(s):
    return datetime.fromisoformat(s)


ours = [m for m in msgs if m["sender"] != CLIENT]
cli = [m for m in msgs if m["sender"] == CLIENT]
print("messages", len(msgs), "client", len(cli), "ours", len(ours), "service", len(svc))
print("first", msgs[0]["ts"], "last", msgs[-1]["ts"])
print("last client msg", cli[-1]["ts"])

ASK = re.compile(
    r"\?|\bpls\b|\bplease\b|\bcan (we|you|i)\b|\bcould\b|\bwould\b|"
    r"make sure|following up|bumping|\blmk\b|let me know",
    re.I,
)
asks = [m for m in cli if m.get("text") and ASK.search(m["text"])]
print("client asks", len(asks))

unanswered = []
lags = []
for m in asks:
    t = dt(m["ts"])
    later = [dt(o["ts"]) for o in ours if dt(o["ts"]) > t]
    if not later or (min(later) - t).total_seconds() > 86400:
        unanswered.append((m["ts"][:16], (m.get("text") or "")[:80]))
    if later:
        lags.append((min(later) - t).total_seconds() / 60)
print("unanswered_over_24h", len(unanswered))
for u in unanswered:
    print("   ", u)
print("median_first_reply_min", round(statistics.median(lags), 1))
print("asks_slower_than_12h", sum(1 for x in lags if x > 720))

NUDGE = re.compile(r"bump|following up|just checking|any confirmation|still the same|again|\^", re.I)
nudges = [m for m in cli if m.get("text") and NUDGE.search(m["text"])]
print("client_repeat_nudge_messages", len(nudges))

relay = [m for m in ours if m.get("text") and re.search(r"@natehei|@roflo1424|\^\^", m["text"] or "")
         and m["sender"] in {"Mayson Chat", "Noah Chat", "Derrek"}]
print("internal_relay_pings", len(relay))


def gaps(seq):
    out = []
    for a, b in zip(seq, seq[1:]):
        out.append(((b - a).total_seconds() / 86400, a.isoformat()[:16], b.isoformat()[:16]))
    return sorted(out, reverse=True)


allts = [dt(o["ts"]) for o in ours]
print("top team silence:", [(round(g[0], 1), g[1], g[2]) for g in gaps(allts)[:6]])
nt = [dt(o["ts"]) for o in ours if o["sender"] not in TEMPLATED]
print("top non-templated silence:", [(round(g[0], 1), g[1], g[2]) for g in gaps(nt)[:5]])

VENDOR = {"Masa", "Vladan | Chat Manager", "Day | Account Executive", "Alex Chatting Team",
          "Maciej | Supervisor", "Emmanuel | General Manager", "George"}
CHATSIDE = VENDOR | {"Noah Chat", "Nate (Noah)", "Ronnie Chat"}
cs = [dt(o["ts"]) for o in ours if o["sender"] in CHATSIDE]
print("chat-side last msg", cs[-1].isoformat()[:16])
print("top chat-side silence:", [(round(g[0], 1), g[1], g[2]) for g in gaps(cs)[:4]])
vt = [dt(o["ts"]) for o in ours if o["sender"] in VENDOR]
print("vendor last msg", vt[-1].isoformat()[:16])

from collections import Counter
print(Counter(m["sender"] for m in ours).most_common())

# monthly client message volume
print(Counter(m["ts"][:7] for m in cli))
print("service events:", [(s["ts"][:16], s.get("event")) for s in svc])
