import json

P = "data/state/liza-kovalenko-x-altr.json"
F = "data/weeks/2026-10-16/liza-kovalenko-x-altr.json"
s = json.load(open(P))
f = json.load(open(F))

s["as_of"] = "2026-10-16"
s["last_report_window"] = {
    "start": "2026-10-09T09:05:57-04:00",
    "end": "2026-10-16T09:06:40-04:00",
    "length": "one week",
    "note": "29 non-service msgs + 2 service events (ChatAddUser x2 10-13 18:08 = Spencer P, Jeremy Tarr). Client 8; ALTR 21 (Stephski 8, Mayson 4, Melissa 2, Vivek 2, Spencer P 2, Aroosha 1, Jeremy Tarr 1, Mica 1); vendor 0. Billing 8/21 (38%). CREDENTIAL HYGIENE: no new credentials this window; plaintext IG passwords (08-31 client, 09-12 Michelle) and live IG 2FA code (10-08 17:11 client) still in chat - always render [REDACTED].",
}

s["churn_watch"] = {
    "level": "high",
    "signals_present": [
        "Owner silent 30+ days: Derrek last posted 2026-08-04 (73 days at 10-16).",
        "Long-promised deliverable with no written proof: Phone Farm updates (08-01), paid-ads stats (2025-11-18), IG recovery status (46d), written confirmation 09-24 customs delivered (22d).",
        "ZERO ASKS: client asks 3 -> 0; all 8 client msgs acknowledgements/billing.",
        "Fast/over payment tell: $3,189 received vs $2,224.88 owed; 'I'll pay all at once' (10-13); 'Will send shortly' 1 min after Oct 1-14 invoice.",
    ],
    "signals_absent": [
        "Results question answered with call offer: no results question; Melissa sent written earnings/performance report 10-09.",
        "Majority ALTR msgs billing: 8/21 (38%) this window, down from 57%.",
        "No export/login/data asks; no mention of other agencies.",
    ],
    "trend": "Worsening. Exit-signature pattern (zero asks + prompt settling + warm acknowledgements) appeared this window on top of unchanged structural signals. If the Oct 1-14 invoice is paid fast with zero asks again, treat as active exit; owner outreach needed now.",
}

