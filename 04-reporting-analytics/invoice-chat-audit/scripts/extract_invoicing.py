#!/usr/bin/env python3
"""Extract invoicing-relevant conversation segments from parsed chats.

Usage: python3 scripts/extract_invoicing.py [--parsed data/parsed] [--out data/invoicing]

For each chat:
  data/invoicing/<chat>.jsonl - included messages tagged with segment_id + hit info
  data/invoicing/<chat>.md    - redacted, human/LLM-readable transcript by segment
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.keywords import is_primary, is_invoice_pdf
from config.redact import redact
from config.roles import role_of

CONTEXT = 6  # messages of context on each side of a primary hit


def load(path):
    return [json.loads(ln) for ln in path.open(encoding="utf-8")]


def find_hits(msgs):
    """Return set of indices that are primary invoicing hits."""
    hits = set()
    for i, m in enumerate(msgs):
        if m["service"]:
            continue
        text = m.get("text") or ""
        links = " ".join(m.get("links") or [])
        media = m.get("media") or {}
        if is_primary(text) or is_primary(links):
            hits.add(i)
        elif media.get("name") and (is_invoice_pdf(media["name"]) or is_primary(media["name"] or "")):
            hits.add(i)
        elif m.get("topic") == "Invoicing" and (text or media):
            hits.add(i)
    return hits


def expand(msgs, hits):
    """Expand hits by +-CONTEXT messages and full reply chains; merge into segments."""
    by_id = {m["id"]: i for i, m in enumerate(msgs) if m.get("id") is not None}
    include = set()
    for i in hits:
        lo, hi = max(0, i - CONTEXT), min(len(msgs) - 1, i + CONTEXT)
        include.update(range(lo, hi + 1))
        # upward reply chain
        j = i
        for _ in range(20):
            rt = msgs[j].get("reply_to")
            if rt is None or rt not in by_id:
                break
            j = by_id[rt]
            include.add(j)
    # direct replies to hits
    hit_ids = {msgs[i]["id"] for i in hits}
    for i, m in enumerate(msgs):
        if m.get("reply_to") in hit_ids:
            include.add(i)

    ordered = sorted(include)
    segments = []
    cur = []
    for idx in ordered:
        if cur and idx - cur[-1] > 1:
            segments.append(cur)
            cur = []
        cur.append(idx)
    if cur:
        segments.append(cur)
    return segments


def fmt_msg(chat, m, hits_idx, idx):
    ts = (m.get("ts") or "")[:16].replace("T", " ")
    sender = m.get("sender") or "?"
    role = role_of(chat, sender)
    role_tag = f" ({role})" if role in ("client", "staff_billing") else ""
    parts = [f"[{ts}] #{m.get('id')} {sender}{role_tag}"]
    if m.get("topic"):
        parts.append(f"[topic:{m['topic']}]")
    if m.get("reply_to") is not None and m.get("topic") is None:
        parts.append(f"[reply→{m['reply_to']}]")
    if m.get("forwarded"):
        parts.append("[fwd]")
    head = " ".join(parts)
    body_bits = []
    media = m.get("media")
    if media:
        name = media.get("name") or media.get("href") or media.get("kind")
        body_bits.append(f"[{media.get('kind', 'media').upper()}: {name}]")
    if m.get("text"):
        body_bits.append(m["text"])
    if m.get("reactions"):
        rx = " ".join(f"{{{r.get('emoji', '?')} {', '.join(r.get('by') or ['?'])}}}"
                      for r in m["reactions"])
        body_bits.append(rx)
    body = " ".join(body_bits) if body_bits else "(no text)"
    marker = "*" if idx in hits_idx else " "
    return redact(f"{marker}{head}: {body}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parsed", default="data/parsed")
    ap.add_argument("--out", default="data/invoicing")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(Path(args.parsed).glob("*.jsonl")):
        chat = path.stem
        msgs = load(path)
        hits = find_hits(msgs)
        segments = expand(msgs, hits)

        jl = out_dir / f"{chat}.jsonl"
        md = out_dir / f"{chat}.md"
        n_inc = 0
        with jl.open("w", encoding="utf-8") as jfh, md.open("w", encoding="utf-8") as mfh:
            mfh.write(f"# Invoicing extract — {chat}\n\n")
            mfh.write(f"Primary hits: {len(hits)} · segments: {len(segments)} · "
                      f"lines marked * are keyword/PDF/topic hits\n")
            for si, seg in enumerate(segments, 1):
                first, last = msgs[seg[0]], msgs[seg[-1]]
                mfh.write(f"\n### Segment {si}  "
                          f"({(first.get('ts') or '')[:10]} → {(last.get('ts') or '')[:10]})\n")
                for idx in seg:
                    m = msgs[idx]
                    if m["service"]:
                        if m.get("service_text"):
                            mfh.write(f"  [service] {redact(m['service_text'])}\n")
                        continue
                    mfh.write(fmt_msg(chat, m, hits, idx) + "\n")
                    rec = dict(m)
                    rec["segment_id"] = si
                    rec["is_hit"] = idx in hits
                    jfh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n_inc += 1
        print(f"{chat}: {len(hits)} hits → {len(segments)} segments, {n_inc} messages")


if __name__ == "__main__":
    main()
