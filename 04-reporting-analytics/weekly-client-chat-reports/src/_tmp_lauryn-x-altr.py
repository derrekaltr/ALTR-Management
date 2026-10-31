"""Best-effort CS metrics for lauryn-x-altr over full history."""
import json
from datetime import datetime
from statistics import median

CLIENT = {"LA Client"}
BROADCAST = ("leak", "Leak", "DMCA", "removal")
msgs = []
for line in open("data/chats/lauryn-x-altr.jsonl"):
    m = json.loads(line)
    if m.get("service") or not m.get("sender"):
        continue
    m["dt"] = datetime.fromisoformat(m["ts"])
    msgs.append(m)
msgs.sort(key=lambda m: m["dt"])

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
end = datetime.fromisoformat("2026-10-16T09:06:40-04:00")
print("trailing silence days", round((end - ours[-1]["dt"]).total_seconds() / 86400, 1))
since = [m for m in msgs if m["ts"] >= "2026-10-09"]
print("since 10-09:", len(since), "client", sum(m["sender"] in CLIENT for m in since))
lastq = qs[-1]
print("last q open hours", round((end - lastq["dt"]).total_seconds() / 3600, 1), lastq["ts"])