s["open_complaints"] = [
    {"issue": "Credential/2FA exposure. Plaintext passwords for 3 IG handles (client 08-31 at Vivek's request; Michelle re-posted @Lizakovaal's 09-12) + live 6-digit IG 2FA code posted by client 10-08 at unintroduced IG farm vendor's request. Never disclosed/deleted/rotated. Membership changed again 10-13 (+2: Spencer P, Jeremy Tarr). No new exposure 10-09..10-16.", "owner": "Derrek / Vivek / Michelle / IG farm vendor", "first_raised": "2026-08-31", "worsened_on": ["2026-09-12", "2026-10-08"], "status": "recurring", "days_outstanding": 46, "escalation": "OWNER-LEVEL; termination-grade if she discovers it unprompted."},
    {"issue": "09-24 customs delivery lost in Ronnie->Aroosha handoff; 10-08 client re-pointed to her Dropbox link, Aroosha 'Thank you so much!!' (implicitly found) but no written confirmation they reached the fan. 10-08 top-spender request and 10-11 voice/video custom open; per-custom price never given. Customs owner now Spencer P (3rd owner in 3 weeks).", "owner": "Aroosha / Spencer P", "first_raised": "2026-09-25", "status": "in_progress", "days_outstanding": 22, "next_check": "Did Spencer/Aroosha confirm delivery of the 09-24 three in writing and give the price on the 10-08 request?"},
    {"issue": "Content format question 'What exactly you need , reels/ picks?' (09-24) unanswered 22 days / four windows. Mica's 10-14 bare-link drop didn't answer it. Spencer P now claims 'content uploads' - ownership unclear.", "owner": "Mica Vecco / Spencer P", "first_raised": "2026-09-25", "status": "recurring", "days_outstanding": 22},
    {"issue": "NEW: link-in-bio reversal + internal debugging in client chat. 10-11 Mayson: domain lizaswrld.com back, 'completely safe', put it in bio (client 'Amazing !!'); 10-12 Mayson/Vivek debug in group ('@fonta is the domain the problem?' / 'Yes'); 10-15 domain taken down, switch to xli.ink direct link. No client reaction yet.", "owner": "Mayson / Vivek", "first_raised": "2026-10-11", "status": "new", "days_outstanding": 5},
    {"issue": "Three deleted/suspended IG accounts (@Lizakovaal, @lizkovalenkoo, @Lizaakovalenk0) - no written status ever. Vendor logged into @Lizakovaal 10-08 (unexplained). Vivek posted 10-12 (first since 08-31) only about the bio domain. Same IG-integrity problem since 2025-10-10; what the $40k Phone Farm / Meta Support Rep were sold as fixing.", "owner": "Vivek / Derrek", "first_raised": "2025-10-10", "escalated_to_deleted": "2026-08-30", "status": "recurring", "days_outstanding": 371, "days_since_credentials_handed_over": 46},
    {"issue": "Owner silence - Derrek last posted 2026-08-04 (73 days). Phone Farm update promise (08-01) undelivered; never introduced IG farm vendor; $5,000 under-credit unacknowledged.", "owner": "Derrek", "first_raised": "2026-08-14", "status": "recurring", "days_silent": 73},
    {"issue": "$5,000 under-credit (found by the client with receipts; corrected silently 09-09) never acknowledged.", "owner": "Derrek / Stephski", "first_raised": "2026-09-04", "corrected_on": "2026-09-09", "status": "in_progress", "days_unacknowledged": 37},
    {"issue": "Reconciliation: IMPROVED. 10-12 Stephski flagged non-arrival of remainder herself (first time ALTR caught it before the client); 10-15 confirmed $3,189 with number, overpayment rolled over. Still open: $420 (09-24, Jose M Munoz Linss) bounce cause unidentified; $3,189 vs $2,224.88 difference unexplained in chat.", "owner": "Stephski", "first_raised": "2026-10-01", "status": "in_progress", "days_outstanding": 15},
    {"issue": "Seventh-banking-change risk. Six ALTR banking changes since 2025-09-27; 3 bounce episodes since the 08-15 account-number change. No change announced 10-09..10-16 (invoice says use info at bottom of PDF).", "owner": "Stephski / Derrek", "first_raised": "2025-09-27", "status": "recurring", "change_count": 6, "change_log": ["2025-09-27 OF Match Ent -> Social Depot LLC (JPMorgan Chase)", "2026-04-15 new bank", "2026-06-15 Mercury", "2026-07-01 Bank of America ('last change I promise!')", "2026-08-15 new account number", "2026-09-15 beneficiary name change"], "bounce_log": ["2026-08 wires bounced after 08-15 account-number change, resent", "2026-09-24 $420 wire (Jose M Munoz Linss) bounced, reported by client 10-08"]},
    {"issue": "Reel-inspo format REGRESSED: concrete tip 10-06 got warm reply; 10-14 back to 8 bare links, no reply.", "owner": "Mica Vecco", "first_raised": "2026-06-09", "status": "recurring", "days_outstanding": 129},
    {"issue": "OF 'tag a creator' flag never diagnosed; 'So I just tag someone and that’s it ?' (08-09) unanswered 68 days. Ronnie silent since 09-23 yet named as current AM by Jeremy Tarr 10-13.", "owner": "Ronnie / Jeremy Tarr", "first_raised": "2026-01-26", "status": "recurring", "days_outstanding": 263},
    {"issue": "DMCA takedown reporting dark in this chat since 2026-03-04 (226 days). Melissa's performance report now lands here; leak-removal update does not.", "owner": "Nick (DMCA) / Melissa / Derrek", "first_raised": "2026-03-04", "status": "recurring", "days_outstanding": 226},
    {"issue": "Facebook access asks dead: Mica 03-11 (219d), Mayson 09-16 duplicate (30d). Client declined FB management Jan 2026.", "owner": "Mica Vecco / Mayson", "first_raised": "2026-03-11", "status": "recurring", "days_outstanding": 219},
]

s["resolved_last_period"] = [
    {"issue": "Sep 15-30 remainder ($2,224.88) unverified - resolved: $3,189 received, confirmed with number, overpayment rolled into Oct 1-14 invoice.", "owner": "Stephski", "first_raised": "2026-10-08", "resolved_on": "2026-10-15", "evidence": "2026-10-15 Stephski: 'we recieved! it was $3189 so i rolled over the over payment below'"},
    {"issue": "Client-audited reconciliation (ALTR never caught missing funds first) - partially resolved: Stephski flagged non-arrival proactively.", "owner": "Stephski", "first_raised": "2026-08-25", "resolved_on": "2026-10-12", "evidence": "2026-10-12 Stephski: 'Hi love just letting you know we havent seen it come through on our side yet'"},
]

