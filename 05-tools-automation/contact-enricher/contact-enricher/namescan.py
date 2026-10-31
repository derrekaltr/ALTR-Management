#!/usr/bin/env python3
"""Capture names from low-volume conversations that don't qualify for full analysis.

Scans unsaved handles below the main message threshold, uses a cheap regex
prefilter to find self-introductions, then confirms names in batched claude -p
calls. Results land in data/name_candidates.json and are written as minimal
contacts (name + number only) by --apply.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys

import common
import extract
import write_contacts

INTRO_PATTERNS = re.compile(
    r"(?:"
    r"\bthis is ([A-Z][a-z]{1,15})"
    r"|\bmy name is ([A-Z][a-z]{1,15})"
    r"|\bit'?s ([A-Z][a-z]{1,15})\b"
    r"|\bi'?m ([A-Z][a-z]{1,15})\b"
    r"|\bnames? ([A-Z][a-z]{1,15})\b"
    r"|^([A-Z][a-z]{1,15})(?: [A-Z][a-z]{1,15})?$"
    r")",
    re.M,
)

BATCH_PROMPT = """For each conversation excerpt below, identify the OTHER person's real
name if they clearly stated or revealed it. "Me:" is the phone owner; "Them:" is the
other person. Only report a name you are confident about (stated introduction, sign-off,
or payment-app name). If no clear name, use null.

Respond with ONLY a JSON array, one object per conversation, in the same order:
[{{"handle": string, "name": string or null, "confidence": 0.0-1.0}}]

CONVERSATIONS:
{blocks}
"""

MAX_EXCERPT_MSGS = 12
BATCH_SIZE = 15
CANDIDATES_PATH = None  # set in main


def candidate_handles(conn, saved_keys, max_messages, min_messages):
    rows = conn.execute(
        """
        SELECT h.id, count(m.ROWID) AS total, sum(1 - m.is_from_me) AS received
        FROM handle h
        JOIN message m ON m.handle_id = h.ROWID
        WHERE m.associated_message_type = 0
        GROUP BY h.id
        """
    ).fetchall()
    out = []
    for hid, total, received in rows:
        if min_messages <= total < max_messages and received >= 1:
            if not common.is_saved(hid, saved_keys):
                out.append(hid)
    return out


def excerpt(conn, handle_id):
    rows = extract.fetch_messages(conn, handle_id)
    lines = []
    for row in rows[:MAX_EXCERPT_MSGS]:
        text = extract.message_text(row)
        if not text or not text.strip():
            continue
        text = text.replace("\n", " ").strip()[:200]
        lines.append(f"{'Me' if row[2] else 'Them'}: {text}")
    return lines


def has_intro(lines):
    """Cheap prefilter: does the other person appear to state a name?"""
    for line in lines:
        if not line.startswith("Them: "):
            continue
        if INTRO_PATTERNS.search(line[6:]):
            return True
    return False


def confirm_batch(batch):
    blocks = []
    for handle, lines in batch:
        blocks.append(f"--- handle: {handle} ---\n" + "\n".join(lines))
    prompt = BATCH_PROMPT.format(blocks="\n\n".join(blocks))
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "json"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:400])
    payload = json.loads(proc.stdout)["result"]
    payload = re.sub(r"^```(?:json)?|```$", "", payload.strip(), flags=re.M).strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", payload, re.S)
        return json.loads(match.group(0)) if match else []


def scan(args):
    tmpdir = common.make_tmpdir()
    try:
        conn = sqlite3.connect(common.snapshot_db(common.CHAT_DB, tmpdir))
        saved_keys = common.load_saved_contact_keys(tmpdir)
        handles = candidate_handles(
            conn, saved_keys, args.max_messages, args.min_messages
        )
        print(f"{len(handles)} unsaved handles below the {args.max_messages}-message threshold")

        prefiltered = []
        for handle in handles:
            lines = excerpt(conn, handle)
            if lines and has_intro(lines):
                prefiltered.append((handle, lines))
        print(f"{len(prefiltered)} passed the name-introduction prefilter")
        if args.limit:
            prefiltered = prefiltered[: args.limit]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    results = []
    for i in range(0, len(prefiltered), BATCH_SIZE):
        batch = prefiltered[i : i + BATCH_SIZE]
        try:
            for item in confirm_batch(batch):
                if item.get("name") and item.get("confidence", 0) >= 0.6:
                    results.append(item)
        except Exception as exc:
            print(f"  batch {i // BATCH_SIZE} failed: {exc}", file=sys.stderr)
        print(f"  processed {min(i + BATCH_SIZE, len(prefiltered))}/{len(prefiltered)}, "
              f"{len(results)} names so far")

    with open(CANDIDATES_PATH, "w") as f:
        json.dump(results, f, indent=1)
    print(f"{len(results)} name candidates written to {CANDIDATES_PATH}")
    return results


def apply_candidates(candidates, yes):
    tmpdir = common.make_tmpdir()
    try:
        saved_keys = common.load_saved_contact_keys(tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if not write_contacts.ensure_contacts_running():
        print("could not reach Contacts.app — is it installed and permitted?", file=sys.stderr)
        return

    today = datetime.date.today().isoformat()
    if not yes:
        print(f"About to create {len(candidates)} minimal contacts (name + number).")
        if input("Proceed? [y/N] ").strip().lower() != "y":
            print("aborted")
            return

    created = failed = 0
    for item in candidates:
        handle = item["handle"]
        if common.is_saved(handle, saved_keys):
            continue
        analysis = {
            "handle": handle,
            "name": item["name"],
            "category": "Personal",
            "message_count": 0,
            "first_date": "",
            "last_date": "",
        }
        note = f"{write_contacts.MARKER}\nAuto-added from Messages {today}\nContact: {handle}"
        try:
            write_contacts.create_contact(analysis, note)
            created += 1
            print(f"  created: {item['name']} ({handle})")
        except Exception as exc:
            failed += 1
            print(f"  FAILED {handle}: {exc}", file=sys.stderr)
    print(f"created {created}, failed {failed}")


def main():
    global CANDIDATES_PATH
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-messages", type=int, default=20)
    ap.add_argument("--min-messages", type=int, default=3)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--apply", action="store_true", help="create the contacts")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument(
        "--from-file", action="store_true", help="apply saved candidates without rescanning"
    )
    args = ap.parse_args()

    CANDIDATES_PATH = os.path.join(common.DATA_DIR, "name_candidates.json")
    os.makedirs(common.DATA_DIR, exist_ok=True)

    if args.from_file:
        with open(CANDIDATES_PATH) as f:
            candidates = json.load(f)
    else:
        candidates = scan(args)

    if args.apply:
        apply_candidates(candidates, args.yes)
    else:
        print("dry run — nothing written. Re-run with --apply to create contacts.")


if __name__ == "__main__":
    main()
