"""Check Lauren Blake 10-16 outputs: state JSON parses; no obvious secrets leaked."""
import json
import re

for p in ["data/state/lauren-blake-x-altr.json", "data/weeks/2026-10-16/lauren-blake-x-altr.json"]:
    raw = open(p).read()
    json.loads(raw)
    hits = re.findall(r"\b\d{6,}\b|[\w.+-]+@[\w-]+\.\w+", raw)
    print(p, "OK; numeric/email-like tokens:", sorted(set(hits)))
