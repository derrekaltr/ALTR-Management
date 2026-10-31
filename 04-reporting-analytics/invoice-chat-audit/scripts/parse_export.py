#!/usr/bin/env python3
"""Parse Telegram Desktop HTML exports into normalized JSONL, one file per chat.

Usage: python3 scripts/parse_export.py "<export_dir>" [--out data/parsed]

Each chat folder under <export_dir> must contain messages.html (and optionally
messages2.html, messages3.html, ... which continue chronologically).

Output schema (one JSON object per line):
  chat, id, ts, sender, joined, service, service_text, reply_to, topic,
  text, links, media {kind, name, size, href}, reactions [{emoji, by}],
  source_file
"""
import argparse
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

TS_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2}) UTC([+-]\d{2}):?(\d{2})")
GOTO_RE = re.compile(r"#go_to_message(-?\d+)")
TOPIC_RE = re.compile(r"created topic «(.+?)»")


def parse_ts(title):
    m = TS_RE.search(title)
    if not m:
        return None
    d, mo, y, h, mi, s, oh, om = m.groups()
    return f"{y}-{mo}-{d}T{h}:{mi}:{s}{oh}:{om}"


class TelegramExportParser(HTMLParser):
    """State-machine parser for Telegram Desktop HTML export files."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.messages = []
        self.depth = 0
        self.msg = None            # current message dict
        self.msg_depth = None
        # capture state: (field, start_depth, buffer)
        self.capture = None
        self.in_reply_to = False
        self.in_reactions = False
        self.cur_reaction = None
        self.in_media = None       # media dict being built
        self.media_field = None    # 'name' | 'size' capture inside media

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def classes(attrs):
        return dict(attrs).get("class", "").split()

    def start_capture(self, field):
        self.capture = [field, self.depth, []]

    def end_capture(self):
        field, _, buf = self.capture
        text = "".join(buf)
        # collapse whitespace but keep intentional newlines from <br>
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
        text = "\n".join(lines).strip()
        self.capture = None
        return field, text

    # -- HTMLParser hooks ---------------------------------------------------
    def handle_starttag(self, tag, attrs):
        self.depth += 1
        if tag == "br":
            self.depth -= 1  # br is void
            if self.capture:
                self.capture[2].append("\n")
            return
        if tag in ("img", "meta", "link", "input", "hr"):
            self.depth -= 1  # void elements
            a = dict(attrs)
            if self.in_reactions and self.cur_reaction is not None and a.get("title"):
                self.cur_reaction["by"].append(a["title"])
            return

        cls = self.classes(attrs)
        a = dict(attrs)

        if tag == "div" and "message" in cls:
            self.flush_message()
            mid = a.get("id", "")
            try:
                num = int(mid.replace("message", ""))
            except ValueError:
                num = None
            self.msg = {
                "id": num,
                "ts": None,
                "sender": None,
                "joined": "joined" in cls,
                "service": "service" in cls,
                "service_text": None,
                "reply_to": None,
                "topic": None,
                "text": "",
                "links": [],
                "media": None,
                "reactions": [],
            }
            self.msg_depth = self.depth
            return

        if self.msg is None:
            return

        # timestamp
        if tag == "div" and "date" in cls and "details" in cls and a.get("title"):
            self.msg["ts"] = parse_ts(a["title"])
            return
        # sender
        if tag == "div" and "from_name" in cls:
            self.start_capture("sender")
            return
        # service body
        if tag == "div" and self.msg["service"] and "body" in cls and "details" in cls:
            self.start_capture("service_text")
            return
        # reply
        if tag == "div" and "reply_to" in cls:
            self.in_reply_to = True
            return
        if tag == "a" and self.in_reply_to:
            m = GOTO_RE.search(a.get("href", ""))
            if m:
                self.msg["reply_to"] = int(m.group(1))
            return
        # text body
        if tag == "div" and cls == ["text"]:
            self.start_capture("text")
            return
        # links inside text
        if tag == "a" and self.capture and self.capture[0] == "text":
            href = a.get("href", "")
            if href and not href.startswith("#"):
                self.msg["links"].append(href)
            return
        # media
        if "media_wrap" in cls:
            return
        if tag in ("a", "div") and any(c.startswith("media_") or c == "media" for c in cls) and "media_wrap" not in cls:
            kind = "file"
            for c in cls:
                if c == "media_file":
                    kind = "file"
                elif c == "media_photo":
                    kind = "photo"
                elif c == "media_video":
                    kind = "video"
                elif c == "media_voice_message":
                    kind = "voice"
                elif c == "media_audio_file":
                    kind = "audio"
                elif c == "media_contact":
                    kind = "contact"
                elif c == "media_location":
                    kind = "location"
                elif c == "media_poll":
                    kind = "poll"
                elif c == "media_call":
                    kind = "call"
            self.in_media = {"kind": kind, "name": None, "size": None, "href": a.get("href")}
            return
        if tag == "a" and "photo_wrap" in cls:
            self.msg["media"] = {"kind": "photo", "name": None, "size": None, "href": a.get("href")}
            return
        if tag == "a" and "video_file_wrap" in cls:
            self.msg["media"] = {"kind": "video", "name": None, "size": None, "href": a.get("href")}
            return
        if tag == "a" and "sticker_wrap" in cls:
            self.msg["media"] = {"kind": "sticker", "name": None, "size": None, "href": a.get("href")}
            return
        if self.in_media is not None and tag == "div":
            if "title" in cls:
                self.start_capture("media_name")
                return
            if "status" in cls:
                self.start_capture("media_size")
                return
        # reactions
        if tag == "span" and "reactions" in cls:
            self.in_reactions = True
            return
        if tag == "span" and "reaction" in cls and self.in_reactions:
            self.cur_reaction = {"emoji": None, "by": []}
            return
        if tag == "span" and "emoji" in cls and self.cur_reaction is not None:
            self.start_capture("reaction_emoji")
            return
        if self.in_reactions and self.cur_reaction is not None and a.get("title"):
            self.cur_reaction["by"].append(a["title"])
            return

    def handle_endtag(self, tag):
        if tag in ("br", "img", "meta", "link", "input", "hr"):
            return
        if self.capture and self.depth == self.capture[1]:
            field, text = self.end_capture()
            if self.msg is not None:
                if field == "sender":
                    self.msg["sender"] = text
                elif field == "service_text":
                    self.msg["service_text"] = text
                elif field == "text":
                    self.msg["text"] = text
                elif field == "media_name" and self.in_media is not None:
                    self.in_media["name"] = text
                elif field == "media_size" and self.in_media is not None:
                    self.in_media["size"] = text
                elif field == "reaction_emoji" and self.cur_reaction is not None:
                    self.cur_reaction["emoji"] = text
        if tag == "div" and self.in_reply_to:
            self.in_reply_to = False
        if self.in_media is not None and tag == "div" and self.capture is None:
            # close media block when its container div ends (heuristic: name+size set)
            pass
        if tag == "span" and self.cur_reaction is not None and self.capture is None:
            # reaction span closing handled when reactions span closes
            pass
        if self.msg is not None and self.msg_depth is not None and self.depth == self.msg_depth:
            self.flush_message()
        if tag == "span" and self.in_reactions and self.cur_reaction is not None:
            # end of a reaction sub-span: commit when emoji present and depth shallow
            if self.cur_reaction.get("emoji") and self.msg is not None:
                # commit once per reaction span end; avoid duplicates by checking last
                if not self.msg["reactions"] or self.msg["reactions"][-1] is not self.cur_reaction:
                    self.msg["reactions"].append(self.cur_reaction)
        self.depth -= 1

    def handle_data(self, data):
        if self.capture:
            self.capture[2].append(data)

    def flush_message(self):
        if self.msg is not None:
            if self.in_media is not None:
                self.msg["media"] = self.in_media
                self.in_media = None
            # dedupe reactions (same object may be appended via nested spans)
            seen = []
            for r in self.msg["reactions"]:
                if r not in seen:
                    seen.append(r)
            self.msg["reactions"] = seen
            self.messages.append(self.msg)
        self.msg = None
        self.msg_depth = None
        self.in_media = None
        self.cur_reaction = None
        self.in_reactions = False

    def close(self):
        self.flush_message()
        super().close()


def natural_key(p):
    m = re.match(r"messages(\d*)\.html$", p.name)
    return int(m.group(1)) if m and m.group(1) else 0


def parse_chat(chat_dir):
    files = sorted(chat_dir.glob("messages*.html"), key=natural_key)
    all_msgs = []
    for f in files:
        parser = TelegramExportParser()
        parser.feed(f.read_text(encoding="utf-8"))
        parser.close()
        for m in parser.messages:
            m["source_file"] = f.name
        all_msgs.extend(parser.messages)

    # sender carry-forward for joined messages; forwarded messages carry
    # "Name DD.MM.YYYY HH:MM:SS" in from_name — strip the timestamp suffix
    fwd_re = re.compile(r"\s+\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}$")
    last_sender = None
    for m in all_msgs:
        if m["service"]:
            continue
        if m["sender"]:
            cleaned = fwd_re.sub("", m["sender"])
            m["forwarded"] = cleaned != m["sender"]
            m["sender"] = cleaned
            last_sender = cleaned
        elif m["joined"]:
            m["sender"] = last_sender
            m["forwarded"] = False

    # topic map from creation service messages
    topics = {}
    for m in all_msgs:
        if m["service"] and m["service_text"] and m["id"] is not None and m["id"] > 0:
            tm = TOPIC_RE.search(m["service_text"])
            if tm:
                topics[m["id"]] = tm.group(1)

    # topic resolution (direct + transitive through reply chain)
    by_id = {m["id"]: m for m in all_msgs if m["id"] is not None}
    for m in all_msgs:
        rt = m["reply_to"]
        if rt in topics:
            m["topic"] = topics[rt]
    for m in all_msgs:  # transitive, in order (targets are earlier messages)
        rt = m["reply_to"]
        if m["topic"] is None and rt in by_id and by_id[rt].get("topic"):
            m["topic"] = by_id[rt]["topic"]

    return all_msgs, topics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("--out", default="data/parsed")
    args = ap.parse_args()

    export_dir = Path(args.export_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    chat_dirs = sorted(d for d in export_dir.iterdir() if d.is_dir() and list(d.glob("messages*.html")))
    if not chat_dirs:
        sys.exit(f"No chat folders with messages.html found under {export_dir}")

    for chat_dir in chat_dirs:
        chat = chat_dir.name
        msgs, topics = parse_chat(chat_dir)
        out = out_dir / f"{chat}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for m in msgs:
                m["chat"] = chat
                fh.write(json.dumps(m, ensure_ascii=False) + "\n")
        n_default = sum(1 for m in msgs if not m["service"])
        n_null_ts = sum(1 for m in msgs if not m["service"] and not m["ts"])
        print(f"{chat}: {len(msgs)} msgs ({n_default} default, {len(topics)} topics: "
              f"{', '.join(topics.values())}), null-ts={n_null_ts}")


if __name__ == "__main__":
    main()
