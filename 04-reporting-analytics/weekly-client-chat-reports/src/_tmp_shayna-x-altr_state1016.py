import json

# ---- 1. verify every evidence quote is verbatim in the chat ----
msgs = [json.loads(l) for l in open("data/chats/shayna-x-altr.jsonl")]
texts = [m.get("text") or "" for m in msgs]
W = json.load(open("data/weeks/2026-10-16/shayna-x-altr.json"))
bad = 0
for sec in ("reminders", "complaints", "commitments", "payments"):
    for it in W[sec]:
        for ev in it.get("evidence", []):
            q = ev["quote"]
            if not any(q in t for t in texts):
                bad += 1
                print("NOT VERBATIM:", sec, ev["date"], q[:80])
print("quote check done, bad =", bad)

# ---- 2. update carry-forward state ----
P = "data/state/shayna-x-altr.json"
S = json.load(open(P))
S["as_of"] = "2026-10-16"

S["open_complaints"] = [
    {"issue": "NEW: Link in bio unreliable / lost traffic. On 10/11 Mayson said the domain (shaynasworld.vip) was back and 'completely safe'. On 10/15 she said 'I’m not getting traffic because of it', and the domain was 'taken down' and replaced with xli.ink/shayna-holt that night. She asked about flagging 3x (10/12, 10/15, 10/16), and the 10/16 answer was hedged ('as how instagram currently stands'). CHECK: is the xli.ink link live in her bio and getting traffic? Any written explanation of why the domain was pulled? Does she re-ask?",
     "first_raised": "2026-10-15", "owner": "Mayson / Vivek", "status": "in_progress", "last_raised": "2026-10-16", "days_outstanding": 1,
     "movement_last_window": "NEW; replacement delivered in 9.5h"},
    {"issue": "Slow response / dropped threads (Fred). Fred posted 0 messages 10/9-10/16 and has been silent since 10/6. Nothing on the 7/21 live (20d since 'Will keep you updated!'), the $600 custom, the 10/2 and 10/8 relays, or VIP DEE. Mayson is fast, so the gap is Fred-specific. CHECK: does Fred post at all? Relay confirmations without a re-ask?",
     "first_raised": "2026-08-07", "owner": "Fred", "status": "recurring", "last_raised": "2026-10-06", "days_outstanding": 70,
     "movement_last_window": "REGRESSED (Fred absent all window)"},
    {"issue": "Untracked fan payments / Notion. The 7/21 $500 live tip (fan on a $9,000 VIP run) is unscheduled at 87d. Unlogged: Dante $600 (9/3), the 8/16 big-spender custom, the 8/23 Jim push, the 7/21 fan and the 9/26 $600 custom. CHECK: logged? scheduled?",
     "first_raised": "2026-04-22", "owner": "Fred", "status": "recurring", "last_raised": "2026-09-26", "days_outstanding": 177,
     "movement_last_window": "NONE"},
    {"issue": "Management-run second IG still unproven (client said 10/3 'I don’t think we’ve ever started an extra IG for me'; got 'We did' + Drive link). On 10/12 Mica asked for reels again without proof, and the client ignored it (2nd ignored reel ask). Phone-farm updates promised 8/1 are 76d old. CHURN SIGNAL: long-promised deliverable with no written proof. CHECK: handle/posts/metrics shown in writing? Does she upload reels or keep ignoring?",
     "first_raised": "2026-09-10", "owner": "Mayson / Mica Vecco / Derrek", "status": "recurring", "last_raised": "2026-10-03", "days_outstanding": 36,
     "movement_last_window": "NONE; client silent on reel asks"},
    {"issue": "DMCA / leak removal. Melissa's ~10/9 weekly report was MISSED, the first miss since 9/25. The ~10/16 report was not in by 09:06 window close. The client's 9/30 new-leaks ask is 16d old with only Derrek's 'Yep'. CHECK: did a 10/16 report land later that day? Report ~10/23? New leaks actioned with an ETA?",
     "first_raised": "2026-09-15", "owner": "Melissa / Derrek", "status": "recurring", "last_raised": "2026-09-30", "days_outstanding": 31,
     "movement_last_window": "REGRESSED"},
    {"issue": "PAYMENT OPS. Sept 15-30 (due ~10/8) is 8d past due with no 'sent', chase or receipt. Neither the 10/13 reminder nor the 10/15 invoice mentioned it. Aug 15-31 is 38d past due and unreconciled. Receipts are unconfirmed for 8/26 and 9/15. The Oct 1-14 invoice was issued 10/15, due ~10/22. CHECK: is anything reconciled? Was Oct 1-14 paid by ~10/22, and how fast? (A sudden fast, clean payment with zero asks is a churn tell.)",
     "first_raised": "2026-07-05", "owner": "Stephski", "status": "recurring", "last_raised": "2026-10-15", "days_outstanding": 103,
     "movement_last_window": "MIXED: reminder and invoice on time; open invoices untouched"},
    {"issue": "PAID-BUT-UNDELIVERED lives. Jason @u415682280 $1,000 (paid 7/7, withdrew 9/9) and Manuel @u20689003 $600 (paid 5/22). Neon View 9/10 never confirmed. The 7/21 $500 live is stalled. FIVE windows unmentioned.",
     "first_raised": "2026-05-22", "owner": "Fred (owner-level: Derrek)", "status": "recurring", "last_raised": "2026-09-26", "days_outstanding": 147,
     "exposure_remaining_usd": 2100, "movement_last_window": "NONE"},
    {"issue": "Monthly check-in call never held (agreed 8/28). No time was ever proposed. Mayson was in the chat 5 of 6 days 10/11-10/16 and did not raise it.",
     "first_raised": "2026-08-28", "owner": "Mayson", "status": "recurring", "last_raised": "2026-10-01", "days_outstanding": 49,
     "movement_last_window": "NONE"},
    {"issue": "Private 1:1 lives ban (since 7/27). No breach. The 9/22 VIP DEE instruction is unacknowledged (24d). The 9/3 internal-notes fix is unconfirmed (43d).",
     "first_raised": "2026-07-27", "owner": "Fred", "status": "recurring", "last_raised": "2026-09-22", "days_outstanding": 81,
     "movement_last_window": "NONE"},
    {"issue": "Chatter-conduct backlog (no new instances): VIP full-nude make-whole and the unnamed replacement chatter (8/11); no-freebies vault-notes rule (8/6); PG mass folder (8/5); freeloader block (7/28, re-raised 9/7); 9/6 no-lowballing relay; 8/7 custom question; OF auto-scheduler check.",
     "first_raised": "2026-04-15", "owner": "Fred", "status": "recurring", "last_raised": "2026-09-07", "days_outstanding": 184,
     "movement_last_window": "NONE"},
]

