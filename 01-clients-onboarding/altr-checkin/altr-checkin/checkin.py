#!/usr/bin/env python3
"""ALTR client 1-week check-in.

Scans the Messages database daily (via launchd) for onboarding group chats
with Eric. One week after an onboarding chat is created, automatically sends
the client the standard check-in message (personalized with her first name)
as a direct 1:1 iMessage, and posts a macOS notification confirming the send.

If the client's name can't be extracted from the intro message, the message
is sent without a name ("Hey!" instead of "Hey Name!").

Usage:
  checkin.py            normal run (creates baseline state on first run)
  checkin.py --dry-run  report what would happen; writes no state, sends nothing
  checkin.py --test [handle]
                        immediately send a test message to the given handle
                        (default: your own iMessage email)
  checkin.py --warmup   touch the Messages app once to trigger the macOS
                        Automation permission prompt under launchd
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

ERIC = "+13217940412"
# Team members: never treated as the client when identifying who to message.
TEAM_NUMBERS = {
    ERIC,
    "+447872579141",  # Ollie
}
# Test sends go to Daniel Veritrade (per Derrek), never to a client.
TEST_HANDLE = "+17863036688"

DB_PATH = Path.home() / "Library/Messages/chat.db"
APP_DIR = Path(__file__).resolve().parent
STATE_PATH = APP_DIR / "state.json"
LOG_PATH = APP_DIR / "checkin.log"

SCAN_WINDOW_DAYS = 60
CHECKIN_AFTER_DAYS = 7
# If a check-in is this many days overdue (e.g. sends were failing), don't
# send a stale "been about a week" message - flag it for manual handling.
EXPIRE_AFTER_DAYS = 5
SEND_SHORTCUT = "ALTR Send"
# First names of team members, so intro lines like "Amber this is Eric
# (Onboarding Director)" never extract a team member's name as the client.
TEAM_NAMES = {"eric", "ollie"}

ONBOARDING_KEYWORDS = (
    "onboard",
    "integrat",
    "altrmgmt.com/apply",
    "contract",
)

DRAFT_TEMPLATE = (
    "Hey{name}! It's been about a week since you joined the ALTR team - "
    "just wanted to check in and see how everything's going so far. "
    "Is there anything we could be doing better, or anything you'd like "
    "from us? We're always looking to improve \U0001f64f"
)

APPLE_EPOCH_OFFSET = 978307200


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def decode_body(blob):
    """Extract plain text from a typedstream attributedBody blob."""
    if not blob:
        return None
    m = re.search(rb"NSString\x01\x94\x84\x01\+", blob)
    if not m:
        m = re.search(rb"NSString.{1,10}?\+", blob, re.S)
        if not m:
            return None
    i = m.end()
    ln = blob[i]
    if ln == 0x81:
        ln = int.from_bytes(blob[i + 1:i + 3], "little")
        i += 3
    elif ln == 0x82:
        ln = int.from_bytes(blob[i + 1:i + 5], "little")
        i += 5
    else:
        i += 1
    return blob[i:i + ln].decode("utf-8", errors="replace")


def apple_ts(dt):
    return int((dt.timestamp() - APPLE_EPOCH_OFFSET) * 1_000_000_000)


def from_apple_ts(ns):
    return datetime.fromtimestamp(ns / 1_000_000_000 + APPLE_EPOCH_OFFSET)


def find_onboarding_chats(conn):
    """Return onboarding candidates: group chats with Eric created recently."""
    cutoff = apple_ts(datetime.now() - timedelta(days=SCAN_WINDOW_DAYS))
    rows = conn.execute(
        """
        SELECT c.ROWID, c.guid, c.display_name, MIN(m.date) AS first_date
        FROM chat c
        JOIN chat_handle_join chj ON chj.chat_id = c.ROWID
        JOIN handle h ON h.ROWID = chj.handle_id
        JOIN chat_message_join cmj ON cmj.chat_id = c.ROWID
        JOIN message m ON m.ROWID = cmj.message_id
        WHERE c.style = 43 AND h.id = ?
        GROUP BY c.ROWID
        HAVING first_date >= ?
        ORDER BY first_date
        """,
        (ERIC, cutoff),
    ).fetchall()

    chats = []
    for rowid, guid, display_name, first_date in rows:
        participants = [
            r[0]
            for r in conn.execute(
                "SELECT h.id FROM chat_handle_join chj "
                "JOIN handle h ON h.ROWID = chj.handle_id WHERE chj.chat_id = ?",
                (rowid,),
            )
        ]
        msgs = conn.execute(
            """
            SELECT m.is_from_me, h.id, m.text, m.attributedBody
            FROM message m
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE cmj.chat_id = ?
            ORDER BY m.date
            """,
            (rowid,),
        ).fetchall()

        texts = []
        senders_with_msgs = set()
        for is_from_me, hid, text, body in msgs:
            t = text or decode_body(body)
            if t:
                texts.append((bool(is_from_me), t))
            if not is_from_me and hid:
                senders_with_msgs.add(hid)

        all_text = " ".join(t for _, t in texts).lower()
        is_onboarding = (display_name or "").lower().find("onboarding") >= 0 or any(
            kw in all_text for kw in ONBOARDING_KEYWORDS
        )
        if not is_onboarding:
            continue

        clients = [p for p in participants if p not in TEAM_NUMBERS]
        if not clients:
            continue
        # Prefer a client who has actually sent messages in the chat.
        clients.sort(key=lambda p: (p not in senders_with_msgs, p))

        name = None
        for is_from_me, t in texts[:15]:
            if not is_from_me:
                continue
            for m in re.finditer(
                r"(?:this is|meet)\s+([A-Za-z]+)|get\s+([A-Za-z]+)\s+onboarded",
                t,
                re.I,
            ):
                cand = m.group(1) or m.group(2)
                if cand.lower() not in TEAM_NAMES:
                    name = cand.capitalize()
                    break
            if name is None:
                # Intros like "Amber this is Eric (Onboarding Director)"
                # address the client by name first.
                first = re.match(r"([A-Za-z]+)[ ,]+this is\b", t.strip(), re.I)
                if first and first.group(1).lower() not in TEAM_NAMES | {
                    "hey", "hi", "hello", "guys", "team", "everyone", "ok", "so",
                }:
                    name = first.group(1).capitalize()
            if name:
                break

        first_dt = from_apple_ts(first_date)
        chats.append(
            {
                "guid": guid,
                # macOS updates can change the guid's service prefix
                # (iMessage;+; -> any;+;), so state is keyed by the stable
                # trailing chat identifier only.
                "key": guid.split(";")[-1],
                "display_name": display_name or "",
                "created": first_dt,
                "due": first_dt + timedelta(days=CHECKIN_AFTER_DAYS),
                "clients": clients,
                "name": name or "client",
                "name_found": name is not None,
            }
        )
    return chats


def load_state():
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
        state["chats"] = {
            k.split(";")[-1]: v for k, v in state["chats"].items()
        }
        return state
    return None


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def notify(text):
    safe = text.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e",
         f'display notification "{safe}" with title "ALTR Check-In"'],
        capture_output=True,
    )


def send_imessage(handle, text):
    """Send via the Shortcuts app, then verify the message actually landed
    in the Messages database before reporting success.

    AppleScript's `send` in Messages is broken on this macOS (exits 0
    without sending), which is why sending goes through the user-installed
    "ALTR Send iMessage" shortcut and success is only ever claimed after
    the sent message is observed in chat.db.
    """
    if "\n" in text:
        raise RuntimeError("message must be single-line for the send shortcut")
    start_ns = apple_ts(datetime.now() - timedelta(seconds=10))
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(f"{handle}\n{text}")
        path = f.name
    try:
        out = subprocess.run(
            ["shortcuts", "run", SEND_SHORTCUT, "-i", path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if out.returncode != 0:
            raise RuntimeError(
                f"send shortcut failed: {out.stderr.strip()[:300]}"
            )
    finally:
        os.unlink(path)

    probe = text[:80]
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    deadline = time.time() + 45
    while time.time() < deadline:
        rows = conn.execute(
            """
            SELECT m.text, m.attributedBody
            FROM message m
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            JOIN chat_handle_join chj ON chj.chat_id = cmj.chat_id
            JOIN handle h ON h.ROWID = chj.handle_id
            WHERE m.is_from_me = 1 AND m.date >= ? AND h.id = ?
            """,
            (start_ns, handle),
        ).fetchall()
        for t, body in rows:
            if probe in (t or decode_body(body) or ""):
                return
        time.sleep(3)
    raise RuntimeError(
        "message not found in Messages DB after send; treating as failed"
    )


def process_chat(chat, state):
    client = chat["clients"][0]
    label = f"{chat['name']} ({client})"
    now = datetime.now().isoformat(timespec="seconds")

    # No name extracted -> greet without one ("Hey!" instead of "Hey Name!").
    name_part = f" {chat['name']}" if chat["name_found"] else ""
    text = DRAFT_TEMPLATE.format(name=name_part)
    try:
        send_imessage(client, text)
    except Exception as e:
        log(f"SEND FAILED for {label}: {e} (will retry next run)")
        notify(f"Failed to send check-in to {label}. Will retry tomorrow.")
        return
    state["chats"][chat["key"]] = {
        "status": "sent", "client": client, "name": chat["name"], "at": now,
    }
    log(f"SENT check-in to {label} (verified in Messages DB)")
    notify(f"Sent 1-week check-in to {label}")


def main():
    dry_run = "--dry-run" in sys.argv

    if "--warmup" in sys.argv:
        # Poke Messages once so macOS shows the Automation permission
        # prompt in this (launchd) context while the user is present.
        out = subprocess.run(
            ["osascript", "-e", 'tell application "Messages" to get name'],
            capture_output=True, text=True, timeout=120,
        )
        if out.returncode == 0:
            log("WARMUP OK: Messages automation permission granted")
        else:
            log(f"WARMUP FAILED: {out.stderr.strip()}")
        return

    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        handle = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else TEST_HANDLE
        text = DRAFT_TEMPLATE.format(name=" Testy") + " [TEST]"
        send_imessage(handle, text)
        log(f"TEST message sent and verified to {handle}")
        return

    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.execute("SELECT 1 FROM chat LIMIT 1")
    except sqlite3.Error as e:
        log(f"ERROR: cannot read Messages database ({e}). "
            "Grant Full Disk Access to python3 in System Settings > "
            "Privacy & Security > Full Disk Access.")
        subprocess.run(
            ["osascript", "-e",
             'display notification "Grant Full Disk Access to python3 in '
             'System Settings > Privacy & Security so daily client check-ins '
             'can run." with title "ALTR Check-In needs permission"'],
            capture_output=True,
        )
        sys.exit(1)
    chats = find_onboarding_chats(conn)
    now = datetime.now()

    state = load_state()
    first_run = state is None
    if first_run:
        state = {"chats": {}}

    handled_numbers = {v["client"] for v in state["chats"].values()}

    for chat in chats:
        key = chat["key"]
        handled = state["chats"].get(key)
        due = chat["due"]
        overdue_at_install = first_run and due < now

        if dry_run:
            status = (
                handled["status"] if handled
                else "would-baseline-skip (past due at install)" if overdue_at_install
                else "DUE NOW -> would auto-send" if due <= now
                else f"waiting (due {due:%Y-%m-%d %H:%M})"
            )
            log(
                f"[dry-run] {chat['name']} {chat['clients']} chat='{chat['display_name']}' "
                f"created {chat['created']:%Y-%m-%d} due {due:%Y-%m-%d} -> {status}"
            )
            continue

        if handled:
            continue
        if overdue_at_install:
            state["chats"][key] = {
                "status": "skipped",
                "client": chat["clients"][0],
                "name": chat["name"],
                "at": now.isoformat(timespec="seconds"),
                "reason": "past due when automation installed",
            }
            log(f"Baseline: skipping {chat['name']} {chat['clients'][0]} (already past 1-week mark)")
            continue
        if due > now:
            continue
        if chat["clients"][0] in handled_numbers:
            state["chats"][key] = {
                "status": "skipped",
                "client": chat["clients"][0],
                "name": chat["name"],
                "at": now.isoformat(timespec="seconds"),
                "reason": "client already handled via another chat",
            }
            continue
        if now > due + timedelta(days=EXPIRE_AFTER_DAYS):
            # Too stale to say "it's been about a week" - never auto-send.
            state["chats"][key] = {
                "status": "expired",
                "client": chat["clients"][0],
                "name": chat["name"],
                "at": now.isoformat(timespec="seconds"),
                "reason": f"check-in window missed by more than {EXPIRE_AFTER_DAYS} days",
            }
            log(f"EXPIRED: {chat['name']} {chat['clients'][0]} was due {due:%Y-%m-%d}; too stale to auto-send")
            notify(f"Missed the check-in window for {chat['name']} - handle manually if you still want to reach out.")
            continue

        process_chat(chat, state)
        handled_numbers = {v["client"] for v in state["chats"].values()}

    if not dry_run:
        save_state(state)
        log("Run complete")


if __name__ == "__main__":
    main()
