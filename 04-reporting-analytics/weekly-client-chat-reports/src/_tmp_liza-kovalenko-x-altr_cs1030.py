"""Dump the Liza chat to a readable, credential-masked text file for the 10-30 CS gap pass.

Also prints basic metrics: client questions, unanswered >24h (topic-agnostic, burst-based),
max team silence, and the message list since 2026-10-16.
"""
import json
import re
import sys
from datetime import datetime, timedelta

ROOT = "/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro"
SLUG = "liza-kovalenko-x-altr"
CLIENT = {"Eli"}

rows = [json.loads(l) for l in open(f"{ROOT}/data/chats/{SLUG}.jsonl")]

CRED_WORDS = re.compile(r"(?i)\bpass(word)?\b|\bpw\b|login|2fa|\bcode\b|credential")


def mask(t: str) -> str:
    if not t:
        return t
    # Mask any 6-digit code anywhere (2FA codes) and any password-looking token after 'password'/'pw'/':'
    t = re.sub(r"\b\d{6}\b", "[6DIGIT]", t)
    if CRED_WORDS.search(t):
        # replace tokens that look like passwords (contain digit+letter or symbols, len>=6)
        def repl(m):
            tok = m.group(0)
            if re.search(r"\d", tok) and re.search(r"[A-Za-z]", tok) and len(tok) >= 6:
                return "[PW]"
            if re.search(r"[!@#$%^&*_\-+=]", tok) and len(tok) >= 6 and not tok.startswith("@"):
                return "[PW]"
            return tok
        t = re.sub(r"\S+", repl, t)
    # lines of the form "handle / password" posted by client: mask anything after a known handle
    return t


def parse(ts):
    return datetime.fromisoformat(ts)


out = []
for r in rows:
    t = (r.get("text") or "").replace("\n", " / ")
    t = mask(t)
    extra = ""
    if r.get("media"):
        extra += f" [media:{r['media']}]"
    if r.get("service"):
        extra += f" [service:{r.get('event') or r.get('service')}]"
    if r.get("reply_to"):
        extra += f" (re:{r['reply_to']})"
    out.append(f"{r['id']}|{r['ts'][:16]}|{r.get('sender')}|{t}{extra}")

if len(sys.argv) >= 3 and sys.argv[1] == "dump":
    a, b = int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else len(out)
    print("\n".join(out[a:b]))
    sys.exit(0)
print("dumped", len(out), "lines")

# ---- metrics ----
msgs = [r for r in rows if not r.get("service") and r.get("sender")]
client = [r for r in msgs if r["sender"] in CLIENT]
team = [r for r in msgs if r["sender"] not in CLIENT]

# questions = client msgs with '?'
qs = [r for r in client if "?" in (r.get("text") or "")]
# bursts: group client msgs within 6h
bursts = []
for r in client:
    if bursts and parse(r["ts"]) - parse(bursts[-1][-1]["ts"]) < timedelta(hours=6):
        bursts[-1].append(r)
    else:
        bursts.append([r])
q_bursts = [b for b in bursts if any("?" in (m.get("text") or "") for m in b)]
unans = []
for b in q_bursts:
    last = parse(b[-1]["ts"])
    nxt = [t for t in team if parse(t["ts"]) > last]
    if not nxt or parse(nxt[0]["ts"]) - last > timedelta(hours=24):
        unans.append(b)
print("client msgs", len(client), "team msgs", len(team))
print("client question msgs", len(qs), "question bursts", len(q_bursts), "bursts w/o team reply <24h", len(unans))
for b in unans:
    lag = None
    last = parse(b[-1]["ts"])
    nxt = [t for t in team if parse(t["ts"]) > last]
    if nxt:
        lag = (parse(nxt[0]["ts"]) - last).total_seconds() / 86400
    q = [mask((m.get("text") or "").replace("\n", " / "))[:90] for m in b if "?" in (m.get("text") or "")]
    print(f"  {b[-1]['ts'][:10]} lag={None if lag is None else round(lag,1)}d :: {q[0]}")

# max team silence
gaps = []
for a, b in zip(team, team[1:]):
    gaps.append(((parse(b["ts"]) - parse(a["ts"])).total_seconds() / 86400, a["ts"][:10], b["ts"][:10]))
gaps.sort(reverse=True)
print("top team gaps", [(round(g, 1), s, e) for g, s, e in gaps[:5]])
tail = (parse(rows[-1]["ts"]) - parse(team[-1]["ts"])).total_seconds() / 86400
print("last team msg", team[-1]["ts"], "last client msg", client[-1]["ts"])

# window since 10-16
print("\n---- since 2026-10-16 ----")
for line in out:
    if line.split("|")[1] >= "2026-10-16":
        print(line)
