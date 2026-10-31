"""CS gap metrics for lauryn-x-altr over full history (2026-10-30 run) + delta dump since 10-14."""
import json
import sys
from datetime import datetime
from statistics import median

CLIENT = {"LA Client"}
BROADCAST = ("leak", "Leak", "DMCA", "removal")
END = datetime.fromisoformat("2026-10-30T09:05:30-04:00")

msgs = []
for line in open("data/chats/lauryn-x-altr.jsonl"):
    m = json.loads(line)
    if m.get("service") or not m.get("sender"):
        continue
    m["dt"] = datetime.fromisoformat(m["ts"])
    msgs.append(m)
msgs.sort(key=lambda m: m["dt"])

mode = sys.argv[1] if len(sys.argv) > 1 else "metrics"

if mode == "dump":
    since = sys.argv[2] if len(sys.argv) > 2 else "2026-10-14"
    until = sys.argv[3] if len(sys.argv) > 3 else "9999"
    for m in msgs:
        if since <= m["ts"][:10] <= until:
            t = (m.get("text") or "").replace("\n", " / ")
            med = " [media:%s]" % m["media"] if m.get("media") else ""
            rp = " (re:%s)" % m["reply_to"] if m.get("reply_to") else ""
            print(m["id"], m["ts"][:16], m["sender"] + ":", t + med + rp)
    sys.exit()

if mode == "grep":
    pat = sys.argv[2].lower()
    for m in msgs:
        t = (m.get("text") or "")
        if pat in t.lower():
            print(m["id"], m["ts"][:16], m["sender"] + ":", t.replace("\n", " / ")[:220])
    sys.exit()

if mode == "verify":
    # Each evidence quote (text before any trailing " (" annotation, split on " / ") must
    # appear verbatim in a message from that sender on that date.
    f = json.load(open("data/analysis/cs-gaps-2026-10-30/lauryn-x-altr.json"))
    bad = 0
    for dim, d in f["dimensions"].items():
        for ev in d["evidence"]:
            q = ev["quote"]
            if "redacted]" in q:
                continue
            core = q.split(" (")[0]
            for part in core.split(" / "):
                hit = [m for m in msgs if part in (m.get("text") or "") and m["sender"] == ev["who"]
                       and m["ts"].startswith(ev["date"])]
                if not hit:
                    bad += 1
                    print("MISS", dim, ev["date"], ev["who"], repr(part))
    print("misses:", bad, "| dims:", len(f["dimensions"]), "| keys:", sorted(f.keys()))
    sys.exit()

if mode == "ids":
    want = {int(x) for x in sys.argv[2].split(",")}
    for m in msgs:
        if m["id"] in want:
            print(m["id"], m["ts"][:16], m["sender"] + ":", (m.get("text") or "").replace("\n", " / "))
    sys.exit()

client = [m for m in msgs if m["sender"] in CLIENT]
ours = [m for m in msgs if m["sender"] not in CLIENT]
print("total", len(msgs), "client", len(client), "ours", len(ours))
print("first", msgs[0]["ts"], "last", msgs[-1]["ts"], "last client", client[-1]["ts"])

qs = [m for m in client if "?" in (m.get("text") or "")]
lags, over24 = [], []
for q in qs:
    nxt = next((o for o in ours if o["dt"] > q["dt"]), None)
    if nxt is None:
        over24.append((q["ts"], q["text"], "no reply yet"))
        continue
    h = (nxt["dt"] - q["dt"]).total_seconds() / 3600
    lags.append(h)
    if h > 24:
        over24.append((q["ts"], q["text"][:80], round(h, 1)))
lags.sort()
print("questions", len(qs), "median lag min", round(median(lags) * 60, 1),
      "p90 h", round(lags[int(len(lags) * 0.9)], 2))
print("over24", over24)


def max_gap(seq):
    best = (0, None, None)
    for a, b in zip(seq, seq[1:]):
        d = (b["dt"] - a["dt"]).total_seconds() / 86400
        if d > best[0]:
            best = (round(d, 1), a["ts"][:10], b["ts"][:10])
    return best


nb = [o for o in ours if not any(s in (o.get("text") or "") for s in BROADCAST)]
print("max silence all outbound", max_gap(ours))
print("max silence excl broadcasts", max_gap(nb))
print("trailing silence days (ours)", round((END - ours[-1]["dt"]).total_seconds() / 86400, 1))
print("trailing silence days (client)", round((END - client[-1]["dt"]).total_seconds() / 86400, 1))
since = [m for m in msgs if m["ts"] > "2026-10-16T09:06:40-04:00"]
print("since 10-16 export:", len(since), "client", sum(m["sender"] in CLIENT for m in since))
from collections import Counter
print("senders since:", Counter(m["sender"] for m in since))
print("senders all-time:", Counter(m["sender"] for m in msgs).most_common())
# per-sender last message
last = {}
for m in msgs:
    last[m["sender"]] = m["ts"][:10]
print("last per sender:", sorted(last.items(), key=lambda x: x[1]))
