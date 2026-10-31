#!/usr/bin/env python3
"""
analyze.py — group swapd listings by service, judge provider activity from recent
reviews, rank by price, and recommend cheaper alternatives.

Reads:  data/listings.json, catalog.json
Writes: data/services.json

Stdlib only. Run:  python3 scripts/analyze.py
"""
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Activity thresholds (days since last review/comment).
ACTIVE_DAYS = 30
STALE_DAYS = 90

# Quality gate (from swapd's seller card "SUCCESS RATE"). A provider is only trusted for
# outreach/recommendation if their success rate clears this AND they have real feedback.
MIN_SUCCESS_RATE = 60.0

# Canonical service ids are derived as "<platform>_<action>". Detecting platform and
# action separately (with word boundaries) avoids cross-platform bleed — e.g. a bare
# "unban" in a Facebook listing must not fold into instagram_unban. Extend freely.
PLATFORMS = {
    "instagram": ["instagram", "insta", "ig"],
    "tiktok": ["tiktok", "tik tok"],
    "youtube": ["youtube", "yt"],
    "facebook": ["facebook", "fb", "meta"],
    "twitter": ["twitter", "x", "twitter/x"],
    "snapchat": ["snapchat", "snap"],
    "telegram": ["telegram"],
    "linkedin": ["linkedin"],
    "google": ["google"],
    "reddit": ["reddit"],
    "wikipedia": ["wikipedia", "wiki"],
    "whatsapp": ["whatsapp"],
}
# Order matters: the FIRST action that matches wins, so put more specific actions first.
ACTIONS = {
    "unban": ["unban", "un-ban", "reinstat", "recover", "reactivat", "restore",
              "disabled account", "banned account", "suspension", "appeal"],
    "verification": ["verif", "verified", "blue badge", "blue tick", "blue check"],
    "monetization": ["monetiz", "monetis", "adsense"],
    "shielding": ["shielding", "shield"],
    "removal": ["removal", "remove", "deindex", "takedown", "take down",
                "delete", "deletion", "review removal", "content removal"],
    "username_claim": ["username claim", "handle claim", "claim service"],
    "creation": ["creation", "page creation", "article creation"],
    "followers": ["follower", "subscriber growth"],
}


def _has(hay, terms):
    # Match term with a leading word-boundary; allow common suffixes (removal->removals,
    # remove->removed/removing) so plurals/tenses group with their base action.
    for t in terms:
        if re.search(r"\b" + re.escape(t) + r"(?:s|es|ed|ing|d)?\b", hay):
            return True
    return False


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def parse_date(value):
    """Accept ISO date/datetime strings; return a date or None."""
    if not value:
        return None
    if isinstance(value, (int, float)):  # epoch seconds
        try:
            return datetime.fromtimestamp(value).date()
        except (OverflowError, OSError, ValueError):
            return None
    s = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:len(fmt) + 2], fmt).date()
        except ValueError:
            continue
    # Last resort: leading YYYY-MM-DD
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            return None
    return None


def build_alias_index(catalog):
    """Map lowercase alias/display/service -> canonical service id."""
    index = {}
    meta = {}
    for entry in catalog.get("services", []):
        canon = entry.get("service")
        if not canon:
            continue
        meta[canon] = {
            "display": entry.get("display") or canon.replace("_", " ").title(),
            "your_price": entry.get("your_cost", entry.get("your_price")),
            "in_catalog": True,
        }
        keys = [canon, entry.get("display", "")] + entry.get("aliases", [])
        for k in keys:
            if k:
                index[k.lower().strip()] = canon
    return index, meta


def normalize_service(listing, alias_index):
    """Return a canonical service id for a listing."""
    if listing.get("service_type"):
        return listing["service_type"]
    hay = " ".join(
        str(listing.get(f, "")) for f in ("title", "category", "body_excerpt")
    ).lower()
    # 1) catalog aliases (longest first so specific wins)
    for alias in sorted(alias_index, key=len, reverse=True):
        if alias and alias in hay:
            return alias_index[alias]
    # 2) platform + action detection (word-boundary matched)
    platform = next((p for p, terms in PLATFORMS.items() if _has(hay, terms)), None)
    action = next((a for a, terms in ACTIONS.items() if _has(hay, terms)), None)
    if platform and action:
        return f"{platform}_{action}"
    if action:
        return action
    if platform:
        return f"{platform}_service"
    # 3) fallback: slug of title
    title = (listing.get("title") or "unknown").lower()
    slug = re.sub(r"[^a-z0-9]+", "_", title).strip("_")
    return slug[:60] or "unknown"


