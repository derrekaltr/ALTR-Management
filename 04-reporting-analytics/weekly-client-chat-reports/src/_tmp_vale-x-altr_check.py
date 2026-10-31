import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
msgs = [json.loads(l) for l in (ROOT / "data/chats/vale-x-altr.jsonl").read_text().splitlines() if l.strip()]
texts = [(m.get("ts", "")[:10], m.get("text", "") or "") for m in msgs if not m.get("service")]
f = json.loads((ROOT / "data/weeks/2026-10-16/vale-x-altr.json").read_text())
st = json.loads((ROOT / "data/state/vale-x-altr.json").read_text())
print("state parses ok; as_of", st["as_of"])

bad = 0
def walk(o):
    global bad
    if isinstance(o, dict):
        if "quote" in o and "date" in o:
            q = o["quote"]
            parts = [p for p in q.split("[REDACTED]") if p.strip()]
            ok = any(d == o["date"] and all(p in t for p in parts) for d, t in texts)
            if not ok:
                bad += 1
                print("MISSING:", o["date"], q[:90])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(f)
print("quote mismatches:", bad)

# window stats
lo, hi = "2026-10-09T09:05:57", "2026-10-16T09:06:40"
win = [m for m in msgs if not m.get("service") and lo <= m["ts"][:19] <= hi]
c = sum(1 for m in win if m["sender"] == "Vale")
print("window", len(win), "client", c, "team", len(win) - c, "ids", win[0]["id"], win[-1]["id"])

# secret scan on output
s = json.dumps(f, ensure_ascii=False)
for pat in [r"\b\d{6}\b", r"[\w.]+@[\w-]+\.(com|net|org)", r"\+?\d[\d\s\-()]{9,}\d", r"(?i)password[:\s]+\S+"]:
    for mm in re.finditer(pat, s):
        print("SECRET?", pat, s[max(0, mm.start()-30):mm.end()+30])
