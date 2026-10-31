#!/usr/bin/env python3
"""
next_batch.py — enforce the "max 5 sends per day" outreach cap.

Workflow:
  1. You approve sellers (from the pending queue):
         python3 scripts/next_batch.py approve Syndicate porcupine WALKER
  2. Get today's sendable batch (respects the 5/day cap and what was already sent today):
         python3 scripts/next_batch.py
  3. After the assistant sends a message via the browser, mark it sent:
         python3 scripts/next_batch.py sent Syndicate

Status flow: pending_approval -> approved -> sent -> (replied_yes|replied_no|no_response).
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "outreach.json"
MAX_SENDS_PER_DAY = 5


def load():
    return json.loads(OUT.read_text())


def save(d):
    OUT.write_text(json.dumps(d, indent=2))


def sent_today(contacts):
    today = date.today().isoformat()
    return [c for c in contacts.values()
            if (c.get("sent_at") or "")[:10] == today]


def main():
    d = load()
    contacts = d.get("contacts", {})
    args = sys.argv[1:]

    if args and args[0] == "approve":
        for s in args[1:]:
            if s in contacts:
                contacts[s]["status"] = "approved"
                contacts[s]["approved"] = True
        save(d)
        print(f"approved: {', '.join(args[1:])}")
        return

    if args and args[0] == "sent":
        now = datetime.now().isoformat(timespec="seconds")
        for s in args[1:]:
            if s in contacts:
                contacts[s]["status"] = "sent"
                contacts[s]["sent_at"] = now
        save(d)
        print(f"marked sent: {', '.join(args[1:])}")
        return

    # Default: show today's sendable batch under the cap.
    already = len(sent_today(contacts))
    remaining = max(0, MAX_SENDS_PER_DAY - already)
    approved_unsent = [c for c in contacts.values()
                       if c.get("status") == "approved" and not c.get("sent_at")]
    pending = [c for c in contacts.values() if c.get("status") == "pending_approval"]

    print(f"Daily cap: {MAX_SENDS_PER_DAY} · already sent today: {already} · "
          f"remaining today: {remaining}")
    print(f"Approved & unsent: {len(approved_unsent)} · Pending approval: {len(pending)}")
    batch = approved_unsent[:remaining]
    if batch:
        print(f"\nSEND NEXT ({len(batch)}):")
        for c in batch:
            print(f"  - {c['seller']} ({c.get('success_rate')}%) -> {', '.join(c['services'])}")
    elif remaining == 0:
        print("\nDaily limit reached — no more sends today.")
    else:
        print("\nNothing approved yet. Approve sellers first.")


if __name__ == "__main__":
    main()
