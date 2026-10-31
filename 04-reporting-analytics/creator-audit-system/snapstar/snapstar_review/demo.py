"""Demo mode: fabricate captures + reviews so the PDF pipeline can be exercised
end-to-end without touching Snapchat or the Claude API.

Placeholder images are generated with a tiny pure-Python PNG writer (no Pillow
dependency) — soft vertical gradients standing in for screenshots.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from .models import (
    CapturedImage,
    CaptureStatus,
    Category,
    CreatorReview,
    ItemReview,
    Manifest,
    ReviewedItem,
    Severity,
    Surface,
)


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_placeholder_png(
    path: Path, width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]
) -> None:
    """Write a vertical-gradient PNG without any imaging dependency."""
    rows = bytearray()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        rows.append(0)  # no filter
        rows.extend(bytes((r, g, b)) * width)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(rows), 6))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def _demo_creator_one(captures_dir: Path) -> tuple[Manifest, CreatorReview]:
    """A creator with cleanup to do."""
    username = "demo.creator"
    out = captures_dir / username
    out.mkdir(parents=True, exist_ok=True)
    write_placeholder_png(out / "profile_full.png", 640, 900, (24, 24, 24), (70, 60, 45))
    write_placeholder_png(out / "tile_00.png", 480, 640, (140, 60, 80), (40, 20, 30))
    write_placeholder_png(out / "tile_01.png", 480, 640, (60, 90, 140), (20, 30, 50))
    write_placeholder_png(out / "tile_02.png", 480, 640, (200, 170, 120), (90, 70, 40))

    manifest = Manifest(
        username=username,
        creator_name="Demo Creator",
        url=f"https://www.snapchat.com/@{username}",
        status=CaptureStatus.OK,
        display_name="Demo 🔥 Creator",
        bio="your favorite bad influence 😈 | 18+ links below ⬇️ | vip list open",
        images=[
            CapturedImage(item_id="profile_full", path="profile_full.png", surface=Surface.PROFILE, label="Full public profile page"),
            CapturedImage(item_id="tile_00", path="tile_00.png", surface=Surface.SPOTLIGHT, label="Spotlight post #1"),
            CapturedImage(item_id="tile_01", path="tile_01.png", surface=Surface.STORY, label="Story post #2"),
            CapturedImage(item_id="tile_02", path="tile_02.png", surface=Surface.SPOTLIGHT, label="Spotlight post #3"),
        ],
    )

    review = CreatorReview(
        username=username,
        creator_name="Demo Creator",
        status=CaptureStatus.OK,
        captured_at=manifest.captured_at,
        display_name=manifest.display_name,
        bio=manifest.bio,
        items=[
            ReviewedItem(
                item_id="bio", surface=Surface.BIO, label="Bio",
                text_content=manifest.bio,
                review=ItemReview(
                    severity=Severity.CRITICAL,
                    categories=[Category.ADULT_PLATFORM_REFERENCE, Category.SUGGESTIVE_TEXT, Category.MONETIZATION_SOLICITATION],
                    rationale="The bio combines '18+ links below', a devil emoji, and a 'vip list' upsell — a verification reviewer will read this as adult-content promotion at a glance.",
                    removal_action="Edit your bio: Profile -> Edit Profile -> Bio. Remove '18+ links below ⬇️' and 'vip list open'; keep it to a neutral tagline (e.g. lifestyle, travel, fitness).",
                ),
            ),
            ReviewedItem(
                item_id="display_name", surface=Surface.DISPLAY_NAME, label="Display Name",
                text_content=manifest.display_name,
                review=ItemReview(
                    severity=Severity.LOW, borderline=True,
                    categories=[Category.IDENTITY_INNUENDO],
                    rationale="The 🔥 in the display name is mild on its own, but combined with the current bio it reinforces a 'spicy content' signal.",
                    removal_action="Edit your display name: Profile -> Edit Profile -> Name. Consider dropping the 🔥 until verification is granted.",
                ),
            ),
            ReviewedItem(
                item_id="tile_00", surface=Surface.SPOTLIGHT, label="Spotlight post #1",
                image_path="tile_00.png",
                review=ItemReview(
                    severity=Severity.HIGH,
                    categories=[Category.REVEALING_ATTIRE, Category.SUGGESTIVE_POSE],
                    rationale="Lingerie-adjacent styling with body-emphasizing framing. Not explicit, but well past what Snapchat allows on a public profile seeking verification.",
                    removal_action="Delete this Spotlight post: Profile -> Spotlight tab -> open the post -> ⋯ -> Delete.",
                ),
            ),
            ReviewedItem(
                item_id="tile_01", surface=Surface.STORY, label="Story post #2",
                image_path="tile_01.png",
                review=ItemReview(
                    severity=Severity.MEDIUM, borderline=True,
                    categories=[Category.SUGGESTIVE_TEXT],
                    rationale="The outfit is fine but the caption's emoji cluster (🍑💦) reads as innuendo. Reviewers scan captions as closely as imagery.",
                    removal_action="Delete this Story snap: Profile -> My Story -> open the snap -> ⋯ -> Delete Snap. Repost without the caption if you want to keep the clip.",
                ),
            ),
            ReviewedItem(
                item_id="tile_02", surface=Surface.SPOTLIGHT, label="Spotlight post #3",
                image_path="tile_02.png",
                review=ItemReview(
                    severity=Severity.CLEAN,
                    rationale="Everyday fashion content with no suggestive framing — exactly the kind of post that supports a verification application.",
                ),
            ),
            ReviewedItem(
                item_id="profile_full", surface=Surface.PROFILE, label="Full public profile page",
                image_path="profile_full.png",
                review=ItemReview(
                    severity=Severity.LOW,
                    categories=[Category.THIRD_PARTY_WATERMARK],
                    rationale="One visible repost carries a TikTok watermark; Snapchat deprioritizes watermarked content and it looks unpolished to a reviewer.",
                    removal_action="Delete the watermarked repost and re-upload the original clip without the watermark.",
                ),
            ),
        ],
    )
    return manifest, review


def _demo_creator_two(captures_dir: Path) -> tuple[Manifest, CreatorReview]:
    """A creator who is nearly ready."""
    username = "demo.model"
    out = captures_dir / username
    out.mkdir(parents=True, exist_ok=True)
    write_placeholder_png(out / "profile_full.png", 640, 900, (18, 18, 18), (45, 55, 70))
    write_placeholder_png(out / "tile_00.png", 480, 640, (90, 130, 110), (30, 50, 40))

    manifest = Manifest(
        username=username,
        creator_name="Demo Model",
        url=f"https://www.snapchat.com/@{username}",
        status=CaptureStatus.OK,
        display_name="Demo Model",
        bio="travel • fitness • daily vlogs",
        images=[
            CapturedImage(item_id="profile_full", path="profile_full.png", surface=Surface.PROFILE, label="Full public profile page"),
            CapturedImage(item_id="tile_00", path="tile_00.png", surface=Surface.SPOTLIGHT, label="Spotlight post #1"),
        ],
    )
    review = CreatorReview(
        username=username,
        creator_name="Demo Model",
        status=CaptureStatus.OK,
        captured_at=manifest.captured_at,
        display_name=manifest.display_name,
        bio=manifest.bio,
        items=[
            ReviewedItem(
                item_id="bio", surface=Surface.BIO, label="Bio", text_content=manifest.bio,
                review=ItemReview(severity=Severity.CLEAN, rationale="Neutral lifestyle bio with no risk signals."),
            ),
            ReviewedItem(
                item_id="tile_00", surface=Surface.SPOTLIGHT, label="Spotlight post #1",
                image_path="tile_00.png",
                review=ItemReview(
                    severity=Severity.MEDIUM, borderline=True,
                    categories=[Category.REVEALING_ATTIRE],
                    rationale="Swimwear content framed to emphasize the body. A beach vlog context would pass; this framing is a judgment call a cautious applicant should remove.",
                    removal_action="Delete this Spotlight post: Profile -> Spotlight tab -> open the post -> ⋯ -> Delete.",
                ),
            ),
            ReviewedItem(
                item_id="profile_full", surface=Surface.PROFILE, label="Full public profile page",
                image_path="profile_full.png",
                review=ItemReview(severity=Severity.CLEAN, rationale="Overall profile impression is brand-safe and consistent."),
            ),
        ],
    )
    return manifest, review


def build_demo_data(output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    captures_dir = output_dir / "captures"
    reviews_dir = output_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    for manifest, review in (
        _demo_creator_one(captures_dir),
        _demo_creator_two(captures_dir),
    ):
        (captures_dir / manifest.username / "manifest.json").write_text(
            manifest.model_dump_json(indent=2)
        )
        (reviews_dir / f"{review.username}.json").write_text(
            review.model_dump_json(indent=2)
        )
    print(f"[demo] fabricated captures + reviews under {output_dir}/", flush=True)
