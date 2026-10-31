"""One check cycle: fetch -> dedupe -> analyze (relevance gate) -> send -> mark.

Error isolation rings:
  1. per-platform  — an Instagram batch failure never blocks TikTok or Stories
  2. per-post      — one post failing (image/Claude/Telegram) never blocks the rest
  3. per-item      — scraper error items and malformed items are skipped in the parsers
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import anthropic

from . import analyze, images, notify
from .config import AppConfig, ModelConfig
from .sources import Post, instagram, stories, tiktok
from .sources.apify import ApifyError
from .state import StateStore

log = logging.getLogger(__name__)

# Ignore posts older than this even if unseen — guards against a scraper
# suddenly returning deep history and flooding the channels.
MAX_POST_AGE = timedelta(hours=48)

_FETCHERS = {
    "instagram": instagram.fetch_posts,
    "instagram_story": stories.fetch_posts,
    "tiktok": tiktok.fetch_posts,
}

_LAST_STORY_FETCH_KEY = "last_story_fetch"


@dataclass
class CycleSummary:
    platforms_checked: int = 0
    platforms_failed: int = 0
    accounts_seeded: int = 0
    posts_sent: int = 0
    posts_skipped: int = 0
    posts_failed: int = 0
    failures: list[str] = field(default_factory=list)

    @property
    def all_platforms_failed(self) -> bool:
        return self.platforms_checked > 0 and self.platforms_failed == self.platforms_checked

    def one_liner(self) -> str:
        return (
            f"platforms ok {self.platforms_checked - self.platforms_failed}/"
            f"{self.platforms_checked}, accounts seeded {self.accounts_seeded}, "
            f"posts sent {self.posts_sent}, skipped as irrelevant {self.posts_skipped}, "
            f"failed {self.posts_failed}"
        )


def _select_models(config: AppConfig, only_model: str | None) -> list[ModelConfig]:
    if not only_model:
        return config.models
    matches = [m for m in config.models if m.name.lower() == only_model.lower()]
    if not matches:
        known = ", ".join(m.name for m in config.models)
        raise SystemExit(f"No model named '{only_model}' in models.yaml (known: {known})")
    return matches


def _stories_due(store: StateStore, config: AppConfig, now: datetime) -> bool:
    """Stories are billed on every fetch while active, so poll them less often."""
    last = store.get_meta(_LAST_STORY_FETCH_KEY)
    if last is None:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return True
    return now - last_dt >= timedelta(minutes=config.stories_min_interval_minutes)


def _fetch_platform(platform: str, handles: list[str], config: AppConfig) -> list[Post] | None:
    """Returns parsed posts, or None if the whole platform batch failed."""
    try:
        posts = _FETCHERS[platform](handles, config.results_limit, config.apify_token)
        log.info("%s: fetched %d posts for %d account(s)", platform, len(posts), len(handles))
        return posts
    except ApifyError as exc:
        log.error("%s: fetch failed: %s", platform, exc)
        return None


def _process_post(
    post: Post,
    model: ModelConfig,
    config: AppConfig,
    client: anthropic.Anthropic,
    store: StateStore,
    dry_run: bool,
) -> tuple[str, str | None]:
    """Analyze and deliver one post. Returns ('sent'|'skipped', summary); raises on failure."""
    image = images.download_image(post.image_url) if post.image_url else None
    if image is None and not post.caption.strip():
        # Nothing to analyze (e.g. a story whose media couldn't be fetched).
        log.info("%s/@%s: post %s has no usable image or caption; skipping",
                 post.platform, post.handle, post.post_id)
        return "skipped", None

    summary = analyze.summarize_post(
        client, model.name, post, image,
        recent_updates=store.recent_summaries(model.name),
    )
    if summary is None:
        log.info("%s/@%s: post %s judged not relevant or duplicate; skipping",
                 post.platform, post.handle, post.post_id)
        return "skipped", None

    caption = notify.build_caption(model.name, post.platform, summary, post.post_url)
    if dry_run:
        print(f"\n--- DRY RUN: would send to chat {model.telegram_chat_id} ---")
        print(caption)
        print("--- end ---\n")
        return "sent", summary
    notify.send_update(config.telegram_bot_token, model.telegram_chat_id, caption, image)
    return "sent", summary


def run_cycle(
    config: AppConfig,
    store: StateStore,
    *,
    force: bool = False,
    dry_run: bool = False,
    seed_only: bool = False,
    only_model: str | None = None,
) -> CycleSummary:
    summary = CycleSummary()
    models = _select_models(config, only_model)
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    now = datetime.now(timezone.utc)

    ig_handles = {m.instagram.lower(): m for m in models if m.instagram}
    handle_maps: dict[str, dict[str, ModelConfig]] = {
        "instagram": ig_handles,
        "tiktok": {m.tiktok.lower(): m for m in models if m.tiktok},
    }
    if config.include_stories and ig_handles:
        if force or seed_only or _stories_due(store, config, now):
            handle_maps["instagram_story"] = ig_handles
        else:
            log.info("instagram_story: not due yet (interval %d min); skipping this cycle",
                     config.stories_min_interval_minutes)

    for platform, handle_map in handle_maps.items():
        if not handle_map:
            continue
        summary.platforms_checked += 1

        posts = _fetch_platform(platform, list(handle_map), config)
        if posts is None:
            summary.platforms_failed += 1
            continue
        if platform == "instagram_story" and not dry_run:
            store.set_meta(_LAST_STORY_FETCH_KEY, now.isoformat())

        posts_by_handle: dict[str, list[Post]] = {h: [] for h in handle_map}
        for post in posts:
            if post.handle in posts_by_handle:
                posts_by_handle[post.handle].append(post)
            else:
                log.debug("%s: ignoring post from unconfigured account %r", platform, post.handle)

        for handle, model in handle_map.items():
            account_posts = sorted(
                posts_by_handle[handle],
                key=lambda p: p.timestamp or datetime.min.replace(tzinfo=timezone.utc),
            )
            if not account_posts:
                log.info("%s/@%s: no posts returned", platform, handle)
                continue

            # First sight of an account (or an explicit seed run): record
            # everything silently so we never spam a channel with history.
            if seed_only or (not force and not store.is_account_seeded(platform, handle)):
                if not dry_run:
                    for post in account_posts:
                        store.record_seeded(platform, post.post_id, model.name)
                    store.seed_account(platform, handle)
                summary.accounts_seeded += 1
                log.info(
                    "%s/@%s: %sseeded %d post(s) silently for %s",
                    platform, handle,
                    "would have " if dry_run else "",
                    len(account_posts), model.name,
                )
                continue

            if force:
                account_posts = account_posts[-1:]  # latest post only

            for post in account_posts:
                if not force:
                    if post.timestamp and now - post.timestamp > MAX_POST_AGE:
                        store.record_seeded(platform, post.post_id, model.name)
                        continue
                    if not store.should_process(platform, post.post_id):
                        continue

                try:
                    outcome, sent_summary = _process_post(
                        post, model, config, client, store, dry_run
                    )
                except Exception as exc:  # ring 2: never let one post kill the cycle
                    summary.posts_failed += 1
                    summary.failures.append(f"{platform}/@{handle} post {post.post_id}: {exc}")
                    log.error("%s/@%s: post %s failed: %s", platform, handle, post.post_id, exc)
                    if not dry_run:
                        attempts = store.record_failure(platform, post.post_id, model.name)
                        log.info("post %s attempt %d recorded", post.post_id, attempts)
                    continue

                if outcome == "skipped":
                    summary.posts_skipped += 1
                    if not dry_run:
                        store.record_skipped(platform, post.post_id, model.name)
                    continue

                summary.posts_sent += 1
                log.info(
                    "%s/@%s: %s update for %s (post %s)",
                    platform, handle,
                    "printed" if dry_run else "sent",
                    model.name, post.post_id,
                )
                if not dry_run:
                    store.mark_sent(platform, post.post_id, model.name, sent_summary)

    return summary


def send_test_messages(config: AppConfig, only_model: str | None = None) -> int:
    """Post a connectivity test to every configured channel. Returns failure count."""
    failures = 0
    for model in _select_models(config, only_model):
        try:
            notify.send_message(
                config.telegram_bot_token,
                model.telegram_chat_id,
                f"✅ Monitor connected — this is the update channel for {model.name}.",
            )
            print(f"OK    {model.name} (chat {model.telegram_chat_id})")
        except notify.TelegramError as exc:
            failures += 1
            print(f"FAIL  {model.name} (chat {model.telegram_chat_id}): {exc}")
    return failures
