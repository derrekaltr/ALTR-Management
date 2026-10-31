"""Shared helpers: paths, JSONL IO, checkpoints, field normalization."""

import json
import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


def data_dir(target: str) -> Path:
    d = ROOT / "data" / target.lstrip("@").lower()
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_rubric() -> dict:
    with open(ROOT / "rubric.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apify_client():
    from apify_client import ApifyClient

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("APIFY_TOKEN is not set. Copy .env.example to .env and add your Apify API token.")
    return ApifyClient(token)


def read_jsonl(path: Path):
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def append_jsonl(path: Path, items) -> int:
    n = 0
    with open(path, "a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            n += 1
    return n


def load_checkpoint(path: Path, default: dict) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return dict(default)


def save_checkpoint(path: Path, ckpt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ckpt, f)
    tmp.replace(path)


def first_of(item: dict, *keys, default=None):
    """Return the first present, non-None value among possible field spellings."""
    for k in keys:
        if k in item and item[k] is not None:
            return item[k]
    return default


def norm_username(item: dict):
    u = first_of(item, "username", "userName", "handle")
    return u.strip().lstrip("@").lower() if isinstance(u, str) and u.strip() else None


def norm_follower_item(item: dict) -> dict:
    """Normalize one row of a follower-export dataset (actor schemas vary)."""
    return {
        "username": norm_username(item),
        "full_name": first_of(item, "full_name", "fullName", "name", default="") or "",
        "is_private": bool(first_of(item, "is_private", "isPrivate", "private", default=False)),
        "is_verified": bool(first_of(item, "is_verified", "isVerified", "verified", default=False)),
    }


def norm_profile_item(item: dict) -> dict:
    """Normalize one row of a profile-detail dataset (apify/instagram-profile-scraper)."""
    external = first_of(item, "externalUrl", "external_url", "externalURL")
    if not external:
        urls = first_of(item, "externalUrls", "bioLinks", default=[]) or []
        for u in urls:
            candidate = u.get("url") or u.get("link") if isinstance(u, dict) else u
            if candidate:
                external = candidate
                break
    followers = first_of(item, "followersCount", "followers_count", "followers", "followerCount", default=0)
    try:
        followers = int(followers)
    except (TypeError, ValueError):
        followers = 0
    return {
        "username": norm_username(item),
        "full_name": first_of(item, "fullName", "full_name", "name", default="") or "",
        "biography": first_of(item, "biography", "bio", default="") or "",
        "external_url": external or "",
        "followers": followers,
        "is_private": bool(first_of(item, "private", "is_private", "isPrivate", default=False)),
    }


_NAME_TOKEN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ']+")


def first_name(full_name: str) -> str:
    tokens = _NAME_TOKEN.findall(full_name or "")
    return tokens[0].title() if tokens else ""
