#!/usr/bin/env python3
"""
build_outreach.py — draft UNIQUE, approval-gated outreach messages.

A seller is queued only if they offer a NEW service (one ALTR doesn't sell) that is
social-media relevant, and they clear the quality gate (success rate > 60% with feedback).
One personalized draft per seller — each message is unique (varied phrasing + the seller's
real track record + their specific service). Nothing is sent here; status starts as
'pending_approval'. Sending is capped at MAX_SENDS_PER_DAY (see next_batch.py).

Pending drafts are refreshed on re-run; approved/sent entries are left untouched.

Run:  python3 scripts/build_outreach.py
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SOCIAL_ACTIONS = {"unban", "removal", "verification", "monetization", "shielding",
                  "username_claim", "followers", "recovery"}
SOCIAL_PLATFORMS = {"instagram", "tiktok", "youtube", "facebook", "twitter", "snapchat",
                    "telegram", "threads", "linkedin", "whatsapp", "google", "reddit"}

# Human, plain templates. Arc: inquiry about the service they saw -> we have a big marketplace
# that could sell it -> bulk clientele = better price down the line -> we'll show what we can do
# first -> what do you need to get started (so we can build it into our system).
# Reference ONE service. {s}=seller, {svc}=service.
TEMPLATES = [
    "Hi {s}, making an inquiry about your {svc} service I saw on swapd. I run a big services "
    "marketplace (ALTR) that could sell this. If I bring you bulk clients, would you be able to "
    "do a better price down the line? Happy to show you what we can do first — what do you need "
    "to get started so I can have it ready and built into our system?",

    "Hey {s}, I saw your {svc} listing and wanted to ask — I run a large services marketplace "
    "(ALTR) that could move this. If we sent you bulk clientele, could you work out a better rate "
    "down the road? We'll prove ourselves first. What do you need from a client to get started, "
    "so I can set it up in our system?",

    "Hi {s}, quick inquiry on your {svc}. We're ALTR, a big services marketplace that could sell "
    "this for you. If we bring steady bulk clients, would a better price be possible down the "
    "line? Happy to show you what we can do first — just let me know what you need to get a job "
    "started so I can build it into our flow.",

    "Hey {s}, reaching out about the {svc} service you offer. I run a services marketplace (ALTR) "
    "with the reach to sell this at volume. If I bring bulk clientele, could we get to a better "
    "price over time? We'll show you what we can do first. What's needed to get started? I'd like "
    "to have it ready in our system.",

    "Hi {s}, saw your {svc} and wanted to inquire. ALTR (my services marketplace) could sell this "
    "to a lot of clients. If we send bulk volume, would a better price be on the table down the "
    "line? Happy to prove it first — what do you need to get started so I can wire it into our "
    "system?",

    "Hey {s}, inquiring about your {svc} service. I run a large services marketplace (ALTR) that "
    "could push real volume on this. If I bring you bulk clients, could you do better pricing "
    "down the road? We'll show results first — what do you need to get started so I can build it "
    "into our system?",
]


def relevant(service_id):
    parts = service_id.split("_")
    if parts[0] in SOCIAL_PLATFORMS:
        return True
    return any(service_id == a or service_id.startswith(a + "_") or service_id.endswith("_" + a)
               for a in SOCIAL_ACTIONS)


def primary_service(displays):
    """Pick ONE service to name — prefer a specific 2-word label over a generic '* Service'.
    Strip a trailing 'Service' so templates saying '{svc} service' don't double up."""
    ds = sorted(set(displays))
    specific = [d for d in ds if len(d.split()) >= 2 and not d.lower().endswith("service")]
    name = (specific or ds)[0]
    words = name.split()
    if len(words) > 1 and words[-1].lower() == "service":
        name = " ".join(words[:-1])
    return name


def make_message(e):
    s = e["seller"]
    svc = primary_service(e["services"])
    h = sum(ord(c) for c in s)  # deterministic per-seller variant selection
    return TEMPLATES[h % len(TEMPLATES)].format(s=s, svc=svc)


def main():
    services = json.loads((DATA / "services.json").read_text()).get("services", {})
    outreach = json.loads((DATA / "outreach.json").read_text()) if (DATA / "outreach.json").exists() \
        else {"contacts": {}}
    contacts = outreach.setdefault("contacts", {})
    today = date.today().isoformat()

    by_seller = {}
    for sid, svc in services.items():
        if not svc.get("is_new") or not relevant(sid):
            continue
        for p in svc.get("providers", []):
            if not p.get("qualified") or not p.get("seller"):
                continue
            e = by_seller.setdefault(p["seller"], {
                "seller": p["seller"], "seller_url": p.get("seller_url"),
                "services": [], "service_ids": [], "listings": [],
                "success_rate": p.get("success_rate"), "transactions": p.get("transactions"),
                "review_count": p.get("review_count"), "member_since": p.get("member_since"),
            })
            e["services"].append(svc["display"])
            e["service_ids"].append(sid)
            e["listings"].append(p.get("listing_url"))

    added = refreshed = 0
    for seller, e in by_seller.items():
        existing = contacts.get(seller)
        if existing and existing.get("status") not in (None, "pending_approval"):
            continue  # don't disturb approved/sent/replied
        record = {
            "seller": seller,
            "seller_url": e["seller_url"],
            "service_ids": sorted(set(e["service_ids"])),
            "services": sorted(set(e["services"])),
            "listing_urls": [u for u in e["listings"] if u],
            "success_rate": e["success_rate"],
            "transactions": e["transactions"],
            "review_count": e["review_count"],
            "subject": f"Inquiry about your {primary_service(e['services'])}",
            "message": make_message(e),
            "status": "pending_approval",
            "drafted_at": today,
            "approved": False,
            "sent_at": None,
            "reply_text": None,
            "regular_price": None,
            "bulk_price": None,
        }
        if existing:
            refreshed += 1
        else:
            added += 1
        contacts[seller] = record

    (DATA / "outreach.json").write_text(json.dumps(outreach, indent=2))
    pending = sum(1 for c in contacts.values() if c["status"] == "pending_approval")
    print(f"outreach: +{added} new, {refreshed} refreshed ({pending} pending approval)")


if __name__ == "__main__":
    main()