S["resolved_previously"].append(
    {"issue": "Mica client-specific reel inspo gap (none 9/15-10/13)", "owner": "Mica Vecco", "resolved_on": "2026-10-14",
     "note": "6 reel links incl. Halloween ideas: 'hi @shayna! here’s your reel inspo 💖💖'. Reopen if the weekly cadence lapses."})

S["open_commitments"] = [
    {"what": "Working, unflagged link in bio that drives traffic (xli.ink/shayna-holt replaced the pulled domain 10/15)", "who": "Mayson / Vivek", "date": "2026-10-15", "status": "pending", "days_outstanding": 1,
     "note": "The 10/11 'completely safe' domain was taken down 10/15. Traffic recovery unconfirmed."},
    {"what": "Report the 7/21 backlog-live fan's availability and lock a time", "who": "Fred", "date": "2026-09-26", "status": "overdue", "days_outstanding": 20},
    {"what": "Sell the dirty-talk custom (fan u561673786) at her $600; confirm and log on Notion", "who": "Fred", "date": "2026-09-26", "status": "overdue", "days_outstanding": 20},
    {"what": "Action her 9/30 new leaks with instructions/ETA", "who": "Derrek / Melissa", "date": "2026-09-30", "status": "overdue", "days_outstanding": 16, "note": "Only 'Yep'."},
    {"what": "Weekly leak-removal report (missed ~10/9; ~10/16 not in by window close; next ~10/23); explain the Michelle-to-Melissa handover", "who": "Melissa", "date": "2026-10-09", "status": "overdue", "days_outstanding": 7},
    {"what": "Show the management-run second IG in writing (handle, posts, metrics)", "who": "Mayson / Mica Vecco", "date": "2026-10-03", "status": "overdue", "days_outstanding": 13,
     "note": "Reels requested again 10/12 instead; client ignored."},
    {"what": "Confirm chatters were told about the 10/2 girls' night and the 10/8 birthday", "who": "Fred", "date": "2026-10-08", "status": "overdue", "days_outstanding": 8},
    {"what": "Hold the monthly check-in call with a fixed date/time", "who": "Mayson", "date": "2026-08-28", "status": "overdue", "days_outstanding": 49},
    {"what": "Acknowledge the 9/22 VIP DEE deflection instruction", "who": "Fred", "date": "2026-09-22", "status": "overdue", "days_outstanding": 24},
    {"what": "Correct internal notes so the no-private-lives ban is written down; confirm in chat", "who": "Fred", "date": "2026-09-03", "status": "overdue", "days_outstanding": 43},
    {"what": "Refund/credit/substitute decision: Jason $1,000 and Manuel $600; confirm Neon View 9/10 live", "who": "Fred (owner-level: Derrek)", "date": "2026-09-09", "status": "overdue", "days_outstanding": 37},
    {"what": "Confirm Sept 15-30 payment (due ~10/8); reconcile Aug 15-31; receipts for 8/26 and 9/15", "who": "Stephski", "date": "2026-10-08", "status": "overdue", "days_outstanding": 8},
    {"what": "Confirm the Oct 1-14 payment on arrival (due ~10/22) with a written receipt", "who": "Stephski", "date": "2026-10-22", "status": "pending"},
    {"what": "Weekly client-specific reel-inspo cadence (resumed 10/14; next ~10/21)", "who": "Mica Vecco", "date": "2026-10-21", "status": "pending"},
    {"what": "Consolidate social-account asks (@itsshaynaholt 8/28, Snapchat 9/9, Facebook 9/16)", "who": "Mayson", "date": "2026-08-28", "status": "overdue", "days_outstanding": 49,
     "note": "Logins collected via DM 10/12 and used 10/14 (accounts unspecified). May be partly progressing; confirm."},
    {"what": "Phone-farm updates ('plenty of updates starting next week')", "who": "Derrek", "date": "2026-08-01", "status": "overdue", "days_outstanding": 76},
    {"what": "Relay 9/6 no-lowballing instruction (long sex-positions video) and confirm", "who": "Fred", "date": "2026-09-06", "status": "overdue", "days_outstanding": 40},
    {"what": "Freeloader block / mute after 7 unpurchased PPVs", "who": "Fred", "date": "2026-07-28", "status": "overdue", "days_outstanding": 80},
    {"what": "Make whole VIP full-nude payers; name replacement chatter", "who": "Fred", "date": "2026-08-11", "status": "overdue", "days_outstanding": 66},
    {"what": "Answer 8/7 question: does flagged fan have a custom?", "who": "Fred", "date": "2026-08-07", "status": "overdue", "days_outstanding": 70},
    {"what": "No-free-photos/sexting rule in vault notes, confirmed to client", "who": "Fred", "date": "2026-08-06", "status": "overdue", "days_outstanding": 71},
    {"what": "Client-approved PG mass-message folder", "who": "Fred", "date": "2026-08-05", "status": "overdue", "days_outstanding": 72},
    {"what": "Log on Notion: Dante $600, 8/16 big-spender custom, 8/23 Jim push, 7/21 $500 live fan, 9/26 $600 custom", "who": "Fred", "date": "2026-09-01", "status": "overdue", "days_outstanding": 45},
    {"what": "Daily OF auto-scheduler check", "who": "Fred", "date": "2026-08-05", "status": "pending", "note": "No incident since 8/5; never confirmed running."},
    {"what": "STANDING: no new private 1:1 lives sold; paid backlog honoured by her choice; VIP DEE deflected with travel excuses", "who": "Fred", "date": "2026-07-27", "status": "pending"},
    {"what": "STANDING: every custom approved AND priced by her before sale", "who": "Fred", "date": "2026-04-15", "status": "pending", "note": "4 for 4 since 9/8; no new ask 10/2-10/16."},
    {"what": "STANDING: chatter scripts synced to her real life (back from Colorado trip; birthday 10/8 passed)", "who": "Fred", "date": "2026-10-06", "status": "pending"},
]

