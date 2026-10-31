import json, sys
since = sys.argv[1] if len(sys.argv) > 1 else "2026-09-16"
for line in open("data/chats/haileigh-cox-x-altr.jsonl"):
    m = json.loads(line)
    if m.get("ts", "") < since:
        continue
    if m.get("service"):
        print(m["id"], m["ts"][:16], "SERVICE", m.get("event"), m.get("actor", ""), m.get("members", ""))
        continue
    print(m["id"], m["ts"][:16], m.get("sender"), "|", (m.get("text") or "")[:400].replace("\n", " "), "| media=" + str(m.get("media", "")), "re=" + str(m.get("reply_to", "")))
