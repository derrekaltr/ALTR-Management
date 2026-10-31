"""Configuration loading (config.yaml + .env)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

DEFAULTS: dict[str, Any] = {
    "model": "claude-sonnet-5",
    "capture": {
        "delay_seconds": 8,
        "headless": True,
        "timeout_seconds": 30,
        "max_tiles": 12,
    },
    "scoring": {
        "weights": {"critical": 25, "high": 10, "medium": 4, "low": 1},
        "thresholds": {"ready": 0, "nearly_ready": 5, "needs_cleanup": 20},
    },
    "report": {
        "prepared_by": "ALTR Talent Management",
        "contact": "",
    },
}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        elif value is not None:
            out[key] = value
    return out


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load config.yaml merged over defaults; also loads .env for the API key."""
    load_dotenv()
    config = DEFAULTS
    candidate = Path(path) if path else Path("config.yaml")
    if candidate.exists():
        with open(candidate) as f:
            user_config = yaml.safe_load(f) or {}
        config = _merge(DEFAULTS, user_config)
    return config
