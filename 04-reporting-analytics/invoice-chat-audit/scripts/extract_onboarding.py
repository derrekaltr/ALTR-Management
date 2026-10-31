#!/usr/bin/env python3
"""Extract onboarding-relevant conversation from parsed chats.

Two sources of signal, merged into segments per chat:
  1. The chat-opening window (group creation, intros, first setup steps).
  2. Onboarding keyword hits anywhere in the chat (logins, contracts,
     content drives, page setup, socials, going live, team intros).

Usage: python3 scripts/extract_onboarding.py [--parsed data/parsed] [--out data/onboarding]
Output: data/onboarding/<chat>.md  (redacted, human/LLM-readable)
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.redact import redact
from config.roles import role_of

CONTEXT = 4          # messages of context around a keyword hit
OPENING_MSGS = 120   # first N non-service messages are always included

KEYWORDS = re.compile(r"""(?ix)
    \bonboard | \bwelcome\b | kick[\s-]?off | \bintro(?:duc|s\b)
  | \blog[\s-]?in | \blogin | credential | password | \b2fa\b | \botp\b
  | verification | \bverify | auth\s*code | \bcode\b.{0,20}(?:text|sms|email)
  | contract | agreement | \bsign(?:ed|ing)?\b | docusign | \bw-?9\b | \bkyc\b
  | \bid\b.{0,15}(?:front|back|selfie) | passport | driver'?s?\s+licen
  | onlyfans | \bof\s+(?:page|account|login) | \bfansly | infloww | \binflow\b
  | \bvault | google\s*drive | \bdrive\s*(?:link|folder) | dropbox | \bfolder\b
  | content\s+(?:upload|dump|schedule|calendar|plan)
  | \bmenu\b | \bppv | price\s*list | pricing | \bbio\b | linktree | \blink\s+in\s+bio
  | instagram | \big\b | tiktok | twitter | \bx\s+account | reddit | snapchat
  | \bpromo | shout\s*out | \bads?\b.{0,15}(?:run|buy|budget)
  | questionnaire | \bform\b | \bnotion | \bsheet\b | \bmodel\s+info
  | go(?:ing)?\s+live | launch | \bfirst\s+(?:post|day|week)
  | \bchat(?:ter|ting)\s+team | \bchat\s+manager | account\s+manager
  | \btelegram\s+(?:group|chat) | added\s+to\s+the\s+group
  | \bpercentage | \bsplit\b | \brev\s*share | commission
  | \bpayout | \bbank\b.{0,20}(?:connect|link|setup|set\s+up)
""")


def load(path):
    return [json.loads(ln) for ln in path.open(encoding="utf-8")]


def find_hits(msgs):
    hits = set()
    n_nonservice = 0
    for i, m in enumerate(msgs):
        if m["service"]:
            # group membership / creation events are onboarding signal too
            if m.get("service_text"):
                hits.add(i)
            continue
        if n_nonservice < OPENING_MSGS:
            hits.add(i)
        n_nonservice += 1
        blob = " ".join([
            m.get("text") or "",
            " ".join(m.get("links") or []),
            (m.get("media") or {}).get("name") or "",
            m.get("topic") or "",
        ])
        if KEYWORDS.search(blob):
            hits.add(i)
    return hits


def expand(msgs, hits):
    include = set()
    for i in hits:
        include.update(range(max(0, i - CONTEXT), min(len(msgs) - 1, i + CONTEXT) + 1))
    ordered = sorted(include)
    segments, cur = [], []
    for idx in ordered:
        if cur and idx - cur[-1] > 1:
            segments.append(cur)
            cur = []
        cur.append(idx)
    if cur:
        segments.append(cur)
    return segments


def fmt_msg(chat, m, hits, idx):
    ts = (m.get("ts") or "")[:16].replace("T", " ")
    sender = m.get("sender") or "?"
    role = role_of(chat, sender)
    role_tag = f" ({role})" if role != "unknown" else ""
    head = f"[{ts}] {sender}{role_tag}"
    if m.get("topic"):
        head += f" [topic:{m['topic']}]"
    body_bits = []
    media = m.get("media")
    if media:
        name = media.get("name") or media.get("href") or media.get("kind")
        body_bits.append(f"[{(media.get('kind') or 'media').upper()}: {name}]")
    if m.get("text"):
        body_bits.append(m["text"])
    body = " ".join(body_bits) or "(no text)"
    marker = "*" if idx in hits else " "
    return redact(f"{marker}{head}: {body}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parsed", default="data/parsed")
    ap.add_argument("--out", default="data/onboarding")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(Path(args.parsed).glob("*.jsonl")):
        chat = path.stem
        msgs = load(path)
        hits = find_hits(msgs)
        segments = expand(msgs, hits)
        md = out_dir / f"{chat}.md"
        n = 0
        with md.open("w", encoding="utf-8") as fh:
            fh.write(f"# Onboarding extract — {chat}\n")
            for si, seg in enumerate(segments, 1):
                first, last = msgs[seg[0]], msgs[seg[-1]]
                fh.write(f"\n### Segment {si} ({(first.get('ts') or '?')[:10]} → {(last.get('ts') or '?')[:10]})\n")
                for idx in seg:
                    m = msgs[idx]
                    if m["service"]:
                        if m.get("service_text"):
                            fh.write(f"  [service] {redact(m['service_text'])}\n")
                        continue
                    fh.write(fmt_msg(chat, m, hits, idx) + "\n")
                    n += 1
        print(f"{chat}: {len(hits)} hits, {len(segments)} segments, {n} msgs -> {md}")


if __name__ == "__main__":
    main()
