#!/usr/bin/env python3
"""Parse Telegram Desktop HTML exports into normalized JSONL per client chat.

Usage:
    python3 src/ingest.py "~/Desktop/Telegram Export 8:8"

Each subfolder of the export root is treated as one client chat and must
contain messages.html (and optionally messages2.html, messages3.html, ...).
Output goes to data/chats/<slug>.jsonl and data/chats/<slug>.meta.json.

Re-runnable: messages merge by id with existing data, so both full-history
and incremental exports work.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "chats"

MEDIA_CLASSES = {
    "photo_wrap": "photo",
    "video_file_wrap": "video",
    "media_video": "video",
    "media_voice_message": "voice",
    "media_audio_file": "audio",
    "media_file": "file",
    "sticker_wrap": "sticker",
    "media_poll": "poll",
    "media_contact": "contact",
    "media_location": "location",
}

TS_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})(?: UTC([+-]\d{2}):(\d{2}))?")


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[\s_-]+", "-", name)


def clean_text(node) -> str:
    if node is None:
        return ""
    text = node.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def parse_timestamp(title: str):
    m = TS_RE.search(title or "")
    if not m:
        return None
    d, mo, y, h, mi, s, oh, om = m.groups()
    iso = f"{y}-{mo}-{d}T{h}:{mi}:{s}"
    if oh:
        iso += f"{oh}:{om}"
    return iso


def parse_message_div(div, prev_sender):
    """Parse one div.message; returns (record | None, sender_for_carry)."""
    classes = div.get("class", [])
    mid_raw = div.get("id", "")
    m = re.match(r"message(-?\d+)", mid_raw)
    mid = int(m.group(1)) if m else None

    if "service" in classes:
        body = div.find("div", class_="body")
        text = clean_text(body)
        # Pure date separators ("16 September 2025") carry no event info we need
        if re.fullmatch(r"\d{1,2} [A-Z][a-z]+ \d{4}", text):
            return None, prev_sender
        rec = {"id": mid, "service": True, "event": text}
        details = div.find("div", class_="details") or div
        ts = parse_timestamp(details.get("title", "")) if details else None
        if ts:
            rec["ts"] = ts
        return rec, prev_sender

    if "default" not in classes:
        return None, prev_sender

    body = div.find("div", class_="body", recursive=False)
    if body is None:
        return None, prev_sender

    date_div = body.find("div", class_="date")
    ts = parse_timestamp(date_div.get("title", "")) if date_div else None

    from_div = body.find("div", class_="from_name", recursive=False)
    if from_div is not None:
        # Strip "via @bot" suffixes kept in a nested span
        for span in from_div.find_all("span"):
            span.decompose()
        sender = clean_text(from_div)
    else:
        sender = prev_sender  # "joined" message: same sender as previous

    rec = {"id": mid, "ts": ts, "sender": sender}

    reply = body.find("div", class_="reply_to")
    if reply is not None:
        link = reply.find("a", href=re.compile(r"#go_to_message(\d+)"))
        if link:
            rec["reply_to"] = int(re.search(r"(\d+)", link["href"]).group(1))

    fwd = body.find("div", class_="forwarded")
    if fwd is not None:
        fwd_from = fwd.find("div", class_="from_name")
        if fwd_from:
            rec["forwarded_from"] = clean_text(fwd_from).split("\n")[0]

    media = body.find("div", class_="media_wrap")
    if media is not None:
        kind = "media"
        for cls, name in MEDIA_CLASSES.items():
            if media.find(class_=cls) is not None:
                kind = name
                break
        rec["media"] = kind
        title_div = media.find("div", class_="title")
        if title_div:
            rec["media_title"] = clean_text(title_div)

    text_div = body.find("div", class_="text", recursive=False)
    rec["text"] = clean_text(text_div)

    return rec, sender


def parse_chat_folder(folder: Path):
    """Returns (title, messages, warnings)."""
    warnings = []
    pages = sorted(
        folder.glob("messages*.html"),
        key=lambda p: int(re.search(r"messages(\d*)\.html", p.name).group(1) or 1),
    )
    if not pages:
        return None, [], [f"no messages*.html found in {folder.name}"]

    title = None
    messages = []
    for page in pages:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "lxml")
        if title is None:
            header = soup.find("div", class_="page_header")
            if header:
                title = clean_text(header.find("div", class_="text"))
        prev_sender = None
        history = soup.find("div", class_="history")
        if history is None:
            warnings.append(f"{page.name}: no history section")
            continue
        for div in history.find_all("div", class_="message", recursive=False):
            rec, prev_sender = parse_message_div(div, prev_sender)
            if rec is not None:
                messages.append(rec)
    return title, messages, warnings


def merge_messages(existing, new):
    by_id = {m["id"]: m for m in existing if m.get("id") is not None}
    for m in new:
        if m.get("id") is not None:
            by_id[m["id"]] = m
    return sorted(by_id.values(), key=lambda m: m["id"])


def ingest(export_root: Path):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []
    for folder in sorted(p for p in export_root.iterdir() if p.is_dir()):
        title, messages, warnings = parse_chat_folder(folder)
        slug = slugify(folder.name)
        if not messages:
            warnings = warnings or ["empty export"]
            (OUT_DIR / f"{slug}.meta.json").write_text(json.dumps(
                {"chat": folder.name, "slug": slug, "messages": 0, "warnings": warnings}, indent=2))
            summary.append({"chat": folder.name, "slug": slug, "messages": 0, "warnings": warnings})
            continue

        out_path = OUT_DIR / f"{slug}.jsonl"
        if out_path.exists():
            existing = [json.loads(line) for line in out_path.read_text().splitlines() if line.strip()]
            messages = merge_messages(existing, messages)

        with out_path.open("w", encoding="utf-8") as f:
            for msg in messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")

        chat_msgs = [m for m in messages if not m.get("service")]
        timestamps = [m["ts"] for m in chat_msgs if m.get("ts")]
        senders = {}
        for m in chat_msgs:
            if m.get("sender"):
                senders[m["sender"]] = senders.get(m["sender"], 0) + 1
        meta = {
            "chat": folder.name,
            "title": title,
            "slug": slug,
            "messages": len(chat_msgs),
            "service_events": len(messages) - len(chat_msgs),
            "first_ts": min(timestamps) if timestamps else None,
            "last_ts": max(timestamps) if timestamps else None,
            "senders": dict(sorted(senders.items(), key=lambda kv: -kv[1])),
            "warnings": warnings,
            "ingested_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (OUT_DIR / f"{slug}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        summary.append({"chat": folder.name, "slug": slug, "messages": len(chat_msgs), "warnings": warnings})

    return summary


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    export_root = Path(sys.argv[1]).expanduser()
    if not export_root.is_dir():
        sys.exit(f"export root not found: {export_root}")
    summary = ingest(export_root)
    width = max(len(s["chat"]) for s in summary)
    for s in summary:
        line = f"{s['chat']:<{width}}  {s['messages']:>6} messages"
        if s["warnings"]:
            line += f"  ⚠ {'; '.join(s['warnings'])}"
        print(line)
    print(f"\nOutput: {OUT_DIR}")


if __name__ == "__main__":
    main()
