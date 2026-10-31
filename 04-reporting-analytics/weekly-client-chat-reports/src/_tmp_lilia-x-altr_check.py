import json
P = "data/state/lilia-x-altr.json"
t = open(P).read()
print("occurrences:", t.count("3214470208"))
t = t.replace("3214470208", "[REDACTED]")
json.loads(t)
open(P, "w").write(t)
print("after:", t.count("3214470208"))
