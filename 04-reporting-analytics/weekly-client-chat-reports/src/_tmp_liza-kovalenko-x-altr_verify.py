import json, re

out_path = "data/analysis/cs-gaps-2026-10-09/liza-kovalenko-x-altr.json"
raw = open(out_path).read()
d = json.loads(raw)
msgs = [json.loads(l) for l in open("data/chats/liza-kovalenko-x-altr.jsonl")]
texts = [(m.get("text") or "").replace("\n", " / ") for m in msgs]
allt = "\n".join(texts)

for name, dim in d["dimensions"].items():
    for ev in dim["evidence"]:
        q = ev["quote"]
        for part in re.split(r" / | \.\.\. ", q):
            part = part.replace("[REDACTED credential]", "").strip()
            if not part:
                continue
            if part in allt:
                continue
            curly = part.replace("'", "’")
            if curly in allt:
                print("CURLY", name, repr(part))
            else:
                print("MISSING", name, repr(part))

# secrets check
for s in ["308009"]:
    print("secret present:", s in raw)
print("dims", len(d["dimensions"]))

# --- fix pass: make quotes byte-exact
import sys
if "--fix" in sys.argv:
    for dim in d["dimensions"].values():
        for ev in dim["evidence"]:
            parts = re.split(r"( / | \.\.\. )", ev["quote"])
            fixed = []
            for p in parts:
                core = p.replace("[REDACTED credential]", "")
                if core.strip() and core not in allt and core.replace("'", "’") in allt:
                    p = p.replace("'", "’")
                fixed.append(p)
            ev["quote"] = "".join(fixed)
            if ev["quote"].startswith("Hi there, I'm Aroosha"):
                ev["quote"] = ev["quote"].replace("Hi there, I'm", "Hi there,  I'm")
    json.dump(d, open(out_path, "w"), ensure_ascii=False, indent=2)
    print("fixed")
