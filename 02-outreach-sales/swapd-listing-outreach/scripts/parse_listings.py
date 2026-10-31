#!/usr/bin/env python3
"""
parse_listings.py — merge raw scan batches (data/raw/*.json) into data/listings.json.

Raw records use short keys (from the in-page scanner). This expands them to the canonical
schema, reconstructs URLs, dedups by topic id (merging tags seen across tags/categories),
and preserves first_seen while refreshing last_seen.

Run:  python3 scripts/parse_listings.py
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"

KEYMAP = {
    "id": "id", "ttl": "title", "sl": "seller", "pr": "price", "praw": "price_raw",
    "tat": "turnaround", "rq": "requirements", "tg": "tags", "pd": "post_date",
    "ld": "last_review_date", "sr": "success_rate", "tx": "transactions",
    "rd": "recent_deals", "ar": "rating", "rc": "review_count", "ms": "member_since",
    "pm": "can_pm",
}


def expand(rec):
    out = {full: rec.get(short) for short, full in KEYMAP.items()}
    tid = out["id"]
    out["url"] = f"https://swapd.co/t/{tid}"
    out["seller_url"] = f"https://swapd.co/u/{out['seller']}" if out.get("seller") else None
    out["source_tag"] = rec.get("cat")  # the tag/category this listing was found under
    tags = out.get("tags") or ""
    out["tags"] = [t for t in tags.split(",") if t] if isinstance(tags, str) else tags
    return out


def main():
    today = date.today().isoformat()
    doc = json.loads((DATA / "listings.json").read_text()) if (DATA / "listings.json").exists() \
        else {"meta": {}, "listings": {}}
    listings = doc.get("listings", {})

    seen_now = 0
    for raw_file in sorted(RAW.glob("*.json")):
        batch = json.loads(raw_file.read_text())
        for rec in batch.get("listings", []):
            r = expand(rec)
            tid = r["id"]
            if not tid:
                continue
            seen_now += 1
            if tid in listings:
                prev = listings[tid]
                r["first_seen"] = prev.get("first_seen", today)
                # union of tags across sources
                r["tags"] = sorted(set(r["tags"]) | set(prev.get("tags", [])))
                # keep earliest source_tag list
                srcs = set(filter(None, [prev.get("source_tag"), r.get("source_tag")]))
                r["source_tag"] = ",".join(sorted(srcs))
            else:
                r["first_seen"] = today
            r["last_seen"] = today
            listings[tid] = r

    doc["listings"] = listings
    doc.setdefault("meta", {})["last_run"] = batch.get("scanned_at") if RAW.glob("*.json") else today
    doc["meta"]["last_run"] = doc["meta"].get("last_run") or today
    (DATA / "listings.json").write_text(json.dumps(doc, indent=2))
    print(f"parse: {seen_now} raw records -> {len(listings)} unique listings")


if __name__ == "__main__":
    main()
