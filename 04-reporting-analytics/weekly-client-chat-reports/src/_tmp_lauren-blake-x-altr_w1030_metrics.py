"""Metrics for Lauren Blake CS gap analysis 10/30: team silence gaps, counts, msg #589 check."""
import json
import re
from datetime import datetime

SLUG = "lauren-blake-x-altr"
CLIENT = {"Lauren Blake"}
TEST = {"Antonio Veritrade"}
rows = [json.loads(l) for l in open(f"data/chats/{SLUG}.jsonl", encoding="utf-8")]

def ts(r):
    return datetime.fromisoformat(r["ts"])

# 1) message 589 check: show with any digit run >=4 masked
for r in rows:
    if r["id"] == 589:
        t = re.sub(r"\d{4,}", "####", r.get("text") or "")
        print("#589 masked-digits:", t[:700].replace("\n", " / "))
        print("contains 'password'?", "password" in (r.get("text") or "").lower(),
              "| contains 'code'?", "code" in (r.get("text") or "").lower())

# 2) counts
msgs = [r for r in rows if not r.get("service")]
cli = [r for r in msgs if r["sender"] in CLIENT]
test = [r for r in msgs if r["sender"] in TEST]
ours = [r for r in msgs if r["sender"] not in CLIENT and r["sender"] not in TEST]
print("non-service", len(msgs), "client", len(cli), "ours", len(ours), "test", len(test),
      "service", len(rows) - len(msgs))
from collections import Counter
print("our-side senders:", Counter(r["sender"] for r in ours).most_common())
print("last client msg:", cli[-1]["ts"], "| last our msg:", ours[-1]["ts"])

# 3) longest our-side silence (gap between consecutive our-side msgs), full history and since Oct 15
def gaps(lst, since=None):
    out = []
    for a, b in zip(lst, lst[1:]):
        if since and b["ts"][:10] < since:
            continue
        d = (ts(b) - ts(a)).total_seconds() / 86400
        out.append((round(d, 2), a["id"], a["ts"][:16], a["sender"], b["id"], b["ts"][:16], b["sender"]))
    return sorted(out, reverse=True)[:6]
print("TOP our-side gaps (full):")
for g in gaps(ours): print("  ", g)
print("TOP our-side gaps (since 10-15):")
for g in gaps(ours, "2026-10-15"): print("  ", g)
# gap from last our-side msg to export end
end = ts(rows[-1])
print("export end", rows[-1]["ts"])

# 4) client messages since Oct 15 with '?' or imperative asks
print("client msgs since 10-15:")
for r in cli:
    if r["ts"][:10] >= "2026-10-15":
        print("  #%d %s %s" % (r["id"], r["ts"][:16], (r.get("text") or "[media]")[:120].replace("\n", " / ")))

# 5) week-by-week our-side and client message counts since Oct 1
wk = Counter()
for r in msgs:
    if r["ts"][:10] >= "2026-10-01":
        side = "client" if r["sender"] in CLIENT else ("test" if r["sender"] in TEST else "ours")
        wk[(r["ts"][:10] >= "2026-10-16", side)] += 1
print("Oct1-15 vs Oct16-28:", dict(wk))

# 6) service events
for r in rows:
    if r.get("service") and r["ts"][:10] >= "2026-09-01":
        print("service", r["id"], r["ts"][:16], r["event"])
# 7) missing ids
ids = [r["id"] for r in rows]
print("missing ids:", [i for i in range(1, max(ids) + 1) if i not in set(ids)])
