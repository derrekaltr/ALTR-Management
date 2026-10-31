"""Scratch: CS-gap metrics for haileigh-cox-x-altr."""
import json
import datetime

PATH = "data/chats/haileigh-cox-x-altr.jsonl"
CLIENT = {"Hailey Client"}
AS_OF = datetime.datetime.fromisoformat("2026-09-25T09:31:50-04:00")

rows = [json.loads(l) for l in open(PATH)]
msgs = [r for r in rows if not r.get("service")]


def dt(r):
    return datetime.datetime.fromisoformat(r["ts"])


team = [r for r in msgs if r["sender"] not in CLIENT]
client = [r for r in msgs if r["sender"] in CLIENT]

gaps = []
for a, b in zip(team, team[1:]):
    gaps.append(((dt(b) - dt(a)).total_seconds() / 86400, a["ts"][:10], b["ts"][:10]))
gaps.sort(reverse=True)
print("TOP TEAM SILENCE GAPS (days, from, to):")
for g in gaps[:12]:
    print(" ", round(g[0], 1), g[1], "->", g[2])
print("gap since last team msg:", round((AS_OF - dt(team[-1])).total_seconds() / 86400, 1), team[-1]["ts"])
print("last client msg:", client[-1]["ts"], "|", (client[-1].get("text") or "")[:60])
print("total msgs:", len(msgs), "client:", len(client), "team:", len(team))

q = [r for r in client if "?" in (r.get("text") or "")]
print("client messages containing '?':", len(q))

un = []
for r in q:
    t = dt(r)
    nxt = [x for x in team if dt(x) > t]
    if not nxt:
        un.append((r["ts"][:16], (r.get("text") or "")[:100], "NEVER"))
        continue
    d = (dt(nxt[0]) - t).total_seconds() / 3600
    if d > 24:
        un.append((r["ts"][:16], (r.get("text") or "")[:100], round(d, 1)))
print("client questions with no team message within 24h:", len(un))
for u in un:
    print("  ", u)

# median / typical first-response latency to client questions
lat = []
for r in q:
    t = dt(r)
    nxt = [x for x in team if dt(x) > t]
    if nxt:
        lat.append((dt(nxt[0]) - t).total_seconds() / 3600)
lat.sort()
if lat:
    print("first-response latency to client questions (h): median",
          round(lat[len(lat) // 2], 2), "p75", round(lat[int(len(lat) * .75)], 2),
          "max", round(lat[-1], 1))

# Stricter: a client question counts as answered only if a team message within 24h
# either replies directly to it, or replies to another client message sent within
# the surrounding 10 minutes (same conversational block).
by_id = {r["id"]: r for r in rows}
client_ids = {r["id"] for r in client}
strict = []
for r in q:
    t = dt(r)
    block = {
        x["id"]
        for x in client
        if abs((dt(x) - t).total_seconds()) <= 600
    }
    hit = None
    for x in team:
        d = (dt(x) - t).total_seconds() / 3600
        if d <= 0 or d > 24:
            continue
        if x.get("reply_to") in block:
            hit = (d, x)
            break
    if not hit:
        strict.append((r["ts"][:16], (r.get("text") or "")[:110]))
print()
print("STRICT: client questions with no direct reply within 24h:", len(strict), "of", len(q))
for s in strict:
    print("  ", s)

# leak-recap cadence (Michelle / Nick DMCA)
print()
recaps = [r for r in team if "leak removal" in (r.get("text") or "").lower()
          or "Takedown Update" in (r.get("text") or "")]
print("leak recaps:", [r["ts"][:10] for r in recaps][-14:])

print()
print("LAST MESSAGE PER SENDER:")
last = {}
for r in msgs:
    last[r["sender"]] = r["ts"][:10]
for k, v in sorted(last.items(), key=lambda x: x[1]):
    print("  ", v, k, round((AS_OF - datetime.datetime.fromisoformat(v + "T00:00:00-04:00")).days), "days")

print()
print("ALL MESSAGES (any sender) since 2026-09-01:")
for r in rows:
    if r["ts"] >= "2026-09-01":
        print("  ", r["ts"][:16], r.get("sender") or "SERVICE:" + str(r.get("event")), "|",
              (r.get("text") or r.get("media") or "")[:70].replace("\n", " "))

print()
print("Mica reel-inspo dates:", [r["ts"][:10] for r in team
                                if "reel" in (r.get("text") or "").lower()
                                and r["sender"] == "Mica Vecco"][-10:])
print("Stephski share of 2026 team msgs:",
      sum(1 for r in team if r["sender"] == "Stephski" and r["ts"] >= "2026-01"),
      "of", sum(1 for r in team if r["ts"] >= "2026-01"))

# monthly outbound-only check: months where team sent nothing unprompted
from collections import Counter
print("client msgs by month:", sorted(Counter(r["ts"][:7] for r in client).items()))
print("team msgs by month:", sorted(Counter(r["ts"][:7] for r in team).items()))
