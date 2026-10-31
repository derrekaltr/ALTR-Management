#!/usr/bin/env python3
"""Extract per-person conversation dossiers from the Messages database.

Only handles NOT already saved in macOS Contacts are extracted. Output goes to
data/dossiers/<handle>.json for analyze.py to consume.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3

import common

MONEY_KEYWORDS = re.compile(
    r"(earn|paid|payout|revenue|made \$|\$\d|percent|%|split|invoice|zelle|venmo|cashapp|cash app)",
    re.I,
)
MAX_TRANSCRIPT_EARLY = 50
MAX_TRANSCRIPT_LATE = 250
MAX_MSG_CHARS = 500
MAX_ATTACHMENTS = 5


def qualifying_handles(conn, min_messages, min_each_way):
    """Handles with a real two-way conversation, grouped by handle id."""
    rows = conn.execute(
        """
        SELECT h.id, count(m.ROWID) AS total,
               sum(m.is_from_me) AS sent,
               sum(1 - m.is_from_me) AS received,
               max(m.ROWID) AS max_rowid,
               min(m.date) AS first_date, max(m.date) AS last_date
        FROM handle h
        JOIN message m ON m.handle_id = h.ROWID
        WHERE m.associated_message_type = 0
        GROUP BY h.id
        """
    ).fetchall()
    out = []
    for hid, total, sent, received, max_rowid, first, last in rows:
        if total >= min_messages and sent >= min_each_way and received >= min_each_way:
            out.append(
                {
                    "handle": hid,
                    "total": total,
                    "sent": sent,
                    "received": received,
                    "max_rowid": max_rowid,
                    "first_date": common.apple_date_to_unix(first),
                    "last_date": common.apple_date_to_unix(last),
                }
            )
    return out


def fetch_messages(conn, handle_id):
    return conn.execute(
        """
        SELECT m.ROWID, m.date, m.is_from_me, m.text, m.attributedBody,
               m.cache_has_attachments
        FROM message m
        JOIN handle h ON m.handle_id = h.ROWID
        WHERE h.id = ? AND m.associated_message_type = 0
        ORDER BY m.date
        """,
        (handle_id,),
    ).fetchall()


def fetch_attachments(conn, message_rowid):
    return conn.execute(
        """
        SELECT a.filename, a.mime_type
        FROM message_attachment_join j
        JOIN attachment a ON a.ROWID = j.attachment_id
        WHERE j.message_id = ?
        """,
        (message_rowid,),
    ).fetchall()


def message_text(row):
    _, _, _, text, blob, _ = row
    return text if text else common.decode_attributed_body(blob)


def fmt_date(unix_ts):
    if not unix_ts:
        return "????-??-??"
    return datetime.datetime.fromtimestamp(unix_ts).strftime("%Y-%m-%d")


def build_dossier(conn, info):
    handle = info["handle"]
    rows = fetch_messages(conn, handle)

    # Transcript: earliest N (introductions/names) + latest M (current context).
    if len(rows) > MAX_TRANSCRIPT_EARLY + MAX_TRANSCRIPT_LATE:
        sample = rows[:MAX_TRANSCRIPT_EARLY] + rows[-MAX_TRANSCRIPT_LATE:]
        gap = True
    else:
        sample = rows
        gap = False

    transcript = []
    for i, row in enumerate(sample):
        if gap and i == MAX_TRANSCRIPT_EARLY:
            transcript.append("[... older messages omitted ...]")
        text = message_text(row)
        if not text or not text.strip():
            if row[5]:
                text = "[attachment]"
            else:
                continue
        text = text.replace("\n", " ").strip()
        if len(text) > MAX_MSG_CHARS:
            text = text[:MAX_MSG_CHARS] + "…"
        who = "Me" if row[2] else "Them"
        transcript.append(f"[{fmt_date(common.apple_date_to_unix(row[1]))}] {who}: {text}")

    # Attachments: prefer images near money/earnings talk, then most recent.
    scored = []
    for i, row in enumerate(rows):
        if not row[5]:
            continue
        for filename, mime in fetch_attachments(conn, row[0]):
            if not filename or not (mime or "").startswith("image/"):
                continue
            path = os.path.expanduser(filename)
            if not os.path.exists(path):
                continue
            near_money = any(
                MONEY_KEYWORDS.search(message_text(rows[j]) or "")
                for j in range(max(0, i - 2), min(len(rows), i + 3))
            )
            scored.append((near_money, row[1], path))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    attachments = []
    for _, _, path in scored:
        if path not in attachments:
            attachments.append(path)
        if len(attachments) >= MAX_ATTACHMENTS:
            break

    return {
        "handle": handle,
        "total": info["total"],
        "sent": info["sent"],
        "received": info["received"],
        "max_rowid": info["max_rowid"],
        "first_date": fmt_date(info["first_date"]),
        "last_date": fmt_date(info["last_date"]),
        "transcript": transcript,
        "attachments": attachments,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-messages", type=int, default=20)
    ap.add_argument("--min-each-way", type=int, default=3)
    ap.add_argument("--limit", type=int, help="only extract first N handles (testing)")
    ap.add_argument("--handles", help="comma-separated handle ids to extract (testing)")
    ap.add_argument("--force", action="store_true", help="re-extract even if unchanged")
    args = ap.parse_args()

    tmpdir = common.make_tmpdir()
    try:
        chat = sqlite3.connect(common.snapshot_db(common.CHAT_DB, tmpdir))
        saved_keys = common.load_saved_contact_keys(tmpdir)
        print(f"loaded {len(saved_keys)} saved-contact keys for exclusion")

        infos = qualifying_handles(chat, args.min_messages, args.min_each_way)
        print(f"{len(infos)} handles qualify before exclusion")

        infos = [i for i in infos if not common.is_saved(i["handle"], saved_keys)]
        print(f"{len(infos)} handles remain after excluding saved contacts")

        if args.handles:
            wanted = set(args.handles.split(","))
            infos = [i for i in infos if i["handle"] in wanted]
        if args.limit:
            infos = infos[: args.limit]

        dossier_dir = os.path.join(common.DATA_DIR, "dossiers")
        os.makedirs(dossier_dir, exist_ok=True)
        written = skipped = 0
        for info in infos:
            out_path = os.path.join(
                dossier_dir, common.safe_filename(info["handle"]) + ".json"
            )
            if not args.force and os.path.exists(out_path):
                with open(out_path) as f:
                    if json.load(f).get("max_rowid") == info["max_rowid"]:
                        skipped += 1
                        continue
            dossier = build_dossier(chat, info)
            with open(out_path, "w") as f:
                json.dump(dossier, f, indent=1)
            written += 1
        print(f"dossiers: {written} written, {skipped} unchanged")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