def activity_for(last_review, today):
    d = parse_date(last_review)
    if not d:
        return "unknown", None
    age = (today - d).days
    if age < 0:
        age = 0
    if age <= ACTIVE_DAYS:
        return "active", age
    if age <= STALE_DAYS:
        return "stale", age
    return "cold", age


def to_number(price):
    if isinstance(price, (int, float)):
        return float(price)
    if not price:
        return None
    m = re.search(r"[\d][\d,]*(?:\.\d+)?", str(price))
    return float(m.group().replace(",", "")) if m else None


def main():
    today = date.today()
    listings_doc = load_json(DATA / "listings.json", {"listings": {}})
    catalog = load_json(ROOT / "catalog.json", {"services": []})
    alias_index, service_meta = build_alias_index(catalog)

    services = {}
    for lid, listing in listings_doc.get("listings", {}).items():
        canon = normalize_service(listing, alias_index)
        listing["service_type"] = canon  # backfill (in-memory)
        meta = service_meta.get(canon, {})
        svc = services.setdefault(canon, {
            "display": meta.get("display") or canon.replace("_", " ").title(),
            "in_catalog": bool(meta.get("in_catalog")),
            "your_price": meta.get("your_price"),
            "providers": [],
        })
        price = to_number(listing.get("price"))
        activity, age = activity_for(listing.get("last_review_date"), today)
        success = listing.get("success_rate")  # 0-100 from seller card, or None
        reviews = listing.get("review_count") or 0
        transactions = listing.get("transactions") or 0
        qualified = (
            isinstance(success, (int, float)) and success > MIN_SUCCESS_RATE
            and (reviews > 0 or transactions > 0)
        )
        svc["providers"].append({
            "listing_id": lid,
            "seller": listing.get("seller"),
            "seller_url": listing.get("seller_url"),
            "listing_url": listing.get("url"),
            "price": price,
            "price_raw": listing.get("price_raw") or listing.get("price"),
            "turnaround": listing.get("turnaround"),
            "requirements": listing.get("requirements"),
            "activity": activity,
            "review_age_days": age,
            "last_review_date": listing.get("last_review_date"),
            "last_seen": listing.get("last_seen"),
            "success_rate": success,
            "transactions": transactions,
            "rating": listing.get("rating"),
            "review_count": reviews,
            "recent_deals": listing.get("recent_deals"),
            "member_since": listing.get("member_since"),
            "qualified": qualified,
        })

    # Rank + recommend per service. Only QUALIFIED providers (success rate > threshold with
    # real feedback) count toward best-price, outreach, and recommendations.
    for canon, svc in services.items():
        svc["is_new"] = not svc["in_catalog"]  # new service = one ALTR doesn't sell yet
        svc["providers"].sort(
            key=lambda p: (not p["qualified"], p["price"] is None, p["price"] or 0)
        )
        qualified_priced = [
            p for p in svc["providers"] if p["price"] is not None and p["qualified"]
        ]
        svc["qualified_count"] = sum(1 for p in svc["providers"] if p["qualified"])
        best = qualified_priced[0] if qualified_priced else None
        svc["best_price"] = best["price"] if best else None
        svc["best_provider"] = best["seller"] if best else None
        for p in svc["providers"]:
            p["is_best_price"] = bool(best and p is best)

        rec = None
        yp = to_number(svc.get("your_price"))
        if best:
            sr = best.get("success_rate")
            sr_txt = f", {sr:.1f}% success" if isinstance(sr, (int, float)) else ""
            if svc["in_catalog"]:
                # Existing service: flag a cheaper trusted provider vs ALTR's cost.
                if yp is not None and best["price"] < yp:
                    rec = (
                        f"Test {best['seller']} at ${best['price']:,.0f}"
                        f"{sr_txt} — saves ${yp - best['price']:,.0f} vs your ${yp:,.0f}."
                    )
                elif yp is None and len(qualified_priced) > 1:
                    rec = (
                        f"Cheapest trusted provider: {best['seller']} at "
                        f"${best['price']:,.0f}{sr_txt}. Add your cost to see savings."
                    )
            else:
                # New service: an onboarding opportunity — surface the best trusted provider.
                rec = (
                    f"New service opportunity — best trusted provider {best['seller']} at "
                    f"${best['price']:,.0f}{sr_txt}. Candidate for outreach."
                )
        svc["recommendation"] = rec

    out = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "service_count": len(services),
        "services": dict(sorted(services.items())),
    }
    (DATA / "services.json").write_text(json.dumps(out, indent=2))
    recs = sum(1 for s in services.values() if s["recommendation"])
    print(f"analyze: {len(services)} service types, {recs} recommendations "
          f"-> {DATA / 'services.json'}")


if __name__ == "__main__":
    sys.exit(main())
