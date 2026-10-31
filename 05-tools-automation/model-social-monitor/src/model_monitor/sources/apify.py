"""Minimal Apify run-sync client."""

from __future__ import annotations

import logging

import httpx

log = logging.getLogger(__name__)

# Apify holds the sync connection for up to 300s; give httpx a little headroom.
_TIMEOUT_S = 360


class ApifyError(Exception):
    pass


def run_actor(actor_id: str, run_input: dict, token: str) -> list[dict]:
    """Run an actor synchronously and return its dataset items.

    actor_id uses the 'owner~name' form, e.g. 'apify~instagram-post-scraper'.
    Raises ApifyError on any failure (including the 408 sync timeout) so the
    caller can skip this platform for the current cycle.
    """
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    try:
        resp = httpx.post(
            url,
            params={"format": "json", "clean": "true"},
            headers={"Authorization": f"Bearer {token}"},
            json=run_input,
            timeout=_TIMEOUT_S,
        )
    except httpx.HTTPError as exc:
        raise ApifyError(f"network error calling {actor_id}: {exc}") from exc

    if resp.status_code == 408:
        raise ApifyError(f"{actor_id} timed out (sync 300s limit); will retry next cycle")
    if resp.status_code >= 400:
        raise ApifyError(f"{actor_id} returned HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        items = resp.json()
    except ValueError as exc:
        raise ApifyError(f"{actor_id} returned non-JSON output") from exc
    if not isinstance(items, list):
        raise ApifyError(f"{actor_id} returned unexpected output shape: {type(items).__name__}")

    log.debug("%s returned %d items", actor_id, len(items))
    return items
