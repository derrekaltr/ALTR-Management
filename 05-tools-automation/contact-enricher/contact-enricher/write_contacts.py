#!/usr/bin/env python3
"""Create NEW macOS Contacts from analyses. Never modifies existing contacts.

Default is a dry run that writes data/review.md. Use --apply to actually create
contacts (after reviewing). Contacts previously created by this tool get only
their auto-notes block refreshed when new messages arrive.
"""

import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import time

import common

MARKER = "═══ Auto-notes (Claude) ═══"
BUSINESS_CATEGORIES = {"ALTR Media Group", "ALTR MGMT", "ALTR Services"}
MIN_NAME_CONFIDENCE = 0.4
MAX_KEY_FACTS = 12


def _run_osascript(script, timeout):
    proc = subprocess.run(
        ["osascript", "-"],
        input=script,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def ensure_contacts_running(attempts=3):
    """Contacts.app must be running for AppleScript writes; relaunch if it isn't."""
    for attempt in range(attempts):
        try:
            _run_osascript(
                'with timeout of 60 seconds\n'
                'tell application "Contacts" to return count of people\n'
                'end timeout',
                90,
            )
            return True
        except (RuntimeError, subprocess.TimeoutExpired):
            subprocess.run(["open", "-a", "Contacts"], capture_output=True)
            time.sleep(5)
    return False


def applescript(script, timeout=120):
    try:
        return _run_osascript(script, timeout)
    except RuntimeError as exc:
        # -600 means Contacts was quit mid-run; relaunch and retry once.
        if "-600" not in str(exc):
            raise
        if not ensure_contacts_running():
            raise
        return _run_osascript(script, timeout)


def as_str(value):
    """Quote a Python string as an AppleScript string literal."""
    escaped = (value or "").replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", '" & linefeed & "')
    return f'"{escaped}"'


def split_name(full_name):
    parts = (full_name or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def build_note(analysis):
    today = datetime.date.today().isoformat()
    lines = [
        MARKER,
        f"Category: {analysis['category']}",
        f"Messages: {analysis['message_count']} ({analysis['first_date']} → {analysis['last_date']})",
        f"Contact: {analysis['handle']}",
        "",
        analysis.get("summary", "").strip(),
    ]
    facts = analysis.get("key_facts") or []
    if facts:
        lines.append("")
        lines.append("Key facts:")
        lines.extend(f"• {fact}" for fact in facts[:MAX_KEY_FACTS])
    services = analysis.get("services_discussed") or []
    if services:
        lines.append("")
        lines.append("Services discussed: " + "; ".join(services))
    lines.append("")
    lines.append(f"(auto-generated from Messages, updated {today})")
    return "\n".join(lines)


def load_analyses():
    out = []
    for path in sorted(glob.glob(os.path.join(common.DATA_DIR, "analyses", "*.json"))):
        with open(path) as f:
            out.append(json.load(f))
    return out


def creatable(analysis):
    """Can we create a contact? Requires a usable name."""
    name = (analysis.get("name") or "").strip()
    return bool(name) and analysis.get("name_confidence", 0) >= MIN_NAME_CONFIDENCE


def create_contact(analysis, note):
    first, last = split_name(analysis["name"])
    handle = analysis["handle"]
    org = analysis["category"] if analysis["category"] in BUSINESS_CATEGORIES else ""
    props = [f"first name:{as_str(first)}"]
    if last:
        props.append(f"last name:{as_str(last)}")
    if org:
        props.append(f"organization:{as_str(org)}")
    props.append(f"note:{as_str(note)}")

    if "@" in handle:
        detail = (
            f'make new email at end of emails of p with properties '
            f'{{label:"work", value:{as_str(handle)}}}'
        )
    else:
        detail = (
            f'make new phone at end of phones of p with properties '
            f'{{label:"mobile", value:{as_str(handle)}}}'
        )

    script = f"""with timeout of 120 seconds
tell application "Contacts"
    set p to make new person with properties {{{", ".join(props)}}}
    {detail}
    save
    return id of p
end tell
end timeout"""
    return applescript(script)


def get_note(contact_id):
    script = f"""with timeout of 120 seconds
tell application "Contacts"
    set p to first person whose id is {as_str(contact_id)}
    set n to note of p
    if n is missing value then return ""
    return n
end tell
end timeout"""
    return applescript(script)


def update_note(contact_id, new_block):
    """Refresh only the auto-notes block; anything the user typed above it stays."""
    existing = get_note(contact_id)
    prefix = existing.split(MARKER)[0].rstrip() if MARKER in existing else existing.rstrip()
    combined = f"{prefix}\n\n{new_block}" if prefix else new_block
    script = f"""with timeout of 120 seconds
tell application "Contacts"
    set p to first person whose id is {as_str(contact_id)}
    set note of p to {as_str(combined)}
    save
end tell
end timeout"""
    applescript(script)


def write_review(analyses, to_create, skipped_saved, no_name, out_path):
    by_category = {}
    for analysis in to_create:
        by_category.setdefault(analysis["category"], []).append(analysis)

    lines = [
        "# Contact enrichment — proposed new contacts",
        "",
        f"Generated {datetime.date.today().isoformat()}. "
        f"{len(analyses)} conversations analyzed, {len(to_create)} contacts proposed.",
        "",
        "Existing contacts are never modified. Review below, then run:",
        "`python3 write_contacts.py --apply`",
        "",
    ]
    for category in sorted(by_category):
        entries = by_category[category]
        lines.append(f"## {category} ({len(entries)})")
        lines.append("")
        for analysis in sorted(entries, key=lambda a: a.get("name") or ""):
            lines.append(f"### {analysis['name']} — {analysis['handle']}")
            conf = analysis.get("category_confidence", 0)
            lines.append(
                f"*{analysis['message_count']} messages, "
                f"{analysis['first_date']} → {analysis['last_date']}, "
                f"category confidence {conf:.2f}*"
            )
            lines.append("")
            lines.append(analysis.get("summary", ""))
            facts = (analysis.get("key_facts") or [])[:MAX_KEY_FACTS]
            if facts:
                lines.append("")
                lines.extend(f"- {fact}" for fact in facts)
            lines.append("")

    if no_name:
        lines.append(f"## Skipped — no confident name ({len(no_name)})")
        lines.append("")
        lines.append("These had conversations worth noting but no identifiable name. "
                     "Add manually if wanted.")
        lines.append("")
        for analysis in no_name:
            lines.append(
                f"- **{analysis['handle']}** ({analysis['category']}, "
                f"{analysis['message_count']} msgs): {analysis.get('summary', '')[:300]}"
            )
        lines.append("")

    if skipped_saved:
        lines.append(f"## Skipped — already in Contacts ({len(skipped_saved)})")
        lines.append("")
        lines.extend(f"- {handle}" for handle in skipped_saved)
        lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually create contacts")
    ap.add_argument("--limit", type=int, help="only process first N (testing)")
    ap.add_argument("--yes", action="store_true", help="skip the backup confirmation")
    ap.add_argument(
        "--include-personal",
        action="store_true",
        help="also create contacts categorized Personal/Unknown",
    )
    args = ap.parse_args()

    analyses = load_analyses()
    if not analyses:
        print("no analyses found — run extract.py and analyze.py first")
        return

    # Fresh existence check against Contacts' own database at write time.
    tmpdir = common.make_tmpdir()
    try:
        saved_keys = common.load_saved_contact_keys(tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    to_create, skipped_saved, no_name = [], [], []
    for analysis in analyses:
        if common.is_saved(analysis["handle"], saved_keys):
            skipped_saved.append(analysis["handle"])
            continue
        if not args.include_personal and analysis["category"] not in BUSINESS_CATEGORIES:
            if not creatable(analysis):
                continue
        if creatable(analysis):
            to_create.append(analysis)
        else:
            no_name.append(analysis)

    if args.limit:
        to_create = to_create[: args.limit]

    review_path = os.path.join(common.DATA_DIR, "review.md")
    write_review(analyses, to_create, skipped_saved, no_name, review_path)
    print(f"review written to {review_path}")
    print(
        f"{len(to_create)} to create, {len(no_name)} without a name, "
        f"{len(skipped_saved)} already saved"
    )

    if not args.apply:
        print("\ndry run — nothing written to Contacts. Re-run with --apply when ready.")
        return

    if not args.yes:
        print(
            "\nBACK UP FIRST: Contacts.app → File → Export → Contacts Archive.\n"
            "This only CREATES contacts; existing ones are never modified."
        )
        if input("Proceed? [y/N] ").strip().lower() != "y":
            print("aborted")
            return

    if not ensure_contacts_running():
        print("could not reach Contacts.app — is it installed and permitted?", file=sys.stderr)
        return

    state = common.load_state()
    created = refreshed = failed = 0
    for analysis in to_create:
        handle = analysis["handle"]
        prior = state["handles"].get(handle, {})
        prior_id = prior.get("contact_id")
        try:
            # Already created by us: refresh the notes block instead of duplicating.
            if prior_id:
                if prior.get("written_rowid") == analysis["analyzed_rowid"]:
                    continue
                update_note(prior_id, build_note(analysis))
                state["handles"][handle]["written_rowid"] = analysis["analyzed_rowid"]
                common.save_state(state)
                refreshed += 1
                print(f"  refreshed notes: {analysis['name']} ({handle})")
                continue

            contact_id = create_contact(analysis, build_note(analysis))
            state["handles"].setdefault(handle, {})
            state["handles"][handle].update(
                {
                    "contact_id": contact_id,
                    "written_rowid": analysis["analyzed_rowid"],
                    "name": analysis["name"],
                    "category": analysis["category"],
                }
            )
            common.save_state(state)
            created += 1
            print(f"  created: {analysis['name']} ({handle}) [{analysis['category']}]")
        except Exception as exc:
            failed += 1
            print(f"  FAILED {handle}: {exc}", file=sys.stderr)
    print(f"\ncreated {created} contacts, refreshed {refreshed}, {failed} failures")


if __name__ == "__main__":
    main()
