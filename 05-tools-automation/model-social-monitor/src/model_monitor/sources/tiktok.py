"""TikTok posts via the clockworks~tiktok-scraper actor."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from . import Post
from .apify import run_actor

log = logging.getLogger(__name__)

ACTOR_ID = "clockworks~tiktok-scraper"


def fetch_posts(handles: list[str], results_limit: int, token: str) -> list[Post]:
    run_input = {
        "profiles": handles,
        "resultsPerPage": results_limit,
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "excludePinnedPosts": True,
    }
    items = run_actor(ACTOR_ID, run_input, token)
    return parse_items(items)


def _parse_timestamp(item: dict) -> datetime | None:
    iso = item.get("createTimeISO")
    if isinstance(iso, str):
        try:
            return datetime.fromisoformat(iso.replace("Z", "+00:00"))
        except ValueError:
            pass
    unix = item.get("createTime")
    if isinstance(unix, (int, float)) and unix > 0:
        return datetime.fromtimestamp(unix, tz=timezone.utc)
    return None


def parse_items(items: list[dict]) -> list[Post]:
    posts: list[Post] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        # Private/deleted profiles arrive as error items in the dataset.
        if item.get("errorCode") or item.get("error"):
            log.warning(
                "tiktok: scraper error item for %r: %s",
                item.get("input") or item.get("authorMeta", {}).get("name"),
                item.get("errorCode") or item.get("error"),
            )
            continue
        post_id = item.get("id")
        author = item.get("authorMeta") or {}
        handle = author.get("name") if isinstance(author, dict) else None
        if not post_id or not handle:
            continue

        video_meta = item.get("videoMeta") or {}
        cover_url = video_meta.get("coverUrl") if isinstance(video_meta, dict) else None

        posts.append(
            Post(
                platform="tiktok",
                post_id=str(post_id),
                handle=str(handle).lower(),
                caption=str(item.get("text") or ""),
                timestamp=_parse_timestamp(item),
                image_url=cover_url,
                post_url=item.get("webVideoUrl"),
            )
        )
    return posts