S["completed_recently"] = [
    {"what": "Link-page edits (follower count, bio text) done in 2.5h", "who": "Mayson", "date": "2026-10-12",
     "evidence": "'The link is fixed Shayna !!' / client: 'Yes it’s great thank you'"},
    {"what": "Pre-invoice OF-withdrawal reminder (a day early)", "who": "Stephski", "date": "2026-10-13"},
    {"what": "Oct 1-14 invoice issued as announced", "who": "Stephski", "date": "2026-10-15"},
    {"what": "Client-specific reel inspo (6 links incl. Halloween)", "who": "Mica Vecco", "date": "2026-10-14"},
    {"what": "Replacement link (xli.ink) within 9.5h of traffic complaint", "who": "Mayson / Vivek", "date": "2026-10-15"},
    {"what": "Login alert confirmed within 1 min; logins kept to DMs", "who": "Mayson", "date": "2026-10-14"},
]

ph = S["payment_history"]
for e in ph:
    if e.get("invoice_period") == "Aug 15-31":
        e["days_late"] = 38
        e["note"] = "Never chased/acknowledged; four invoices issued since (incl. Oct 1-14)"
    if e.get("invoice_period") == "Sept 1-14":
        e["note"] = "Reminder sent 9/14; paid in 4h36m; 5th account-detail change (name change); receipt unconfirmed 31d at 10/16"
    if e.get("invoice_period") == "Aug 1-14":
        e["note"] = "4th account change; receipt never confirmed (51d at 10/16)"
    if e.get("invoice_period") == "Sept 15-30":
        e["late"] = True
        e["days_late"] = 8
        e["status"] = "UNCONFIRMED 8d past due at 10/16: no 'sent', no chase, no receipt; not mentioned in 10/13 reminder or 10/15 invoice"
    if e.get("invoice_period") == "Oct 1-14":
        e.update({"reminder": "2026-10-13", "sent": "2026-10-15", "due": "2026-10-22", "date": None, "late": None,
                  "receipt_confirmed": False, "status": "issued 10/15 13:45 after 10/13 reminder; unpaid within terms at 10/16"})
