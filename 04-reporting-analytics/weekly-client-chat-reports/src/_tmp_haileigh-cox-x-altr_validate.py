import json, re
for p in ("data/state/haileigh-cox-x-altr.json", "data/weeks/2026-10-16/haileigh-cox-x-altr.json"):
    txt = open(p).read()
    json.loads(txt)
    phones = re.findall(r"\d{3}[- ]?\d{3}[- ]?\d{4}", txt)
    print(p, "json ok; phone-like:", phones)
