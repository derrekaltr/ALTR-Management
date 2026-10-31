"""Load and validate .env + config/models.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is missing or invalid, with a human-readable message."""


@dataclass
class ModelConfig:
    name: str
    telegram_chat_id: int
    instagram: str | None = None
    tiktok: str | None = None

    @property
    def first_name(self) -> str:
        return self.name.split()[0]


@dataclass
class AppConfig:
    models: list[ModelConfig]
    results_limit: int
    include_stories: bool
    stories_min_interval_minutes: int
    apify_token: str
    anthropic_api_key: str
    telegram_bot_token: str
    state_db_path: Path
    log_level: str = "INFO"
    instagram_handles: dict[str, ModelConfig] = field(default_factory=dict)
    tiktok_handles: dict[str, ModelConfig] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.instagram_handles = {
            m.instagram.lower(): m for m in self.models if m.instagram
        }
        self.tiktok_handles = {m.tiktok.lower(): m for m in self.models if m.tiktok}


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value or value.startswith("xxx") or "xxxxxxxx" in value:
        raise ConfigError(
            f"{name} is not set. Copy .env.example to .env and fill in your real "
            f"{name} (see SETUP.md)."
        )
    return value


def _parse_model(raw: object, index: int) -> ModelConfig:
    if not isinstance(raw, dict):
        raise ConfigError(f"Model entry #{index + 1} in models.yaml is not a mapping.")

    name = str(raw.get("name") or "").strip()
    if not name:
        raise ConfigError(f"Model entry #{index + 1} in models.yaml is missing 'name'.")

    chat_id = raw.get("telegram_chat_id")
    if chat_id is None:
        raise ConfigError(f"Model '{name}' is missing telegram_chat_id.")
    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        raise ConfigError(
            f"Model '{name}' has an invalid telegram_chat_id ({chat_id!r}). "
            "It should be a number like -1001234567890."
        ) from None
    if chat_id >= 0:
        raise ConfigError(
            f"Model '{name}' needs her real Telegram channel id — channel ids are "
            f"negative numbers starting with -100 (got {chat_id}). "
            "SETUP.md step 2 shows how to get it."
        )

    instagram = str(raw["instagram"]).strip().lstrip("@") if raw.get("instagram") else None
    tiktok = str(raw["tiktok"]).strip().lstrip("@") if raw.get("tiktok") else None
    if not instagram and not tiktok:
        raise ConfigError(
            f"Model '{name}' has neither an 'instagram' nor a 'tiktok' handle — "
            "there is nothing to monitor for her."
        )

    return ModelConfig(name=name, telegram_chat_id=chat_id, instagram=instagram, tiktok=tiktok)


def load_config(repo_root: Path, models_path: Path | None = None) -> AppConfig:
    load_dotenv(repo_root / ".env")

    models_path = models_path or repo_root / "config" / "models.yaml"
    if not models_path.exists():
        raise ConfigError(
            f"Config file not found: {models_path}\n"
            "Copy config/models.example.yaml to config/models.yaml and edit it."
        )

    try:
        data = yaml.safe_load(models_path.read_text()) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse {models_path}: {exc}") from exc

    raw_models = data.get("models")
    if not isinstance(raw_models, list) or not raw_models:
        raise ConfigError(f"{models_path} must contain a non-empty 'models:' list.")

    models = [_parse_model(raw, i) for i, raw in enumerate(raw_models)]

    seen_names = set()
    for m in models:
        if m.name.lower() in seen_names:
            raise ConfigError(f"Model '{m.name}' appears more than once in models.yaml.")
        seen_names.add(m.name.lower())

    poll = data.get("poll") or {}
    try:
        results_limit = int(poll.get("results_limit", 8))
    except (TypeError, ValueError):
        raise ConfigError("poll.results_limit in models.yaml must be a number.") from None
    results_limit = max(1, min(results_limit, 30))

    include_stories = bool(poll.get("include_stories", True))
    try:
        stories_min_interval = int(poll.get("stories_min_interval_minutes", 30))
    except (TypeError, ValueError):
        raise ConfigError(
            "poll.stories_min_interval_minutes in models.yaml must be a number."
        ) from None
    stories_min_interval = max(0, stories_min_interval)

    state_db_path = Path(os.environ.get("STATE_DB_PATH", "data/state.db"))
    if not state_db_path.is_absolute():
        state_db_path = repo_root / state_db_path

    return AppConfig(
        models=models,
        results_limit=results_limit,
        include_stories=include_stories,
        stories_min_interval_minutes=stories_min_interval,
        apify_token=_require_env("APIFY_TOKEN"),
        anthropic_api_key=_require_env("ANTHROPIC_API_KEY"),
        telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        state_db_path=state_db_path,
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    )
