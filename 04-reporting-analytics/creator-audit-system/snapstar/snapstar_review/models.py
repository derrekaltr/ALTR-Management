"""Data models shared across the capture -> review -> report pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class CaptureStatus(str, Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
    PRIVATE = "private"
    BOT_WALL = "bot_wall"
    ERROR = "error"


class Surface(str, Enum):
    PROFILE = "profile"
    STORY = "story"
    SPOTLIGHT = "spotlight"
    AVATAR = "avatar"
    BIO = "bio"
    DISPLAY_NAME = "display_name"
    USERNAME = "username"
    MANUAL = "manual"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CLEAN = "clean"


SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.CLEAN,
]


class Category(str, Enum):
    EXPLICIT_NUDITY = "explicit_nudity"
    IMPLIED_NUDITY = "implied_nudity"
    REVEALING_ATTIRE = "revealing_attire"
    SUGGESTIVE_POSE = "suggestive_pose"
    SUGGESTIVE_TEXT = "suggestive_text"
    ADULT_PLATFORM_REFERENCE = "adult_platform_reference"
    MONETIZATION_SOLICITATION = "monetization_solicitation"
    IDENTITY_INNUENDO = "identity_innuendo"
    THIRD_PARTY_WATERMARK = "third_party_watermark"
    OTHER = "other"


CATEGORY_LABELS: dict[Category, str] = {
    Category.EXPLICIT_NUDITY: "Explicit / nudity",
    Category.IMPLIED_NUDITY: "Implied nudity",
    Category.REVEALING_ATTIRE: "Revealing attire",
    Category.SUGGESTIVE_POSE: "Suggestive pose / framing",
    Category.SUGGESTIVE_TEXT: "Suggestive caption / emoji",
    Category.ADULT_PLATFORM_REFERENCE: "Adult platform reference",
    Category.MONETIZATION_SOLICITATION: "Paid-content solicitation",
    Category.IDENTITY_INNUENDO: "Name / bio innuendo",
    Category.THIRD_PARTY_WATERMARK: "Third-party watermark",
    Category.OTHER: "Other",
}


class CapturedImage(BaseModel):
    item_id: str
    path: str  # relative to the creator's capture dir
    surface: Surface
    label: str = ""


class Manifest(BaseModel):
    """What the capture stage found for one creator."""

    username: str
    creator_name: str = ""
    notes: str = ""
    url: str = ""
    status: CaptureStatus = CaptureStatus.ERROR
    status_detail: str = ""
    captured_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    display_name: str = ""
    bio: str = ""
    subscriber_count: str = ""
    images: list[CapturedImage] = Field(default_factory=list)


class ItemReview(BaseModel):
    """Claude's verdict on a single captured item (structured output schema)."""

    severity: Severity
    categories: list[Category] = Field(default_factory=list)
    rationale: str = ""
    removal_action: str = ""
    borderline: bool = False


class ReviewedItem(BaseModel):
    item_id: str
    surface: Surface
    label: str = ""
    image_path: str = ""  # empty for text-only items
    text_content: str = ""  # the text reviewed, for text items
    review: ItemReview


class CreatorReview(BaseModel):
    """Full review result for one creator; input to the report stage."""

    username: str
    creator_name: str = ""
    status: CaptureStatus = CaptureStatus.OK
    status_detail: str = ""
    captured_at: str = ""
    reviewed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    display_name: str = ""
    bio: str = ""
    subscriber_count: str = ""
    items: list[ReviewedItem] = Field(default_factory=list)

    def flagged_items(self) -> list[ReviewedItem]:
        flagged = [i for i in self.items if i.review.severity != Severity.CLEAN]
        return sorted(flagged, key=lambda i: SEVERITY_ORDER.index(i.review.severity))

    def severity_counts(self) -> dict[str, int]:
        counts = {s.value: 0 for s in SEVERITY_ORDER}
        for item in self.items:
            counts[item.review.severity.value] += 1
        return counts
