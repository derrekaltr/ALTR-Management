"""Stage 5: turn the scored leads into deliverables — qualified_leads.csv
(sorted by score, everyone who passed the gates) and handles.txt.

An optional review_decisions.csv can drop specific accounts: add a row
`username,reject,note` to remove a false positive. Everything else is kept.
"""

import csv

from .common import data_dir


def _read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def export(target: str, min_score: int = 1) -> None:
    d = data_dir(target)
    leads = _read_csv(d / "scored_leads.csv")
    if not leads:
        raise SystemExit(f"{d / 'scored_leads.csv'} not found or empty — run qualify first.")

    decisions = {r["username"].strip().lstrip("@").lower(): r.get("decision", "").strip().lower()
                 for r in _read_csv(d / "review_decisions.csv")}
    rows, dropped = [], 0
    for r in leads:
        if int(r["score"]) < min_score:
            continue
        if decisions.get(r["username"]) == "reject":
            dropped += 1
            continue
        rows.append(r)
    rows.sort(key=lambda r: (-int(r["score"]), -int(r["followers"])))

    out_csv = d / "qualified_leads.csv"
    fields = ["username", "score", "gender", "profile_url", "followers", "external_url", "biography", "reasons"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({**r, "profile_url": f"https://instagram.com/{r['username']}"})

    out_txt = d / "handles.txt"
    out_txt.write_text("\n".join(f"@{r['username']}" for r in rows) + "\n", encoding="utf-8")

    dist = {s: sum(1 for r in rows if int(r["score"]) == s) for s in (5, 4, 3, 2, 1)}
    print(f"Exported {len(rows):,} leads (min score {min_score}"
          + (f", {dropped} manually rejected" if dropped else "") + ")")
    print("  by score:  " + "  ".join(f"{s}★:{dist[s]:,}" for s in (5, 4, 3, 2, 1)))
    print(f"  {out_csv}\n  {out_txt}")


def status(target: str) -> None:
    d = data_dir(target)
    counts = []
    for name in ("followers_raw.jsonl", "candidates.jsonl", "profiles_raw.jsonl"):
        p = d / name
        n = sum(1 for line in open(p, encoding="utf-8") if line.strip()) if p.exists() else 0
        counts.append((name, n))
    for name in ("scored_leads.csv", "disqualified.csv", "qualified_leads.csv"):
        p = d / name
        counts.append((name, max(0, sum(1 for _ in open(p, encoding="utf-8")) - 1) if p.exists() else 0))
    width = max(len(n) for n, _ in counts)
    for name, n in counts:
        print(f"  {name:<{width}}  {n:>10,}")
