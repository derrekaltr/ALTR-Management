import json, datetime, bisect

PATH = "/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro/data/chats/liza-kovalenko-x-altr.jsonl"
CLIENT = {"Eli"}
rows = [json.loads(l) for l in open(PATH)]
msgs = [r for r in rows if not r.get("service")]
NOW = datetime.datetime.fromisoformat("2026-09-25T09:00:00-04:00")
TOPICS = {2, 3, 4, 5, 100}


def dt(r):
    return datetime.datetime.fromisoformat(r["ts"])


byid = {r["id"]: r for r in msgs}


def topic(r):
    """resolve to a forum topic id by walking reply chain"""
    seen = 0
    cur = r
    while seen < 20:
        rt = cur.get("reply_to")
        if rt is None:
            return "root"
        if rt in TOPICS:
            return rt
        cur = byid.get(rt)
        if cur is None:
            return "root"
        seen += 1
    return "root"


bursts = []
cur = None
for r in msgs:
    if r["sender"] in CLIENT:
        if cur and (dt(r) - dt(cur[-1])).total_seconds() < 6 * 3600 and topic(r) == topic(cur[-1]):
            cur.append(r)
        else:
            if cur:
                bursts.append(cur)
            cur = [r]
    else:
        if cur:
            bursts.append(cur)
            cur = None
if cur:
    bursts.append(cur)

team = [r for r in msgs if r["sender"] not in CLIENT]
teamts = [dt(r) for r in team]

qbursts = [b for b in bursts if any("?" in (m.get("text") or "") for m in b)]
print("client bursts:", len(bursts), "| question bursts:", len(qbursts))

over24, never = [], []
for b in qbursts:
    last = dt(b[-1])
    ids = {m["id"] for m in b}
    tp = topic(b[-1])
    i = bisect.bisect_right(teamts, last)
    lag = None
    for j in range(i, len(team)):
        if topic(team[j]) == tp or team[j].get("reply_to") in ids:
            lag = (teamts[j] - last).total_seconds() / 3600
            break
    if lag is None:
        never.append(b)
    elif lag > 24:
        over24.append((round(lag, 1), b))

print("question bursts unanswered in-thread >24h:", len(over24) + len(never), "(never:", len(never), ")")
for lag, b in sorted(over24, reverse=True):
    print(f"  {b[0]['ts'][:10]} lag={lag}h :: " + " | ".join((m.get('text') or '')[:55] for m in b[:3]))
for b in never:
    print(f"  {b[0]['ts'][:10]} NEVER :: " + " | ".join((m.get('text') or '')[:55] for m in b[:4]))

# all client bursts: lag to any in-thread team reply
lags = []
for b in bursts:
    last = dt(b[-1])
    ids = {m["id"] for m in b}
    tp = topic(b[-1])
    i = bisect.bisect_right(teamts, last)
    for j in range(i, len(team)):
        if topic(team[j]) == tp or team[j].get("reply_to") in ids:
            lags.append((teamts[j] - last).total_seconds() / 3600)
            break
lags.sort()
print("in-thread reply lag (h): median", round(lags[len(lags)//2], 2), "p75", round(lags[int(len(lags)*.75)], 2), "p90", round(lags[int(len(lags)*.9)], 2), "n", len(lags))
