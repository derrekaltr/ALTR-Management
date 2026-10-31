import json
P = "data/state/lilia-x-altr.json"
s = json.load(open(P))

s["as_of"] = "2026-10-16"
s["window_covered"] = ("2026-10-09T09:05:57-04:00 -> 2026-10-16T09:06:40-04:00. 48 non-service msgs: 23 client, 25 team "
                       "(Melissa 12, Mayson 5, Stephski 4, Vivek 2, Fred 1, Mica 1). No service events. Message ids 1261-1262 "
                       "missing (deleted) on Oct 13 between 13:42 and 20:09. No unknown senders; Jeremy Tarr / Spencer P not present in this chat.")

oc = {c["issue"][:40]: c for c in s["open_complaints"]}
def find(prefix):
    for c in s["open_complaints"]:
        if c["issue"].startswith(prefix):
            return c
    raise KeyError(prefix)

c = find("Chat team sells high spenders")
c["last_raised"] = "2026-10-13"; c["age_days"] = 126; c["escalation_count"] = 13
c["escalation_dates"].append("2026-10-13")
c["spenders_affected"] = ["frumby", "Matt (new 2026-10-13)"]
c["status"] = ("recurring - 13th escalation Oct 13: 'Hey they are sending matt stuff he already has!' -> Fred within 1 min "
               "'Hey checking with the team now! Apologies' -> client 'It’s fine he hasn’t noticed' / 'So just leave it!'. "
               "LOWERED EXPECTATIONS = churn tell. Sep 23 'We’ll check' now 23 days with no follow-up; Jul 24 chatter unnamed 84 days. "
               "Next week: did Fred report back on Matt despite 'leave it'; any frumby/Matt incident count; purchase-history check.")

c = find("Client-originated Halloween")
c["age_days"] = 15
c["status"] = "open - 15 days, still no specific OF-side reply (Fred's only msg this week was the Matt apology). Mica sent Halloween reel inspo Oct 14 (social only). Client uploading to high-end folder Oct 13. Next: price/Teddi flag/seller; costumes arrived?; any set sold."

c = find("Invoicing does not confirm")
c["age_days"] = 28; c["last_raised"] = "2026-10-06"
c["status"] = "recurring - Oct 6 payment + $27 still unacknowledged 10 days; Sep 18 (28d), Sep 3 (43d). Day-before reminder FIXED (sent Oct 13). Oct 15 invoice: client promised same-day payment; watch for ALTR receipt with amount."

c = find("Chatters do not communicate fan requests")
c["age_days"] = 79; c["days_unanswered"] = 48; c["status"] = "recurring - 48 days unanswered, seven windows."

c = find("TikTok shadowban never checked")
c["age_days"] = 59; c["last_raised"] = "2026-10-13"; c["escalation_count"] = 7; c["days_silent"] = None
c["status"] = ("recurring - Vivek resurfaced Oct 12 22:31 after 49 days ('Hey ma’am' / 'Send logins') after Mayson tagged @fonta twice re the flagged bio; "
               "client sent a screenshot + offered login code Oct 13 20:09; Mayson re-tagged Oct 14; Vivek silent since. "
               "Client Oct 13: 'Is me being shadowbanned going to effect it at all?' - unanswered (platform ambiguous; asked in Social Media topic re IG reel/link). "
               "Second time Vivek went quiet after requesting logins (Aug 24, Oct 12).")

c = find("Account/Drive confusion")
c["age_days"] = 126
c["status"] = "in_progress - second warmed-up IG account (lost login) 21 days no reply; no written account map; no Reels Drive upload confirmed. Melissa's Oct 12 repost used an existing reel ('no we do not' need the original)."

c = find("Her phone number was briefly public")
c["age_days"] = 24; c["status"] = "in_progress but stalled - 24 days, no movement."

c = find("Service-suspension line")
c["status"] = "RESOLVED 2026-10-15 - Oct 15 invoice text: 'Please use the invoicing information at the bottom of the PDF to ensure a smooth process' - pausing line gone."
c["closed"] = "2026-10-15"

