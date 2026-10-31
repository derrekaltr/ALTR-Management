import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "data/analysis/cs-gaps-2026-10-16")
stale = {"amber-haze-x-altr": ["18 days and counting", "gone 18 days", "issued in 18 days"],
         "alex-paige-moore-x-altr": ["gone 22 days"], "vicky-x-altr": ["52 days"], "paige-x-altr": [], "chey-mai-x-altr": [], "kaitlynn-x-altr": []}
secret = re.compile(r"(pass(word)?\s*[:=]\s*\S+|https?://\S*(onlyfans|verify|session|token|drive\.google|calendly|commas)\S*|\b\d{6}\b|\b(?:\d[ -]?){13,16}\b)", re.I)
for s, pats in stale.items():
    p = os.path.join(DST, s + ".json")
    t = open(p).read()
    d = json.loads(t)
    for pat in pats:
        if pat in t:
            print("STALE", s, pat)
    for m in secret.finditer(t):
        print("SECRET?", s, t[max(0, m.start() - 60): m.end() + 20].replace("\n", " "))
    req = ["client", "slug", "status", "status_reason", "last_client_message", "dimensions", "metrics", "what_client_wanted", "what_worked", "top_fix", "churn_timeline", "warning_signs_missed"]
    miss = [k for k in req if k not in d]
    assert len(d["dimensions"]) == 10, s
    for k, v in d["dimensions"].items():
        assert 2 <= len(v["evidence"]) <= 3, (s, k)
    print(s, "ok" if not miss else miss, d["status"], d["last_client_message"], "timeline", len(d["churn_timeline"]), "signs", len(d["warning_signs_missed"]), "dangling", len(d["dangling_as_of_2026-10-16"]))
