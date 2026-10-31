"""One-off builder for lilia-x-altr week 2026-10-09 findings + state.

Every evidence quote is looked up in data/chats/lilia-x-altr.jsonl and must
occur verbatim in a real message, or the script aborts.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MSGS = [json.loads(l) for l in open(ROOT / "data/chats/lilia-x-altr.jsonl")]
SENDER_MAP = {"Fredo": "Fredo (Fred, OFM)", "Michelle Queue": "Michelle Queue (Michelle)",
              "Melissa Userfacing": "Melissa Userfacing (Melissa)", "Mayson Chat": "Mayson Chat (Mayson)"}


def q(sub, date=None, sender=None):
    for m in MSGS:
        t = m.get("text") or ""
        if sub in t and (date is None or m["ts"].startswith(date)) and (sender is None or m.get("sender") == sender):
            return {"quote": sub, "date": m["ts"][:10], "sender": SENDER_MAP.get(m["sender"], m["sender"])}
    raise SystemExit(f"QUOTE NOT FOUND: {sub!r} {date}")


week = {
    "client": "Lilia",
    "slug": "lilia-x-altr",
    "week_ending": "2026-10-09",
    "summary": (
        "Two-week window (Sep 25 to Oct 9), because the Oct 2 run never published. 63 messages: 33 client, 30 team. "
        "The client is warm, busy and selling. ALTR is mostly showing up for billing. "
        "REVENUE SHE BROUGHT US: on Oct 1 she bought ten Halloween costumes for sexting sets and said Teddi 'said he will buy all of them' at 'Usually he pays 1,000 per set!'. That is about $10k of pre-sold demand. "
        "On Oct 3 she uploaded a new set. On Oct 4 she set a goal of '10 sexting sets to this month'. "
        "Fred, who runs the OnlyFans side, posted 2 messages in 14 days, both on Oct 4: 'Amazing thank you!' and 'New stuff looks great so we'll get a push on it'. Nobody has acknowledged the Halloween plan, flagged Teddi or agreed a price. She is also selling to Teddi herself ('teddi asked for one of his favorite sets so I'll send it to him for 200'). "
        "STILL NOT FIXED: on Sep 23 she told us she deletes our chatters' old-content mis-sends from frumby's inbox and pays him back in free content. 16 days have now passed since Fred's 'We'll check' with no follow-up. The chatter Fred promised to remove on Jul 24 is still unnamed after 77 days. TikTok has gone 52 days without a check. The Aug 29 lost-spender complaint is 41 days unanswered. Her lost-login second IG account, raised Sep 25, has had no reply. "
        "MONEY: Stephski issued the Sept 15-30 invoice on cadence on Oct 1. The 'pausing in work' line is still in it, and the day-before reminder was skipped again. "
        "On Oct 4 the client had the money ready and asked 'Same Zelle right'. Nobody answered her until 29.6 hours later, after she sent '???' and Mayson and Melissa each pinged Stephski. "
        "She paid almost all of it on Oct 6, five days after issue, and said she owes $27 more because of a new limit. "
        "ALTR has still not stated a received amount in chat for any invoice. The Sep 18 payment is now 21 days unconfirmed and the Sep 3 invoice 36 days. The $192 gap is 45 days old. "
        "WHAT IMPROVED: the DMCA leak-removal breakdown came back on Oct 2, after 24 days and three missed windows, now sent by Melissa. Mica cleared up the Reels Drive and the new ALTR-made IG account, and sent reel inspo and a social tip. Mayson ran a check-up call on Oct 5 within minutes of the client saying yes, though nothing was written up afterwards. "
        "CHURN WATCH: several tells are now stacking up. She paid fast and with zero friction on her side, and even chased us to be allowed to pay. Her asks fell from about 8 in the week to Sep 25, to 3 in Sep 25 to Oct 2, to 1 in Oct 2 to Oct 9, and that one was a billing check. She has raised zero chatter complaints in 16 days, after telling us she now fixes the problems herself. Half of ALTR's messages in the Oct 2 to Oct 9 week were billing. Several long-promised deliverables still have no written proof. The owner has been silent for 23 days."
    ),
    "health": {
        "score": 48,
        "trend": "down",
        "rationale": (
            "48, down from 51 (last published, Sep 25) and 50 (the unpublished Oct 2 run). "
            "Up: the DMCA weekly breakdown resumed on Oct 2 after 24 days; she has never had to chase it, and it was the account's main source of goodwill. Mica carried social and cleared up the Drive and account confusion. The invoice was paid within terms. Mayson held a check-up call immediately. The client is upbeat and planning about $10k of Halloween content plus 10 sexting sets this month. "
            "Down: the core operator was close to absent, with Fred on 2 messages in 14 days and neither one addressing the Halloween plan, the Sep 23 frumby disclosure, the phone-number incident or any of the 10+ overdue OnlyFans items. "
            "Her pre-payment Zelle check went unanswered for 29.6 hours. That matters on an account where ALTR's receiving details have changed six times. "
            "Billing hygiene has not moved: no receipts in chat, the pausing line is still in, the reminder was skipped, and the $192 gap is 45 days old. "
            "Churn tells, scored as risk rather than health: (1) her asks are trending to zero, about 8 in the week to Sep 25, then 3, then 1, and the last one was billing. (2) Eager, fast payment: she chased ALTR so she could pay. (3) Zero chatter complaints for 16 days, from a client who told us on Sep 23 that she now fixes those failures silently, so silence here is not compliance. (4) In the Oct 2-9 week, 7 of 14 ALTR messages were billing. (5) Long-promised deliverables still have no written proof: the chatter removal, the purchase-history check, Teddi's CRM notes, TikTok and the written account map. (6) She keeps doing ALTR's job herself: selling to Teddi directly, uploading and foldering her own sets, policing frumby's inbox. "
            "Not yet present: the owner has been silent 23 days (crosses 30 on Oct 16). Results or revenue questions have not been deflected to a call, although the Oct 5 check-up call left no written recap. "
            "Her tone is warm, she has not mentioned leaving and she has never disputed an invoice. That keeps the score in the high 40s."
        ),
    },
    "reminders": [
        {
            "employee": "Fred",
            "topic": "Stop sending frumby content he already owns. That is 12 logged escalations since Jun 12, plus at least 3 incidents she disclosed on Sep 23 that she had absorbed herself. Fred's 'We'll check' was 16 days ago and nothing has followed. His only messages in this window were two generic replies on Oct 4. The chatter he promised to remove on Jul 24 is still unnamed after 77 days.",
            "count": 12, "age_days": 119, "first_raised": "2026-06-12",
            "evidence": [
                q("The chatters keep sending content he already has! It’s a second account!", "2026-07-24"),
                q("it's the same chatter who's letting the side down so I will take them off your", "2026-07-24"),
                q("Ur chatters have to stop doing this please", "2026-09-14"),
                q("they keep sending frumby stuff he already has so I deleted so he doesn’t get pissed", "2026-09-23"),
                q("We’ll check", "2026-09-23"),
            ],
        },
        {
            "employee": "Stephski",
            "topic": "Her pre-payment check on Oct 4 ('Same Zelle right') took three prompts and 29.6 hours to answer: her own '???', a Mayson tag and a Melissa relay. On this account, ALTR's receiving details have changed six times.",
            "count": 3, "age_days": 5, "first_raised": "2026-10-04",
            "evidence": [
                q("Heating the invoice now it hit my bank! Same Zelle right", "2026-10-04"),
                q("???", "2026-10-05"),
                q("@stephskiii", "2026-10-05", "Mayson Chat"),
                q("@stephskiii, Lilia wants to verify if it is the same # for zelle :)", "2026-10-05"),
                q("Yes same zelle! its on the bottom of the PDF", "2026-10-05"),
            ],
        },
        {
            "employee": "Stephski",
            "topic": "The client keeps the ledger, not ALTR. She has now reported her own running balance unprompted for the fifth time ('I just owe u 27'). ALTR has never stated a received amount in chat. The $192 gap (Aug 25) and the Sep 18 round-up are both still unreconciled.",
            "count": 5, "age_days": 53, "first_raised": "2026-08-17",
            "evidence": [
                q("1,192 is what I owe! I’m keeping track!", "2026-08-17"),
                q("192 (keeping track) it’s still giving me that limit…", "2026-08-25"),
                q("I just rounded it up", "2026-09-18"),
                q("I just owe u 27 I’ll get that in tomorrow", "2026-10-06"),
            ],
        },
        {
            "employee": "Vivek",
            "topic": "Check whether her TikTok is shadowbanned. She asked four times in August and has since gone quiet. It is now 52 days since she supplied the login, and Vivek's last message was 46 days ago.",
            "count": 4, "age_days": 52, "first_raised": "2026-08-18",
            "evidence": [
                q("Did u find out if I was shadowbanned?", "2026-08-19"),
                q("I’m definitely shadowbanned on TikTok so I can’t really post anything", "2026-08-22"),
                q("Did I end up being shadowbanned", "2026-08-23"),
            ],
        },
    ],
    "complaints": [
        {
            "issue": "Chatters sell frumby content he already owns, and she has stopped reporting it. She deletes the mis-sends and compensates him herself. Fred has posted nothing on it in the 16 days since 'We'll check'. Still missing: an incident count, a named chatter (promised Jul 24), a purchase-history check, and an answer on what 'Hayley content' is. Her zero complaints this window are not evidence that it is fixed.",
            "status": "recurring", "owner": "Fred", "age_days": 119,
            "first_raised": "2026-06-12", "last_raised": "2026-09-23", "escalation_count": 12,
            "evidence": [
                q("He got pissed twice about them sending Hayley content (old content) which he bought a long time ago… so I know what he has bought so I delete the old content and then I have to message him saying I’ll make up for it", "2026-09-23"),
                q("Amazing thanks for the information I’ll clarify with the team!", "2026-09-23"),
            ],
        },
        {
            "issue": "Her client-originated Halloween plan (10 sexting sets, Teddi pre-committed at ~$1,000/set) has had no specific acknowledgement from the OnlyFans side in 8 days. Fred's only reply was generic. Meanwhile she is selling to Teddi herself at $200.",
            "status": "new", "owner": "Fred", "age_days": 8,
            "first_raised": "2026-10-01", "last_raised": "2026-10-04",
            "evidence": [
                q("Just bought ten Halloween costumes for OF all of them will be sexting sets doing different things… easy money for the high spenders. Talked to teddie and he said he will buy all of them u send him. Usually he pays 1,000 per set!", "2026-10-01"),
                q("I’m waiting for the costumes to come in the mail! I’ll upload everything myself for u and put it all in a folder on OF to sell", "2026-10-01"),
                q("Also teddi asked for one of his favorite sets so I’ll send it to him for 200", "2026-10-03"),
                q("New stuff looks great so we’ll get a push on it", "2026-10-04"),
                q("I’m goal is to get 10 sexting sets to this month..: so we can make some moneyyyy!", "2026-10-04"),
            ],
        },
        {
            "issue": "Invoicing never confirms receipt or states an amount in chat. The Oct 6 payment was met with 'haha no worries at all', which is not a receipt. The Sep 18 payment (21 days) and the Sep 3 invoice (36 days) are still unconfirmed, the $192 gap is 45 days old, and the round-up has not been credited. The day-before OF-withdrawal reminder was skipped for the second cycle running, so the client had to wait on her bank ('just waiting for it to hit the bank').",
            "status": "recurring", "owner": "Stephski", "age_days": 45,
            "first_raised": "2026-08-25", "last_raised": "2026-10-06",
            "evidence": [
                q("Zelle worked in full this time yayyy", "2026-09-18"),
                q("Yesss just waiting for it to hit the bank and will pay! X", "2026-10-02"),
                q("I just owe u 27 I’ll get that in tomorrow", "2026-10-06"),
                q("haha no worries at all", "2026-10-06"),
            ],
        },
        {
            "issue": "The service-suspension line was kept word for word on the Oct 1 invoice. It was flagged for removal before Oct 1, and this client paid within terms again.",
            "status": "recurring", "owner": "Stephski", "age_days": 24,
            "first_raised": "2026-09-15", "last_raised": "2026-10-01",
            "evidence": [q("As always, we appreciate you paying within the next 7 days to avoid any pausing in work!", "2026-10-01")],
        },
        {
            "issue": "Her Oct 4 pre-payment check of the receiving details took 29.6 hours and three internal prompts to answer. The question exists because ALTR has changed its receiving details six times since June.",
            "status": "resolved", "owner": "Stephski", "age_days": 5,
            "first_raised": "2026-10-04", "last_raised": "2026-10-05",
            "evidence": [
                q("Before I send it!", "2026-10-04"),
                q("Just want to make sure no typo haha", "2026-10-04"),
                q("???", "2026-10-05"),
                q("cross reference there", "2026-10-05"),
            ],
        },
        {
            "issue": "Aug 29 lost high spender (~$300) because the chatters did not pass on a fan request. 41 days with no acknowledgement.",
            "status": "recurring", "owner": "Fred", "age_days": 72,
            "first_raised": "2026-07-29", "last_raised": "2026-08-29",
            "evidence": [
                q("Plead communicate this we lost out on 300", "2026-08-29"),
                q("I’ve lost my high spender because of communication and this", "2026-08-29"),
            ],
        },
        {
            "issue": "TikTok shadowban never checked, and the Aug 24 'Facebook' screenshots were never read. 52 days. Vivek last posted Aug 24.",
            "status": "recurring", "owner": "Vivek", "age_days": 52,
            "first_raised": "2026-08-18", "last_raised": "2026-08-24",
            "evidence": [
                q("@fonta always u can check of I’m shadowbanned on TikTok", "2026-08-18"),
                q("Let me know when u need it and try to log in and I can send u the code", "2026-08-24"),
                q("Facebook", "2026-08-24"),
            ],
        },
        {
            "issue": "IG account clarity. Mica cleared up the Reels Drive and the new ALTR-made account (progress). Her warmed-up second account, whose login she has lost, has had no reply in 14 days. No reels upload has been confirmed yet.",
            "status": "in_progress", "owner": "Mica Vecco / Mayson", "age_days": 119,
            "first_raised": "2026-06-12", "last_raised": "2026-09-29",
            "evidence": [
                q("No one has access to my second account right now as I don’t loose my username or password to it", "2026-09-25"),
                q("I think they said they wanted to run my second account, since it’s been warmed up! But literally don’t now my username or password…", "2026-09-25"),
                q("we made a new one for you! we need content for it (reels)", "2026-09-29"),
                q("This month has been the most hectic month! I will get on it! I promise!", "2026-09-29"),
            ],
        },
        {
            "issue": "Phone number exposed on her IG story (Sep 22). Her question 'I think I'm good?' is still unanswered and the spender who 'was throwing a fuss' is still unidentified. 17 days with no movement.",
            "status": "in_progress", "owner": "Fred", "age_days": 17,
            "first_raised": "2026-09-22", "last_raised": "2026-09-23",
            "evidence": [
                q("I hang got any weird messages so I think I’m good?", "2026-09-23"),
                q("I believe there was a specific spender who was throwing a fuss about a guy with you on there but the chatters played it off.", "2026-09-23"),
            ],
        },
        {
            "issue": "DMCA weekly leak-removal breakdown was missing from Sep 8 to Oct 2 (24 days, three windows). It RESUMED on Oct 2 from Melissa. Watch that it lands again around Oct 9.",
            "status": "resolved", "owner": "Melissa", "age_days": 31,
            "first_raised": "2026-09-08", "last_raised": "2026-10-02",
            "evidence": [
                q("Hey love! Here’s your weekly update on the leak removal breakdown for the past 7 days", "2026-09-08"),
                q("Here’s your weekly update on the leak removal breakdown for the past 7 days", "2026-10-02"),
            ],
        },
    ],
    "commitments": [
        {
            "what": "Acknowledge and plan the Halloween drop: confirm a per-set price (she cites ~$1,000), flag Teddi in the CRM as pre-committed, sequence the 10 sets and name who sells them",
            "who": "Fred", "status": "overdue", "due": "2026-10-03", "age_days": 8,
            "evidence": [
                q("Talked to teddie and he said he will buy all of them u send him. Usually he pays 1,000 per set!", "2026-10-01"),
                q("I’m still waiting on Halloween costumes", "2026-10-03"),
            ],
        },
        {
            "what": "Investigate the Sep 23 old-content disclosure: pull the frumby logs, count the mis-sends, quantify her compensation, name the chatter promised removal on Jul 24, install a purchase-history check",
            "who": "Fred", "status": "overdue", "due": "2026-07-24", "age_days": 77,
            "evidence": [
                q("it's the same chatter who's letting the side down so I will take them off your", "2026-07-24"),
                q("We’ll check", "2026-09-23"),
            ],
        },
        {
            "what": "Push the new set she uploaded Oct 3",
            "who": "Fred", "status": "pending", "due": "2026-10-09", "age_days": 5,
            "evidence": [
                q("Uploading a new set should be in by today or tomorrow I’m still waiting on Halloween costumes", "2026-10-03"),
                q("New stuff looks great so we’ll get a push on it", "2026-10-04"),
            ],
        },
        {
            "what": "Client: send the sexting sets offered Sep 18 ('easy 4,000'). At least one new set landed Oct 3. The rest are now folded into her 10-sets-this-month goal",
            "who": "Lilia (client)", "status": "done", "due": "2026-09-24", "age_days": 21,
            "evidence": [
                q("Sending two sexting sets tomorrow easy 4,000 from high spenders", "2026-09-18"),
                q("Uploading a new set should be in by today or tomorrow", "2026-10-03"),
            ],
        },
        {
            "what": "Confirm receipt in chat with amounts: the Oct 6 payment, the Sep 18 payment plus round-up, and the Sep 3 invoice; reconcile the $192 gap",
            "who": "Stephski", "status": "overdue", "due": "2026-09-19", "age_days": 36,
            "evidence": [
                q("I will get that paid! Thank you x", "2026-09-04"),
                q("I just rounded it up", "2026-09-18"),
                q("I just owe u 27 I’ll get that in tomorrow", "2026-10-06"),
            ],
        },
        {
            "what": "Remove the 'to avoid any pausing in work' line from her invoice template (missed on Oct 1; next chance Oct 15)",
            "who": "Stephski", "status": "overdue", "due": "2026-10-01", "age_days": 24,
            "evidence": [q("As always, we appreciate you paying within the next 7 days to avoid any pausing in work!", "2026-10-01")],
        },
        {
            "what": "Send the day-before OF-withdrawal reminder before the Oct 15 invoice (skipped Sep 30; she then had to wait for her bank)",
            "who": "Stephski", "status": "pending", "due": "2026-10-14", "age_days": 25,
            "evidence": [
                q("Hi love! Just letting you know your invoice will be sent tomorrow, so it would be great if you could initiate a OF withdrawl today", "2026-09-14"),
                q("Yesss just waiting for it to hit the bank and will pay! X", "2026-10-02"),
            ],
        },
        {
            "what": "Client: send the $27 remainder of the Sept 15-30 invoice",
            "who": "Lilia (client)", "status": "pending", "due": "2026-10-07", "age_days": 3,
            "evidence": [
                q("I just owe u 27 I’ll get that in tomorrow", "2026-10-06"),
                q("Didn’t know I had a limit of that now", "2026-10-06"),
            ],
        },
        {
            "what": "Report back on the Aug 29 lost high spender (~$300)",
            "who": "Fred", "status": "overdue", "due": "2026-08-29", "age_days": 41,
            "evidence": [q("Plead communicate this we lost out on 300", "2026-08-29")],
        },
        {
            "what": "Close out the exposed-phone-number incident (answer her, identify the spender, advise on rotating the number)",
            "who": "Fred", "status": "overdue", "due": "2026-09-24", "age_days": 17,
            "evidence": [q("I hang got any weird messages so I think I’m good?", "2026-09-23")],
        },
        {
            "what": "Check the TikTok shadowban and read the Aug 24 Facebook screenshots (reassign off Vivek)",
            "who": "Vivek", "status": "overdue", "due": "2026-08-18", "age_days": 52,
            "evidence": [q("Yes need a login code", "2026-08-24")],
        },
        {
            "what": "Tell her plainly whether ALTR still needs her warmed-up second IG account (login lost). If it does, help her recover it",
            "who": "Mayson", "status": "overdue", "due": "2026-09-11", "age_days": 29,
            "evidence": [
                q("I still need to get u the insta login… need to figure it out", "2026-09-16"),
                q("I think they said they wanted to run my second account, since it’s been warmed up!", "2026-09-25"),
            ],
        },
        {
            "what": "Post a written recap of the check-up calls: Sep 8 (trial reels, never recapped) and Oct 5 (also no recap)",
            "who": "Mayson", "status": "overdue", "due": "2026-10-06", "age_days": 31,
            "evidence": [
                q("Here it is!", "2026-09-08"),
                q("Hey @Liliaanglex let me know when you wanna hop on our check up call!", "2026-10-05"),
                q("https://meet.google.com/nuk-isrc-rnr", "2026-10-05"),
            ],
        },
        {
            "what": "Send one written map of every account and Drive ALTR runs for her and what feeds each. Partly done verbally by Mica on Sep 25 and Sep 29",
            "who": "Mica Vecco", "status": "pending", "due": "2026-10-09", "age_days": 29,
            "evidence": [q("this is your drive", "2026-09-25"), q("i believe one has already been made", "2026-09-25")],
        },
        {
            "what": "Client: upload reels to the Reels Drive for the new ALTR-made account. No upload confirmed yet",
            "who": "Lilia (client)", "status": "pending", "due": "2026-10-09", "age_days": 10,
            "evidence": [
                q("Yes sorry I’ve been moving non stop these past days! I need to go through my videos", "2026-09-29"),
                q("This month has been the most hectic month! I will get on it! I promise!", "2026-09-29"),
            ],
        },
        {
            "what": "Client: fill out the new private-platform intake form. Completion not confirmed in chat",
            "who": "Lilia (client)", "status": "pending", "due": "2026-10-09", "age_days": 11,
            "evidence": [q("Yessss I’ll add a bunch of stuff to it!", "2026-09-28")],
        },
        {
            "what": "Restore the weekly DMCA leak-removal breakdown in this chat",
            "who": "Melissa", "status": "done", "due": "2026-09-15", "age_days": 0,
            "evidence": [q("Here’s your weekly update on the leak removal breakdown for the past 7 days", "2026-10-02")],
        },
        {
            "what": "Issue the Sept 15-30 invoice on cadence",
            "who": "Stephski", "status": "done", "due": "2026-10-01", "age_days": 0,
            "evidence": [q("Good afternoon queen! Here is your invoice for September 15-30th", "2026-10-01")],
        },
        {
            "what": "Older idle OnlyFans items, all untouched again: Teddi CRM notes (Aug 30), $100/min shower custom (Aug 11), Adam West red set (Aug 19), Aug 26 share-for-share and set-repricing instructions, $750 whipped-cream decision (Aug 31), high-spender folders (Aug 10), written price floor in CRM (Aug 28)",
            "who": "Fred", "status": "overdue", "due": "2026-08-31", "age_days": 60,
            "evidence": [
                q("Absolutely we have a note system inside of the CRM we use", "2026-08-30"),
                q("Amazing - will inform team, thank you", "2026-08-11"),
                q("Adam west wanted the red set u Dan sell those for a lot he will pay", "2026-08-19"),
            ],
        },
        {
            "what": "Freeze the receiving details in writing (no seventh change)",
            "who": "Stephski", "status": "pending", "due": "2026-10-15", "age_days": 51,
            "evidence": [q("Wait a different Zelle again?", "2026-09-16"), q("Yes same zelle! its on the bottom of the PDF", "2026-10-05")],
        },
    ],
    "payments": [
        {
            "note": "Sept 15-30 invoice: issued on cadence on Oct 1 (amount only in the PDF; pausing line kept; no day-before reminder). Stephski nudged on Oct 2. The client's Zelle check waited 29.6 hours. She paid on Oct 6, five days after issue and inside the 7-day terms, short by $27 because of a new sending limit, which she promised for Oct 7. The $27 send is not confirmed in chat as of window close. ALTR gave no receipt or amount, only 'haha no worries at all'.",
            "amount": "not stated in chat (PDF only); paid except $27 per client",
            "date": "2026-10-06", "status": "paid except $27 / receipt not confirmed", "late": False,
            "evidence": [
                q("Hi @Liliaanglex just making sure you saw this", "2026-10-02"),
                q("Heating the invoice now it hit my bank! Same Zelle right", "2026-10-04"),
                q("I just owe u 27 I’ll get that in tomorrow", "2026-10-06"),
                q("haha no worries at all", "2026-10-06"),
            ],
        },
        {
            "note": "Earlier cycles still unconfirmed by ALTR: Sep 18 full payment plus voluntary round-up (21 days), Aug 15-31 invoice issued Sep 3 (36 days), and the $192 gap from Aug 25 (45 days). ALTR has never written a received amount in chat. The client is the only one keeping a ledger.",
            "amount": "unknown (PDF only); $192 disputed; round-up uncredited",
            "date": "2026-09-18", "status": "unconfirmed / unreconciled", "late": False,
            "evidence": [
                q("Zelle worked in full this time yayyy", "2026-09-18"),
                q("192 (keeping track) it’s still giving me that limit…", "2026-08-25"),
                q("Yes mam you’re totaled at $0 owed now", "2026-08-26"),
            ],
        },
        {
            "note": "Churn lens on payment: since mid-August she has paid in full, inside terms and without being chased, and this cycle she chased ALTR so she could pay. Per ALTR's churn pattern, fast, clean, eager payment combined with falling asks is a risk tell, not a health sign. Next: Oct 1-14 invoice around Oct 15. Watch for a day-before reminder on Oct 14, the pausing line removed, receipts in chat and no seventh detail change.",
            "amount": None, "date": "2026-10-15", "status": "upcoming", "late": False, "evidence": [],
        },
    ],
    "client_priorities": [
        "Monetising high spenders with themed content: 10 Halloween costume sexting sets pre-sold to Teddi (~$1,000/set), a goal of 10 sexting sets in October, one teaser per set on her wall",
        "Protecting frumby and Teddi. She polices frumby's inbox for old-content mis-sends herself and sells to Teddi directly when he asks",
        "Getting paid out cleanly: she verifies receiving details before sending ('Just want to make sure no typo') and tracks her own balance",
        "Clarity on IG accounts: she understands the new ALTR-made account; her warmed-up second account (login lost) is still unresolved",
        "Personality-driven social content. She took Mica's tip enthusiastically ('Get ready I will definitely do!')",
        "Price discipline: $200/video, $200/pic package, $100/min customs",
        "Getting through her house move. September was 'the most hectic month' and content is slower until she is settled",
        "TikTok unblocked, DMCA updates kept weekly, and a ledger that matches her own running total",
    ],
    "suggestions": [
        "Have Fred write one specific reply on the Halloween plan this week: price per set, Teddi flagged as pre-committed in the CRM, which chatter sells, and a launch date tied to costume arrival. Have him also ask whether she wants ALTR or herself to sell to Teddi, since she is already selling to him at $200.",
        "Close the frumby loop in writing. Give her the log count, the named chatter, the purchase-history check that now exists, and an offer to cover what she gave away. Assume her silence since Sep 23 means she is still cleaning up after us.",
        "Have Stephski send one message that confirms the Oct 6 payment amount and the $27, the Sep 18 payment and round-up, the Sep 3 invoice, and the $192. Before Oct 15, remove the pausing line, send the day-before reminder on Oct 14, and pin the Zelle details as frozen so she never has to ask 'Same Zelle right' again.",
        "Set a same-day SLA for billing questions on this account. A client holding money ready should never wait 29.6 hours.",
        "Have Mayson post a 3-line written recap of the Oct 5 check-up call (and the Sep 8 one): what was discussed, what she agreed, and what ALTR owes.",
        "Have Mica or Mayson tell her whether ALTR still needs her second IG account, then send the one-page account and Drive map.",
        "Reassign the TikTok shadowban check off Vivek (52 days).",
        "Ask her a direct, open question about results, e.g. 'How do you feel October is going on OF?', and answer in writing. Her asks have fallen to 1 a week; re-open the channel before silence hardens.",
    ],
    "wins": [
        "The DMCA weekly leak-removal breakdown came back on Oct 2 (Melissa), ending a 24-day gap",
        "The Sept 15-30 invoice was paid within terms (Oct 6), $27 short only because of a sending limit she flagged herself",
        "Mica: Drive and new-account clarity on Sep 25 and 29, weekly reel inspo, and an Oct 6 social tip that drew 'Love it! Thank you!'",
        "Mayson ran a check-up call on Oct 5 within minutes of her saying yes",
        "The client is producing: a new set uploaded Oct 3, 10 Halloween sets planned, and a goal of 10 sexting sets this month",
        "Melissa's intake form drew an immediate yes, and Melissa relayed the Zelle question to Stephski",
    ],
    "week_stats": {
        "messages": 63,
        "client_messages": 33,
        "team_messages": 30,
        "client_asks": 4,
    },
}

out = ROOT / "data/weeks/2026-10-09/lilia-x-altr.json"
out.write_text(json.dumps(week, ensure_ascii=False, indent=2) + "\n")
print("wrote", out)
