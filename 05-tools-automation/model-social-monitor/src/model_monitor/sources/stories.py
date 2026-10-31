"""Instagram Stories via the dami_studio~instagram-stories-scraper actor.

Notes on this actor (verified Sept 2026):
- Pay per row (~$2.50/1k), no Instagram login/cookies needed.
- Max 5 profiles per run, so we chunk.
- Profiles with no active stories / private profiles produce unbilled
  diagnostic rows (NO_CURRENT_STORIES, PRIVATE_OR_RESTRICTED, NOT_FOUND)
  instead of failing the run.
- Active stories are returned on every run until they expire (~24h), so the
  same story is re-billed each poll — hence the separate, longer stories
  polling interval in config.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from . import Post
from .apify import run_actor

log = logging.getLogger(__name__)

ACTOR_ID = "dami_studio~instagram-stories-scraper"
_MAX_PROFILES_PER_RUN = 5


def fetch_posts(handles: list[str], results_limit: int, token: str) -> list[Post]:
    posts: list[Post] = []
    for i in range(0, len(handles), _MAX_PROFILES_PER_RUN):
        chunk = handles[i : i + _MAX_PROFILES_PER_RUN]
        run_input = {
            "profiles": chunk,
            "maxStoriesPerProfile": results_limit,
            "includeHighlights": False,
        }
        items = run_actor(ACTOR_ID, run_input, token)
        posts.extend(parse_items(items))
    return posts


def _parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, (int, float)) and value > 0:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None


def parse_items(items: list[dict]) -> list[Post]:
    posts: list[Post] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        story_id = item.get("storyId")
        handle = item.get("sourceUsername")
        if not story_id or not handle:
            # Diagnostic rows (NO_CURRENT_STORIES etc.) land here.
            diag = (
                item.get("diagnostic") or item.get("status")
                or item.get("errorCode") or item.get("error")
            )
            if diag:
                who = (
                    item.get("profile") or item.get("username")
                    or item.get("profileUsername") or item.get("requestedProfile")
                    or item.get("handle") or item.get("input") or "unknown account"
                )
                log.info("stories: %s for %r", diag, who)
            continue

        record_type = item.get("recordType")
        if record_type and record_type != "story":
            continue  # highlights, if the actor returns them anyway
        if item.get("isSponsored"):
            log.info("stories/@%s: skipping sponsored story %s", handle, story_id)
            continue

        handle = str(handle).lower()
        posts.append(
            Post(
                platform="instagram_story",
                post_id=str(story_id),
                handle=handle,
                caption=str(item.get("caption") or ""),
                timestamp=_parse_timestamp(item.get("takenAt")),
                image_url=item.get("imageUrl"),
                post_url=f"https://www.instagram.com/stories/{handle}/{story_id}/",
            )
        )
    return posts
