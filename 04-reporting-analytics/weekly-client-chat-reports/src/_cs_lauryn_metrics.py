"""Ad-hoc metrics for the Lauryn CS gap analysis (2026-09-11 run)."""
import bisect
import datetime
import json

PATH = "data/chats/lauryn-x-altr.jsonl"
CLIENT = {"LA Client"}

msgs = []
with open(PATH) as fh:
    for line in fh:
        d = json.loads(line)
        if d.get("sender"):
            msgs.append(d)


def P(t):
    return datetime.datetime.fromisoformat(t)


client = [m for m in msgs if m["sender"] in CLIENT]
ours = [m for m in msgs if m["sender"] not in CLIENT]
print("non-service total", len(msgs), "client", len(client), "ours", len(ours))

qs = [m for m in client if "?" in (m.get("text") or "")]
print("client questions containing '?':", len(qs))

ots = [P(m["ts"]) for m in ours]
lags = []
breaches = []
for m in qs:
    t = P(m["ts"])
    i = bisect.bisect_right(ots, t)
    if i < len(ots):
        lag = (ots[i] - t).total_seconds() / 3600.0
        lags.append(lag)
        if lag > 24:
            breaches.append((m["ts"][:16], (m.get("text") or "")[:70], round(lag, 1)))
    else:
        breaches.append((m["ts"][:16], (m.get("text") or "")[:70], "NEVER"))
lags.sort()
print(
    "first-reply-by-anyone lag h: median",
    round(lags[len(lags) // 2], 3),
    "mean",
    round(sum(lags) / len(lags), 2),
    "p90",
    round(lags[int(len(lags) * 0.9)], 2),
)
print("strict >24h breaches:", len(breaches))
for b in breaches:
    print("   ", b)

# ---- team silence: consecutive days with zero outbound from our side ----
AUTOMATED = {"Nick | DMCA", "Michelle Queue"}
for label, senders in (("all outbound", None), ("excluding DMCA/leak broadcasts", AUTOMATED)):
    ts = [P(m["ts"]) for m in ours if not senders or m["sender"] not in senders]
    ts.sort()
    gap = max((b - a, a, b) for a, b in zip(ts, ts[1:]))
    print(
        label,
        "-> longest outbound gap %.1f days" % (gap[0].total_seconds() / 86400.0),
        gap[1].isoformat()[:16],
        "->",
        gap[2].isoformat()[:16],
    )

# trailing silence to window close
end = P("2026-09-11T09:03:48-04:00")
for label, senders in (("all outbound", None), ("excluding DMCA/leak broadcasts", AUTOMATED)):
    ts = [P(m["ts"]) for m in ours if not senders or m["sender"] not in senders]
    print(label, "-> last outbound", max(ts).isoformat()[:16],
          "(%.1f days before window close)" % ((end - max(ts)).total_seconds() / 86400.0))

print("last client message:", max(P(m["ts"]) for m in client).isoformat()[:16])
