"""Download post images from IG/TikTok CDNs.

CDN URLs are signed and expire, and often reject non-browser clients — so we
download once ourselves and reuse the bytes for both the Claude vision call
and the Telegram upload.
"""

from __future__ import annotations

import logging

import httpx

log = logging.getLogger(__name__)

MAX_BYTES = int(4.5 * 1024 * 1024)  # stay under the Claude API's 5MB image limit

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "image/*,*/*;q=0.8",
}

_ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def download_image(url: str) -> tuple[bytes, str] | None:
    """Return (bytes, media_type), or None if the image can't be used."""
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=30, follow_redirects=True)
    except httpx.HTTPError as exc:
        log.warning("image download failed (%s): %s", exc.__class__.__name__, url[:120])
        return None
    if resp.status_code != 200:
        log.warning("image download returned HTTP %d: %s", resp.status_code, url[:120])
        return None

    data = resp.content
    if not data or len(data) > MAX_BYTES:
        log.warning("image skipped (size %d bytes): %s", len(data), url[:120])
        return None

    media_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if media_type not in _ALLOWED_MEDIA_TYPES:
        media_type = "image/jpeg"
    return data, media_type
