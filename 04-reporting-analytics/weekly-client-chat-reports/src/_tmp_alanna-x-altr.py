import json
from pathlib import Path

for p in ["data/state/alanna-x-altr.json", "data/weeks/2026-10-16/alanna-x-altr.json"]:
    text = Path(p).read_text()
    json.loads(text)
    leaks = [s for s in ("2136762479", "J_robinette") if s in text]
    print(p, "valid json", "LEAKS:" if leaks else "no leaks", leaks or "")
