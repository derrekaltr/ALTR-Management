"""Send updates to Telegram channels via the Bot API."""

from __future__ import annotations

import logging
import time

import httpx

from .sources import PLATFORM_LABELS

log = logging.getLogger(__name__)

PHOTO_CAPTION_LIMIT = 1024
MESSAGE_LIMIT = 4096


class TelegramError(Exception):
    pass


def build_caption(model_name: str, platform: str, summary: str, post_url: str | None) -> str:
    platform_label = PLATFORM_LABELS.get(platform, platform)
    parts = [f"\U0001f195 {model_name} — {platform_label}", "", summary]
    if post_url:
        parts += ["", post_url]
    return "\n".join(parts)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _call(bot_token: str, method: str, *, data: dict, files: dict | None = None) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    for attempt in (1, 2):
        try:
            resp = httpx.post(url, data=data, files=files, timeout=60)
        except httpx.HTTPError as exc:
            raise TelegramError(f"{method}: network error: {exc}") from exc

        if resp.status_code == 200:
            return

        retry_after = None
        try:
            body = resp.json()
            retry_after = (body.get("parameters") or {}).get("retry_after")
            description = body.get("description", "")
        except ValueError:
            description = resp.text[:200]

        if resp.status_code == 429 and attempt == 1 and isinstance(retry_after, (int, float)):
            wait = min(float(retry_after), 60.0)
            log.warning("telegram rate limited; waiting %.0fs", wait)
            time.sleep(wait)
            continue

        raise TelegramError(f"{method}: HTTP {resp.status_code}: {description}")


def send_photo(bot_token: str, chat_id: int, caption: str, image: tuple[bytes, str]) -> None:
    data, media_type = image
    ext = media_type.split("/")[-1]
    _call(
        bot_token,
        "sendPhoto",
        data={"chat_id": str(chat_id), "caption": truncate(caption, PHOTO_CAPTION_LIMIT)},
        files={"photo": (f"post.{ext}", data, media_type)},
    )


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    _call(
        bot_token,
        "sendMessage",
        data={"chat_id": str(chat_id), "text": truncate(text, MESSAGE_LIMIT)},
    )


def send_update(
    bot_token: str,
    chat_id: int,
    caption: str,
    image: tuple[bytes, str] | None,
) -> None:
    """Send with the photo when we have one; fall back to text if the upload is rejected."""
    if image is not None:
        try:
            send_photo(bot_token, chat_id, caption, image)
            return
        except TelegramError as exc:
            log.warning("sendPhoto failed (%s); falling back to text message", exc)
    send_message(bot_token, chat_id, caption)