ph.append({"invoice_period": "Oct 15-31", "sent": None, "due": None, "date": None, "late": None, "receipt_confirmed": False,
           "status": "expected ~11/1 with reminder ~10/30"})

for f in S["fan_money_exposure"]:
    if f.get("fan", "").startswith("Jason"):
        f["days_held"] = 101; f["status"] = "Fan withdrew 9/9; no refund/credit discussed; 5 windows unmentioned"
    elif f.get("fan", "").startswith("Manuel"):
        f["days_held"] = 147; f["status"] = "Undelivered; fan asking for videos instead; 5 windows unmentioned"
    elif f.get("fan", "").startswith("Unnamed"):
        f["days_held"] = 87; f["status"] = "Surfaced 9/25; Tuesday 9/29 proposed; Fred silent since 9/26 on it (20d), never scheduled"
    elif f.get("fan", "").startswith("Neon"):
        f["days_held"] = 37
    elif f.get("fan", "").startswith("VIP full"):
        f["days_held"] = 66
    elif f.get("fan", "").startswith("u561673786"):
        f["status"] = "Sale never confirmed in chat (20d); not on Notion"

S["payment_risk"] = {
    "level": "medium-high",
    "summary": "Unchanged. Sept 15-30 is 8d past due with no payment message and no chase. Aug 15-31 is 38d past due and unreconciled. Receipts are unconfirmed for the last two known payments. Stephski's 10/13 reminder and 10/15 Oct 1-14 invoice were on time but did not mention the open balances, so up to three invoices may now be stacked. Held fan money: $2,100 known plus the unquantified VIP group, plus the unconfirmed $600 custom. Per ALTR's churn pattern, a sudden fast, clean payment of Oct 1-14 with no asks would be a churn tell, not a recovery.",
    "next_invoice_due": "Oct 1-14 due ~2026-10-22; Oct 15-31 invoice ~11/1 (reminder ~10/30)",
    "watch": [
        "Any reconciliation of Aug 15-31 and Sept 15-30 (paid X / outstanding Y)",
        "Oct 1-14 turnaround by ~10/22",
        "Written receipts for 8/26 and 9/15",
        "Any 6th account-detail change",
        "Chargebacks on Jason/Manuel/VIP payers",
    ],
}

