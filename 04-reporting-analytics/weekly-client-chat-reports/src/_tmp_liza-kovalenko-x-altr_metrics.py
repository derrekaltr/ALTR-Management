import json
from datetime import datetime, timedelta

PATH = "data/chats/liza-kovalenko-x-altr.jsonl"
CLIENT = {"Eli"}
msgs = [json.loads(l) for l in open(PATH)]
byid = {m["id"]: m for m in msgs}
for m in msgs:
    m["dt"] = datetime.fromisoformat(m["ts"])


def topic(m, depth=0):
    rt = m.get("reply_to")
    if not rt or rt not in byid or depth > 50:
        return "general"
    r = byid[rt]
    if r.get("service") and "TopicCreate" in (r.get("event") or ""):
        return rt
    return topic(r, depth + 1)


real = [m for m in msgs if not m.get("service")]
for m in real:
    m["topic"] = topic(m)
client = [m for m in real if m.get("sender") in CLIENT]
ours = [m for m in real if m.get("sender") not in CLIENT]
print("total", len(real), "client", len(client), "ours", len(ours), "first", real[0]["ts"][:10], "last", real[-1]["ts"][:10])

# bursts: same topic, gaps < 6h
bursts = []
for m in client:
    b = next((b for b in reversed(bursts) if b["topic"] == m["topic"]), None)
    if b and (m["dt"] - b["end"]) < timedelta(hours=6) and not any(
        o["topic"] == m["topic"] and b["end"] < o["dt"] < m["dt"] for o in ours
    ):
        b["end"] = m["dt"]
        b["msgs"].append(m)
    else:
        bursts.append({"topic": m["topic"], "start": m["dt"], "end": m["dt"], "msgs": [m]})
qb = [b for b in bursts if any("?" in (x.get("text") or "") for x in b["msgs"])]
lags = []
over = []
never = []
for b in qb:
    rep = next((o for o in ours if o["topic"] == b["topic"] and o["dt"] > b["end"]), None)
    if rep is None:
        never.append(b)
        over.append(b)
        continue
    lag = (rep["dt"] - b["end"]).total_seconds() / 3600
    lags.append(lag)
    if lag > 24:
        over.append(b)
lags.sort()
pct = lambda p: lags[int(p * (len(lags) - 1))]
print("bursts", len(bursts), "question bursts", len(qb), "over24", len(over), "never", len(never))
print("median %.1f p75 %.1f p90 %.1f" % (pct(.5), pct(.75), pct(.9)))
for b in never:
    print(" NEVER", b["start"].date(), b["topic"], [x.get("text") for x in b["msgs"] if "?" in (x.get("text") or "")])
for b in over:
    if b["start"].date().isoformat() >= "2026-09-01":
        print(" OVER", b["start"].date(), b["topic"], [x.get("text") for x in b["msgs"] if "?" in (x.get("text") or "")])

# team silence
gaps = []
for a, b in zip(ours, ours[1:]):
    gaps.append(((b["dt"] - a["dt"]).total_seconds() / 86400, a["ts"][:10], b["ts"][:10]))
gaps.sort(reverse=True)
print("top gaps", [("%.1f" % g, s, e) for g, s, e in gaps[:5]])
now = datetime.fromisoformat("2026-10-09T09:00:00-04:00")
print("since last ours %.1f days" % ((now - ours[-1]["dt"]).total_seconds() / 86400))
# senders since 09-25
from collections import Counter
print(Counter(m["sender"] for m in real if m["ts"][:10] >= "2026-09-25"))
