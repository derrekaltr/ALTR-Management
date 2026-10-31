"""Roster for a cs-gap run: msg counts, last activity, prior-run status."""
import glob, json, os, sys

prev = sys.argv[1] if len(sys.argv) > 1 else "2026-09-25"
for f in sorted(glob.glob("data/chats/*.jsonl")):
    s = os.path.basename(f)[:-6]
    L = [json.loads(l) for l in open(f)]
    p = f"data/analysis/cs-gaps-{prev}/{s}.json"
    st = ""
    if os.path.exists(p):
        d = json.load(open(p))
        st = f"{d.get('status')} lastclient={d.get('last_client_message')}"
    new = sum(1 for m in L if m["ts"][:10] > prev)
    print(f"{s:28} {len(L):5} last={L[-1]['ts'][:10]} new_since={new:4} | {prev}: {st}")
