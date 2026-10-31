"""Stage 2 (free): cut the follower list before paying for profile details.

Drops private accounts and clearly-male first names. Ambiguous/unknown names
are KEPT — we never discard a potential lead on a weak signal; the rubric and
the review pass sort them out after profile enrichment.
"""

import csv

import gender_guesser.detector as gender_detector

from .common import append_jsonl, data_dir, first_name, norm_follower_item, read_jsonl

DROP_GENDERS = {"male", "mostly_male"}


def prefilter(target: str) -> None:
    d = data_dir(target)
    raw = d / "followers_raw.jsonl"
    out = d / "candidates.jsonl"
    rejected_csv = d / "prefilter_rejected.csv"
    if not raw.exists():
        raise SystemExit(f"{raw} not found — run scrape-followers first.")
    out.unlink(missing_ok=True)

    detector = gender_detector.Detector(case_sensitive=False)
    seen, kept, rejected = set(), [], []
    for item in read_jsonl(raw):
        row = norm_follower_item(item)
        u = row["username"]
        if not u or u in seen:
            continue
        seen.add(u)
        if row["is_private"]:
            rejected.append((u, row["full_name"], "private"))
            continue
        name = first_name(row["full_name"])
        guess = detector.get_gender(name) if name else "unknown"
        if guess in DROP_GENDERS:
            rejected.append((u, row["full_name"], f"male_name:{name}"))
            continue
        row["name_gender_guess"] = guess
        kept.append(row)

    append_jsonl(out, kept)
    with open(rejected_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["username", "full_name", "reason"])
        w.writerows(rejected)

    print(f"Prefilter: {len(seen):,} unique followers → {len(kept):,} candidates "
          f"({len(rejected):,} dropped: private or male name — see {rejected_csv.name})")
    print(f"Estimated profile-scrape cost for candidates ≈ ${len(kept) / 1000 * 1.60:,.2f}")
