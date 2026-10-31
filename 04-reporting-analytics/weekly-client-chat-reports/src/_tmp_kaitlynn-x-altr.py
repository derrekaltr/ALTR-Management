import json, re
from pathlib import Path

p = Path("data/state/kaitlynn-x-altr.json")
s = json.loads(p.read_text())

CARRY = "prior engagement 2026-08-07 → 2026-09-10"

# --- scrub links from carried state (dashboard is public; don't propagate Drive/payment/meet links)
def scrub(o):
    if isinstance(o, dict):
        return {k: scrub(v) for k, v in o.items()}
    if isinstance(o, list):
        return [scrub(v) for v in o]
    if isinstance(o, str):
        o = re.sub(r"https://drive\.google\.com/\S+", "[Drive link removed]", o)
        o = re.sub(r"https://commas\.com/\S+", "[payment link removed]", o)
        o = re.sub(r"https://meet\.google\.com/\S+", "[meeting link removed]", o)
        o = re.sub(r"https://calendly\.com/\S+", "[Calendly link removed]", o)
        return o
    return o

s = scrub(s)
s["as_of"] = "2026-10-16"

prior_status = s["account_status"]
s["account_status"] = {
    "state": "re-onboarding (unconfirmed)",
    "previous_state": "churned",
    "prior_engagement": {k: prior_status.get(k) for k in (
        "onboarded", "churn_notice_date", "final_invoice_date", "final_payment_date",
        "chat_departure", "engagement_length_days", "balance_outstanding", "retention_attempt")},
    "new_group_created": "2026-10-09T18:19:02-04:00",
    "new_group": "A new 'Kaitlynn x ALTR' supergroup was created 2026-10-09 18:19. It started as a basic group and was upgraded (ChannelMigrateFrom). Topics: OnlyFans, Social Media, Promo, DMCA, Invoicing. The old chat was already a forum supergroup with topics from 2026-08-07, so this is a separate group, not the old one upgraded. Onboarding messages from Mayson (content Drive with a 30-reels/month quota) and Mica (Social Media Director intro plus a Calendly link), and Mayson pointing her to Ollie for OnlyFans. Client has posted NOTHING as of 2026-10-16.",
    "resign_vs_new_account": "Evidence points to the SAME creator re-signing. The new group tags the same Telegram handle used in the old chat, the team is the same (Ollie, Mica, Mayson), and Mayson says the Drive already holds content. UNCONFIRMED: no client message, no contract, invoice or welcome-back. It is unknown whether this is the same OnlyFans account or a new one. Mayson's 'If it's already posted on your main account' refers to a separate social account, like the 'still being warmed up' Instagram from 2026-08-30.",
    "unexplained_event": "ChatDeleteUser at 2026-10-10T14:47:13-04:00. Removed member and actor are unknown. Could be the client leaving 16.5h after onboarding. Verify in Telegram.",
    "note": "NEXT RUN: (1) did Kaitlynn post in the new group? (2) Who was removed on 10/10? (3) Has anyone acknowledged a carried item (the $91 refund at minimum)? If the 10/10 removal was her, revert state to churned. Do not score this as a healthy return until she speaks."
}

for item in s.get("open_complaints", []):
    item["carried_from_prior_engagement"] = True
    item["carried_note"] = f"Carried from {CARRY}. Not acknowledged in the new group as of 2026-10-16."
for item in s.get("open_commitments", []):
    item["carried_from_prior_engagement"] = True
    item["carried_note"] = f"Carried from {CARRY}. Not acknowledged in the new group as of 2026-10-16."

# Relevance for a re-sign: most-important carried items flagged
priority = {
    "free full nude previews": "HIGH: she will check this first if it is the same OnlyFans page.",
    "$91.00 owner waiver": "HIGH: credit on the first invoice of any re-sign.",
    "changed her OnlyFans password": "HIGH: ALTR access revoked. New credentials must be collected privately (never in the group) and logged.",
    "Google Drive uploads failing": "MEDIUM: a new Drive and the same 30-reels quota were issued 2026-10-09 without confirming uploads work.",
    "Payment-path friction": "MEDIUM: offer the non-wire option on the first invoice.",
    "Instagram actively flagging": "MEDIUM: Mica's promised profile audit should start here.",
}
for item in s.get("open_complaints", []):
    for key, txt in priority.items():
        if key in item["issue"]:
            item["resign_relevance"] = txt

