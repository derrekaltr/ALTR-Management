"""Post sources (Apify scrapers) and the shared Post shape."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

PLATFORM_LABELS = {
    "instagram": "Instagram",
    "instagram_story": "Instagram Story",
    "tiktok": "TikTok",
}


@dataclass
class Post:
    platform: str  # 'instagram' | 'instagram_story' | 'tiktok'
    post_id: str
    handle: str  # lowercased account username, used to route to a model
    caption: str
    timestamp: datetime | None
    image_url: str | None
    post_url: str | None
