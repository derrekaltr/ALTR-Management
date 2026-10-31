import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
txt = open(os.path.join(ROOT, "data/state/_narrative-2026-10-16.json")).read()
pat = re.compile(r"amber|alex paige|vicky|valerie|chey|kaitlynn|paige-x|churn", re.I)
for m in pat.finditer(txt):
    print("...", txt[max(0, m.start() - 300): m.end() + 400].replace("\\n", " "), "\n")
# also other clients' chats mentioning these names since 10/09
import glob
for p in glob.glob(os.path.join(ROOT, "data/chats/*.jsonl")):
    for l in open(p):
        r = json.loads(l)
        if r.get("ts", "") >= "2026-09-22" and re.search(r"amber|alex paige|vicky|valeri|chey|kaitlynn|\bpaige\b", r.get("text") or "", re.I):
            print(os.path.basename(p), r["ts"][:10], r.get("sender"), (r.get("text") or "")[:300].replace("\n", " / "))
