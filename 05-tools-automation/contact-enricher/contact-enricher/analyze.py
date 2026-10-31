#!/usr/bin/env python3
"""Classify conversation dossiers with headless Claude Code (claude -p).

Each dossier becomes data/analyses/<handle>.json:
{name, name_confidence, category, category_confidence, summary, key_facts,
 services_discussed, analyzed_rowid}
"""

import argparse
import concurrent.futures
import glob
import json
import os
import re
import subprocess

import common

CATEGORIES = ["ALTR Media Group", "ALTR MGMT", "ALTR Services", "Personal", "Unknown"]

PROMPT_TEMPLATE = """You are classifying a text-message conversation to build a contact entry.
The phone owner runs three business lines:

1. "ALTR Media Group" — music promotion / traffic driving (phone farm). Clients want
   to promote music, audio tracks, brands, or creator content, drive streams/traffic.
2. "ALTR MGMT" (aka Alter Management / Social Depot) — OnlyFans management agency.
   Signals: earnings screenshots, revenue percentage splits, account management,
   chatting/marketing for OF creators.
3. "ALTR Services" — social media account services: Instagram unbans, account
   recoveries, shadow-ban removal, IG restriction fixes, TikTok verifications,
   TikTok unbans, meta/social platform account issues.

Anyone else is "Personal" (friend/family/acquaintance) or "Unknown" (can't tell).

Below is the conversation with {handle} ({total} messages, {first_date} to {last_date}).
{attachment_note}

Determine:
- The person's real name (from introductions, sign-offs, payment app names, context).
- Which category best fits them.
- A 2-4 sentence summary: who they are, what they wanted/bought, current status,
  anything useful for follow-up.
- key_facts: short bullet facts worth remembering (prices agreed, accounts worked on,
  outcomes, referrals).
- services_discussed: specific services/products discussed, if any.

Respond with ONLY this JSON (no markdown fences, no other text):
{{"name": string or null, "name_confidence": 0.0-1.0, "category": one of {categories},
"category_confidence": 0.0-1.0, "summary": string, "key_facts": [strings],
"services_discussed": [strings]}}

TRANSCRIPT:
{transcript}
"""

ATTACHMENT_NOTE = (
    "Also examine these image attachments from the conversation (use the Read tool "
    "on each path); they may contain earnings screenshots, account screenshots, or "
    "other identifying context:\n{paths}"
)


def build_prompt(dossier):
    attachment_note = ""
    if dossier.get("attachments"):
        attachment_note = ATTACHMENT_NOTE.format(
            paths="\n".join(dossier["attachments"])
        )
    return PROMPT_TEMPLATE.format(
        handle=dossier["handle"],
        total=dossier["total"],
        first_date=dossier["first_date"],
        last_date=dossier["last_date"],
        attachment_note=attachment_note,
        categories=json.dumps(CATEGORIES),
        transcript="\n".join(dossier["transcript"]),
    )


def parse_json_reply(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    candidates = [text]
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        candidates.append(match.group(0))
    last_error = None
    for candidate in candidates:
        for attempt in (candidate, candidate.replace("\n", " ")):
            try:
                # strict=False tolerates raw control characters inside strings.
                return json.loads(attempt, strict=False)
            except json.JSONDecodeError as exc:
                last_error = exc
    raise last_error


def run_claude(prompt, timeout, retries=2):
    last_error = None
    for attempt in range(retries + 1):
        try:
            proc = subprocess.run(
                [
                    "claude", "-p",
                    "--output-format", "json",
                    "--allowedTools", "Read",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"claude -p failed: {proc.stderr[:500]}")
            wrapper = json.loads(proc.stdout)
            return parse_json_reply(wrapper["result"])
        except (json.JSONDecodeError, RuntimeError, subprocess.TimeoutExpired) as exc:
            last_error = exc
    raise last_error


def validate(result):
    if result.get("category") not in CATEGORIES:
        result["category"] = "Unknown"
    result.setdefault("name", None)
    result.setdefault("name_confidence", 0.0)
    result.setdefault("category_confidence", 0.0)
    result.setdefault("summary", "")
    result.setdefault("key_facts", [])
    result.setdefault("services_discussed", [])
    return result


def analyze_one(dossier_path, timeout):
    with open(dossier_path) as f:
        dossier = json.load(f)
    handle = dossier["handle"]
    out_path = os.path.join(
        common.DATA_DIR, "analyses", common.safe_filename(handle) + ".json"
    )
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing = json.load(f)
        if existing.get("analyzed_rowid") == dossier["max_rowid"]:
            return handle, "unchanged"

    result = validate(run_claude(build_prompt(dossier), timeout))
    result["handle"] = handle
    result["analyzed_rowid"] = dossier["max_rowid"]
    result["message_count"] = dossier["total"]
    result["first_date"] = dossier["first_date"]
    result["last_date"] = dossier["last_date"]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=1)
    return handle, f"{result['category']} / {result.get('name')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="analyze at most N dossiers")
    ap.add_argument("--handles", help="comma-separated handle ids (testing)")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600, help="seconds per claude call")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(common.DATA_DIR, "dossiers", "*.json")))
    if args.handles:
        wanted = {common.safe_filename(h) for h in args.handles.split(",")}
        paths = [p for p in paths if os.path.splitext(os.path.basename(p))[0] in wanted]
    if args.limit:
        paths = paths[: args.limit]

    print(f"analyzing {len(paths)} dossiers ({args.parallel} in parallel)")
    done = errors = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(analyze_one, p, args.timeout): p for p in paths}
        for fut in concurrent.futures.as_completed(futures):
            path = futures[fut]
            try:
                handle, status = fut.result()
                done += 1
                print(f"  [{done}/{len(paths)}] {handle}: {status}")
            except Exception as exc:
                errors += 1
                print(f"  ERROR {os.path.basename(path)}: {exc}")
    print(f"done: {done} ok, {errors} errors")


if __name__ == "__main__":
    main()
