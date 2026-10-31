"""Claude vision review of captured content against the verification rubric."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import anthropic

from .capture import load_manifests
from .models import (
    CaptureStatus,
    CreatorReview,
    ItemReview,
    Manifest,
    ReviewedItem,
    Severity,
    Surface,
)
from .rubric import IMAGE_REVIEW_SYSTEM, TEXT_REVIEW_SYSTEM

MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
MAX_IMAGE_BYTES = 4_500_000  # API limit is 5MB per image; leave headroom


def _image_block(path: Path) -> dict[str, Any] | None:
    media_type = MEDIA_TYPES.get(path.suffix.lower())
    if not media_type or not path.is_file() or path.stat().st_size > MAX_IMAGE_BYTES:
        return None
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": media_type, "data": data},
    }


def _review_call(
    client: anthropic.Anthropic,
    model: str,
    system: str,
    content: list[dict[str, Any]],
) -> ItemReview:
    response = client.messages.parse(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_format=ItemReview,
    )
    return response.parsed_output


def _review_image_item(
    client: anthropic.Anthropic, model: str, manifest: Manifest, image, base_dir: Path
) -> ReviewedItem | None:
    block = _image_block(base_dir / image.path)
    if block is None:
        return ReviewedItem(
            item_id=image.item_id,
            surface=image.surface,
            label=image.label,
            image_path=image.path,
            review=ItemReview(
                severity=Severity.LOW,
                rationale="Image could not be reviewed automatically (unsupported "
                "format or too large). Check it manually before applying.",
                removal_action="Review this item manually in the Snapchat app.",
                borderline=True,
            ),
        )
    prompt = (
        f"Creator: {manifest.creator_name} (@{manifest.username}).\n"
        f"Item: {image.label or image.item_id} — surface: {image.surface.value}.\n"
        "Review this image against the rubric and return your structured verdict."
    )
    review = _review_call(
        client, model, IMAGE_REVIEW_SYSTEM, [block, {"type": "text", "text": prompt}]
    )
    return ReviewedItem(
        item_id=image.item_id,
        surface=image.surface,
        label=image.label,
        image_path=image.path,
        review=review,
    )


def _text_items(manifest: Manifest) -> list[tuple[str, Surface, str]]:
    items = [("username", Surface.USERNAME, f"@{manifest.username}")]
    if manifest.display_name:
        items.append(("display_name", Surface.DISPLAY_NAME, manifest.display_name))
    if manifest.bio:
        items.append(("bio", Surface.BIO, manifest.bio))
    return items


def review_creator(
    client: anthropic.Anthropic, manifest: Manifest, base_dir: Path, model: str
) -> CreatorReview:
    result = CreatorReview(
        username=manifest.username,
        creator_name=manifest.creator_name,
        status=manifest.status,
        status_detail=manifest.status_detail,
        captured_at=manifest.captured_at,
        display_name=manifest.display_name,
        bio=manifest.bio,
        subscriber_count=manifest.subscriber_count,
    )
    if manifest.status != CaptureStatus.OK:
        return result

    for item_id, surface, text in _text_items(manifest):
        prompt = (
            f"Creator: {manifest.creator_name} (@{manifest.username}).\n"
            f"Field: {surface.value}.\n"
            f"Content:\n{text}\n\n"
            "Review this text field against the rubric and return your structured verdict."
        )
        review = _review_call(
            client, model, TEXT_REVIEW_SYSTEM, [{"type": "text", "text": prompt}]
        )
        result.items.append(
            ReviewedItem(
                item_id=item_id,
                surface=surface,
                label=surface.value.replace("_", " ").title(),
                text_content=text,
                review=review,
            )
        )

    for image in manifest.images:
        print(f"[review]   @{manifest.username} / {image.item_id}", flush=True)
        reviewed = _review_image_item(client, model, manifest, image, base_dir)
        if reviewed:
            result.items.append(reviewed)
    return result


def run_review(
    output_dir: str | Path,
    cfg: dict[str, Any],
    only: list[str] | None = None,
    force: bool = False,
) -> list[CreatorReview]:
    """Review captured creators. Already-reviewed creators are skipped unless
    `force` (so one-at-a-time runs never re-spend on prior audits); `only`
    restricts the run to specific usernames."""
    manifests = load_manifests(output_dir)
    if only:
        wanted = {u.lstrip("@").lower() for u in only}
        manifests = [m for m in manifests if m.username.lower() in wanted]
    if not manifests:
        raise SystemExit(
            f"No captures found under {output_dir}/captures — run `snapstar capture` first."
        )
    client = anthropic.Anthropic()
    model = cfg["model"]
    reviews_dir = Path(output_dir) / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    reviews = []
    for manifest in manifests:
        if not force and (reviews_dir / f"{manifest.username}.json").exists():
            print(f"[review] @{manifest.username}: already reviewed — skipping "
                  "(use --force to redo)", flush=True)
            continue
        print(f"[review] @{manifest.username} ({len(manifest.images)} images)", flush=True)
        base_dir = Path(output_dir) / "captures" / manifest.username
        review = review_creator(client, manifest, base_dir, model)
        (reviews_dir / f"{manifest.username}.json").write_text(
            review.model_dump_json(indent=2)
        )
        reviews.append(review)
    return reviews


def load_reviews(output_dir: str | Path) -> list[CreatorReview]:
    reviews_dir = Path(output_dir) / "reviews"
    reviews = []
    if reviews_dir.is_dir():
        for path in sorted(reviews_dir.glob("*.json")):
            reviews.append(CreatorReview.model_validate_json(path.read_text()))
    return reviews
