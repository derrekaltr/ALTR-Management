"""Automated capture of public Snapchat web profiles with Playwright.

Snapchat exposes public profiles at https://www.snapchat.com/@{username}
(bio, avatar, public Stories, Spotlight, Lenses). We drive a real Chromium
browser, save a full-profile screenshot plus individual story/Spotlight tile
screenshots, and record everything in a per-creator manifest.json.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout, sync_playwright

from .models import CapturedImage, CaptureStatus, Manifest, Surface

PROFILE_URL = "https://www.snapchat.com/@{username}"
FALLBACK_URL = "https://www.snapchat.com/add/{username}"

# selectors are best-effort: Snapchat's markup changes, so every extraction
# is wrapped in try/except and missing pieces simply stay blank
TILE_SELECTORS = [
    'a[href*="/spotlight/"]',
    'a[href*="/story/"]',
    '[class*="StoryCard"]',
    '[class*="SpotlightTile"]',
]

NOT_FOUND_MARKERS = ["couldn't find", "page not found", "oops!"]
BOT_WALL_MARKERS = ["unusual traffic", "verify you are human", "captcha", "access denied"]


def read_roster(path: str | Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    roster = []
    for row in rows:
        username = (row.get("snap_username") or "").strip().lstrip("@")
        if not username:
            continue
        roster.append(
            {
                "snap_username": username,
                "creator_name": (row.get("creator_name") or username).strip(),
                "notes": (row.get("notes") or "").strip(),
            }
        )
    return roster


def _meta(page: Page, name: str) -> str:
    try:
        el = page.query_selector(f'meta[property="{name}"], meta[name="{name}"]')
        return (el.get_attribute("content") or "").strip() if el else ""
    except Exception:
        return ""


def _first_text(page: Page, selectors: list[str]) -> str:
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                text = (el.inner_text() or "").strip()
                if text:
                    return text
        except Exception:
            continue
    return ""


def _classify_page(page: Page, http_status: int) -> tuple[CaptureStatus, str]:
    if http_status == 404:
        return CaptureStatus.NOT_FOUND, "Profile URL returned 404"
    try:
        body = (page.inner_text("body") or "").lower()[:5000]
    except Exception:
        body = ""
    for marker in BOT_WALL_MARKERS:
        if marker in body:
            return CaptureStatus.BOT_WALL, f"Bot wall detected ({marker!r})"
    for marker in NOT_FOUND_MARKERS:
        if marker in body:
            return CaptureStatus.NOT_FOUND, "Profile not found on page"
    if http_status >= 400:
        return CaptureStatus.ERROR, f"HTTP {http_status}"
    return CaptureStatus.OK, ""


def _capture_tiles(page: Page, out_dir: Path, max_tiles: int) -> list[CapturedImage]:
    images: list[CapturedImage] = []
    seen_boxes: set[tuple[int, int]] = set()
    index = 0
    for selector in TILE_SELECTORS:
        try:
            elements = page.query_selector_all(selector)
        except Exception:
            continue
        for el in elements:
            if index >= max_tiles:
                return images
            try:
                box = el.bounding_box()
                if not box or box["width"] < 60 or box["height"] < 60:
                    continue
                key = (int(box["x"]), int(box["y"]))
                if key in seen_boxes:
                    continue
                seen_boxes.add(key)
                href = (el.get_attribute("href") or "") if el.get_attribute("href") is not None else ""
                surface = Surface.SPOTLIGHT if "/spotlight/" in href else Surface.STORY
                filename = f"tile_{index:02d}.jpg"
                el.screenshot(path=str(out_dir / filename), type="jpeg", quality=80)
                images.append(
                    CapturedImage(
                        item_id=f"tile_{index:02d}",
                        path=filename,
                        surface=surface,
                        label=f"{surface.value.title()} post #{index + 1}"
                        + (f" ({href})" if href else ""),
                    )
                )
                index += 1
            except Exception:
                continue
    return images


def capture_profile(page: Page, creator: dict[str, str], out_dir: Path, cfg: dict[str, Any]) -> Manifest:
    username = creator["snap_username"]
    manifest = Manifest(
        username=username,
        creator_name=creator.get("creator_name", username),
        notes=creator.get("notes", ""),
        url=PROFILE_URL.format(username=username),
    )
    timeout_ms = int(cfg["timeout_seconds"]) * 1000

    http_status = 0
    try:
        response = page.goto(manifest.url, timeout=timeout_ms, wait_until="domcontentloaded")
        http_status = response.status if response else 0
        page.wait_for_timeout(3000)  # let client-side content settle
    except PlaywrightTimeout:
        manifest.status = CaptureStatus.ERROR
        manifest.status_detail = "Navigation timed out"
        return manifest

    status, detail = _classify_page(page, http_status)
    if status == CaptureStatus.NOT_FOUND:
        # some usernames resolve on /add/ but not /@
        try:
            response = page.goto(
                FALLBACK_URL.format(username=username),
                timeout=timeout_ms,
                wait_until="domcontentloaded",
            )
            page.wait_for_timeout(2000)
            status, detail = _classify_page(page, response.status if response else 0)
            if status == CaptureStatus.OK:
                manifest.url = FALLBACK_URL.format(username=username)
        except Exception:
            pass
    manifest.status = status
    manifest.status_detail = detail
    if status != CaptureStatus.OK:
        try:  # keep evidence of whatever we hit
            page.screenshot(path=str(out_dir / "page.jpg"), type="jpeg", quality=70)
        except Exception:
            pass
        return manifest

    manifest.display_name = _first_text(page, ["h1", '[class*="DisplayName"]']) or _meta(
        page, "og:title"
    )
    manifest.bio = _meta(page, "og:description") or _first_text(
        page, ['[class*="Bio"]', '[class*="bio"]']
    )
    manifest.subscriber_count = _first_text(
        page, ['[class*="Subscriber"]', '[class*="subscriber"]']
    )

    try:
        page.screenshot(
            path=str(out_dir / "profile_full.jpg"), full_page=True, type="jpeg", quality=80
        )
        manifest.images.append(
            CapturedImage(
                item_id="profile_full",
                path="profile_full.jpg",
                surface=Surface.PROFILE,
                label="Full public profile page",
            )
        )
    except Exception as exc:
        manifest.status_detail = f"Profile screenshot failed: {exc}"

    manifest.images.extend(_capture_tiles(page, out_dir, int(cfg["max_tiles"])))
    return manifest


def _collect_manual(out_dir: Path, manifest: Manifest) -> None:
    """Pick up extra screenshots the team dropped into captures/<user>/manual/."""
    manual_dir = out_dir / "manual"
    if not manual_dir.is_dir():
        return
    for i, file in enumerate(sorted(manual_dir.iterdir())):
        if file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            manifest.images.append(
                CapturedImage(
                    item_id=f"manual_{i:02d}",
                    path=f"manual/{file.name}",
                    surface=Surface.MANUAL,
                    label=f"Team-provided screenshot: {file.name}",
                )
            )


def run_capture(roster_path: str | Path, output_dir: str | Path, cfg: dict[str, Any]) -> list[Manifest]:
    roster = read_roster(roster_path)
    if not roster:
        raise SystemExit(f"No creators found in roster {roster_path}")
    return capture_creators(roster, output_dir, cfg)


def capture_creators(
    roster: list[dict[str, str]], output_dir: str | Path, cfg: dict[str, Any]
) -> list[Manifest]:
    captures_dir = Path(output_dir) / "captures"
    capture_cfg = cfg["capture"]
    manifests: list[Manifest] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=bool(capture_cfg["headless"]))
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        for i, creator in enumerate(roster):
            username = creator["snap_username"]
            out_dir = captures_dir / username
            out_dir.mkdir(parents=True, exist_ok=True)
            print(f"[capture] @{username} ...", flush=True)
            manifest = capture_profile(page, creator, out_dir, capture_cfg)
            if manifest.status == CaptureStatus.BOT_WALL:
                print(f"[capture] @{username}: bot wall — retrying once", flush=True)
                time.sleep(max(10, int(capture_cfg["delay_seconds"])))
                manifest = capture_profile(page, creator, out_dir, capture_cfg)
            _collect_manual(out_dir, manifest)
            (out_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2))
            print(
                f"[capture] @{username}: {manifest.status.value}"
                f" ({len(manifest.images)} images)",
                flush=True,
            )
            manifests.append(manifest)
            if i < len(roster) - 1:
                time.sleep(int(capture_cfg["delay_seconds"]))
        browser.close()
    return manifests


def load_manifests(output_dir: str | Path) -> list[Manifest]:
    captures_dir = Path(output_dir) / "captures"
    manifests = []
    if captures_dir.is_dir():
        for manifest_path in sorted(captures_dir.glob("*/manifest.json")):
            manifests.append(Manifest(**json.loads(manifest_path.read_text())))
    return manifests
