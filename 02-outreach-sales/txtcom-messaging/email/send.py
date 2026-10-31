#!/usr/bin/env python3
"""
ALTR · TXT Line promo — mass email sender.

Reads recipients from creators.csv, personalizes promo-email.html /
promo-email.txt, and sends via SMTP with throttling and a resumable
sent log. Stdlib only — no pip installs needed.

Usage:
  python3 send.py --test you@yourdomain.com   # send one test to yourself
  python3 send.py --dry-run                   # render + validate, send nothing
  python3 send.py                             # the real run
  python3 send.py --limit 50                  # cap this run at 50 sends

Config: copy config.example.env to config.env and fill it in.
Already-sent addresses (in sent_log.csv) are skipped automatically,
so you can stop and re-run safely.
"""

import argparse
import csv
import random
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

HERE = Path(__file__).parent
CSV_PATH = HERE / "creators.csv"
LOG_PATH = HERE / "sent_log.csv"
HTML_PATH = HERE / "promo-email.html"
TEXT_PATH = HERE / "promo-email.txt"
CONFIG_PATH = HERE / "config.env"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

REQUIRED_KEYS = [
    "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
    "FROM_EMAIL", "FROM_NAME", "SUBJECT",
    "CTA_URL", "UNSUBSCRIBE_URL", "COMPANY_ADDRESS",
]


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(f"Missing {CONFIG_PATH.name}. Copy config.example.env to config.env and fill it in.")
    cfg = {}
    for line in CONFIG_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    missing = [k for k in REQUIRED_KEYS if not cfg.get(k)]
    if missing:
        sys.exit(f"config.env is missing: {', '.join(missing)}")
    return cfg


def render(template: str, row: dict, cfg: dict) -> str:
    """Replace {{placeholder}} tokens from the CSV row, then from config."""
    out = template
    values = {
        "first_name": (row.get("first_name") or "there").strip() or "there",
        "email": row["email"],
        "cta_url": cfg["CTA_URL"],
        "unsubscribe_url": cfg["UNSUBSCRIBE_URL"].replace("{email}", row["email"]),
        "company_address": cfg["COMPANY_ADDRESS"],
    }
    # Any extra CSV columns become placeholders too (e.g. {{handle}}).
    for k, v in row.items():
        values.setdefault(k.strip(), (v or "").strip())
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    leftover = re.findall(r"\{\{\s*[\w.-]+\s*\}\}", out)
    if leftover:
        raise ValueError(f"unreplaced placeholders: {set(leftover)}")
    return out


def load_recipients() -> list[dict]:
    if not CSV_PATH.exists():
        sys.exit(f"Missing {CSV_PATH.name}. Copy creators.csv.example and add your list.")
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "email" not in rows[0]:
        sys.exit("creators.csv needs at least an 'email' column (plus optional first_name).")
    seen, out, bad = set(), [], []
    for row in rows:
        email = (row.get("email") or "").strip().lower()
        if not EMAIL_RE.match(email):
            bad.append(email or "<blank>")
            continue
        if email in seen:
            continue
        seen.add(email)
        row["email"] = email
        out.append(row)
    if bad:
        print(f"  ! skipping {len(bad)} invalid address(es): {', '.join(bad[:5])}{' …' if len(bad) > 5 else ''}")
    return out


def load_sent() -> set:
    if not LOG_PATH.exists():
        return set()
    with open(LOG_PATH, newline="", encoding="utf-8") as f:
        return {r["email"] for r in csv.DictReader(f) if r.get("status") == "sent"}


def log_result(email: str, status: str, detail: str = ""):
    new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["email", "status", "detail", "timestamp"])
        w.writerow([email, status, detail, datetime.now(timezone.utc).isoformat()])


def build_message(row: dict, cfg: dict, html_tpl: str, text_tpl: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = render(cfg["SUBJECT"], row, cfg)
    msg["From"] = formataddr((cfg["FROM_NAME"], cfg["FROM_EMAIL"]))
    msg["To"] = row["email"]
    msg["Message-ID"] = make_msgid(domain=cfg["FROM_EMAIL"].split("@")[-1])
    unsub = cfg["UNSUBSCRIBE_URL"].replace("{email}", row["email"])
    msg["List-Unsubscribe"] = f"<{unsub}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(render(text_tpl, row, cfg))
    msg.add_alternative(render(html_tpl, row, cfg), subtype="html")
    return msg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="render and validate everything, send nothing")
    ap.add_argument("--test", metavar="EMAIL", help="send a single test email to this address and exit")
    ap.add_argument("--limit", type=int, default=0, help="max sends this run (0 = no cap)")
    args = ap.parse_args()

    cfg = load_config()
    html_tpl = HTML_PATH.read_text(encoding="utf-8")
    text_tpl = TEXT_PATH.read_text(encoding="utf-8")
    delay_min = float(cfg.get("DELAY_SECONDS_MIN", 20))
    delay_max = float(cfg.get("DELAY_SECONDS_MAX", 45))

    def connect():
        port = int(cfg["SMTP_PORT"])
        if port == 465:
            s = smtplib.SMTP_SSL(cfg["SMTP_HOST"], port, context=ssl.create_default_context())
        else:
            s = smtplib.SMTP(cfg["SMTP_HOST"], port, timeout=30)
            s.starttls(context=ssl.create_default_context())
        s.login(cfg["SMTP_USER"], cfg["SMTP_PASS"])
        return s

    if args.test:
        row = {"email": args.test.lower(), "first_name": "TestName"}
        msg = build_message(row, cfg, html_tpl, text_tpl)
        with connect() as s:
            s.send_message(msg)
        print(f"Test email sent to {args.test}. Check inbox AND spam folder, on phone + desktop.")
        return

    recipients = load_recipients()
    already = load_sent()
    queue = [r for r in recipients if r["email"] not in already]
    print(f"List: {len(recipients)} valid · already sent: {len(already)} · queued: {len(queue)}")
    if args.limit:
        queue = queue[: args.limit]
        print(f"Capped this run at {len(queue)}.")

    if args.dry_run:
        errors = 0
        for row in queue:
            try:
                build_message(row, cfg, html_tpl, text_tpl)
            except Exception as e:
                errors += 1
                print(f"  ! {row['email']}: {e}")
        print(f"Dry run complete: {len(queue) - errors} ok, {errors} error(s). Nothing sent.")
        return

    if not queue:
        print("Nothing to send.")
        return

    sent = failed = 0
    server = connect()
    try:
        for i, row in enumerate(queue, 1):
            try:
                msg = build_message(row, cfg, html_tpl, text_tpl)
                server.send_message(msg)
                sent += 1
                log_result(row["email"], "sent")
                print(f"[{i}/{len(queue)}] sent → {row['email']}")
            except smtplib.SMTPServerDisconnected:
                print("  reconnecting…")
                server = connect()
                continue  # this row retries next run via the log
            except Exception as e:
                failed += 1
                log_result(row["email"], "failed", str(e)[:200])
                print(f"[{i}/{len(queue)}] FAILED → {row['email']}: {e}")
            if i < len(queue):
                time.sleep(random.uniform(delay_min, delay_max))
    finally:
        try:
            server.quit()
        except Exception:
            pass
    print(f"\nDone. Sent {sent}, failed {failed}. Log: {LOG_PATH.name}")


if __name__ == "__main__":
    main()