c = find("ALTR's receiving details keep changing")
c["age_days"] = 116; c["status"] = "recurring/quiet - no 7th change; Oct 15 invoice points to PDF banking info; client did not ask 'same Zelle' this cycle. Still no written freeze."

c = find("CRM notes do not reach")
c["age_days"] = 42; c["status"] = "in_progress but unverified 42 days."

c = find("Chat team underpricing")
c["age_days"] = 97; c["status"] = "recurring - no new report. Still no written floor in CRM."

c = find("ALTR presence on the account is thin")
c["age_days"] = 28; c["last_raised"] = "2026-10-16"
c["status"] = "improving - Oct 9-16: Melissa 12, Mayson 5, Stephski 4, Vivek 2, Fred 1, Mica 1 (25 team msgs, billing 4). Fred (core operator) still 1 msg. Owner 0 (30 days)."

c = find("Ledger mismatch")
c["age_days"] = 52; c["status"] = "open - 52 days; ALTR still states no amounts."

c = find("Billing questions go unanswered")
c["status"] = "RESOLVED (pattern held this cycle) - no billing question this window; client acknowledged Oct 13 reminder and Oct 15 invoice within minutes; Stephski replied 'Thanks angel!' in 12 min."
c["closed"] = "2026-10-15"

c = find("Calls with no written recap")
c["age_days"] = 38; c["last_raised"] = "2026-10-15"; c["owner"] = "Mayson / Melissa"
c["status"] = "recurring - Melissa Oct 15 call (unprompted offer, held 12 PM) also unrecapped by window close. Mitigant: Melissa's Oct 9 written two-week earnings & performance report."

# move resolved complaints out
resolved = [x for x in s["open_complaints"] if x.get("closed")]
s["open_complaints"] = [x for x in s["open_complaints"] if not x.get("closed")]
for r in resolved:
    s["resolved_recently"].append({"issue": r["issue"][:160], "first_raised": r["first_raised"], "closed": r["closed"], "status": r["status"]})

s["open_complaints"].append({
    "issue": "ALTR-built link-in-bio domain (Mayson, Oct 11: 'it won’t get flagged and it’s completely safe') got her bio flagged Oct 12 ('I just got flagged for my bio', 'Should I take down the link'). Mayson tagged @fonta (Vivek) Oct 12 x2, Oct 14; Vivek 'Send logins' then silent. Oct 15 22:02 Mayson took the domain down and switched her to a direct link; client 'Okay illl put it on now! Thank u'.",
    "first_raised": "2026-10-12", "last_raised": "2026-10-13", "age_days": 4, "escalation_count": 3,
    "owner": "Mayson / Vivek",
    "status": "in_progress - replacement link given Oct 15 (client accepting). Open: confirm the new link isn't flagged; answer her shadowban question; Vivek to finish/close the login thread and the login screenshot she posted Oct 13 should be removed."})

for r in s["resolved_recently"]:
    if r["issue"].startswith("Weekly DMCA"):
        r["status"] = "HELD - Melissa delivered Oct 2 and Oct 9 (on schedule). Verify ~Oct 16."
    if r["issue"].startswith("Fred only reachable"):
        r["status"] = "STILL THIN - 1 msg in window (Oct 13 Matt apology, 1-minute response)."
    if r["issue"].startswith("Custom-approval rule"):
        r["status"] = "WORKING - 46 days, zero reported violations."
    if r["issue"].startswith("Invoice cadence"):
        r["status"] = "HELD Oct 15 - on cadence, day-before reminder sent Oct 13, pausing line removed. Remaining gap: receipts/amounts."

# commitments
def com(prefix):
    for x in s["open_commitments"]:
        if x["what"].startswith(prefix):
            return x
    raise KeyError(prefix)

done = []
x = com("Remove the 'to avoid any pausing"); x["status"] = "done - removed in Oct 15 invoice text"; x["closed"] = "2026-10-15"; done.append(x)
x = com("Send the day-before OF-withdrawal"); x["status"] = "done - sent Oct 13 ('your next invoice will be sent out in 2 days'). Keep watching each cycle (~Oct 30)."; x["closed"] = "2026-10-13"; done.append(x)
s["open_commitments"] = [y for y in s["open_commitments"] if not y.get("closed")]
for d in done:
    s["completed_recently"].insert(0, {"what": d["what"], "who": d["who"], "date": d["closed"], "closed": d["closed"], "status": d["status"]})

