#!/usr/bin/env python3
"""Dump per-chat transcript text files for the deep-read set."""
import json, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "transcripts")
os.makedirs(OUT, exist_ok=True)
WA_MEDIA = os.path.expanduser("~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/")

ranking = json.load(open(os.path.join(HERE, "chat_ranking.json")))
BIZNAME = re.compile(r"unban|recover|verif|altr|client|badge|meta|banned|shadowban|\big\b|ig |instagram|restriction|disabled|appeal|invoice|payment|services", re.I)

selected = {}
for i, r in enumerate(ranking):
    key = (r["src"], r["chat_id"])
    if i < 150 or (BIZNAME.search(r["chat"]) and r["msgs"] >= 20):
        selected[key] = r

msgs = defaultdict(list)
for fn in ("imessage.jsonl", "whatsapp.jsonl"):
    with open(os.path.join(HERE, fn)) as f:
        for line in f:
            m = json.loads(line)
            key = (m["src"], m["chat_id"])
            if key in selected:
                msgs[key].append(m)

REACT = {2000: "loved", 2001: "liked", 2002: "disliked", 2003: "laughed", 2004: "emphasized", 2005: "questioned"}
manifest = []
for key, r in selected.items():
    ms = msgs.get(key, [])
    if not ms:
        continue
    slug = re.sub(r"[^A-Za-z0-9]+", "_", r["chat"])[:40].strip("_") or "chat"
    fname = f"{key[0]}_{key[1]}_{slug}.txt"
    path = os.path.join(OUT, fname)
    with open(path, "w") as f:
        f.write(f"CHAT: {r['chat']}\nSOURCE: {key[0]}  GROUP: {r['group']}  MESSAGES: {len(ms)}\n")
        f.write(f"WINDOW: {r['first']} .. {r['last']}\n")
        f.write("=" * 70 + "\n")
        for m in ms:
            t = (m.get("text") or "").replace("\r", " ")
            rc = m.get("react", 0)
            if rc in REACT:
                t = f"[reaction: {REACT[rc]}] {t}"
            elif rc and rc >= 3000:
                t = f"[reaction removed] {t}"
            line = f"[{m['ts']}] {m['sender'] or '?'}: {t}"
            for a in m.get("atts", []):
                p = a.get("path") or ""
                if p and not p.startswith("/") and not p.startswith("~"):
                    p = WA_MEDIA + p
                p = os.path.expanduser(p)
                exists = os.path.exists(p)
                line += f"\n    [ATTACHMENT{'(missing)' if not exists else ''}: {p}]"
            f.write(line + "\n")
    manifest.append({"file": f"transcripts/{fname}", "chat": r["chat"], "src": key[0], "chat_id": key[1],
                     "group": r["group"], "msgs": len(ms), "score": r["score"], "anger": r["anger"],
                     "money": r["money"], "svc": r["svc"], "last": r["last"], "atts": r["atts"],
                     "size_kb": round(os.path.getsize(path) / 1024)})

manifest.sort(key=lambda x: -x["score"])
json.dump(manifest, open(os.path.join(HERE, "manifest.json"), "w"), indent=1, ensure_ascii=False)
print(f"dumped {len(manifest)} transcripts, total {sum(m['size_kb'] for m in manifest)/1024:.1f} MB")
for m in manifest[:10]:
    print(m["size_kb"], "KB", m["file"])
