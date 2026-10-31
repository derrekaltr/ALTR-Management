"""Monthly content drop: generate ideas per client and send a Content Snare request.

For each client in clients.csv:
  1. Get this month's content ideas — from ideas_override/YYYY-MM/<email>.md if
     present (e.g. pasted from GPTease), otherwise generated with the Claude API,
     tailored to the client's comfort level (non_nude / topless / full_nude).
  2. Create + publish a Content Snare request from the matching tier template.
     Content Snare's communications schedule then handles all reminders.
  3. Write outbox/YYYY-MM/<email>.md with the ideas + the request link, ready to
     send to the client (or wire up SMTP/your CRM to send automatically).

Usage:
  python3 monthly_drop.py            # real run
  python3 monthly_drop.py --dry-run  # generate ideas only, no Content Snare calls
"""

import calendar
import csv
import datetime
import os
import re
import sys

from cs_common import BASE_DIR, cs_api, load_env

load_env()

TEMPLATE_BY_TIER = {
    "non_nude": os.environ.get("CS_TEMPLATE_NON_NUDE", "Content Drop — Non Nude"),
    "topless": os.environ.get("CS_TEMPLATE_TOPLESS", "Content Drop — Topless"),
    "full_nude": os.environ.get("CS_TEMPLATE_FULL_NUDE", "Content Drop — Full Nude"),
}

TIER_GUIDANCE = {
    "non_nude": (
        "The creator does NOT shoot nude or topless content. Every idea must work "
        "fully clothed or in swimwear/lingerie-level outfits at most: lifestyle, "
        "cosplay, fitness, tease/implied, POV girlfriend-experience themes."
    ),
    "topless": (
        "The creator is comfortable with topless/partially nude content but not "
        "full nudity. Mix clothed tease concepts with artistic topless concepts."
    ),
    "full_nude": (
        "The creator is comfortable with full nude content. Mix clothed tease, "
        "topless, and tasteful full-nude concepts (boudoir, artistic, implied-solo)."
    ),
}

IDEA_PROMPT = """You are a content strategist for an OnlyFans creator agency.
Generate exactly 8 photo/video shoot concepts for the coming month for this creator.

Creator profile:
- Niche: {niche}
- Notes from her manager: {notes}
- Comfort level: {tier}. {tier_guidance}

Rules:
- Stay strictly within the stated comfort level; never suggest anything beyond it.
- Describe each concept in tasteful, non-graphic language: theme, outfit/styling,
  setting, lighting/mood, and 2-3 shot or clip suggestions. No explicit sexual
  descriptions — these are professional shoot briefs.
- Make ideas seasonal for {month_name} and varied (mix of quick phone content and
  one bigger "set piece" shoot).

Format as a markdown numbered list. Each item: a bold title line, then the brief.
Output only the list, no preamble."""


def slug(email):
    return re.sub(r"[^a-z0-9]+", "-", email.lower()).strip("-")


def month_context(today):
    last_day = calendar.monthrange(today.year, today.month)[1]
    return {
        "key": today.strftime("%Y-%m"),
        "name": today.strftime("%B %Y"),
        "due": today.replace(day=last_day).isoformat(),
    }


def get_ideas(client, month):
    override = os.path.join(BASE_DIR, "ideas_override", month["key"], f"{slug(client['email'])}.md")
    if os.path.exists(override):
        print(f"  using override file: {override}")
        with open(override) as f:
            return f.read().strip()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            f"No ANTHROPIC_API_KEY set and no override file for {client['email']} "
            f"(expected {override}). Either set the key in .env or paste ideas "
            "(e.g. from GPTease) into that file."
        )

    import anthropic

    api = anthropic.Anthropic()
    tier = client["comfort_level"]
    prompt = IDEA_PROMPT.format(
        niche=client.get("niche") or "general",
        notes=client.get("notes") or "none",
        tier=tier.replace("_", " "),
        tier_guidance=TIER_GUIDANCE[tier],
        month_name=month["name"],
    )
    response = api.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in response.content if b.type == "text").strip()


def create_request(client, month):
    payload = {
        "client_email": client["email"],
        "client_full_name": client["full_name"],
        "name": f"{month['name']} Content Drop — {client['full_name'].split()[0]}",
        "request_template_name": TEMPLATE_BY_TIER[client["comfort_level"]],
        "communication_template_name": os.environ.get("CS_COMMUNICATION_TEMPLATE", "Default"),
        "folder_name": os.environ.get("CS_FOLDER_NAME", "Monthly Content Drops"),
        "due": month["due"],
        "status": "published",
        "comments_enabled": True,
        "share_via_link_enabled": True,
    }
    return cs_api("POST", "/requests", payload)


def write_outbox(client, month, ideas, request):
    out_dir = os.path.join(BASE_DIR, "outbox", month["key"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{slug(client['email'])}.md")
    link = request.get("share_link") or request.get("url") or "(publish pending)"
    with open(path, "w") as f:
        f.write(
            f"# {month['name']} Content Drop — {client['full_name']}\n\n"
            f"Hey {client['full_name'].split()[0]}! Here are your content ideas for "
            f"{month['name']}. Upload everything here by {month['due']}:\n\n"
            f"**Upload link:** {link}\n\n---\n\n{ideas}\n"
        )
    return path


def main():
    dry_run = "--dry-run" in sys.argv
    month = month_context(datetime.date.today())
    clients_path = os.path.join(BASE_DIR, "clients.csv")

    with open(clients_path) as f:
        clients = [row for row in csv.DictReader(f) if row.get("email")]

    for client in clients:
        tier = (client.get("comfort_level") or "").strip().lower()
        if tier not in TEMPLATE_BY_TIER:
            print(f"SKIP {client['email']}: comfort_level must be one of {list(TEMPLATE_BY_TIER)}")
            continue
        client["comfort_level"] = tier

        print(f"\n=== {client['full_name']} ({tier}) ===")
        ideas = get_ideas(client, month)

        if dry_run:
            request = {}
            print("  dry run — skipping Content Snare request creation")
        else:
            request = create_request(client, month)
            print(f"  Content Snare request created: {request.get('id')} ({request.get('status')})")

        path = write_outbox(client, month, ideas, request)
        print(f"  ideas + link written to {path}")

    print("\nDone. Content Snare will handle reminder emails per your communications schedule.")


if __name__ == "__main__":
    main()