upd = {
 "Acknowledge and plan the Halloween": (15, "overdue - 15 days; no specific reply. Fred's only msg this week was the Matt apology."),
 "Investigate the Sep 23 old-content": (84, "overdue - 84 days on the naming; 23 days since 'We’ll check'; new Matt incident Oct 13. TOP ITEM."),
 "Confirm in writing receipt": (31, "overdue - Oct 6 payment + $27 still unacknowledged 10 days."),
 "Report back on the Aug 29": (48, "overdue - 48 days, seven windows."),
 "Restore the weekly DMCA": (None, None),
 "Check whether her TikTok": (59, "overdue - 59 days. Vivek resurfaced Oct 12 ('Send logins'), client supplied access Oct 13, Vivek silent again."),
 "Read and respond to the three screenshots": (53, "overdue - 53 days."),
 "Resolve her warmed-up second IG": (36, "overdue - 21 days since her 9/25 message, no reply."),
 "Send her one written map": (36, "pending/overdue - no written map."),
 "Client: upload reels": (17, "pending - no upload confirmed. Do not chase hard; she is uploading OF content again."),
 "Client: fill out ALTR's new private-platform": (18, "pending - completion not confirmed."),
 "Make Teddi's CRM notes": (47, "overdue - 47 days."),
 "Close out the exposed-phone-number": (24, "overdue - 24 days."),
 "Brief the chat team on the accepted shower": (66, "overdue - 66 days."),
 "Sell the red set to Adam West": (58, "overdue - 58 days."),
 "Get her a decision back to the fan": (46, "overdue - 46 days."),
 "Acknowledge and action her Aug 26": (51, "overdue - 51 days."),
 "Organise and price her uploaded": (67, "overdue - 67 days; she uploads to the high-end folder herself (Oct 13)."),
 "Enforce the $200/video": (49, "overdue - 49 days."),
 "Freeze the receiving details": (58, "pending - no 7th change; no written freeze; Oct 15 invoice points to PDF."),
 "Post a written recap of the Sep 8": (38, "overdue - Sep 8 + Oct 5 (Mayson) + Oct 15 (Melissa) calls all unrecapped."),
 "Reconcile Mayson's Aug 30": (47, "overtaken - quota not mentioned since; consider closing."),
 "Reconcile the $192 gap": (52, "overdue - 52 days."),
 "Deliver the promised IG phone-farm": (76, "overdue - 76 days; owner silent 30 days (last owner msg 2026-09-16 01:33) - 30-DAY CHURN THRESHOLD CROSSED this window. OWNER-LEVEL: surface privately to Derrek only; NEVER in the client-facing team/employee section."),
 "Push the new set she uploaded Oct 3": (12, "overdue - no sales reported back; more uploads Oct 13 ('I’ll put it in the Hugh end folder')."),
 "Client: send the $27": (10, "pending - not confirmed in chat 10 days. Do NOT chase; ALTR should confirm."),
}
for k, (age, st) in upd.items():
    try:
        x = com(k)
    except KeyError:
        continue
    if age is not None:
        x["age_days"] = age; x["status"] = st
    else:
        s["open_commitments"].remove(x)