s["open_commitments"] = [
    {"what": "Tell Liza her plaintext IG password was re-posted by ALTR; delete the 08-31, 09-12 and 10-08 credential/2FA messages; rotate all three passwords; move 2FA/credential exchange (incl. IG farm vendor) to DM", "who": "Derrek / Vivek", "date": "2026-08-31", "promised_due": "2026-08-31", "status": "overdue", "days_overdue": 46},
    {"what": "Recover or state outcome on the three deleted IG accounts", "who": "Vivek", "date": "2026-08-31", "promised_due": "not stated", "status": "overdue", "days_overdue": 46},
    {"what": "Confirm in writing the 09-24 customs (first three) were received and delivered; give price on 10-08 top-spender request", "who": "Aroosha / Spencer P", "date": "2026-10-08", "promised_due": "not stated", "status": "pending", "days_open": 8},
    {"what": "Answer 'What exactly you need , reels/ picks?'", "who": "Mica Vecco / Spencer P", "date": "2026-09-24", "promised_due": "2026-09-24", "status": "overdue", "days_overdue": 22},
    {"what": "CLIENT, blocked on ALTR: upload content to Drive. Do NOT chase until her format question is answered.", "who": "Liza Kovalenko (client) / Mica Vecco", "date": "2026-09-24", "promised_due": "2026-09-24", "status": "pending", "days_overdue": 0},
    {"what": "CLIENT: pay Oct 1-14 invoice ('Will send shortly' 10-15)", "who": "Liza Kovalenko (client)", "date": "2026-10-15", "promised_due": "~2026-10-22", "status": "pending", "days_overdue": 0},
    {"what": "CLIENT: fulfil 10-11 voice-note/video custom ('Thank you will do xx')", "who": "Liza Kovalenko (client)", "date": "2026-10-12", "promised_due": "not stated", "status": "pending", "days_overdue": 0},
    {"what": "Handle all customs, content uploads, backend chat assistance (new owner)", "who": "Spencer P", "date": "2026-10-13", "promised_due": "ongoing", "status": "pending", "days_overdue": 0},
    {"what": "Day-to-day AM, respond 'as quickly as possible'", "who": "Jeremy Tarr", "date": "2026-10-13", "promised_due": "ongoing", "status": "pending", "days_overdue": 0},
    {"what": "Identify why the 09-24 $420 wire bounced; explain $3,189 vs $2,224.88", "who": "Stephski", "date": "2026-10-08", "promised_due": "not stated", "status": "pending", "days_overdue": 0},
    {"what": "CLIENT: fill out Melissa's intake form ('Ok ill do', 10-02)", "who": "Liza Kovalenko (client)", "date": "2026-10-02", "promised_due": "not stated", "status": "pending", "days_overdue": 0},
    {"what": "Acknowledge the $5,000 under-credit to the client", "who": "Derrek", "date": "2026-09-09", "promised_due": "2026-09-10", "status": "overdue", "days_overdue": 36},
    {"what": "Phone Farm / backup-IG rollout updates", "who": "Derrek", "date": "2026-08-01", "promised_due": "week of 2026-08-09", "status": "overdue", "days_overdue": 68},
    {"what": "Paid-IG-ads statistics summary", "who": "Derrek", "date": "2025-11-18", "promised_due": "2025-11-23", "status": "overdue", "days_overdue": 327},
    {"what": "Investigate OF tag-a-creator flag", "who": "Ronnie / Jeremy Tarr", "date": "2026-08-09", "promised_due": "not stated", "status": "overdue", "days_overdue": 68},
    {"what": "Trial-reels call follow-up", "who": "Mayson", "date": "2026-09-04", "promised_due": "2026-09-07", "status": "overdue", "days_overdue": 39},
    {"what": "Monthly call (last real call 2026-06-07, 131 days)", "who": "Mayson / Derrek / Jeremy Tarr", "date": "2026-07-20", "promised_due": "2026-07-21", "status": "overdue", "days_overdue": 87},
    {"what": "Restart or explain DMCA takedown reporting in this chat", "who": "Nick (DMCA) / Melissa / Derrek", "date": "2026-03-04", "promised_due": "not stated", "status": "overdue", "days_overdue": 226},
    {"what": "Close the Facebook access loop with one owner", "who": "Mica Vecco / Mayson", "date": "2026-03-11", "promised_due": "not stated", "status": "overdue", "days_overdue": 219},
    {"what": "Keep concrete social tips like 10-06 on a weekly cadence (10-14 reverted to bare links)", "who": "Mica Vecco", "date": "2026-10-06", "promised_due": "weekly", "status": "overdue", "days_overdue": 2},
    {"what": "Repeat proactive IG security advisories like Mica's 09-17 post (none since) - urgent given 2FA posted in chat", "who": "Mica Vecco", "date": "2026-09-17", "promised_due": "ongoing", "status": "pending", "days_overdue": 0},
]

