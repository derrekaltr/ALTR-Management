"""Build the 2026-10-16 post-mortem CS-gap JSONs for the churned group.

Base = the 2026-10-09 run (full-history analysis). Only Kaitlynn's chat changed since then
(new group 2026-10-09). For the other five there are zero new messages, so this run
re-dates every elapsed-time figure to 2026-10-16, adds a structured `dangling_as_of_2026-10-16`
list (money / access / credentials / content / fan liabilities), and extends the timeline
and missed-warning-signs.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data/analysis/cs-gaps-2026-10-09")
DST = os.path.join(ROOT, "data/analysis/cs-gaps-2026-10-16")
os.makedirs(DST, exist_ok=True)

POSTMORTEM_SIGN = lambda items: {
    "date": "2026-10-09",
    "signal": "The 2026-10-09 post-mortem listed these open items by name (" + items + "). Seven days later none has moved and ALTR has sent nothing.",
    "what_we_should_have_done": "Turn each post-mortem dangling item into a ticket with an owner and a due date the same day; review closure in the following week's run.",
}


def replace_in(obj, pairs):
    """Apply literal string replacements to every string inside internal_failure fields."""
    for dim in obj["dimensions"].values():
        for a, b in pairs:
            dim["internal_failure"] = dim["internal_failure"].replace(a, b)


def fix_quote(obj, dim, old_start, new_quote):
    for e in obj["dimensions"][dim]["evidence"]:
        if e["quote"].startswith(old_start):
            e["quote"] = new_quote
            return
    raise SystemExit(f"quote not found: {dim} {old_start}")


UPD = {}

# ---------------------------------------------------------------- Amber Haze
UPD["amber-haze-x-altr"] = dict(
    status_reason=(
        "Gave notice 2026-09-21 12:55, 86 minutes after her seventh written escalation of the same low-revenue complaint was answered with a third call offer in 18 days. "
        "No message from anyone in the chat since; as of 2026-10-16 that is 25 days with no acknowledgement, no save attempt and no exit conversation. "
        "Nothing changed between 2026-10-09 and 2026-10-16: every item flagged last week is still open. "
        "STILL DANGLING - MONEY OWED TO US: the final invoice she asked for and promised to pay 'straight away' (2026-09-15 to 2026-09-21 revenue at 30%) has never been issued (25 days); the longer it waits, the less likely it is paid. "
        "ALTR ASSETS / FAN LIABILITY: the ALTR laptop shipped to her on 2026-06-02 has never been recovered or written off; fan-paid customs (Wesley's Aug 11/14 sends, the custom sheet) have no confirmed delivery, which is open chargeback exposure. "
        "ACCESS NOT HANDED BACK: her main Instagram login, the three management IG accounts built on her name, the Facebook page, link.me and the amberhaze.vip domain, OnlyFans via Infloww plus a staff phone login, her Google Drives (one shared to a staff member's personal Gmail), the shared iPhone album, the Snapchat we had her create and an off-chat WhatsApp IG-rep group. "
        "CREDENTIALS NOT ROTATED: her Instagram password sits in plaintext in the group from 2026-05-09, 2026-05-20 and 2026-09-07 (the last now 39 days live), with a 2FA code (2026-05-10) and a link.me password posted by our own staff (2026-05-07); the previous agency's authenticator was never confirmed removed."
    ),
    replace=[("have now gone 18 days with no reply of any kind", "have now gone 25 days (to 2026-10-16) with no reply of any kind"),
             ("has not been issued in 18 days", "has not been issued in 25 days"),
             ("no owner - 18 days and counting", "no owner - 25 days and counting")],
    metrics={"our_side_silence_since_termination_days": 25, "final_invoice_days_unissued": 25, "days_since_live_ig_password_posted": 39},
    method_note=" 2026-10-16 re-run: re-checked the tail - still no message from anyone after 2026-09-21 12:55; elapsed-day figures re-dated to 2026-10-16; all other counts unchanged.",
    timeline_tail=[
        {"date": "2026-09-21 to 2026-10-16", "event": "POST-EXIT: zero ALTR messages for 25 days. Final invoice never issued. No access handed back, no credentials rotated, no word on DMCA continuation, the management IG accounts or the ALTR laptop she holds."},
        {"date": "2026-10-09 to 2026-10-16", "event": "The 2026-10-09 post-mortem named every dangling item; a week later none has moved."},
    ],
    extra_signs=[POSTMORTEM_SIGN("final invoice, laptop, IG password, account access")],
    dangling=[
        {"type": "money_owed_to_us", "item": "Final invoice for 2026-09-15 to 2026-09-21 at 30% - requested by the client, never issued", "since": "2026-09-21", "days_open": 25, "next_action": "Billing issues it this week with a one-line apology for the delay; the client offered to pay immediately."},
        {"type": "altr_equipment", "item": "ALTR laptop shipped to her for Omegle content - not recovered, not written off", "since": "2026-06-02", "days_open": 136, "next_action": "Owner decides recover vs write off and tells her in the same message as the invoice."},
        {"type": "fan_liability", "item": "Fan-paid customs (Wesley Aug 11/14, custom sheet) with no confirmed delivery - chargeback exposure", "since": "2026-08-14", "days_open": 63, "next_action": "Chat lead confirms delivered or refunded per fan; log the decision."},
        {"type": "access_not_returned", "item": "Main IG login, 3 management IGs on her name, FB page, link.me + amberhaze.vip, OF via Infloww + staff phone login, Google Drives (incl. a staff personal Gmail share), shared iPhone album, Snapchat, WhatsApp IG-rep group", "since": "2026-09-21", "days_open": 25, "next_action": "Written offboarding checklist: disconnect Infloww, log staff phone out, hand over or delete the management IGs and FB page, unshare Drives, release the domain."},
        {"type": "credentials_unrotated", "item": "IG password in the group 3x (latest 2026-09-07), a 2FA code, the link.me password posted by staff; previous agency authenticator never confirmed removed", "since": "2026-09-07", "days_open": 39, "next_action": "Tell her to rotate IG and link.me passwords and re-do 2FA; delete the messages from the group."},
        {"type": "service_status", "item": "DMCA leak-removal reporting stopped 2026-09-08 with no word on whether takedowns continue", "since": "2026-09-08", "days_open": 38, "next_action": "State in writing whether DMCA coverage ends with the contract."},
    ],
)

# ---------------------------------------------------------------- Alex Paige Moore
UPD["alex-paige-moore-x-altr"] = dict(
    status_reason=(
        "Resigned warmly on 2026-09-17 after twelve months. Nobody has acknowledged it: the only replies since were billing (a 2026-09-21 chase for $5,259.90 that never mentions her leaving) and Mayson's 'Thanks' when she posted 'Final invoice paid' with a receipt on 2026-09-23. "
        "No message from anyone since; as of 2026-10-16 that is 29 days with no exit conversation, and nothing changed between 2026-10-09 and 2026-10-16. "
        "STILL DANGLING - MONEY EITHER WAY: billing never confirmed the $5,259.90 landed or issued a zero-balance/itemised closing statement; the July reconciliation dispute ($1,989 per billing vs fully paid per her arithmetic) was never closed; her 2026-08-13 request to deduct $2,434 of referral money ALTR owed her was never confirmed; customs already sold to fans (sheet posted 2026-08-25) were never delivered because of her surgery, so fan refunds/chargebacks are unaddressed. "
        "ACCESS NOT HANDED BACK: OnlyFans access, the management-run Instagram, Drive folders and the alexpaige.vip link; her passport and driver's-licence images collected in this group in April have never been deleted. "
        "CREDENTIALS NOT ROTATED: the account password she posted in the group on 2025-09-17 (now ~13 months) has never been rotated, and an unidentified account was bulk-added to this chat on 2026-09-10 while those credentials and ID images remain in its history."
    ),
    replace=[("her resignation has gone 22 days without a single word in reply", "her resignation has gone 29 days (to 2026-10-16) without a single word in reply")],
    metrics={"days_since_resignation_unacknowledged": 29, "days_since_final_payment_without_closing_statement": 23},
    method_note=" 2026-10-16 re-run: tail re-checked, still nothing after 2026-09-23 08:25; elapsed-day figures re-dated to 2026-10-16; other counts unchanged.",
    quote_fixes=[("proactive_communication", "Congrats on an incredible first week", "Congrats on an incredible first week with us 🥳 Your account is already up 27.4%, messages are up 28%, and overall subscription earnings are up 33.6%")],
    timeline_tail=[
        {"date": "2026-10-16", "event": "29 days on: no acknowledgement, no exit conversation, no zero-balance statement, referral deduction and July dispute unreconciled, sold customs unaddressed, no access revocation or credential rotation, ID documents still in the chat. Unchanged since the 2026-10-09 post-mortem."},
    ],
    extra_signs=[POSTMORTEM_SIGN("closing statement, referral reconciliation, ID documents, password")],
    dangling=[
        {"type": "money_unreconciled", "item": "$5,259.90 'Final invoice paid' (receipt posted 2026-09-23) - acknowledged only with 'Thanks'; no confirmation it landed, no zero-balance statement", "since": "2026-09-23", "days_open": 23, "next_action": "Billing confirms receipt against the bank and sends an itemised closing statement showing $0."},
        {"type": "money_disputed", "item": "July reconciliation: billing said $1,989 remaining, her arithmetic said fully paid - never closed", "since": "2026-07-27", "days_open": 81, "next_action": "Fold into the closing statement with the arithmetic shown."},
        {"type": "money_owed_to_client", "item": "$2,434 referral money ALTR owed her, requested as an invoice deduction 2026-08-13 - never confirmed applied", "since": "2026-08-13", "days_open": 64, "next_action": "Owner confirms whether it was deducted; if not, pay it."},
        {"type": "fan_liability", "item": "Customs sold to fans (sheet 2026-08-25) never delivered after her surgery", "since": "2026-08-25", "days_open": 52, "next_action": "Refund or cancel each line; log it."},
        {"type": "access_not_returned", "item": "OnlyFans access, management-run IG, Drive folders, alexpaige.vip", "since": "2026-09-17", "days_open": 29, "next_action": "Disconnect tooling, hand over or delete the managed IG, unshare Drives, release the domain, confirm to her in writing."},
        {"type": "sensitive_data", "item": "Passport and driver's-licence images in the group chat since April; unidentified member bulk-added 2026-09-10", "since": "2026-04-26", "days_open": 173, "next_action": "Delete the images from the chat, remove unknown members, archive or close the group."},
        {"type": "credentials_unrotated", "item": "Account password posted in the group 2025-09-17, never rotated", "since": "2025-09-17", "days_open": 394, "next_action": "Tell her to rotate it; delete the message."},
    ],
)

# ---------------------------------------------------------------- Vicky
UPD["vicky-x-altr"] = dict(
    status_reason=(
        "Terminated 2026-08-18 asking for exactly two things: a final figure and her accounts disconnected from our Infloww. 59 days later (2026-10-16) neither has been confirmed in writing. "
        "Billing attached a file with no stated amount, sent one bare chase on 2026-08-26, and a member - most likely the client - left or was removed on 2026-08-27, so this channel may no longer reach her. No message since Vivek's stray 'Hi' on 2026-09-02; nothing changed between 2026-10-09 and 2026-10-16. "
        "STILL DANGLING - MONEY EITHER WAY: her final Aug 1-18 invoice appears unpaid and its amount was never stated in the chat; on our side, $1,700 of fan money ($700 video call, $1,000 custom) was sold without briefing her and never delivered or refunded. "
        "ACCESS NOT HANDED BACK: Infloww disconnection of both OnlyFans accounts never confirmed; our editor access to her Drive never revoked; the management-run Instagram she supplied content for was never named to her or handed over. "
        "CREDENTIALS NOT ROTATED: she asked five times to change the passwords on both OF accounts (once right after reporting a compromise) and no rotation was ever confirmed; seven live OnlyFans verification session links and a password-reuse instruction remain in the chat history."
    ),
    replace=[("in the 52 days since no owner has contacted her", "in the 59 days since (to 2026-10-16) no owner has contacted her")],
    metrics={"days_since_termination": 59, "max_team_silence_days": 51},
    method_note=" 2026-10-16 re-run: tail re-checked, nothing after 2026-09-02; max_team_silence_days and days_since_termination re-dated to 2026-10-16.",
    quote_fixes=[("chatter_conduct", "I say you sent them massage", "I say you sent them massage “are you single” Some of them i know for a long time and some of them married, so when you ask this they understand that this is not me talking")],
    timeline_tail=[
        {"date": "2026-10-16", "event": "59 days on: no written final figure, no Infloww disconnection confirmed, no password rotation, no owner contact, $1,700 of fan money undelivered and unrefunded, session links still in the history. Unchanged since the 2026-10-09 post-mortem."},
    ],
    extra_signs=[POSTMORTEM_SIGN("final figure, Infloww disconnect, $1,700 fan money, passwords")],
    dangling=[
        {"type": "money_owed_to_us", "item": "Final Aug 1-18 invoice - amount never stated in text, appears unpaid; one bare chase 2026-08-26", "since": "2026-08-18", "days_open": 59, "next_action": "Owner decides collect vs write off; if collecting, state the figure in text on her crypto rail via a channel that still reaches her."},
        {"type": "fan_liability", "item": "$700 video call + $1,000 custom sold without briefing her - never delivered or refunded", "since": "2026-08-04", "days_open": 73, "next_action": "Refund the fans or net it against the final invoice; record the decision."},
        {"type": "access_not_returned", "item": "Infloww connection to both OnlyFans accounts (the one thing she asked for at exit); Drive editor access; unnamed management-run IG", "since": "2026-08-18", "days_open": 59, "next_action": "Disconnect Infloww today and tell her; revoke Drive access; hand over or delete the IG."},
        {"type": "credentials_unrotated", "item": "Both OF passwords (five rotation requests, one after a reported compromise); seven verification session links and a password-reuse instruction in the chat", "since": "2026-07-17", "days_open": 91, "next_action": "Advise her to rotate both passwords; delete the session links from the group."},
        {"type": "channel", "item": "Client left/was removed 2026-08-27 - the group may not reach her", "since": "2026-08-27", "days_open": 50, "next_action": "Close out via an off-chat channel."},
    ],
)

# ---------------------------------------------------------------- Paige
UPD["paige-x-altr"] = dict(
    status_reason=(
        "Resigned 2026-09-02 at week 10 - 'its just not working for me' - and has not spoken since. In the 44 days to 2026-10-16 ALTR has sent her exactly two messages, both collections chases (2026-09-09), the first threatening to pause work she was no longer receiving. Nothing changed between 2026-10-09 and 2026-10-16. "
        "STILL DANGLING - MONEY: the Aug 15-31 invoice (issued 2026-09-01) shows as unpaid per our own chase and was never reconciled or written off; no final statement for Sep 1-2 exists. "
        "OWED TO HER: her swingers-site leak report (exact site supplied 2026-09-01) was claimed and never actioned - 46 days with leaked content live. "
        "ACCESS NOT HANDED BACK: ALTR still holds logins to her Instagram accounts via the phone farm, the management-run IG content Drive and the paigesworld.vip domain; her fourth Instagram lockout was never closed and the 2026-08-14 request to approve a login on an account that was not hers was never explained. "
        "CREDENTIALS NOT ROTATED: six plaintext password posts of hers (2026-07-29 to 2026-08-29), plus login codes, remain in the group unrotated, and an unidentified account was added to this chat on 2026-09-10, eight days after she left."
    ),
    replace=[],
    metrics={"days_since_resignation": 44, "days_leak_unactioned": 46, "max_team_silence_days": 37},
    method_note=" 2026-10-16 re-run: tail re-checked, nothing after 2026-09-10; days_since_resignation, days_leak_unactioned and max_team_silence_days re-dated to 2026-10-16.",
    quote_fixes=[("follow_through", "hii sorry im new to telegram", "hii sorry im new to telegram still figuring it out 😂 ill book now xx")],
    timeline_tail=[
        {"date": "2026-10-16", "event": "44 days on: no owner contact, no exit conversation, Aug 15-31 invoice unreconciled, leak still unactioned (46 days), fourth lockout never closed, six plaintext credentials still in the group, IG access not handed back. Unchanged since the 2026-10-09 post-mortem."},
    ],
    extra_signs=[POSTMORTEM_SIGN("leak takedown, Aug 15-31 invoice, IG access, credentials")],
    dangling=[
        {"type": "money_owed_to_us", "item": "Aug 15-31 invoice (issued 2026-09-01), unpaid per our 2026-09-09 chase; Sep 1-2 never invoiced; no reconciliation or write-off", "since": "2026-09-01", "days_open": 45, "next_action": "Check the bank (she paid previously after an account-number change); then collect or write off with one closing statement."},
        {"type": "owed_to_client", "item": "Leak on a swingers website - site supplied 2026-09-01, claimed by Michelle, never actioned", "since": "2026-08-31", "days_open": 46, "next_action": "File the takedown now and confirm to her regardless of churn - it is her content and our claimed task."},
        {"type": "access_not_returned", "item": "Instagram logins held on the phone farm (two accounts), management IG content Drive, paigesworld.vip domain", "since": "2026-09-02", "days_open": 44, "next_action": "Log the phone farm out of both accounts, unshare the Drive, release the domain, confirm in writing."},
        {"type": "credentials_unrotated", "item": "Six plaintext IG password posts plus login codes in the group; unidentified member added 2026-09-10", "since": "2026-08-29", "days_open": 48, "next_action": "Advise rotation; delete the messages; remove unknown members."},
        {"type": "unexplained_incident", "item": "2026-08-14 request for her to approve a login on an account that was not hers - never explained", "since": "2026-08-14", "days_open": 63, "next_action": "Audit the phone-farm device for cross-linked accounts."},
    ],
)

# ---------------------------------------------------------------- Chey Mai
UPD["chey-mai-x-altr"] = dict(
    status_reason=(
        "Offboarded internally on 2026-09-05 and never told. She last wrote 2026-08-11 (66 days ago as of 2026-10-16); the last message ALTR addressed to her was a payment chase on 2026-08-26; the only record of the decision is two staff lines in a topic she can read ('shes not with us anymore' / 'yes we removed already'). Nothing changed between 2026-10-09 and 2026-10-16. "
        "STILL DANGLING - MONEY OWED TO US: the Jul 15-31 balance she asked four more days for and the combined Aug 1-14 invoice are both unpaid with no receipt, and Aug 15-31 and Sep 1-5 were never invoiced - no final statement, collections handoff or write-off decision exists, and nobody checked whether a payment went to the changed account number announced 2026-08-15. "
        "ACCESS NOT HANDED BACK: the cheyennesworld.vip domain, the reels Drive and her sales-preferences doc were never revoked or returned; nobody confirmed our chat team was removed from her OnlyFans or that her previous team was ever unlinked (asked 2026-06-23, never answered). "
        "CREDENTIALS: none were posted in this chat, so nothing to rotate beyond whatever OnlyFans/tooling access the chat team held, which was never confirmed revoked to her."
    ),
    replace=[],
    metrics={"days_since_last_client_message": 66, "days_since_internal_offboarding": 41, "max_team_silence_days": 51},
    method_note=" 2026-10-16 re-run: tail re-checked, nothing after 2026-09-05; elapsed-day figures re-dated to 2026-10-16.",
    timeline_tail=[
        {"date": "2026-10-16", "event": "41 days after removal: no termination message, no final statement, no collections or write-off decision, two periods unpaid and two never invoiced, domain/Drive/docs not revoked, referee Paige also gone. Unchanged since the 2026-10-09 post-mortem."},
    ],
    extra_signs=[POSTMORTEM_SIGN("termination notice, final statement, collections/write-off, domain and Drive")],
    dangling=[
        {"type": "money_owed_to_us", "item": "Jul 15-31 balance + combined Aug 1-14 invoice - unpaid, no receipt", "since": "2026-08-15", "days_open": 62, "next_action": "First check the changed account for an inbound transfer; then one written final statement and a collect/write-off decision."},
        {"type": "money_uninvoiced", "item": "Aug 15-31 and Sep 1-5 periods never invoiced", "since": "2026-09-01", "days_open": 45, "next_action": "Decide bill or waive; record it."},
        {"type": "client_not_notified", "item": "Removed 2026-09-05 without ever being told", "since": "2026-09-05", "days_open": 41, "next_action": "Send a written termination notice with the final statement (phone channel exists)."},
        {"type": "access_not_returned", "item": "cheyennesworld.vip domain, reels Drive, sales-preferences doc; OnlyFans/chat-team access never confirmed removed; previous-team unlink never confirmed", "since": "2026-09-05", "days_open": 41, "next_action": "Revoke and confirm in the termination message."},
    ],
)

# ---------------------------------------------------------------- Kaitlynn
UPD["kaitlynn-x-altr"] = dict(
    status_reason=(
        "CHURNED - the 2026-10-09 'new group' is not evidence that she came back. She gave notice 2026-09-08, paid in full 2026-09-10 and was removed from the original chat two minutes later; her last message anywhere is 2026-09-10. "
        "On 2026-10-09 a new 'Kaitlynn x ALTR' group was created (basic group, immediately migrated to a supergroup, five topics) and Mayson/Mica posted standard first-time onboarding tagging her handle: a new content Drive with the same 30-reels-a-month quota, Mica's 'excited to get to know you' intro with a self-serve Calendly, and Ollie named as OF contact. "
        "Why churned, not re-onboarding: (1) zero client messages in the new group in 7 days; (2) no welcome-back, contract, invoice, credential handover or reference to the first engagement anywhere; (3) a member was removed (ChatDeleteUser) on 2026-10-10 14:47, 16.5h after the intros, and nobody explained it; (4) the posts are generic templates, consistent with an internal re-add rather than a negotiated return; (5) she locked us out of OnlyFans on 2026-09-07 and nothing shows access was restored. "
        "Counter-evidence: the same Telegram handle is tagged and Mayson says the Drive 'already' has content, so someone at ALTR believes she is back. If she has re-signed, she starts at_risk with twelve first-engagement items unresolved and none acknowledged. Owner should verify privately who was removed on 10/10. "
        "STILL DANGLING - MONEY OWED TO HER: the $90-91 owner waiver that billing charged back on 2026-09-01 and she paid on 2026-09-10 - never refunded (36 days). "
        "ACCESS/CONTENT HELD: the kaitlynn.vip domain, three first-engagement Drives plus the new 2026-10-09 Drive (which already holds her content), content she sent to Mayson's DMs, a management-run backup Instagram warmed up on her name; Infloww disconnection never confirmed. "
        "CREDENTIALS: none posted in either chat; she rotated her own OF password before leaving."
    ),
    replace=[],
    metrics={"days_since_notice": 38, "new_group_client_messages": 0, "new_group_our_messages": 4, "days_since_our_last_message_in_new_group": 6},
    method_note=(" 2026-10-16 re-run: data/chats/kaitlynn-x-altr.jsonl now holds ONLY the new group (11 lines, 2026-10-09 18:19 to 2026-10-10 14:47: ChannelMigrateFrom, five TopicCreate, three Mayson posts, one Mica post, one ChatDeleteUser with no actor/target). "
                 "First-engagement history (2026-08-07 to 2026-09-10) was verified against data/weeks/*/kaitlynn-x-altr.json and data/state/kaitlynn-x-altr.json; all first-engagement metrics are carried unchanged. New-group counts: 0 client messages, 4 ALTR messages, last ALTR message 2026-10-09 22:13."),
    onboarding_extra=(" The 2026-10-09 new group repeated the pattern: a first-meeting template ('excited to get to know you') to a creator we had worked with for five weeks, a new Drive and the same 30-reels quota with the Drive failure never confirmed fixed, and no mention of any first-engagement item.",
                      {"quote": "I’m excited to get to know you during our 1 on 1 session!", "who": "Mica Vecco", "date": "2026-10-09"}),
    disengagement_extra=" On 2026-10-09 a new group was spun up for her with templated onboarding and no acknowledgement of the refund, the nude-preview breach or why she left; a member was removed 16.5h later and nobody on our side commented.",
    security_extra=" A fourth Drive was issued 2026-10-09 into a group from which a member was removed the next day, so ALTR may now hold her content in a share whose recipient has left.",
    timeline_tail=[
        {"date": "2026-10-09", "event": "31 days on: no exit conversation, the clawed-back $90-91 unrefunded, nude-preview breach uninvestigated, domain/Drives/backup IG not handed back."},
        {"date": "2026-10-09 18:19", "event": "NEW GROUP: 'Kaitlynn x ALTR' created and migrated to a supergroup with five topics. Mayson posts a new content Drive with the 30-reels/month quota ('We already have some content in there'); Mica posts a first-time intro and Calendly; 22:13 Mayson names Ollie as OF contact. No reference to the first engagement."},
        {"date": "2026-10-10 14:47", "event": "ChatDeleteUser in the new group, 16.5h after the intros - removed member and actor unknown, never explained."},
        {"date": "2026-10-16", "event": "Day 7 of the new group: zero client messages, no ALTR message since 2026-10-09 22:13, Ollie has not posted, no Calendly booking visible. Treated as churned until she speaks."},
    ],
    extra_signs=[
        {"date": "2026-10-09", "signal": "We restarted contact with a churned client using first-time onboarding templates and a content quota, with no acknowledgement of why she left or of the $90-91 we owe her.", "what_we_should_have_done": "Any return of a churned client opens with a personal owner message: what went wrong, what is fixed (nude-preview investigation, payment link, Drive), and the refund - before any quota or Drive."},
        {"date": "2026-10-10", "signal": "A member was removed from the new group 16.5h after the intros and nobody on our side remarked on it.", "what_we_should_have_done": "Treat any membership change in a client group as an event: identify who left the same day and, if it was the client, reach out off-thread."},
        POSTMORTEM_SIGN("$90-91 refund, exit conversation, nude-preview investigation, domain/Drives/backup IG"),
    ],
    dangling=[
        {"type": "money_owed_to_client", "item": "$90-91 owner waiver (2026-08-21) charged back by billing 2026-09-01 and paid by her 2026-09-10 - never refunded", "since": "2026-09-10", "days_open": 36, "next_action": "Owner refunds it personally with the exit-conversation message."},
        {"type": "content_held", "item": "Four ALTR-issued Drives (three first-engagement + the 2026-10-09 one that 'already' holds content) and content sent to Mayson's DMs", "since": "2026-09-10", "days_open": 36, "next_action": "If she has not re-signed: unshare or hand over and confirm in writing."},
        {"type": "access_not_returned", "item": "kaitlynn.vip domain; management-run backup Instagram warmed up on her name; Infloww disconnection never confirmed", "since": "2026-09-10", "days_open": 36, "next_action": "Release/hand over and confirm."},
        {"type": "status_unverified", "item": "Who was removed from the new group on 2026-10-10; whether she actually re-signed", "since": "2026-10-10", "days_open": 6, "next_action": "Owner checks Telegram and the contract system this week; update status."},
        {"type": "internal_investigation", "item": "Free full-nude previews given away by the chat team (her 2026-09-04 report with screenshot) - never investigated; Ollie named her OF contact again on 2026-10-09", "since": "2026-09-04", "days_open": 42, "next_action": "Chat leadership investigates and records the outcome before anyone works her account again."},
    ],
)


def build(slug):
    d = json.load(open(os.path.join(SRC, slug + ".json")))
    u = UPD[slug]
    d["as_of"] = "2026-10-16"
    d["status_reason"] = u["status_reason"]
    replace_in(d, u.get("replace", []))
    for dim, old, new in u.get("quote_fixes", []):
        fix_quote(d, dim, old, new)
    if "onboarding_extra" in u:
        txt, ev = u["onboarding_extra"]
        oh = d["dimensions"]["onboarding_handoff"]
        oh["internal_failure"] += txt
        oh["evidence"] = oh["evidence"][:2] + [ev]
    if "disengagement_extra" in u:
        d["dimensions"]["disengagement_detection"]["internal_failure"] += u["disengagement_extra"]
    if "security_extra" in u:
        d["dimensions"]["security_hygiene"]["internal_failure"] += u["security_extra"]
    m = d["metrics"]
    for k, v in u["metrics"].items():
        m[k] = v
    m["method"] = m["method"] + u["method_note"]
    # timeline: drop the old "as of 2026-10-09" tail entry and append the new tail
    tl = [e for e in d["churn_timeline"] if not (e["date"] == "2026-10-09" or e["date"].endswith("to 2026-10-09"))]
    d["churn_timeline"] = tl + u["timeline_tail"]
    d["warning_signs_missed"] = d["warning_signs_missed"] + u["extra_signs"]
    d["dangling_as_of_2026-10-16"] = u["dangling"]
    d["changes_since_2026-10-09"] = (
        "No new messages from anyone in the chat; every dangling item from the 2026-10-09 run is still open; elapsed-day figures re-dated."
        if slug != "kaitlynn-x-altr" else
        "Original chat replaced in the export by a new group created 2026-10-09 (templated onboarding, member removed 2026-10-10, zero client messages). Status kept as churned; re-onboarding unverified. First-engagement findings carried unchanged."
    )
    # stable key order
    order = ["client", "slug", "as_of", "status", "status_reason", "last_client_message", "changes_since_2026-10-09", "dimensions", "metrics",
             "what_client_wanted", "what_worked", "top_fix", "churn_timeline", "warning_signs_missed", "dangling_as_of_2026-10-16"]
    out = {k: d[k] for k in order if k in d}
    for k in d:
        if k not in out:
            out[k] = d[k]
    with open(os.path.join(DST, slug + ".json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", slug, {k: v["severity"] for k, v in out["dimensions"].items()})


for s in UPD:
    build(s)