s["open_commitments"] += [
 {"what": "Follow up on the Oct 13 Matt old-content incident and report back in writing (client said 'just leave it' - report anyway)",
  "who": "Fred", "promised": "2026-10-13", "due": "2026-10-16", "age_days": 3,
  "status": "pending - 'Hey checking with the team now! Apologies'."},
 {"what": "Fix the flagged bio/account and answer 'Is me being shadowbanned going to effect it at all?'; remove/rotate after using the login screenshot she posted Oct 13",
  "who": "Vivek", "promised": "2026-10-12", "due": "2026-10-14", "age_days": 4,
  "status": "pending - 'Send logins' Oct 12; client supplied access Oct 13; silent since; Mayson re-tagged Oct 14."},
 {"what": "Confirm the new direct link-in-bio (switched Oct 15) is live and not flagged",
  "who": "Mayson", "promised": "2026-10-15", "due": "2026-10-17", "age_days": 1, "status": "pending"},
 {"what": "Post a written recap of the Oct 15 call", "who": "Melissa", "promised": None, "due": "2026-10-16", "age_days": 1,
  "status": "pending - call held ~12 PM Oct 15; no recap by window close."},
 {"what": "Client: pay the Oct 1-14 invoice (issued Oct 15)", "who": "Lilia (client)", "promised": "2026-10-15", "due": "2026-10-22",
  "age_days": 1, "status": "pending - 'I’ll get it paid today! Thank you!' (Oct 15 13:54). Not confirmed by window close."},
]

s["completed_recently"] = [
 {"what": "Replace the flagged link-in-bio domain with a direct link", "who": "Mayson", "date": "2026-10-15", "closed": "2026-10-15",
  "status": "done - client 'Okay illl put it on now! Thank u'. But the domain Mayson set up Oct 11 caused the flag."},
 {"what": "Two-week earnings and performance report (written, PDF)", "who": "Melissa", "date": "2026-10-09", "closed": "2026-10-09",
  "status": "done - first in this chat; client 'Thank you as always!'. Counts against churn signal 2."},
 {"what": "Weekly DMCA leak-removal breakdown", "who": "Melissa", "date": "2026-10-09", "closed": "2026-10-09", "status": "done - on schedule."},
 {"what": "Reel pushed across 23-account repost network", "who": "Melissa", "date": "2026-10-13", "closed": "2026-10-13", "status": "done - client 'Yayyy thank u!!'."},
 {"what": "Issue the Oct 1-14 invoice on cadence", "who": "Stephski", "date": "2026-10-15", "closed": "2026-10-15", "status": "done - on cadence, pausing line removed."},
 {"what": "Weekly reel inspo incl. Halloween ideas", "who": "Mica Vecco", "date": "2026-10-14", "closed": "2026-10-14", "status": "done."},
] + s["completed_recently"][:8]

for p in s["payment_history"]:
    if p["date"] == "2026-10-01":
        p["outstanding"] = "$27 (client-reported; promised 2026-10-07) - not confirmed as of 2026-10-16"
        p["note"] += " As of 2026-10-16: $27 still not confirmed in chat; no ALTR receipt."
    if p["date"] == "2026-09-03":
        p["outstanding"] = "unknown - unconfirmed 43 days after issue (as of 2026-10-16)"
    if p["date"] == "2026-10-15":
        p.update({"note": "Invoice Oct 1-14, issued 2026-10-15 13:33 by Stephski ON CADENCE. Day-before reminder sent Oct 13 11:47 (client 'Yes! Thank u'). Pausing line REMOVED. Amount PDF-only. Client 13:54: 'I’ll get it paid today! Thank you!'; Stephski 'Thanks angel!'. Payment not confirmed by window close (Oct 16 09:06).",
                  "late": False, "status": "issued / promised same day / unconfirmed", "due": "2026-10-22", "reminder_sent": "2026-10-13",
                  "client_ack_minutes": 21})
s["payment_history"].append({"date": "2026-11-01", "note": "EXPECTED: Oct 15-31 invoice ~Nov 1 (reminder ~Oct 30). Watch: receipts with amounts (Oct 15 payment, $27, Sep 18, Sep 3, $192).", "late": None, "status": "upcoming"})

s["payment_risk"]["altr_side_risk"] = "No written receipt/amount for Oct 6 payment + $27 (10d), Sep 18 (28d), Sep 3 invoice (43d); $192 gap 52 days + uncredited round-up. FIXED this window: pausing line removed, day-before reminder sent Oct 13."
s["payment_risk"]["client_behaviour"] = "Six consecutive zero-chase cycles. Oct 15 invoice: promised same-day payment within 21 minutes. Self-reports balance."
s["payment_risk"]["open_amount"] = "$27 (Sept 15-30, unconfirmed); Oct 1-14 invoice (issued Oct 15, promised same day, unconfirmed); Aug 15-31 unconfirmed; $192 unreconciled."
s["payment_risk"]["next_invoice"] = "Oct 15-31 period, expected ~2026-11-01"
s["payment_risk"]["watch"] = ["Oct 15 payment lands and ALTR confirms the amount", "$27 confirmed", "$192 / Sep 3 / Sep 18 reconciled in writing", "Reminder ~Oct 30", "No seventh receiving-detail change", "Churn tell: fast pay continuing while she waves off problems ('just leave it')"]

