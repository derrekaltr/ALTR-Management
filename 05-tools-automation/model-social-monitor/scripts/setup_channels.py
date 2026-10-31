#!/usr/bin/env python
"""One-shot Telegram channel setup.

Creates one private broadcast channel per model in config/models.yaml,
adds the monitor bot as an admin with post rights, writes each channel's
-100... id back into models.yaml, and saves invite links for your chatters
to config/channel_invites.md.

Run it with:

    venv/bin/pip install telethon
    venv/bin/python scripts/setup_channels.py

You will be asked for:
  * your Telegram API id + hash (2 min to get at https://my.telegram.org
    -> "API development tools"; any app name is fine)
  * your phone number and the login code Telegram sends you

Safe to re-run: models that already have a chat id are skipped, and if a
channel with the right name already exists in your account it's reused
instead of duplicated. If Telegram rate-limits channel creation partway
through (it caps how many you can create per day), just run it again later.
"""

from __future__ import annotations

import asyncio
import getpass
import re
import sys
from pathlib import Path

import httpx
import yaml
from dotenv import dotenv_values

try:
    from telethon import TelegramClient, functions
    from telethon.errors import FloodWaitError
    from telethon.utils import get_peer_id
except ImportError:
    sys.exit(
        "Telethon is not installed. Run this first:\n\n"
        "    venv/bin/pip install telethon\n"
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_YAML = REPO_ROOT / "config" / "models.yaml"
INVITES_MD = REPO_ROOT / "config" / "channel_invites.md"
SESSION = str(REPO_ROOT / "config" / "channel_setup")  # telethon session file
CREATE_DELAY_S = 10  # pause between channel creations to stay under rate limits


def channel_title(model_name: str) -> str:
    return f"{model_name} — Updates"


def set_chat_id_in_yaml(text: str, model_name: str, chat_id: int) -> str:
    """Replace the placeholder telegram_chat_id in one model's block,
    preserving all comments and formatting in the file."""
    pattern = re.compile(
        r"(- name: " + re.escape(model_name) + r"\n"
        r"(?:(?!- name:).)*?telegram_chat_id:)\s*0(\s*(?:#[^\n]*)?\n)",
        re.DOTALL,
    )
    new_text, count = pattern.subn(rf"\g<1> {chat_id}\g<2>", text, count=1)
    if count != 1:
        raise ValueError(
            f"could not find a 'telegram_chat_id: 0' placeholder for {model_name!r}"
        )
    return new_text


def pending_models() -> list[str]:
    data = yaml.safe_load(MODELS_YAML.read_text())
    names = []
    for entry in data.get("models", []):
        if int(entry.get("telegram_chat_id") or 0) == 0:
            names.append(entry["name"])
    return names


def bot_username_from_token(token: str) -> str:
    resp = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=30)
    body = resp.json()
    if not body.get("ok"):
        sys.exit(
            "Your TELEGRAM_BOT_TOKEN in .env doesn't work "
            f"(Telegram said: {body.get('description')}). Fix it and re-run."
        )
    return body["result"]["username"]


async def find_existing_channel(client: TelegramClient, title: str):
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and not dialog.is_group and dialog.title == title:
            return dialog.entity
    return None


async def setup_one(client: TelegramClient, name: str, bot_username: str):
    """Returns (chat_id, invite_link) for one model's channel."""
    title = channel_title(name)

    channel = await find_existing_channel(client, title)
    if channel is not None:
        print(f"  reusing existing channel '{title}'")
    else:
        result = await client(
            functions.channels.CreateChannelRequest(
                title=title,
                about=f"Automated real-life updates about {name}. Read-only.",
                broadcast=True,
                megagroup=False,
            )
        )
        channel = result.chats[0]
        print(f"  created channel '{title}'")

    await client.edit_admin(channel, bot_username, post_messages=True, is_admin=True)
    print(f"  added @{bot_username} as admin")

    invite = await client(functions.messages.ExportChatInviteRequest(peer=channel))
    return get_peer_id(channel), invite.link


async def main() -> None:
    names = pending_models()
    if not names:
        print("Every model in config/models.yaml already has a chat id — nothing to do.")
        return
    print(f"Channels to set up ({len(names)}): {', '.join(names)}\n")

    env = dotenv_values(REPO_ROOT / ".env")
    token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token or "xxx" in token:
        sys.exit("Fill in TELEGRAM_BOT_TOKEN in .env first (SETUP.md step 1).")
    bot_username = bot_username_from_token(token)
    print(f"Bot found: @{bot_username}\n")

    print("Telegram API credentials (from https://my.telegram.org -> API development tools)")
    api_id = int(input("  api_id: ").strip())
    api_hash = getpass.getpass("  api_hash: ").strip()

    client = TelegramClient(SESSION, api_id, api_hash)
    await client.start()  # prompts for phone + login code on first run

    done: list[tuple[str, int, str]] = []
    try:
        for name in names:
            print(f"\n{name}:")
            while True:
                try:
                    chat_id, link = await setup_one(client, name, bot_username)
                    break
                except FloodWaitError as exc:
                    if exc.seconds > 900:
                        print(
                            f"  Telegram wants a {exc.seconds}s cooldown (daily channel "
                            "cap, most likely). Progress so far is saved — re-run this "
                            "script later to finish the rest."
                        )
                        return
                    print(f"  rate limited; waiting {exc.seconds}s...")
                    await asyncio.sleep(exc.seconds + 5)

            MODELS_YAML.write_text(
                set_chat_id_in_yaml(MODELS_YAML.read_text(), name, chat_id)
            )
            done.append((name, chat_id, link))
            print(f"  chat id {chat_id} written to models.yaml")
            await asyncio.sleep(CREATE_DELAY_S)
    finally:
        await client.disconnect()
        if done:
            lines = ["# Channel invite links — share each with that model's chatters\n"]
            for name, chat_id, link in done:
                lines.append(f"- **{name}** (`{chat_id}`): {link}")
            existing = INVITES_MD.read_text() if INVITES_MD.exists() else ""
            INVITES_MD.write_text(existing + "\n".join(lines) + "\n")
            print(f"\nInvite links saved to {INVITES_MD}")
            print(f"Set up {len(done)} channel(s). Next: venv/bin/python -m model_monitor send-test")


if __name__ == "__main__":
    asyncio.run(main())
