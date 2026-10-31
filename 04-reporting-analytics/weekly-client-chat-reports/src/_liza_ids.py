import json, sys

PATH = "/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro/data/chats/liza-kovalenko-x-altr.jsonl"
want = {985, 1023, 1114, 1089, 1050}
for l in open(PATH):
    r = json.loads(l)
    if r.get("id") in want:
        print("=" * 20, r["id"], r["ts"][:16], r.get("sender"))
        print(r.get("text"))