s["client_priorities"] = [
 "Monetising high spenders with themed content - 10 Halloween costume sexting sets (Oct 1), Teddi pre-committed at ~$1,000/set; goal of 10 sexting sets in October; uploading to the high-end folder herself (Oct 13)",
 "Protecting her high spenders (frumby, Teddi, now Matt) - deletes mis-sent old content herself; on Oct 13 told ALTR to 'just leave it' because Matt hadn't noticed",
 "IG safety: a link in bio that doesn't get flagged (ALTR domain flagged Oct 12; switched to direct link Oct 15) and an answer on whether her shadowban hurts reach",
 "Exposure via ALTR's repost network (23-account reel push Oct 13, enthusiastic)",
 "Sell only from the labelled high-spender folder she builds - newest content first",
 "Chatters must communicate with her and ask before acting; the Aug 31 custom-approval rule works",
 "CRM notes the chat team actually reads (Teddi backstory: wife and kids died in a car crash; tests chatters)",
 "Price discipline: $200/video, $200/pic package, $100/min customs; sell 3-minute sexting sets individually with photos",
 "Paying cleanly and correctly - acknowledges invoices within minutes, tracks her own balance",
 "Clarity on IG accounts: new ALTR-made account understood; warmed-up second account with lost login unresolved",
 "Personality-driven social content per Mica's tips",
 "Getting settled after her house move",
 "DMCA weekly and the new two-week earnings report",
 "A stable payment rail and an ALTR balance that matches her own running total",
]

s["churn_signals"] = [
 "2026-10-16 - TWO OF FOUR EXPLICIT SIGNALS PRESENT:",
 "(1) PRESENT - owner silent 30 days in this chat (last Derrek msg 2026-09-16 01:33). Owner-level; handle privately.",
 "(2) NOT PRESENT - no results/revenue question deflected to a call; Melissa sent a WRITTEN two-week earnings & performance report Oct 9. Watch: Oct 15 Melissa call (unprompted) and Oct 5 / Sep 8 Mayson calls all lack written recaps.",
 "(3) PRESENT - long-promised deliverables without written proof: chatter removal (Jul 24, 84d), purchase-history check, Teddi CRM notes (Aug 30), TikTok/shadowban (Aug 18, 59d), account map, owner IG phone-farm update (Aug 1, 76d), Halloween plan reply (15d).",
 "(4) NOT PRESENT - billing 4 of 25 ALTR msgs (down from 7 of 14).",
 "Asks: 2 -> 8 -> 3 -> 1 -> 3 (this window: bio flag/'Should I take down the link', shadowban question, Matt old content). Up off the floor, BUT she withdrew the Matt one herself ('It’s fine he hasn’t noticed' / 'So just leave it!') - lowered expectations from a client with 13 escalations.",
 "Fast payment continues (promised same-day within 21 min) - not a health signal.",
 "MITIGATING: warm tone, uploading new content, enthusiastic about repost network, took Melissa's call instantly, accepted new link immediately.",
]

s["health_history"].append({"week_ending": "2026-10-16", "score": 49, "note": "flat; churn signals 1 and 3 present"})
s["week_stats_history"].append({"week_ending": "2026-10-16", "messages": 48, "client_messages": 23, "team_messages": 25, "client_asks": 3,
    "note": "Melissa 12, Mayson 5, Stephski 4 (billing), Vivek 2, Fred 1, Mica 1."})
