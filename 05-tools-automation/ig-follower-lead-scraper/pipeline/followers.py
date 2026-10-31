"""Stage 1: export the target account's follower list via an Apify actor.

Runs in chunks with a checkpoint so a 200k+ export can resume after failures.
NOTE: the follower actor's exact input/cursor field names must be verified
during the pilot run (see README) — they are collected here, not scattered.
"""

from __future__ import annotations

import os

from .common import (
    append_jsonl,
    apify_client,
    data_dir,
    load_checkpoint,
    norm_username,
    read_jsonl,
    save_checkpoint,
)

DEFAULT_ACTOR = "scraping_solutions/instagram-scraper-followers-following-no-cookies"
COST_PER_1K = 0.60  # USD, per actor listing — re-check before large runs
CHUNK_SIZE = 20000  # actor's documented per-run resultsLimit ceiling

# Keys we scan for a continuation cursor in the actor's OUTPUT / last item.
CURSOR_KEYS = ("nextContinuationToken", "nextCursor", "next_cursor", "cursor",
               "continuationToken", "nextPageToken", "endCursor")


def _find_cursor(obj):
    """Return a continuation token from the actor OUTPUT, or None if the list
    is exhausted. This actor nests it under continuations[].nextContinuationToken
    with a hasNextPage flag; other actors put it at the top level."""
    if not isinstance(obj, dict):
        return None
    conts = obj.get("continuations")
    if isinstance(conts, list) and conts:
        c = conts[0]
        if isinstance(c, dict):
            if c.get("hasNextPage") is False:
                return None
            for k in CURSOR_KEYS:
                if isinstance(c.get(k), str) and c[k]:
                    return c[k]
    for k in CURSOR_KEYS:
        if isinstance(obj.get(k), str) and obj[k]:
            return obj[k]
    return None


def scrape_followers(target: str, limit: int | None = None, yes: bool = False) -> None:
    actor_id = os.environ.get("APIFY_FOLLOWERS_ACTOR", DEFAULT_ACTOR)
    out = data_dir(target) / "followers_raw.jsonl"
    ckpt_path = data_dir(target) / "checkpoints" / "followers.json"
    ckpt = load_checkpoint(ckpt_path, {"scraped": 0, "cursor": None, "runs": [], "exhausted": False})

    if ckpt["exhausted"]:
        print(f"Follower export already complete ({ckpt['scraped']} rows in {out}). Delete the checkpoint to redo.")
        return

    goal = limit if limit else 250000
    est = (goal - ckpt["scraped"]) / 1000 * COST_PER_1K
    print(f"Target @{target}: exporting up to {goal:,} followers (have {ckpt['scraped']:,}). Estimated cost ≈ ${est:,.2f}.")
    if not yes:
        raise SystemExit("Refusing to spend without --yes. Re-run with --yes to proceed.")

    client = apify_client()
    while ckpt["scraped"] < goal:
        chunk = min(CHUNK_SIZE, goal - ckpt["scraped"])
        run_input = {
            "Account": [target.lstrip("@")],
            "resultsLimit": max(50, chunk),  # actor requires 50–20000
            "dataToScrape": "Followers",
        }
        if ckpt["cursor"]:
            run_input["continuationToken"] = ckpt["cursor"]
        print(f"  Apify run: {chunk:,} results (cursor={'yes' if ckpt['cursor'] else 'none'})...")
        run = client.actor(actor_id).call(run_input=run_input)

        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        new = [i for i in items if norm_username(i)]
        append_jsonl(out, new)
        ckpt["scraped"] += len(new)
        ckpt["runs"].append(run["id"])

        cursor = None
        try:
            record = client.key_value_store(run["defaultKeyValueStoreId"]).get_record("OUTPUT")
            if record:
                cursor = _find_cursor(record.get("value"))
        except Exception:
            pass
        if not cursor and items:
            cursor = _find_cursor(items[-1])
        ckpt["cursor"] = cursor

        print(f"  +{len(new):,} rows (total {ckpt['scraped']:,})")
        if len(new) == 0 or (len(new) < chunk and not cursor):
            ckpt["exhausted"] = True
            save_checkpoint(ckpt_path, ckpt)
            print("  Actor returned fewer rows than requested and no cursor — list exhausted (or IG capped pagination).")
            break
        save_checkpoint(ckpt_path, ckpt)

    total = sum(1 for _ in read_jsonl(out))
    print(f"Done. {total:,} raw follower rows in {out}")
