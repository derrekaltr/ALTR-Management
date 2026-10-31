#!/usr/bin/env python3
"""Invariant checks for the pipeline. Exits non-zero on failure.

Usage: python3 scripts/verify.py "<export_dir>"
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.redact import LITERALS

FAIL = 0


def check(name, ok, detail=""):
    global FAIL
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        FAIL = 1


def main():
    export_dir = Path(sys.argv[1])
    parsed_dir = Path("data/parsed")
    inv_dir = Path("data/invoicing")

    for chat_dir in sorted(d for d in export_dir.iterdir()
                           if d.is_dir() and list(d.glob("messages*.html"))):
        chat = chat_dir.name
        raw_count = 0
        for f in chat_dir.glob("messages*.html"):
            raw_count += f.read_text(encoding="utf-8").count('class="message default')
        pf = parsed_dir / f"{chat}.jsonl"
        msgs = [json.loads(ln) for ln in pf.open(encoding="utf-8")]
        default = [m for m in msgs if not m["service"]]
        check(f"{chat}: parsed count == raw count", len(default) == raw_count,
              f"{len(default)} vs {raw_count}")
        check(f"{chat}: no null timestamps", all(m["ts"] for m in default))
        check(f"{chat}: no null senders", all(m["sender"] for m in default))
        ids = [m["id"] for m in msgs if m["id"] is not None and m["id"] > 0]
        check(f"{chat}: ids monotonic across files", ids == sorted(ids))

        # extraction recall: every text mention of 'invoic' is in the extract
        inv_ids = {m["id"] for m in default
                   if re.search("invoic", m.get("text") or "", re.I)}
        ef = inv_dir / f"{chat}.jsonl"
        ext_ids = ({json.loads(ln)["id"] for ln in ef.open(encoding="utf-8")}
                   if ef.exists() else set())
        check(f"{chat}: extraction recall", inv_ids <= ext_ids,
              f"missing {sorted(inv_ids - ext_ids)[:5]}" if inv_ids - ext_ids else "")

    # redaction: known PII literals must not appear in extracts or report
    leak = []
    for p in list(inv_dir.glob("*.md")) + list(Path("report").glob("*.md")):
        content = p.read_text(encoding="utf-8")
        for lit, _ in LITERALS:
            if lit in content:
                leak.append(f"{p}:{lit}")
    check("no PII literals in extracts/report", not leak, "; ".join(leak))

    # git must never track data/
    tracked = subprocess.run(["git", "ls-files", "data/"],
                             capture_output=True, text=True).stdout.strip()
    check("data/ not tracked by git", not tracked, tracked[:100])

    sys.exit(FAIL)


if __name__ == "__main__":
    main()
