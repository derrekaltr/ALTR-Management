#!/usr/bin/env python3
"""Fetch client group chats directly from Telegram (no manual exports).

One-time setup:
  1. Get free API credentials at https://my.telegram.org -> "API development tools"
  2. Copy config/telegram.example.ini to config/telegram.ini and fill them in
  3. Run `python3 src/fetch.py` in a terminal — the first run asks for your
     phone number and a login code (sent to your Telegram app). After that,
     the saved session logs in automatically.

Usage:
    python3 src/fetch.py            # fetch all chats listed in config/clients.yaml
    python3 src/fetch.py --list     # just list your group chats (to check matching)

Writes the same files as ingest.py: data/chats/<slug>.jsonl + <slug>.meta.json,
so the rest of the pipeline (/weekly-report, render) is unchanged. Each run
refetches the full history per chat, which keeps things simple and idempotent.
"""
import asyncio
import configparser
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml
from telethon import TelegramClient
from telethon.tl.types import (
    Message,
    MessageMediaContact,
    MessageMediaDocument,
    MessageMediaGeo,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageService,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "chats"
CONFIG_INI = REPO_ROOT / "config" / "telegram.ini"
SESSION = REPO_ROOT / "data" / "telegram"  # data/ is gitignored


def slugify(name: str) -> str:
    import re
    import unicodedata

    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[\s_-]+", "-", name)


def load_credentials():
    if not CONFIG_INI.exists():
        sys.exit(
            f"Missing {CONFIG_INI}.\n"
            "Copy config/telegram.example.ini to config/telegram.ini and fill in\n"
            "api_id / api_hash from https://my.telegram.org -> API development tools."
        )
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_INI)
    return int(cfg["telegram"]["api_id"]), cfg["telegram"]["api_hash"]


def load_client_folders():
    """Map Telegram group title -> client entry (title defaults to folder name)."""
    clients = yaml.safe_load((REPO_ROOT / "config" / "clients.yaml").read_text())["clients"]
    return {c.get("telegram_title", c["folder"]).strip(): c for c in clients}


def sender_name(msg, entities):
    sid = msg.sender_id
    ent = entities.get(sid)
    if ent is None:
        return "Deleted Account"
    name = " ".join(p for p in (getattr(ent, "first_name", None), getattr(ent, "last_name", None)) if p)
    return name or getattr(ent, "title", None) or getattr(ent, "username", None) or str(sid)


def media_kind(msg):
    m = msg.media
    if m is None:
        return None
    if isinstance(m, MessageMediaPhoto):
        return "photo"
    if isinstance(m, MessageMediaDocument):
        if msg.sticker is not None:
            return "sticker"
        if msg.voice is not None:
            return "voice"
        if msg.video is not None or msg.video_note is not None:
            return "video"
        if msg.audio is not None:
            return "audio"
        return "file"
    if isinstance(m, MessageMediaPoll):
        return "poll"
    if isinstance(m, MessageMediaContact):
        return "contact"
    if isinstance(m, MessageMediaGeo):
        return "location"
    return "media"


async def fetch_messages_with_retry(client, entity, attempts=4):
    delay = 5
    for attempt in range(1, attempts + 1):
        collected = []
        try:
            async for msg in client.iter_messages(entity, reverse=True):
                collected.append(msg)
            return collected
        except Exception as e:
            if attempt == attempts:
                raise
            print(f"    retry {attempt}/{attempts - 1} in {delay}s ({e.__class__.__name__}: {e})")
            await asyncio.sleep(delay)
            delay *= 3
    return []


async def fetch_chat(client, dialog, folder_name):
    slug = slugify(folder_name)
    messages = []
    entities = {}
    for msg in await fetch_messages_with_retry(client, dialog.entity):
        if msg.sender_id not in entities and msg.sender is not None:
            entities[msg.sender_id] = msg.sender
        if isinstance(msg, MessageService):
            event = ""
            try:
                event = msg.action.__class__.__name__.replace("MessageAction", "")
                title = getattr(msg.action, "title", None)
                if title:
                    event += f" «{title}»"
            except Exception:
                pass
            messages.append({"id": msg.id, "service": True, "event": event,
                             "ts": msg.date.astimezone().isoformat(timespec="seconds")})
            continue
        if not isinstance(msg, Message):
            continue
        rec = {
            "id": msg.id,
            "ts": msg.date.astimezone().isoformat(timespec="seconds"),
            "sender": sender_name(msg, entities),
            "text": msg.message or "",
        }
        if msg.reply_to and msg.reply_to.reply_to_msg_id:
            rec["reply_to"] = msg.reply_to.reply_to_msg_id
        kind = media_kind(msg)
        if kind:
            rec["media"] = kind
        if msg.forward is not None:
            rec["forwarded_from"] = getattr(msg.forward, "from_name", None) or "forwarded"
        messages.append(rec)

    out_path = OUT_DIR / f"{slug}.jsonl"
    # Never clobber existing data with an empty/failed fetch
    if not messages and out_path.exists() and out_path.stat().st_size > 0:
        print(f"    ⚠ fetch returned 0 messages — keeping existing {out_path.name}")
        return -1
    with out_path.open("w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    chat_msgs = [m for m in messages if not m.get("service")]
    timestamps = [m["ts"] for m in chat_msgs if m.get("ts")]
    senders = {}
    for m in chat_msgs:
        senders[m["sender"]] = senders.get(m["sender"], 0) + 1
    meta = {
        "chat": folder_name,
        "title": dialog.title,
        "slug": slug,
        "messages": len(chat_msgs),
        "service_events": len(messages) - len(chat_msgs),
        "first_ts": min(timestamps) if timestamps else None,
        "last_ts": max(timestamps) if timestamps else None,
        "senders": dict(sorted(senders.items(), key=lambda kv: -kv[1])),
        "warnings": [],
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": "telegram-api",
    }
    (OUT_DIR / f"{slug}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return len(chat_msgs)


async def main():
    api_id, api_hash = load_credentials()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    list_only = "--list" in sys.argv

    client = TelegramClient(str(SESSION), api_id, api_hash)
    await client.start()

    folders = load_client_folders()
    dialogs = {}
    async for dialog in client.iter_dialogs():
        if not dialog.is_group:
            continue
        ent = dialog.entity
        # Skip dead pre-migration basic groups that share the supergroup's title
        if getattr(ent, "migrated_to", None) or getattr(ent, "deactivated", False):
            continue
        title = dialog.title.strip()
        # On duplicate titles prefer the supergroup (Channel) over a basic Chat
        if title in dialogs and getattr(dialogs[title].entity, "broadcast", None) is not None:
            continue
        dialogs[title] = dialog

    if list_only:
        for title in sorted(dialogs):
            mark = "✓" if title in folders else " "
            print(f" {mark} {title}")
        print("\n✓ = matched to config/clients.yaml")
        return

    missing = [title for title in folders if title not in dialogs]
    width = max(len(folders[t]["folder"]) for t in folders)
    for title in sorted(folders):
        folder_name = folders[title]["folder"]
        if title in missing:
            print(f"{folder_name:<{width}}  ⚠ no matching group chat found (looked for title: {title!r})")
            continue
        n = await fetch_chat(client, dialogs[title], folder_name)
        if n >= 0:
            print(f"{folder_name:<{width}}  {n:>6} messages")
        await asyncio.sleep(2)  # be gentle with the API between chats
    if missing:
        print("\n⚠ Unmatched chats — check the group title matches the 'folder' name in config/clients.yaml")
    print(f"\nOutput: {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
