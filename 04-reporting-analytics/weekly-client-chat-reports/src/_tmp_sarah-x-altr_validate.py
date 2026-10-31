import json

for p in ["data/state/sarah-x-altr.json", "data/weeks/2026-10-16/sarah-x-altr.json"]:
    s = open(p).read()
    json.loads(s)
    print(p, "parses; legal-surname hits:", s.lower().count("henderson"))
