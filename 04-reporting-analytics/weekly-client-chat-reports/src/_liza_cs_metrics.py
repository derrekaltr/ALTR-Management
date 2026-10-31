import json, datetime, bisect, sys

PATH = "/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro/data/chats/liza-kovalenko-x-altr.jsonl"
CLIENT = {"Eli"}
rows = [json.loads(l) for l in open(PATH)]
msgs = [r for r in rows if not r.get("service")]


def dt(r):
    return datetime.datetime.fromisoformat(r["ts"])


NOW = datetime.datetime.fromisoformat("2026-09-25T09:00:00-04:00")

team = [r for r in msgs if r["sender"] not in CLIENT]
client = [r for r in msgs if r["sender"] in CLIENT]

print("total", len(msgs), "client", len(client), "team", len(team))
print("first", msgs[0]["ts"], "last", msgs[-1]["ts"])

gaps = []
for a, b in zip(team, team[1:]):
    g = (dt(b) - dt(a)).total_seconds() / 86400
    if g >= 6:
        gaps.append((round(g, 1), a["ts"][:10], b["ts"][:10], a["sender"], b["sender"]))
gaps.sort(reverse=True)
print("\nTOP TEAM SILENCE GAPS (days)")
for x in gaps[:15]:
    print(x)
print("trailing team silence to 2026-09-25:", round((NOW - dt(team[-1])).total_seconds() / 86400, 1), team[-1]["ts"], team[-1]["sender"])

qs = [r for r in client if "?" in r.get("text", "")]
print("\nclient question-messages:", len(qs))
teamts = [dt(r) for r in team]
un = []
for q in qs:
    t = dt(q)
    i = bisect.bisect_right(teamts, t)
    lag = None if i >= len(teamts) else (teamts[i] - t).total_seconds() / 3600
    if lag is None or lag > 24:
        un.append((q["ts"][:16], "never" if lag is None else round(lag, 1), q.get("text", "")[:120]))
print("questions with no team message within 24h:", len(un))
for x in un:
    print(x)

# median lag for all client messages
lags = []
for c in client:
    t = dt(c)
    i = bisect.bisect_right(teamts, t)
    if i < len(teamts):
        lags.append((teamts[i] - t).total_seconds() / 3600)
lags.sort()
print("\nclient-msg -> next team msg lag hours: median", round(lags[len(lags) // 2], 2), "p75", round(lags[int(len(lags) * .75)], 2), "p90", round(lags[int(len(lags) * .9)], 2))

print("\nSENDER FIRST/LAST")
seen = {}
for r in msgs:
    seen.setdefault(r["sender"], [r["ts"], r["ts"], 0])
    seen[r["sender"]][1] = r["ts"]
    seen[r["sender"]][2] += 1
for k, v in sorted(seen.items(), key=lambda kv: kv[1][1]):
    print(k, "n=", v[2], "first", v[0][:10], "last", v[1][:10], "silent_days", round((NOW - datetime.datetime.fromisoformat(v[1])).total_seconds() / 86400, 1))

print("\nSERVICE EVENTS")
for r in rows:
    if r.get("service"):
        print(r["ts"][:16], r.get("event"))
