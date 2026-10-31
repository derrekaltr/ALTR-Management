"""Update data/state/lilia-x-altr.json for the 2026-10-09 run (keeps existing structure)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data/state/lilia-x-altr.json"
s = json.loads(P.read_text())

s["as_of"] = "2026-10-09"
s["window_covered"] = (
    "2026-09-25T09:08:16-04:00 -> 2026-10-09T09:05:57-04:00 (TWO-WEEK window; the 2026-10-02 run died before publishing "
    "and its state was written mid-window - this run supersedes it). 63 non-service messages: 33 client, 30 team - "
    "Mica 13, Stephski 7, Melissa 4, Mayson 4, Fred 2. Halves: Sep25-Oct2 = 14 client/16 team; Oct2-Oct9 = 19 client/14 team "
    "(7 of 14 team msgs billing). Service events: ChatAddUser 2026-09-25 12:17, ChatDeleteUser 2026-09-29 11:39 (unidentified). "
    "Last message in export 2026-10-06 19:09:24. No unknown senders; no Aroosha / IG-farm vendor activity in this chat."
)

oc = {c["issue"][:40]: c for c in s["open_complaints"]}


def upd(prefix, **kw):
    for c in s["open_complaints"]:
        if c["issue"].startswith(prefix):
            c.update(kw)
            return c
    raise SystemExit("no complaint " + prefix)


upd("Chat team sells high spenders content",
    age_days=119,
    status="recurring - 16 DAYS since Fred's 'We'll check' (Sep 23) with zero follow-up. Fred posted only 2 msgs in the two-week window "
           "(Oct 4, generic). Chatter unnamed 77 days (promised Jul 24). No purchase-history check, no incident count, 'Hayley content' never asked. "
           "Client raised ZERO chatter complaints in-window - per her Sep 23 disclosure she now fixes these silently, so silence is NOT compliance. "
           "Next week: same six checks.")
upd("NEW 2026-10-01: client-originated Hallow",
    issue="Client-originated Halloween revenue plan not specifically acknowledged. Oct 1: 10 costume sexting sets, Teddi 'said he will buy all of them', "
          "'Usually he pays 1,000 per set!' (~$10k). Oct 3: new set uploaded, costumes still in the mail; she is selling Teddi a favourite set herself "
          "for $200. Oct 4: goal of '10 sexting sets to this month'. Fred's only replies (Oct 4): 'Amazing thank you!' / 'New stuff looks great so we'll get a push on it' - no price, no Teddi CRM flag, no sequencing.",
    last_raised="2026-10-04", age_days=8,
    status="new/open - generic ack only. Next week: did Fred reply specifically; did costumes arrive; any Halloween set sold, at what price, by whom (ALTR or her direct to Teddi).")
upd("Invoicing does not confirm receipt of pa",
    last_raised="2026-10-06", age_days=21, escalation_count=3,
    status="recurring - Oct 6 payment answered 'haha no worries at all' (not a receipt, no amount). Sep 18 payment 21 days unconfirmed; Sep 3 invoice 36 days; "
           "day-before reminder skipped second cycle running (Sep 30) - client then had to wait for her bank (Oct 2 'just waiting for it to hit the bank').")
upd("Chatters do not communicate fan requests",
    age_days=72, days_unanswered=41,
    status="recurring - 41 days unanswered across six windows.")
dm = upd("The weekly DMCA leak-removal breakdown h",
         status="RESOLVED 2026-10-02 - Melissa posted 'Here's your weekly update on the leak removal breakdown for the past 7 days' Oct 2 11:29 "
                "(24-day gap, three missed windows). Per-chat owner is now Melissa. Next due ~Oct 9 (just after window close) - verify cadence next run.",
         last_raised="2026-10-02", owner="Melissa")
upd("TikTok shadowban never checked.",
    age_days=52, days_silent=46,
    status="open and abandoned - six consecutive windows with zero TikTok messages. Vivek last posted 2026-08-24. REASSIGN (eighth consecutive report).")
upd("Account/Drive confusion.",
    last_raised="2026-09-29", age_days=119,
    status="in_progress - Mica's 9/25 + 9/29 clarifications held (no further confusion in-window). Open: (a) second warmed-up IG account, lost login - "
           "14 days no reply from anyone; (b) no written account map; (c) still zero uploads confirmed to the Reels Drive (client promised 9/29).")
upd("Her phone number was briefly public",
    age_days=17, status="in_progress but stalled - 17 days, no movement; Fred's 2 in-window msgs did not touch it.")
upd("Service-suspension line",
    age_days=24, status="open - retained verbatim on Oct 1 invoice; client paid within terms anyway (Oct 6). Must be gone from the Oct 15 invoice.")
upd("ALTR's receiving details keep changing",
    last_raised="2026-10-05", age_days=109, escalation_count=7,
    status="recurring - no 7th change, BUT the history now makes her verify before paying: Oct 4 'Same Zelle right' / 'Before I send it!' / "
           "'Just want to make sure no typo haha' took 29.6h, her '???', a Mayson tag and a Melissa relay before Stephski's 'Yes same zelle! its on the bottom of the PDF' (Oct 5 16:48). No written freeze.")
upd("CRM notes do not reach the chat team",
    age_days=35, status="in_progress but unverified 35 days. Teddi now pre-committed to Halloween sets AND being sold to by the client directly.")
upd("Chat team underpricing",
    age_days=90, status="recurring - no new report (she has gone quiet on chatter issues generally). Still no written floor in CRM.")
upd("ALTR presence on the account is thin",
    last_raised="2026-10-09", age_days=21,
    status="recurring - two-week window: Fred 2 msgs (both Oct 4), Vivek 0, Michelle 0, Derrek 0. Mica carried Sep 25-29 (12) then 1. "
           "Oct 2-9: 7 of 14 ALTR msgs were billing.")
upd("Ledger mismatch:",
    last_raised="2026-10-06", age_days=45,
    status="open - 45 days; fifth unprompted self-reported balance Oct 6 ('I just owe u 27'). ALTR still states no amounts.")

s["open_complaints"] = [c for c in s["open_complaints"] if not c["issue"].startswith("The weekly DMCA")]
s["open_complaints"].append({
    "issue": "Billing questions go unanswered for over a day. Oct 4 11:12 'Same Zelle right' (client had funds ready) answered Oct 5 16:48 (29.6h) after '???' + Mayson '@stephskiii' + Melissa relay.",
    "first_raised": "2026-10-04", "last_raised": "2026-10-05", "age_days": 5, "escalation_count": 3, "owner": "Stephski",
    "status": "resolved on the instance; open as a pattern - watch response time on the Oct 15 cycle."})
s["open_complaints"].append({
    "issue": "Calls with no written recap. Mayson's Oct 5 'check up call' (meet.google.com, held immediately) - nothing written to chat afterwards; same as Sep 8 trial-reels call. Churn pattern: substance moved to calls instead of writing.",
    "first_raised": "2026-09-08", "last_raised": "2026-10-05", "age_days": 31, "owner": "Mayson",
    "status": "open - next week: was a recap posted; what was discussed."})

s["resolved_recently"] = [r for r in s["resolved_recently"] if not r["issue"].startswith("Custom-approval")] + [
    {"issue": "Weekly DMCA leak-removal breakdown missing in this chat", "first_raised": "2026-09-08", "closed": "2026-10-02",
     "status": "RESUMED - Melissa Oct 2 11:29 after 24 days. Verify ~Oct 9 delivery next run."},
    {"issue": "Custom-approval rule agreed after the $750 whipped-cream incident", "first_raised": "2026-08-31", "closed": "2026-09-18",
     "status": "WORKING - 39 days, zero reported violations (no customs surfaced in-window)."},
]
for r in s["resolved_recently"]:
    if r["issue"].startswith("Fred only reachable"):
        r["status"] = "REGRESSED - 2 messages in the two-week Sep 25-Oct 9 window (both generic, Oct 4). No @fspitfire tags either."
    if r["issue"].startswith("Invoice cadence"):
        r["status"] = "PARTIALLY HELD Oct 1 (on cadence, banking at bottom). Regressed: day-before reminder skipped Sep 30, pausing line kept, no receipts."
    if r["issue"].startswith("The $500/day"):
        r["status"] = "MOSTLY HOLDS - Oct 6 payment went through except $27 ('Didn't know I had a limit of that now'). A smaller limit has appeared; watch."

# commitments
cm = {c["what"][:40]: c for c in s["open_commitments"]}


def cupd(prefix, **kw):
    for c in s["open_commitments"]:
        if c["what"].startswith(prefix):
            c.update(kw)
            return c
    raise SystemExit("no commitment " + prefix)


cupd("Acknowledge and plan the Halloween", age_days=8, status="overdue - only generic Oct 4 ack ('New stuff looks great so we'll get a push on it'). Costumes still in the mail as of Oct 3.")
cupd("Investigate the Sep 23 old-content", age_days=77, status="overdue - 77 days on the naming; 16 days since 'We'll check'. TOP ITEM.")
cupd("Confirm in writing receipt of the 2026-09-18", age_days=36, status="overdue - now also the Oct 6 payment ('haha no worries at all' is not a receipt).")
cupd("Remove the 'to avoid any pausing", age_days=24, due="2026-10-15", status="overdue - missed Oct 1; remove before Oct 15 invoice.")
cupd("Send the day-before OF-withdrawal", age_days=25, status="pending - skipped Sep 30 (client then waited for her bank Oct 2-4). Watch Oct 14.")
cupd("Report back on the Aug 29 lost", age_days=41, status="overdue - 41 days, six windows.")
cupd("Check whether her TikTok", age_days=52, status="overdue - 52 days, Vivek silent 46 days. REASSIGN.")
cupd("Read and respond to the three screensho", age_days=46, status="overdue - 46 days.")
cupd("Resolve her warmed-up second IG", age_days=29, status="overdue - 14 days since her 9/25 message, no reply from anyone. Mayson active Oct 5 (call) but did not raise it in chat.")
cupd("Send her one written map", age_days=29, status="pending - partial verbal clarification by Mica 9/25, 9/29; no written map.")
cupd("Client: upload reels", age_days=10, status="pending - no upload confirmed by window close; mid-move.")
cupd("Client: fill out ALTR's new private", age_days=11, status="pending - completion not confirmed in chat.")
cupd("Make Teddi's CRM notes", age_days=40, status="overdue - 40 days. Teddi pre-committed to Halloween sets; client also selling to him directly ($200 favourite set, Oct 3).")
cupd("Close out the exposed-phone-number", age_days=17, status="overdue - 17 days, no movement.")
cupd("Brief the chat team on the accepted shower", age_days=59, status="overdue - 59 days idle.")
cupd("Sell the red set to Adam West", age_days=51, status="overdue - 51 days.")
cupd("Get her a decision back to the fan", age_days=39, status="overdue - 39 days, $750 idle.")
cupd("Acknowledge and action her Aug 26", age_days=44, status="overdue - 44 days.")
cupd("Organise and price her uploaded", age_days=60, status="overdue - 60 days; she self-folders and now self-sells to Teddi.")
cupd("Enforce the $200/video", age_days=42, status="overdue - 42 days.")
cupd("Freeze the receiving details", age_days=51, due="2026-10-15", status="pending - no 7th change; but she now has to verify before paying (Oct 4-5). Pin a written freeze.")
cupd("Post a written recap of the Sep 8", age_days=31, what="Post a written recap of the Sep 8 trial-reels call AND the Oct 5 check-up call",
     status="overdue - 31 days on Sep 8; Oct 5 call also unrecapped.")
cupd("Reconcile Mayson's Aug 30", age_days=40, status="overdue but largely overtaken - quota not mentioned since; Mica says 'upload whatever you can'.")
cupd("Reconcile the $192 gap", age_days=45, status="overdue - 45 days.")
cupd("Deliver the promised IG phone-farm", age_days=69,
     status="overdue - 69 days, owner silent (last owner msg 2026-09-16, 23 days; crosses the 30-day churn threshold on 2026-10-16). Possibly partly overtaken by the new ALTR-made IG account. OWNER-LEVEL: surface privately to Derrek only; NEVER in the client-facing team/employee section.")

s["open_commitments"] = [c for c in s["open_commitments"] if not c["what"].startswith("Follow up the two sexting sets")]
s["open_commitments"] += [
    {"what": "Push the new set she uploaded Oct 3 (and the ones toward her 10-sets-in-October goal)", "who": "Fred", "promised": "2026-10-04",
     "due": "2026-10-09", "age_days": 5, "status": "pending - 'New stuff looks great so we'll get a push on it'. Next week: any sales reported back?"},
    {"what": "Client: send the $27 remainder of the Sept 15-30 invoice", "who": "Lilia (client)", "promised": "2026-10-06", "due": "2026-10-07",
     "age_days": 3, "status": "pending - not confirmed in chat by window close. Do NOT chase her over $27; ALTR should confirm receipt when it lands."},
]
s["completed_recently"] = [
    {"what": "Restore the weekly DMCA leak-removal breakdown", "who": "Melissa", "date": "2026-10-02", "closed": "2026-10-02",
     "status": "done - first since Sep 8."},
    {"what": "Client: deliver new sexting set(s) offered Sep 18 ('easy 4,000')", "who": "Lilia (client)", "date": "2026-10-03", "closed": "2026-10-03",
     "status": "done (partial) - at least one new set uploaded Oct 3; rest folded into her 10-sets-in-October goal."},
    {"what": "Pay the Sept 15-30 invoice", "who": "Lilia (client)", "date": "2026-10-06", "closed": "2026-10-06",
     "status": "done except $27 - paid 5 days after issue, inside terms; she verified Zelle first."},
    {"what": "Check-up call", "who": "Mayson", "date": "2026-10-05", "closed": "2026-10-05",
     "status": "done - held immediately; no written recap."},
    {"what": "Issue the Sept 15-30 invoice on cadence", "who": "Stephski", "date": "2026-10-01", "closed": "2026-10-01",
     "status": "done - on cadence; pausing line kept, no day-before reminder, no receipts for prior payments."},
    {"what": "Re-explain the Reels Drive, confirm a new ALTR-run IG account exists, weekly reel inspo + Oct 6 social tip", "who": "Mica Vecco",
     "date": "2026-10-06", "closed": "2026-10-06", "status": "done - client 'Love it! Thank you!'."},
    {"what": "Agency-wide new-platform intake form sent", "who": "Melissa", "date": "2026-09-28", "closed": "2026-09-28",
     "status": "done - client 'Yessss I'll add a bunch of stuff to it!'."},
]

# payments
ph = s["payment_history"]
for p in ph:
    if p["date"] == "2026-09-03":
        p["outstanding"] = "unknown - unconfirmed 36 days after issue (as of 2026-10-09)"
        p["note"] = p["note"].replace("as of 2026-10-02 (29 days)", "as of 2026-10-09 (36 days)")
    if p["date"] == "2026-09-15":
        p["note"] = p["note"].replace("No ALTR receipt as of 2026-10-02 (14 days).", "No ALTR receipt as of 2026-10-09 (21 days).")
    if p["date"] == "2026-10-01":
        p.update({
            "note": "Invoice Sept 15-30, issued 2026-10-01 15:12 by Stephski, ON CADENCE, amount PDF-only, pausing line RETAINED, no day-before reminder Sep 30. "
                    "Oct 2 Stephski nudge -> client 'Yesss just waiting for it to hit the bank and will pay! X'. Oct 4 11:12 client had funds, asked 'Same Zelle right' "
                    "-> '???' Oct 5 13:00 -> Mayson tag + Melissa relay -> Stephski answered Oct 5 16:48 (29.6h). PAID Oct 6 11:02 (screenshot) except $27 "
                    "('I just owe u 27 I'll get that in tomorrow' / 'Didn't know I had a limit of that now'). Stephski: 'haha no worries at all' - no receipt/amount. "
                    "$27 not confirmed by window close.",
            "late": False, "status": "paid except $27 / receipt not confirmed", "paid": "2026-10-06", "days_to_pay": 5,
            "outstanding": "$27 (client-reported; promised 2026-10-07)", "payment_method": "Zelle, single send short $27 due to limit",
            "receipt_verified": False, "billing_question_response_hours": 29.6})
    if p["date"] == "2026-10-15":
        p["note"] = "EXPECTED: Oct 1-14 invoice ~Oct 15; day-before reminder ~Oct 14. Watch: pausing line removed, receipts + amounts in chat (incl. Oct 6 and the $27), $192 reconciled, no 7th detail change, billing questions answered same-day."

s["payment_risk"] = {
    "level": "VERY LOW on client intent/ability; MEDIUM-HIGH on ALTR-side bookkeeping; payment behaviour now also a CHURN TELL",
    "client_behaviour": "Five consecutive zero-chase cycles. Oct 1 invoice paid 5 days after issue (inside terms) bar $27 she flagged herself; she verified the Zelle first and chased ALTR ('???') to be allowed to pay. Self-reports running balance (5th time).",
    "altr_side_risk": "No written receipt/amount for Oct 6 payment, Sep 18 payment (21d) or Sep 3 invoice (36d); $192 gap 45 days + uncredited round-up; pausing line still in template; day-before reminder skipped twice; billing question took 29.6h.",
    "open_amount": "$27 (client-reported, Sept 15-30 invoice); Aug 15-31 invoice unconfirmed; $192 unreconciled; minus uncredited Sep 18 round-up. Net position known only to the client.",
    "next_invoice": "Oct 1-14 period, expected ~2026-10-15",
    "churn_read": "Fast, clean, eager payment while asks fall to ~1/week (billing-only) fits ALTR's pre-exit signature. Do not read payment as health.",
    "watch": [
        "Does the $27 land and does ALTR confirm it",
        "Does ALTR state received amounts for Oct 6 / Sep 18 / Sep 3 and close the $192",
        "Pausing line removed before Oct 15",
        "Day-before reminder sent ~Oct 14",
        "Billing questions answered same-day",
        "No seventh receiving-detail change",
        "Churn tell: fast pay + near-zero non-billing asks continuing",
    ],
}

s["client_priorities"] = [
    "Monetising high spenders with themed content - 10 Halloween costume sexting sets (Oct 1), Teddi pre-committed at ~$1,000/set; one teaser per set on her wall; goal '10 sexting sets to this month' (Oct 4); she uploads and folders herself",
    "Protecting her high spenders above all - she deletes chatters' mis-sent old content from frumby's inbox (3+ times, disclosed Sep 23) and compensates him; she sells to Teddi directly when he asks (favourite set for $200, Oct 3). frumby has bought everything, $200+/video, $8k in a month; Teddi lost his old library",
    "Sell only from the labelled high-spender folder she builds herself - newest content first, never the archive",
    "Chatters must communicate with her and ask before acting; the Aug 31 custom-approval rule works",
    "CRM notes the chat team actually reads - Teddi's wife and kids died in a car crash, her tattoo is an ex's name from college, Teddi tests chatters with questions he already knows",
    "Price discipline: $200/video, $200/pic package, $100/min customs; sell 3-minute sexting sets individually with photos",
    "Paying cleanly and correctly - verifies receiving details before sending ('Just want to make sure no typo haha'), tracks her own balance",
    "Getting through her house move (September 'the most hectic month') - explains delays rather than going quiet",
    "Clarity on IG accounts: understands the new ALTR-made account; unresolved warmed-up second account with lost login",
    "Personality-driven social content per Mica's Oct 6 tip ('Get ready I will definitely do!')",
    "Giving ALTR's new private platform a full picture via the intake form",
    "Big-ticket custom and video-call work (Snapchat) - moves fast when brought these",
    "Getting TikTok unblocked (shadowbanned since Aug 22, untouched 52 days)",
    "DMCA leak removals weekly - resumed Oct 2",
    "She keeps her own OF wall posts; wants ALTR to monetise, not post for her",
    "A stable payment rail and an ALTR balance that matches her own running total",
]

s["churn_signals"] = [
    "2026-10-09 (two-week window) - CHURN TELLS STACKING, no explicit exit signal yet:",
    "(1) Asks trending to zero: retro-count ~2 (wk to 9/18) -> ~8 (wk to 9/25) -> 3 (9/25-10/2) -> 1 (10/2-10/9, and that one was billing: 'Same Zelle right'). Zero chatter complaints in 16 days from a client who said on Sep 23 she now fixes failures silently.",
    "(2) Fast/eager payment: Oct 1 invoice paid in 5 days, she chased ALTR ('???') to be able to pay. Fifth zero-chase cycle.",
    "(3) Billing-heavy ALTR presence: Oct 2-9, 7 of 14 ALTR messages were billing; Fred (core operator) 2 msgs in 14 days.",
    "(4) Long-promised deliverables with no written proof: chatter removal (Jul 24, 77d), purchase-history check, Teddi CRM notes (Aug 30), TikTok (Aug 18), account map, owner's IG phone-farm update (Aug 1).",
    "(5) 'Doing it myself': sells to Teddi directly ($200, Oct 3), uploads/folders her own sets, polices frumby's inbox.",
    "(6) Call without written recap: Mayson's Oct 5 check-up call - substance not in writing (not a deflected results question, so partial signal only).",
    "NOT YET: owner silent 23 days (last Derrek msg 2026-09-16) - crosses 30 days on 2026-10-16. No results question deflected to a call. No export/login/data asks, no other agency mentioned.",
    "MITIGATING: warm tone throughout, planning ~$10k Halloween revenue + 10 sets/month, took Mayson's call instantly, enthusiastic to Mica's tip and the intake form, never disputed an invoice.",
]

s["health_history"] = [h for h in s["health_history"] if h["week_ending"] != "2026-10-02"] + [
    {"week_ending": "2026-10-02", "score": 50, "note": "computed mid-window, never published (run died)"},
    {"week_ending": "2026-10-09", "score": 48, "note": "two-week window Sep 25-Oct 9"},
]
s["week_stats_history"] = [w for w in s["week_stats_history"] if w["week_ending"] != "2026-10-02"] + [
    {"week_ending": "2026-10-02", "messages": 30, "client_messages": 14, "team_messages": 16, "client_asks": 3,
     "note": "unpublished; first half of the 2026-10-09 window - do not add to it"},
    {"week_ending": "2026-10-09", "messages": 63, "client_messages": 33, "team_messages": 30, "client_asks": 4,
     "note": "two-week window incl. the Oct 2 half. Oct 2-9 half alone: 33 msgs (19 client/14 team), 1 client ask (billing). Team: Mica 13, Stephski 7, Melissa 4, Mayson 4, Fred 2."},
]
s["asks_trend"] = [
    {"week_ending": "2026-09-18", "client_asks": 2, "note": "retro-count"},
    {"week_ending": "2026-09-25", "client_asks": 8, "note": "retro-count ($3k custom questions, phone number, deletions, reels)"},
    {"week_ending": "2026-10-02", "client_asks": 3, "note": "reels use, lost 2nd-IG login, Halloween sell plan"},
    {"week_ending": "2026-10-09", "client_asks": 1, "note": "Oct 2-9 half only: 'Same Zelle right' (billing). Two-week window total = 4."},
]
s["engagement_trend"] = [e for e in s["engagement_trend"] if e["week_ending"] != "2026-10-02"] + [
    {"week_ending": "2026-10-02", "messages": 30, "client_messages": 14, "health": 50, "note": "unpublished"},
    {"week_ending": "2026-10-09", "messages": 63, "client_messages": 33, "health": 48, "note": "two-week window"},
]
s["credentials_flags"] = [
    "In-window (Sep 25-Oct 9): NO plaintext credentials posted. (Melissa's 9/28 intake link carries a personal join token - private link, not a credential.)",
    "Historical, still in chat: 2026-05-26 client posted her first OnlyFans account password in plaintext and Fred repeated it back; account logins were later changed (Fred 2026-08-04 'account log ins appear to have been changed'). 2026-08-18/08-24 TikTok login (phone-number username; password sent, likely via screenshot). Recommend redacting the May 26 messages and confirming the OF password was rotated.",
]
s["staffing_notes"] = {
    "Fred (OFM)": "2 MESSAGES IN 14 DAYS (Oct 4: 'Amazing thank you!' / 'New stuff looks great so we'll get a push on it'). Missed: specific reply to the ~$10k Halloween plan, the Sep 23 'We'll check' follow-up (16d), phone-number close-out, the whole overdue backlog (chatter unnamed 77d). COACH: continuous presence; convert disclosures into named controls.",
    "Stephski (invoicing)": "7 msgs, all billing. Oct 1 invoice on cadence but pausing line kept, no day-before reminder, no receipts (Oct 6 / Sep 18 / Sep 3), $192 at 45d. Took 29.6h + 3 prompts to answer 'Same Zelle right'.",
    "Michelle (Promo/DMCA)": "ZERO messages. DMCA now delivered by Melissa.",
    "Melissa (Userfacing)": "4 msgs: 9/28 intake broadcast, Oct 2 DMCA breakdown (restored after 24d), Oct 5 relayed the Zelle question. Good week.",
    "Mayson (queue)": "4 msgs Oct 5: tagged Stephski on the Zelle question, ran a check-up call immediately. No written recap; did not address the lost-login second IG account.",
    "Vivek (Meta Support)": "ZERO messages; silent 46 days. TikTok 52 days. REASSIGN.",
    "Mica Vecco (Social Media Director)": "13 msgs: Drive/new-account clarity 9/25, 9/29, reel inspo 9/29 (one link duplicated), Oct 6 social tip well received. Did not answer the second-account/lost-login message.",
    "Derrek (owner)": "No messages; last 2026-09-16 (23 days). IG phone-farm/backup-posting update 69 days overdue. OWNER-LEVEL: surface privately; never in client-facing team section.",
}
s["notes"] = (
    "2026-10-09 RUN (two-week window absorbing the dead 2026-10-02 run; this state supersedes the mid-window 10-02 state - do not double count the Sep 25-Oct 2 half). "
    "63 msgs (33 client/30 team). HEADLINES: (1) ~$10k Halloween plan (Oct 1) got only a generic Fred ack on Oct 4; Fred 2 msgs in 14 days. "
    "(2) Sep 23 frumby disclosure: 16 days, no follow-up. (3) DMCA breakdown RESUMED Oct 2 (Melissa). (4) Oct 1 invoice paid Oct 6 bar $27; "
    "client's 'Same Zelle right' took 29.6h; still no receipts/amounts; pausing line kept; reminder skipped. (5) Churn tells stacking: asks 8->3->1 (billing), fast eager payment, "
    "billing = half of ALTR msgs Oct 2-9, owner silent 23d (30d on Oct 16). (6) Mayson Oct 5 check-up call, no recap. No unknown senders; no in-window credentials. "
    "PRESERVED FACTS: Teddi lost wife and kids in a car crash, lost his old library (low old-content risk), per client pays ~$1,000/set, pre-committed to all Halloween sets, "
    "client sold him a favourite set for $200 directly Oct 3; asks to be called; tests chatters. frumby is the old-content-exposed spender (bought everything; $200/video; $8k/month). "
    "Adam West wanted the red set. Video calls on Snapchat (username changed Sep 18). Mid-house-move since ~Sep 18. Her phone number was briefly public on IG 9/22 and is also her "
    "Zelle lookup and TikTok login handle. ALTR Zelle receiving number unchanged since Aug 12 (account name changed Sep 15). IG Reels Drive 1V3QQbtME8iF93SST-YxcF9aMj35TdVVa. "
    "Still-unasked question: what is 'Hayley content'."
)

P.write_text(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
print("state written; open complaints", len(s["open_complaints"]), "open commitments", len(s["open_commitments"]))
