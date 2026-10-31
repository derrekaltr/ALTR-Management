#!/usr/bin/env python3
"""Render full, redacted, human/LLM-readable transcripts of every parsed chat.

Usage: python3 scripts/render_transcripts.py [--parsed data/parsed] [--out data/transcripts]

Unlike extract_invoicing.py this renders EVERY message (topic-agnostic
analyses like the services catalog need the whole conversation).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.redact import redact
from config.roles import role_of


def fmt(chat, m):
    ts = (m.get("ts") or "")[:16].replace("T", " ")
    sender = m.get("sender") or "?"
    role = role_of(chat, sender)
    role_tag = f" ({role})" if role == "client" else ""
    parts = [f"[{ts}] #{m.get('id')} {sender}{role_tag}"]
    if m.get("topic"):
        parts.append(f"[topic:{m['topic']}]")
    elif m.get("reply_to") is not None:
        parts.append(f"[reply→{m['reply_to']}]")
    if m.get("forwarded"):
        parts.append("[fwd]")
    head = " ".join(parts)
    bits = []
    media = m.get("media")
    if media:
        name = media.get("name") or media.get("href") or media.get("kind")
        bits.append(f"[{media.get('kind', 'media').upper()}: {name}]")
    if m.get("text"):
        bits.append(m["text"])
    if m.get("reactions"):
        bits.append(" ".join(f"{{{r.get('emoji', '?')} {', '.join(r.get('by') or ['?'])}}}"
                             for r in m["reactions"]))
    return redact(f"{head}: {' '.join(bits) if bits else '(no text)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parsed", default="data/parsed")
    ap.add_argument("--out", default="data/transcripts")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(Path(args.parsed).glob("*.jsonl")):
        chat = path.stem
        msgs = [json.loads(ln) for ln in path.open(encoding="utf-8")]
        out = out_dir / f"{chat}.md"
        with out.open("w", encoding="utf-8") as fh:
            fh.write(f"# Full transcript — {chat}\n\n")
            for m in msgs:
                if m["service"]:
                    if m.get("service_text"):
                        fh.write(f"[service] {redact(m['service_text'])}\n")
                    continue
                fh.write(fmt(chat, m) + "\n")
        print(f"{chat}: {sum(1 for m in msgs if not m['service'])} messages -> {out}")


if __name__ == "__main__":
    main()