S["churn_watch"] = {
    "level": "moderate",
    "summary": "Held at moderate. PRESENT: a long-promised deliverable with no written proof. The second IG is still disputed and unproven 13d after 'We did', ALTR asked for reels again on 10/12 and she ignored it (the second ignored reel ask), and the phone farm promised 8/1 is 76d old. IMPROVED: asks recovered from 0 substantive (10/9) to 5 (10/16), and she was engaged and polite. BUT every ask was reactive to ALTR's link change. She did not chase the leaks, the live, the call or the IG. Her one results-type complaint ('I’m not getting traffic because of it') came after an ALTR promise that was reversed 4 days later. NOT PRESENT: owner silent 30+ days (Derrek's last message was 9/30 'Yep', 16d; it is his only message since 8/1, so it will cross 30d around 10/30 if he stays silent); a results question answered with a call offer (traffic complaint answered in writing the same day); billing-heavy ALTR messaging (3/18). No asks for exports or data, and no mention of other agencies.",
    "signals": {
        "owner_silent_30d": False,
        "owner_days_silent_at_close": 16,
        "results_question_answered_with_call": False,
        "promised_deliverable_no_written_proof": True,
        "majority_billing_messages": False,
        "fast_clean_payment": False,
        "zero_client_asks": False,
        "ignored_alt_requests": "Mica reel asks 10/3 and 10/12 unanswered; Stephski 10/13 reminder and 10/15 invoice not acknowledged yet",
    },
}

S["client_priorities"] = W["client_priorities"]

S["health_history"].append({"week_ending": "2026-10-16", "score": 42, "trend": "up"})
S["week_stats_history"].append({"week_ending": "2026-10-16", "messages": 37, "client_messages": 19, "team_messages": 18, "client_asks": 5,
                                "note": "Mayson 12, Stephski 3, Mica 2, Vivek 1; Fred/Melissa/Derrek 0"})
S["asks_history"].append({"week_ending": "2026-10-16", "client_asks": 5, "substantive": 5,
                          "note": "follower-count fix, bio text change, link flagging assurance (10/12 + 10/16), login-alert check, link status/traffic. All link/access, all reactive to ALTR's 10/11 link message; no older items chased"})

S["predictions_scorecard"] = {
    "set_on": "2026-10-09",
    "results": [
        "(a) Stephski confirmed Sept 15-30 / reconciled Aug 15-31? NO. Reminder sent? YES (10/13, early).",
        "(b) Second IG shown in writing? NO. Reels requested again 10/12; client ignored.",
        "(c) Fred scheduled the 7/21 live / confirmed the $600 custom? NO. Fred posted 0 messages.",
        "(d) Substantive asks recovered above zero? YES, 5, but all about the link change ALTR started.",
        "(e) New leaks actioned / reports ~10/9 and ~10/16? NO. 10/9 report missed; 10/16 not in by close; new leaks 16d.",
        "(f) Call held with a fixed time? NO.",
    ],
    "new_predictions_for_2026-10-23": [
        "(a) Is the xli.ink link live and getting traffic, and does she complain again?",
        "(b) Does Fred post at all? 7/21 live, $600 custom, relay confirmations?",
        "(c) Melissa report back (10/16 late or ~10/23)? New leaks actioned?",
        "(d) Oct 1-14 paid by ~10/22, and how fast? Any reconciliation of Sept 15-30 / Aug 15-31?",
        "(e) Second-IG proof given? Does she upload reels or keep ignoring?",
        "(f) Derrek posts before the 30-day mark (~10/30)?",
    ],
}

S["notes"] = "Window 2026-10-09T09:05:57 to 2026-10-16T09:06:40. Health 42, up 2. Link-in-bio week: edits done fast, the 'completely safe' domain was pulled 4 days later after she lost traffic, and a replacement xli.ink link was delivered. Fred absent all window. Leak report missed 10/9. Senders: Mayson Chat=Mayson, Stephski, Mica Vecco, Vivek (Meta Support Rep, @fonta, added by Derrek 7/29). Fred (Fredo), Melissa (Melissa Userfacing) and Derrek were silent. Jeremy Tarr and Spencer P did not appear. No unknown senders. Message id 1029 is missing from the export (likely deleted)."
S["credentials_flag"] = "No plaintext credentials posted 10/9-10/16. Mayson moved logins to DMs ('Please check dms about pw', 'Our dms so we can get your logins!'), and the client confirmed a 10/14 login alert was ALTR. Historic, still in chat: Facebook password posted by the client 6/2 (msg 348) and Link.me username/password posted by Mica 5/6 (msg 243). Both should be rotated. Values are not stored here."

json.dump(S, open(P, "w"), indent=2, ensure_ascii=False)
print("state written")
