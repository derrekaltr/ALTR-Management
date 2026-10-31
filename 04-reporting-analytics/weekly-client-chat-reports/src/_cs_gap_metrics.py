"""Ad-hoc metrics helper for the CS gap analysis (Amber Haze)."""
import json
import datetime
import statistics
import sys

SLUG = sys.argv[1] if len(sys.argv) > 1 else "amber-haze-x-altr"
CLIENT = sys.argv[2] if len(sys.argv) > 2 else "Kirsten (amber Haze)"
PATH = f"data/chats/{SLUG}.jsonl"

msgs = []
for line in open(PATH):
    d = json.loads(line)
    if d.get("service") or not d.get("sender"):
        continue
    msgs.append(d)


def T(d):
    return datetime.datetime.fromisoformat(d["ts"])


team = [m for m in msgs if m["sender"] != CLIENT]
cli = [m for m in msgs if m["sender"] == CLIENT]
print("total", len(msgs), "client", len(cli), "team", len(team))

gaps = sorted(((T(b) - T(a)).total_seconds() / 86400, a["ts"][:10], b["ts"][:10])
              for a, b in zip(team, team[1:]))
print("MAX TEAM SILENCE %.1f days" % gaps[-1][0])
for g in gaps[-10:]:
    print("  gap %.1f  %s -> %s" % g)

q = [m for m in cli if "?" in (m.get("text") or "")]
print("client msgs containing '?':", len(q))

un = []
lags = []
for m in q:
    t = T(m)
    nxt = [x for x in team if T(x) > t]
    if not nxt:
        un.append((m["ts"][:16], "NEVER", (m.get("text") or "")[:100]))
        continue
    lag = (T(nxt[0]) - t).total_seconds() / 3600
    lags.append(lag)
    if lag > 24:
        un.append((m["ts"][:16], "%.0fh" % lag, (m.get("text") or "")[:100]))

print("unanswered >24h (no team message at all within 24h):", len(un))
for u in un:
    print("   ", u)
print("lag median %.2fh mean %.2fh p75 %.2fh max %.1fh"
      % (statistics.median(lags), statistics.mean(lags),
         statistics.quantiles(lags, n=4)[2], max(lags)))

# nudge escalations
nudges = [m for m in cli if (m.get("text") or "").strip() in
          ("?", "??", "???") or "anyone going to reply" in (m.get("text") or "").lower()
          or (m.get("text") or "").strip().lower().startswith("update")
          or "any update" in (m.get("text") or "").lower()]
print("client nudges:", len(nudges))
for m in nudges:
    print("   ", m["ts"][:16], repr((m.get("text") or "")[:70]))
