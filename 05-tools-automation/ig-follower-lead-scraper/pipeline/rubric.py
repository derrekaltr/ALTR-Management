"""Stage 4: score enriched profiles 1-5 against the rubric.

Hard gates (auto-disqualify): private, followers < min_followers, or male.
Everything that passes the gates is SCORED 1-5 rather than pass/fail — a link
or "check my highlights" mention is a strong signal, not a requirement.
Gender-unknown accounts are included but capped (see rubric.yaml) so
confirmed-female accounts rank above them. Output is sorted by score.
"""

from __future__ import annotations

import csv
import re

import gender_guesser.detector as gender_detector

from .common import data_dir, first_name, load_rubric, norm_profile_item, read_jsonl

_detector = gender_detector.Detector(case_sensitive=False)


def _compile(cfg):
    return [re.compile(p, re.IGNORECASE) for p in cfg.get("highlights_patterns", [])]


_business_cache = {}


def _compile_business(cfg):
    """(term, regex) pairs, cached per config object. Each regex requires a word
    edge (start/end/non-letter) on at least one side: catches compounds like
    'skategroundmag' at the edge while leaving mid-word hits like 'image' alone."""
    key = id(cfg)
    if key not in _business_cache:
        pairs = []
        for t in cfg.get("business_terms", []):
            esc = re.escape(t.lower())
            pairs.append((t, re.compile(rf"(?:^|[^a-z]){esc}|{esc}(?:[^a-z]|$)")))
        _business_cache[key] = pairs
    return _business_cache[key]


def _keyword_hits(text: str, cfg, groups) -> list[str]:
    hits = []
    kw = cfg.get("creator_keywords", {})
    for group in groups:
        for w in kw.get(group, []):
            if w.lower() in text:
                hits.append(f"{group}:{w}")
    return hits


def _gender(profile: dict, cfg) -> tuple[str, str]:
    """Return (verdict, evidence) where verdict is female|male|unknown."""
    bio = profile["biography"].lower()
    g = cfg.get("gender", {})
    female_hit = next((t for t in g.get("female_terms", []) if t.lower() in bio), None)
    male_hit = next((t for t in g.get("male_terms", []) if t.lower() in bio), None)
    if female_hit and not male_hit:
        return "female", f"bio:{female_hit}"
    if male_hit and not female_hit:
        return "male", f"bio:{male_hit}"
    name = first_name(profile["full_name"])
    guess = _detector.get_gender(name) if name else "unknown"
    if guess in ("female", "mostly_female"):
        return "female", f"name:{name}"
    if guess in ("male", "mostly_male"):
        return "male", f"name:{name}"
    return "unknown", ""


def score_profile(profile: dict, cfg, highlights_res=None) -> dict:
    """Score one normalized profile. Returns a dict with score (0 = disqualified),
    gender, and the signals that fired. Score 0 carries a disqualifier reason."""
    if highlights_res is None:
        highlights_res = _compile(cfg)

    if profile["is_private"]:
        return {"score": 0, "gender": "", "reasons": "disqualified:private"}
    if profile["followers"] < cfg["min_followers"]:
        return {"score": 0, "gender": "", "reasons": f"disqualified:followers<{cfg['min_followers']}"}
    name_hay = f"{profile['username']} {profile['full_name']}".lower()
    bio_hay = profile["biography"].lower()
    excl = next((t for t in cfg.get("exclude_name_terms", []) if t.lower() in name_hay), None)
    if not excl:
        excl = next((p for p in cfg.get("exclude_bio_phrases", []) if p.lower() in bio_hay), None)
    if excl:
        return {"score": 0, "gender": "", "reasons": f"disqualified:agency/mgmt:{excl.strip()}"}
    gender, evidence = _gender(profile, cfg)
    if gender == "male":
        return {"score": 0, "gender": "male", "reasons": f"disqualified:male:{evidence}"}
    if gender != "female":
        hit = next((term for term, r in _compile_business(cfg) if r.search(name_hay)), None)
        if hit:
            return {"score": 0, "gender": gender, "reasons": f"disqualified:business:{hit}"}

    bio = profile["biography"].lower()
    url = profile["external_url"].lower()
    has_link = bool(profile["external_url"])

    adult_hits = [f"adult_domain:{d}" for d in cfg.get("adult_domains", []) if d in url]
    adult_hits += _keyword_hits(bio, cfg, ["onlyfans_adjacent"])
    linkhub_hits = [f"linkhub:{d}" for d in cfg.get("linkhub_domains", []) if d in url]
    highlights_hit = next((p.pattern for p in highlights_res if p.search(profile["biography"])), None)
    snap_hits = [f"snapchat:{m}" for m in cfg.get("snapchat_markers", []) if m.lower() in bio]
    platform_hits = _keyword_hits(bio, cfg, ["platforms"])
    creator_hits = _keyword_hits(bio, cfg, ["creator_terms"])

    signals = []
    if adult_hits:
        score = 5
        signals += adult_hits
    elif linkhub_hits or highlights_hit or snap_hits:
        score = 4
        signals += linkhub_hits + snap_hits
        if highlights_hit:
            signals.append(f"highlights:{highlights_hit}")
    elif has_link and (platform_hits or creator_hits):
        score = 3
        signals.append("link_in_bio")
        signals += platform_hits + creator_hits
    elif has_link or platform_hits or creator_hits:
        score = 2
        if has_link:
            signals.append("link_in_bio")
        signals += platform_hits + creator_hits
    else:
        score = 1

    cap = cfg.get("unknown_gender_score_cap", 3)
    if gender == "unknown" and score > cap:
        signals.append(f"capped_from_{score}_gender_unknown")
        score = cap

    reasons = f"{gender}:{evidence}" if evidence else gender
    if signals:
        reasons += "; " + "; ".join(signals)
    return {"score": score, "gender": gender, "reasons": reasons}


FIELDS = ["username", "score", "gender", "followers", "external_url", "biography", "reasons"]


def qualify(target: str) -> None:
    d = data_dir(target)
    raw = d / "profiles_raw.jsonl"
    if not raw.exists():
        raise SystemExit(f"{raw} not found — run scrape-profiles first.")

    cfg = load_rubric()
    highlights_res = _compile(cfg)
    passing, disqualified = [], []
    seen = set()
    for item in read_jsonl(raw):
        profile = norm_profile_item(item)
        if not profile["username"] or profile["username"] in seen:
            continue
        seen.add(profile["username"])
        result = score_profile(profile, cfg, highlights_res)
        row = {
            "username": profile["username"],
            "score": result["score"],
            "gender": result["gender"],
            "followers": profile["followers"],
            "external_url": profile["external_url"],
            "biography": profile["biography"].replace("\n", " | "),
            "reasons": result["reasons"],
        }
        (disqualified if result["score"] == 0 else passing).append(row)

    passing.sort(key=lambda r: (-r["score"], -r["followers"]))

    scored_path = d / "scored_leads.csv"
    with open(scored_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(passing)
    with open(d / "disqualified.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(disqualified)

    dist = {s: sum(1 for r in passing if r["score"] == s) for s in (5, 4, 3, 2, 1)}
    print(f"Scored {len(passing):,} leads (of {len(seen):,} profiles; {len(disqualified):,} disqualified).")
    print("Score distribution:  " + "  ".join(f"{s}★:{dist[s]:,}" for s in (5, 4, 3, 2, 1)))
    print(f"→ {scored_path}")
