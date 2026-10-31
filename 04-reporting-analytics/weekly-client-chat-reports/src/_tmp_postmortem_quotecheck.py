"""Verify every evidence quote in the post-mortem JSONs appears verbatim in the chat history."""
import json, os, sys, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
run = sys.argv[1] if len(sys.argv) > 1 else "cs-gaps-2026-10-09"
slugs = ["amber-haze-x-altr", "alex-paige-moore-x-altr", "vicky-x-altr", "paige-x-altr", "chey-mai-x-altr", "kaitlynn-x-altr"]

def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()

for s in slugs:
    corpus = []
    p = os.path.join(ROOT, "data/chats", s + ".jsonl")
    for l in open(p):
        corpus.append(json.loads(l).get("text") or "")
    # older history for replaced chats lives in data/weeks
    for wp in glob.glob(os.path.join(ROOT, "data/weeks", "*", "**", "*" + s.replace("-x-altr", "") + "*"), recursive=True):
        try:
            corpus.append(open(wp, errors="ignore").read())
        except IsADirectoryError:
            pass
    blob = norm("\n".join(corpus))
    d = json.load(open(os.path.join(ROOT, "data/analysis", run, s + ".json")))
    miss = 0; tot = 0
    for dim, v in d["dimensions"].items():
        for e in v["evidence"]:
            q = e["quote"]
            parts = [x for x in re.split(r"\s/\s|\.\.\.|\[REDACTED[^\]]*\]|\([^)]*REDACTED[^)]*\)|\(.*posted.*\)", q) if len(x.strip()) > 8]
            for part in parts:
                tot += 1
                if norm(part)[:60] not in blob:
                    miss += 1
                    print("  MISS", s, dim, e["date"], repr(part[:90]))
    print(s, "checked", tot, "missing", miss)
