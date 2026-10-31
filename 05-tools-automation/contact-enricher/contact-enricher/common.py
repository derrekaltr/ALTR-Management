"""Shared helpers: database snapshots, AddressBook lookup, phone normalization."""

import glob
import json
import os
import re
import shutil
import sqlite3
import tempfile

HOME = os.path.expanduser("~")
CHAT_DB = os.path.join(HOME, "Library/Messages/chat.db")
ADDRESSBOOK_GLOB = os.path.join(
    HOME, "Library/Application Support/AddressBook/**/AddressBook-v22.abcddb"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_PATH = os.path.join(DATA_DIR, "state.json")

APPLE_EPOCH_OFFSET = 978307200  # 2001-01-01 in unix seconds


def apple_date_to_unix(value):
    if value is None:
        return None
    # Post-High Sierra dates are nanoseconds since 2001; older are seconds.
    if value > 1e12:
        value = value / 1e9
    return value + APPLE_EPOCH_OFFSET


def snapshot_db(path, tmpdir):
    """Copy a sqlite db (with -wal/-shm sidecars) so we never touch the live file."""
    dest = os.path.join(tmpdir, os.path.basename(path))
    shutil.copy2(path, dest)
    for suffix in ("-wal", "-shm"):
        side = path + suffix
        if os.path.exists(side):
            shutil.copy2(side, dest + suffix)
    return dest


def normalize_phone(raw):
    """Reduce a phone-ish string to comparable digits (last 10 when long enough)."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    return digits[-10:] if len(digits) >= 10 else digits


def handle_keys(handle_id):
    """Comparable keys for a Messages handle id (phone number or email)."""
    keys = set()
    if "@" in handle_id:
        keys.add(handle_id.strip().lower())
    else:
        phone = normalize_phone(handle_id)
        if phone:
            keys.add(phone)
    return keys


def load_saved_contact_keys(tmpdir):
    """Phone/email keys for every contact already saved in macOS Contacts."""
    keys = set()
    for db_path in glob.glob(ADDRESSBOOK_GLOB, recursive=True):
        try:
            snap = snapshot_db(db_path, tmpdir)
            conn = sqlite3.connect(snap)
            for (num,) in conn.execute("SELECT ZFULLNUMBER FROM ZABCDPHONENUMBER"):
                phone = normalize_phone(num)
                if phone:
                    keys.add(phone)
            for (addr,) in conn.execute("SELECT ZADDRESS FROM ZABCDEMAILADDRESS"):
                if addr:
                    keys.add(addr.strip().lower())
            conn.close()
        except (sqlite3.Error, OSError) as exc:
            print(f"warning: could not read {db_path}: {exc}")
    return keys


def is_saved(handle_id, saved_keys):
    return bool(handle_keys(handle_id) & saved_keys)


def decode_attributed_body(blob):
    """Extract the visible text from a typedstream attributedBody blob."""
    if not blob:
        return None
    idx = blob.find(b"NSString")
    if idx == -1:
        return None
    idx = blob.find(b"+", idx)
    if idx == -1:
        return None
    idx += 1
    if idx >= len(blob):
        return None
    length = blob[idx]
    if length == 0x81:
        length = int.from_bytes(blob[idx + 1 : idx + 3], "little")
        idx += 3
    elif length == 0x82:
        length = int.from_bytes(blob[idx + 1 : idx + 5], "little")
        idx += 5
    else:
        idx += 1
    return blob[idx : idx + length].decode("utf-8", errors="ignore") or None


def safe_filename(handle_id):
    return re.sub(r"[^A-Za-z0-9@+._-]", "_", handle_id)


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"handles": {}}


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE_PATH)


def make_tmpdir():
    return tempfile.mkdtemp(prefix="contact-enricher-")