s["engagement_trend"].append({"week_ending": "2026-10-16", "messages": 48, "client_messages": 23, "health": 49})
s["asks_trend"].append({"week_ending": "2026-10-16", "client_asks": 3,
    "note": "bio link flagged / 'Should I take down the link' (Oct 12); 'Is me being shadowbanned going to effect it at all?' (Oct 13, unanswered); Matt old content (Oct 13, she withdrew it: 'just leave it')."})
s["client_asks"] = [{"week_ending": a["week_ending"], "count": a["client_asks"]} for a in s["asks_trend"]]

sn = s["staffing_notes"]
sn["Fred (OFM)"] = "1 MSG (Oct 13, 1-min apology on Matt). Still nothing on Halloween (15d), frumby follow-up (23d), chatter naming (84d), phone number, or the older backlog. COACH: report back in writing even when she says 'leave it'."
sn["Stephski (invoicing)"] = "4 msgs, all billing. FIXED: day-before reminder Oct 13, pausing line removed, on-cadence Oct 15 invoice. Still no receipts/amounts; $27 unconfirmed; $192 at 52d."
sn["Melissa (Userfacing)"] = "12 msgs - best week on account: DMCA on time Oct 9, written two-week earnings report Oct 9, 23-account repost Oct 12-13, Oct 15 call (no written recap yet)."
sn["Mayson (queue)"] = "5 msgs: Oct 11 link-in-bio domain promised 'won’t get flagged' -> flagged Oct 12; escalated to Vivek x3; replaced with direct link Oct 15. Did not address second IG account or Oct 5 call recap."
sn["Vivek (Meta Support)"] = "2 msgs Oct 12 ('Hey ma’am' / 'Send logins') after 49 days silent; went quiet again after client supplied access Oct 13. Shadowban question unanswered. Second time going silent after asking for logins."
sn["Mica Vecco (Social Media Director)"] = "1 msg: Oct 14 reel inspo incl. Halloween. Second IG account / map still open."
sn["Derrek (owner)"] = "No messages; last 2026-09-16 01:33 = 30 days at window close - CHURN SIGNAL 1 CROSSED. IG phone-farm update 76 days overdue. OWNER-LEVEL: surface privately; never in client-facing team section."

s["credentials_flags"] = [
 "In-window (Oct 9-16): NO plaintext passwords/codes in text. Oct 12 Vivek 'Send logins' -> Oct 13 20:09 client posted a PHOTO (likely a login screenshot) in the group and offered to send the login code ('Let me know when u log in go to phone number and I’ll send u the code for it'). Image content not visible in export - treat as probable credential exposure in the group; recommend deleting it and rotating after use. Message ids 1261-1262 (Oct 13, between 13:42 and 20:09) were deleted - unknown content.",
] + [f for f in s.get("credentials_flags", []) if not f.startswith("In-window")]

s["notes"] = ("2026-10-16 RUN. 48 msgs (23 client/25 team). HEADLINES: (1) Old-content mis-send hit a 3rd named spender, Matt (Oct 13); Fred apologised in 1 min; client 'So just leave it!' - lowered expectations. "
              "(2) ALTR link-in-bio domain (Oct 11, 'won’t get flagged') got her flagged Oct 12; replaced with direct link Oct 15; Vivek resurfaced after 49d with 'Send logins' then silent; shadowban question unanswered. "
              "(3) Billing fixes landed: reminder Oct 13, on-cadence invoice Oct 15, pausing line removed; still no receipts, $27 unconfirmed. "
              "(4) Melissa strong: DMCA, first written two-week earnings report, 23-account repost, Oct 15 call (no recap). "
              "(5) Owner silent 30 days - churn signal 1 crossed; signal 3 present. Asks 1 -> 3. "
              "PRESERVED FACTS: " + s["notes"].split("PRESERVED FACTS: ", 1)[-1] +
              " NEW: Matt = third spender sent already-owned content (Oct 13). Link in bio now a direct xli.ink link (Oct 15); prior ALTR domain taken down. Client's Telegram handle @Liliaanglex. Vivek's handle @fonta.")

json.dump(s, open(P, "w"), indent=2, ensure_ascii=False)
print("ok", len(s["open_complaints"]), len(s["open_commitments"]))
