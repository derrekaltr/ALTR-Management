"""Metrics for the Lauryn CS gap analysis, 2026-09-25 run."""
import bisect
import datetime
import json
import re

PATH = "data/chats/lauryn-x-altr.jsonl"
CLIENT = {"LA Client"}
END = datetime.datetime.fromisoformat("2026-09-25T09:30:00-04:00")

msgs = [json.loads(l) for l in open(PATH)]
msgs = [m for m in msgs if m.get("sender")]


def P(t):
    return datetime.datetime.fromisoformat(t)


client = [m for m in msgs if m["sender"] in CLIENT]
ours = [m for m in msgs if m["sender"] not in CLIENT]
print("non-service", len(msgs), "client", len(client), "ours", len(ours))
print("first", msgs[0]["ts"][:10], "last", msgs[-1]["ts"][:10])
print("last client msg", max(m["ts"] for m in client)[:16])
print("last our msg", max(m["ts"] for m in ours)[:16])

# last message per sender
last = {}
first = {}
for m in msgs:
    last[m["sender"]] = max(last.get(m["sender"], ""), m["ts"])
    first[m["sender"]] = min(first.get(m["sender"], "9"), m["ts"])
print("\n-- sender first/last --")
for s in sorted(last, key=lambda s: last[s]):
    print("   %-32s %s -> %s" % (s, first[s][:10], last[s][:10]))

qs = [m for m in client if "?" in (m.get("text") or "")]
print("\nclient msgs containing '?':", len(qs))

ots = [P(m["ts"]) for m in ours]
lags, breaches = [], []
for m in qs:
    t = P(m["ts"])
    i = bisect.bisect_right(ots, t)
    if i < len(ots):
        lag = (ots[i] - t).total_seconds() / 3600.0
        lags.append(lag)
        if lag > 24:
            breaches.append((m["ts"][:16], (m.get("text") or "")[:80], round(lag, 1)))
    else:
        breaches.append((m["ts"][:16], (m.get("text") or "")[:80], "NEVER"))
lags.sort()
print("first-reply lag h: median %.3f mean %.2f p90 %.2f" % (
    lags[len(lags) // 2], sum(lags) / len(lags), lags[int(len(lags) * 0.9)]))
print("strict >24h breaches:", len(breaches))
for b in breaches:
    print("   ", b)

# --- question "threads": collapse client question bursts within 30 min ---
bursts = []
for m in qs:
    t = P(m["ts"])
    if bursts and (t - bursts[-1][-1]) < datetime.timedelta(minutes=30):
        bursts[-1].append(t)
    else:
        bursts.append([t])
print("\nclient question bursts (30-min grouping):", len(bursts))
bb = 0
for b in bursts:
    t = b[-1]
    i = bisect.bisect_right(ots, t)
    if i >= len(ots) or (ots[i] - t).total_seconds() / 3600.0 > 24:
        bb += 1
print("bursts with no our-side reply within 24h:", bb)

AUTOMATED = {"Nick | DMCA", "Michelle Queue"}
for label, excl in (("all outbound", set()), ("excl DMCA/leak broadcasts", AUTOMATED)):
    ts = sorted(P(m["ts"]) for m in ours if m["sender"] not in excl)
    gaps = sorted(((b - a, a, b) for a, b in zip(ts, ts[1:])), reverse=True)
    print("\n%s: top 5 outbound gaps" % label)
    for g, a, b in gaps[:5]:
        print("   %.1f d  %s -> %s" % (g.total_seconds() / 86400, a.isoformat()[:16], b.isoformat()[:16]))
    print("   trailing to %s: %.1f d (last %s)" % (
        END.isoformat()[:10], (END - ts[-1]).total_seconds() / 86400, ts[-1].isoformat()[:16]))

# client silence gaps
cts = sorted(P(m["ts"]) for m in client)
cg = sorted(((b - a, a, b) for a, b in zip(cts, cts[1:])), reverse=True)
print("\ntop 5 CLIENT silence gaps")
for g, a, b in cg[:5]:
    print("   %.1f d  %s -> %s" % (g.total_seconds() / 86400, a.isoformat()[:16], b.isoformat()[:16]))
print("   trailing client silence: %.1f d" % ((END - cts[-1]).total_seconds() / 86400))

# keyword scans
def scan(label, pat, senders=None):
    rx = re.compile(pat, re.I)
    hits = [m for m in msgs if rx.search(m.get("text") or "")
            and (senders is None or m["sender"] in senders)]
    print("\n== %s == %d hits" % (label, len(hits)))
    for m in hits[:40]:
        print("   %s | %s | %s" % (m["ts"][:10], m["sender"], (m.get("text") or "")[:120].replace("\n", " ")))


scan("REPORT/GAME PLAN", r"\b(report|game ?plan|recap|monthly review|stats? for|breakdown of your)\b", None)
scan("REVENUE NUMBERS ($/earnings) from our side", r"(\$[0-9][0-9,]{2,}|revenue|earnings|gross|net rev|top ?\d+%)",
     set(m["sender"] for m in ours))
scan("PASSWORDS/LOGINS in chat", r"(password|pw:|login|log in details|passcode|2fa|code)")