s["completed_recently"] = [
    {"what": "Two-week earnings and performance report (written)", "who": "Melissa", "date": "2026-10-09"},
    {"what": "Proactively flagged remainder non-arrival before the client did", "who": "Stephski", "date": "2026-10-12"},
    {"what": "Confirmed $3,189 received with number; overpayment rolled over", "who": "Stephski", "date": "2026-10-15"},
    {"what": "Oct 1-14 invoice issued on schedule with 2-day heads-up", "who": "Stephski", "date": "2026-10-15"},
    {"what": "Direct link in bio (xli.ink) delivered after domain take-down", "who": "Mayson", "date": "2026-10-15"},
    {"what": "Proper self-introductions with role (customs/uploads; AM)", "who": "Spencer P / Jeremy Tarr", "date": "2026-10-13"},
]

# payment history: update remainder entry and add new
for e in s["payment_history"]:
    if e.get("date") == "2026-10-08" and e.get("amount") == 2224.88:
        e["status"] = "received as $3,189 (overpaid ~$964.12, rolled over) - confirmed 2026-10-15"
        e["receipt_verified"] = True
        e["late"] = True
        e["note"] += " UPDATE: Stephski 10-12 'havent seen it come through'; client 10-13 offered to add to next invoice; 10-15 Stephski 'we recieved! it was $3189'. ~1 week past 10-08 due (transit unknown)."
    if e.get("date") == "2026-10-01" and e.get("status") == "partially paid":
        e["status"] = "paid in full (10-02 $6,000 + 10-15 $3,189)"
        e["receipt_verified"] = True
        e["late"] = False
s["payment_history"].append({"date": "2026-10-15", "note": "Oct 1-14 invoice issued 10-15 on schedule (heads-up 10-13); amount in PDF only, includes rolled-over overpayment credit. Client 'Will send shortly' within 1 min.", "late": None, "receipt_verified": None, "status": "issued, unpaid", "due": "~2026-10-22"})

s["payment_risk"] = {
    "level": "low-medium",
    "direction": "improving",
    "summary": "Sep 15-30 invoice fully settled (overpaid). ALTR caught non-arrival itself for the first time (10-12). Residual: $420 bounce cause unidentified; $3,189 vs $2,224.88 unexplained; 3 bounce episodes since 08-15; third-party senders. CHURN READ: overpayment + 'I'll pay all at once' + instant 'Will send shortly' in a zero-ask week = exit-pattern settling, not health.",
    "open_amount": "Oct 1-14 invoice (amount not stated in text), issued 10-15, due ~10-22",
    "drivers": [
        "Six banking changes since 2025-09-27; bounce history (08-15 change; 09-24 $420)",
        "Third-party sender names (Leticia Linss, José Muñoz / Jose M Munoz Linss, Edgardo R Canales)",
        "Side-channel rails bypass Stephski (crypto to Derrek, Zelle, fanbasis 5% surcharge)",
        "Mexican banks require in-person branch visits; partner sends wires",
    ],
    "next_event": "Oct 1-14 payment (~10-22). Fast payment + zero asks again = active exit signal.",
}

s["client_priorities"] = f["client_priorities"]

s["asks_trend"].append({"week_ending": "2026-10-16", "client_asks": 0, "billing_instructions": 1, "note": "All 8 client msgs acknowledgements/billing. Only request was billing: 'please just add what I owe you yo next invoice' (10-13). CHURN ALARM: 3 -> 0."})

s["health_history"].append({"week_ending": "2026-10-16", "score": 43, "trend": "down", "reason": "Billing clean (ALTR caught non-arrival, $3,189 confirmed, invoice on time), Melissa written report. Offset: asks 3->0, 8 ack-only client msgs, overpayment (exit pattern); 3rd customs owner in 3 weeks; 09-24 customs still unconfirmed; reels/picks 22d; link-in-bio reversal + internal debug in chat; creds 46d; owner 73d. Churn signals 1+3 present + both tells."})