s["open_complaints"].insert(0, {
    "issue": "Unexplained ChatDeleteUser in the new group at 2026-10-10 14:47. Removed member unknown; nobody explained it in the chat.",
    "first_raised": "2026-10-10",
    "owner": "Mayson / Ollie Mckinlay (verify)",
    "status": "new",
    "severity": "high",
    "days_open": 6,
    "note": "If it was Kaitlynn, the re-onboarding has stalled. The old chat also had an unexplained ChatAddUser on 2026-09-10."
})

s["open_commitments"] = [
    {
        "what": "Mica: initial profile audit plus 1:1 session",
        "who": "Mica Vecco",
        "date": "2026-10-09",
        "first_raised": "2026-10-09",
        "status": "pending",
        "days_open": 7,
        "quote": "I’ll conduct an initial profile audit and brainstorm creative, tailored ideas to ensure your content aligns with your goals and resonates with your audience.",
        "note": "Self-serve Calendly again. Her rescheduled call from the first engagement was never rebooked."
    },
    {
        "what": "Ollie: OnlyFans point of contact",
        "who": "Ollie Mckinlay",
        "date": "2026-10-09",
        "first_raised": "2026-10-09",
        "status": "pending",
        "days_open": 7,
        "quote": "@kaitlynnandersonof you can ask @olkmck anything you want regarding OF",
        "note": "Ollie has not posted in the new group."
    },
] + s["open_commitments"]

s["client_asks"] = [
    {
        "week_ending": "2026-10-16",
        "window": "2026-10-09T09:05:57-04:00 → 2026-10-16T09:06:40-04:00",
        "asks": [],
        "client_messages": 0,
        "note": "No asks. The client posted nothing in the new group. All 4 messages are team onboarding posts (Mayson 3, Mica 1). Earlier asks are in the client_priorities list carried from the first engagement."
    }
]

s["health_history"].append({"week_ending": "2026-10-16", "score": 35, "trend": "new",
    "note": "New group 2026-10-09; treated as re-onboarding (unconfirmed). Client silent; 10/10 member removal unexplained."})
s["week_stats_history"].append({"week_ending": "2026-10-16", "messages": 4, "client_messages": 0, "team_messages": 4,
    "note": "New group only. Plus 7 service events (ChannelMigrateFrom, 5x TopicCreate, ChatDeleteUser 2026-10-10 14:47). Per-sender: Mayson 3, Mica 1."})
s["engagement_trend"].append({"week_ending": "2026-10-16", "messages": 4, "client_messages": 0, "health": 35,
    "note": "New group. Zero client messages."})

s["assets"]["access"] = "Client changed her OnlyFans password on or before 2026-09-07, so ALTR access is presumed revoked. On any re-sign, collect new credentials privately and never in the group. Kaitlynn.vip domain, the three old Drives, the warmed-up Instagram and the Infloww disconnect were never confirmed handed back or cleaned up after churn."
s["assets"]["new_group_drive"] = "[Drive link removed] (Mayson, 2026-10-09, Social Media content Drive with a 'New Content' folder; Mayson says it already holds some content)"
s["assets"]["topics"] = "NEW GROUP (2026-10-09): OnlyFans, Social Media, Promo, DMCA, Invoicing. Old group (2026-08-07) had the same topics."

s["data_caveats_new"] = "The fetcher matches chats by title, so data/chats/kaitlynn-x-altr.jsonl now holds ONLY the new group created 2026-10-09. The old chat's history (2026-08-07 → 2026-09-10) is no longer in the local file and survives only in this state file and in data/weeks/2026-08-08 … 2026-09-11. Fix: key chats by Telegram chat ID, or archive the old history under its own slug."

s["notes"] = ("UPDATE 2026-10-16: a NEW 'Kaitlynn x ALTR' group was created 2026-10-09 18:19 with standard onboarding from Mayson and Mica, and Ollie named as the OnlyFans contact. This is treated as a re-onboarding of the same creator, UNCONFIRMED (see account_status). Client silent; ChatDeleteUser 2026-10-10 14:47 unexplained. All open_complaints/open_commitments below the first entries are carried from the first engagement and none has been acknowledged in the new group.\n\n"
              "--- PRIOR-ENGAGEMENT NOTES (retained) ---\n" + s["notes"])

p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")

# sanity: no links / obvious secrets remain
txt = p.read_text()
for pat in ["drive.google.com", "commas.com/", "meet.google.com", "calendly.com/"]:
    print(pat, pat in txt)
