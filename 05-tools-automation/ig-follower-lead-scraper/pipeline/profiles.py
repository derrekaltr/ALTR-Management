"""Stage 3: fetch profile details (bio, followers, link, private flag) for
every candidate via apify/instagram-profile-scraper, in resumable batches."""

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

DEFAULT_ACTOR = "apify/instagram-profile-scraper"
COST_PER_1K = 1.60  # USD on paid plans — re-check before large runs
BATCH_SIZE = 1000


def scrape_profiles(target: str, limit: int | None = None, yes: bool = False) -> None:
    actor_id = os.environ.get("APIFY_PROFILES_ACTOR", DEFAULT_ACTOR)
    d = data_dir(target)
    candidates_path = d / "candidates.jsonl"
    out = d / "profiles_raw.jsonl"
    ckpt_path = d / "checkpoints" / "profiles.json"
    if not candidates_path.exists():
        raise SystemExit(f"{candidates_path} not found — run prefilter first.")

    candidates = [r["username"] for r in read_jsonl(candidates_path) if r.get("username")]
    ckpt = load_checkpoint(ckpt_path, {"requested": []})
    requested = set(ckpt["requested"])
    todo = [u for u in candidates if u not in requested]
    if limit:
        todo = todo[:limit]
    if not todo:
        print("All candidates already requested — nothing to do.")
        return

    est = len(todo) / 1000 * COST_PER_1K
    print(f"Fetching profile details for {len(todo):,} of {len(candidates):,} candidates. Estimated cost ≈ ${est:,.2f}.")
    if not yes:
        raise SystemExit("Refusing to spend without --yes. Re-run with --yes to proceed.")

    client = apify_client()
    for i in range(0, len(todo), BATCH_SIZE):
        batch = todo[i:i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1}/{-(-len(todo) // BATCH_SIZE)} ({len(batch):,} usernames)...")
        run = client.actor(actor_id).call(run_input={"usernames": batch})
        items = [it for it in client.dataset(run["defaultDatasetId"]).iterate_items() if norm_username(it)]
        append_jsonl(out, items)
        requested.update(batch)
        ckpt["requested"] = sorted(requested)
        save_checkpoint(ckpt_path, ckpt)
        print(f"  +{len(items):,} profiles (some usernames may be gone/renamed — that's normal)")

    total = sum(1 for _ in read_jsonl(out))
    print(f"Done. {total:,} profiles in {out}")
