"""Instagram feed posts via the apify~instagram-post-scraper actor."""

from __future__ import annotations

import logging
from datetime import datetime

from . import Post
from .apify import run_actor

log = logging.getLogger(__name__)

ACTOR_ID = "apify~instagram-post-scraper"


def fetch_posts(handles: list[str], results_limit: int, token: str) -> list[Post]:
    run_input = {
        "username": handles,
        "resultsLimit": results_limit,
        "skipPinnedPosts": True,
    }
    items = run_actor(ACTOR_ID, run_input, token)
    return parse_items(items)


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_items(items: list[dict]) -> list[Post]:
    posts: list[Post] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("errorCode") or item.get("error"):
            log.warning(
                "instagram: scraper error item for %r: %s",
                item.get("username") or item.get("inputUrl"),
                item.get("errorCode") or item.get("error"),
            )
            continue
        post_id = item.get("id") or item.get("shortCode")
        handle = item.get("ownerUsername")
        if not post_id or not handle:
            continue

        image_url = item.get("displayUrl")
        images = item.get("images")
        if not image_url and isinstance(images, list) and images:
            first = images[0]
            image_url = first if isinstance(first, str) else None

        url = item.get("url")
        if not url and item.get("shortCode"):
            url = f"https://www.instagram.com/p/{item['shortCode']}/"

        posts.append(
            Post(
                platform="instagram",
                post_id=str(post_id),
                handle=str(handle).lower(),
                caption=str(item.get("caption") or ""),
                timestamp=_parse_timestamp(item.get("timestamp")),
                image_url=image_url,
                post_url=url,
            )
        )
    return posts