s["week_stats_history"].append({"week_ending": "2026-10-16", "messages": 29, "client_messages": 8, "team_messages": 21, "client_asks": 0, "note": "Stephski 8, Mayson 4, Melissa 2, Vivek 2, Spencer P 2, Aroosha 1, Jeremy Tarr 1, Mica 1; vendor 0. Billing 8/21."})
s["engagement_trend"].append({"week_ending": "2026-10-16", "messages": 29, "client_messages": 8, "health": 43, "note": "Client 37 -> 8, asks 3 -> 0."})

s["notes"] = (
    "Client posts as 'Eli' (Liza; IG @xanaduexpress). Timezone Mexico City; travels heavily. Warm tone throughout ('Hi love!', 'No worries babe'). Honest to a fault: refused a credit for her own bounced wire.\n\n"
    "WATCH NEXT WEEK, IN ORDER: (1) Client asks - 0 this week after 3; a second zero-ask week with fast Oct 1-14 payment = active exit. (2) Derrek breaks 73-day silence / credential disclosure+rotation / IG status / $5,000 ack. (3) Spencer confirms 09-24 customs delivered in writing; price on 10-08 request; 10-11 custom delivered? (4) 'reels/ picks?' answered (22d) and by whom (Mica vs Spencer). (5) Client reaction to link-in-bio switch (lizaswrld.com -> xli.ink). (6) Oct 1-14 payment speed + any bounce; $420 bounce cause. (7) Jeremy Tarr closes any old loop (tag-a-creator, monthly call). (8) Any further credentials/2FA posted in-group; vendor activity. (9) Any export/login/data asks or mentions of other agencies.\n\n"
    "SILENCE CLOCKS (as of 2026-10-16): Derrek 73d (last 2026-08-04) | Nick DMCA 226d (2026-03-04) | Sophie Logan 354d (2025-10-27) | Nate (Noah) 268d (2026-01-21) | Michelle 34d (2026-09-12) | Ronnie 23d (2026-09-23) | IG farm vendor 8d (2026-10-08) | Melissa 7d (2026-10-09) | Aroosha 5d (2026-10-11) | Vivek 4d (2026-10-12; first since 08-31, domain only) | Spencer P / Jeremy Tarr 3d (2026-10-13) | Mica 2d (2026-10-14) | Stephski / Mayson 1d (2026-10-15).\n\n"
    "SENDERS: 'Aroosha s' = Aroosha (customs 10-05..10-13; uncertain in team.yaml). 'Spencer P' = customs/content uploads/backend chat from 10-13 (uncertain). 'Jeremy Tarr' = AM from 10-13 'alongside Nate, Ronnie, and Sophie' (uncertain). 'Stardust Nexus' / 'Theta SDX' = IG farm vendor (unconfirmed); joined 10-02 / 10-08; never introduced. Mayson tags Vivek as '@fonta'.\n\n"
    "FACTS: Banking changed 6x since 2025-09-27 (latest beneficiary name 2026-09-15). Card links carry 5% surcharge (fanbasis). Crypto rail USDT ERC20 direct to Derrek bypasses Stephski. Third-party senders: Leticia Linss, José Muñoz / Jose M Munoz Linss, Edgardo R Canales. Custom tracking sheet: docs.google.com/spreadsheets/d/1oR5L3Ajngl-TiI-Smv0zdvpw2MUH7992Rdav9ydEELc. Customs delivered via Dropbox link 09-24 (the lost delivery). Content Drive: drive.google.com/drive/folders/1R21PSH_ekNWDMB1M_nSTIN99irWTRE7_. Link in bio: lizaswrld.com restored 10-11, taken down 10-15; now xli.ink/liza-kovalenko. @Lizakovaal is the ALTR-managed reels/backup account; vendor logged in 10-08. Top fan behind 10-05/10-08 custom: $8.6k lifetime. Melissa sends bi-weekly earnings/performance report (10-09). Topics: Social Media (2), Invoicing (3), DMCA Takedowns (4, dead), Onlyfans Updates (5), Promo (100), Resources, Facebook. She declined FB management Jan 2026 after growing 110k followers herself. Proven: specific named asks get fast delivery; concrete written tips get replies; bare inspo links get nothing. "
    "CREDENTIALS: plaintext IG passwords in chat messages of 2026-08-31 (client) and 2026-09-12 (Michelle Queue); live IG 2FA code 2026-10-08 17:11 (client) - always render as [REDACTED]."
)

json.dump(s, open(P, "w"), ensure_ascii=False, indent=2)
print("ok")
