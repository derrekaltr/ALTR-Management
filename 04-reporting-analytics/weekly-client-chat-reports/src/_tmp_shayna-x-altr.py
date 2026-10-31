import json, sys, re
from datetime import datetime
from collections import Counter

P = "data/chats/shayna-x-altr.jsonl"
CLIENT = {"Shayna Holt"}
msgs = [json.loads(l) for l in open(P)]
mode = sys.argv[1] if len(sys.argv) > 1 else "dump"

def dt(m):
    return datetime.fromisoformat(m["ts"].replace("Z", ""))

real = [m for m in msgs if not m.get("service") and m.get("sender")]

if mode == "dump":
    since = sys.argv[2]
    for m in msgs:
        if m["ts"] >= since:
            t = (m.get("text") or "").replace("\n", " / ")
            extra = f" [media:{m['media']}]" if m.get("media") else ""
            ev = f" [svc:{m.get('event')}]" if m.get("service") else ""
            print(f"{m['id']} {m['ts'][:16]} {m.get('sender')}: {t[:400]}{extra}{ev}")
elif mode == "verify":
    needles = ["left on seen", "plenty of updates starting next week", "internal notes with the team",
               "No more for sure", "I really wanna make sure the things", "strategy is for this",
               "Meta Support Rep", "wanna make sure you guys are receiving", "everything is sent",
               "Can't", "has a custom waiting", "Thank you for being so on top", "those weren",
               "spent a total of $60", "charged him 800", "Just keep coming up with excuses",
               "can we get this handled asap", "my apologies on the late responses"]
    for n in needles:
        hits = [(m["ts"][:10], m["sender"]) for m in real if n.lower() in (m.get("text") or "").lower()]
        print(n, "->", hits[:3])
elif mode == "stats":
    c = Counter(m["sender"] for m in real)
    print(c)
    print("first", real[0]["ts"], "last", real[-1]["ts"])
    lastc = [m for m in real if m["sender"] in CLIENT][-1]
    print("last client", lastc["ts"], lastc.get("text"))
    team = [m for m in real if m["sender"] not in CLIENT]
    gaps = sorted(((dt(b) - dt(a)).total_seconds() / 86400, a["ts"], b["ts"]) for a, b in zip(team, team[1:]))[-5:]
    print("team gaps", gaps)
    print("since last team msg", team[-1]["ts"])
    # client ? msgs and first team reply lag
    q = [m for m in real if m["sender"] in CLIENT and "?" in (m.get("text") or "")]
    print("client ? msgs", len(q))
    over = 0
    for m in q:
        nxt = next((x for x in real if x["ts"] > m["ts"] and x["sender"] not in CLIENT), None)
        lag = (dt(nxt) - dt(m)).total_seconds() / 3600 if nxt else None
        if lag is None or lag > 24:
            over += 1
            if m["ts"] >= "2026-09-20":
                print("  >24h:", m["ts"][:16], (m.get("text") or "")[:120], lag)
    print("over24 naive", over)
