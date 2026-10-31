#!/usr/bin/env python3
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date

OUT = "/Users/locklyjailbreak/conductor/workspaces/lead-check-up/dakar/ALTR_Case_Board.xlsx"
ASOF = date(2026, 9, 18)

HDR_FILL = PatternFill('solid', start_color='1F2937')
HDR_FONT = Font(name='Arial', bold=True, color='FFFFFF', size=10)
BASE = Font(name='Arial', size=10)
P0F = PatternFill('solid', start_color='FDE2E2')
P1F = PatternFill('solid', start_color='FFF3D6')
P2F = PatternFill('solid', start_color='E8F1FB')
thin = Border(bottom=Side(style='hair', color='DDDDDD'))

wb = Workbook()

def sheet_with(ws, title, headers, rows, widths, prio_col=None, date_cols=(), money_cols=()):
    ws.title = title
    ws['A1'] = title.replace('_', ' ')
    ws['A1'].font = Font(name='Arial', bold=True, size=13)
    ws['B1'] = 'As of:'
    ws['B1'].font = BASE
    ws['C1'] = ASOF
    ws['C1'].number_format = 'yyyy-mm-dd'
    ws['C1'].font = Font(name='Arial', size=10, color='0000FF')
    hr = 3
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=hr, column=c, value=h)
        cell.fill = HDR_FILL; cell.font = HDR_FONT
        cell.alignment = Alignment(wrap_text=True, vertical='center')
    for r, row in enumerate(rows, hr + 1):
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = BASE
            cell.border = thin
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            if c in money_cols and isinstance(v, (int, float)):
                cell.number_format = '$#,##0;($#,##0);"-"'
                cell.font = Font(name='Arial', size=10, color='0000FF')
            if c in date_cols:
                cell.number_format = 'yyyy-mm-dd'
        if prio_col:
            p = str(row[prio_col - 1])
            fill = P0F if p.startswith('P0') else P1F if p.startswith('P1') else P2F if p.startswith('P2') else None
            if fill:
                for c in range(1, len(headers) + 1):
                    ws.cell(row=r, column=c).fill = fill
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = f'A{hr+1}'
    return hr + len(rows)

# ---------------- TAB 1: PRIORITY BOARD ----------------
# cols: Priority, Bucket, Client/Party, Where, Case, $ At stake, Status, Waiting since, Days waiting (formula), Last msg, Next action
pb = [
 ("P0","REFUND","Adam (reseller)","iMessage 'Adam'","Failed legacy verification; he refunded HIS client out of pocket 9/14 and is still owed his deposit (~half of $8,500). Last reply sent 9/14 was a bank-excuse screenshot, not money.",4250,"Refund owed",date(2026,9,4),None,date(2026,9,17),"Send refund; then revive his $100k Fanduel/X pipeline"),
 ("P0","START WORK","Zoe Rhode @zoerhodeasmr","WA group","Paid $2,500 + $2,500 (9/15) for 3 YouTube unbans. Receipt never confirmed to her ('it says you should have received that. Let me know 🙏').",5000,"Paid, not started",date(2026,9,15),None,date(2026,9,17),"Confirm both $2.5k landed; start 3 YT cases"),
 ("P0","START WORK","Justin Woll's YT client (peptide/Bedros)","WA 'Justin Woll'","Client wired payment 8/18 ('you are good to move on'). Still not done 9/1+. Bedros promised 'all of his big clients' if this lands.",7500,"Paid, stalled 30d",date(2026,8,18),None,date(2026,9,10),"Do the recovery; reply to Justin (silent since 8/27)"),
 ("P0","PAY VENDOR","Ollie / Kelliher Media (chat teams)","iMessage 'Ollie Chat'","$7,216 + $836.74 missing from Aug 3–16 invoice (screenshot-verified). 'Wire heading out' photo 9/15 was just a bank-teller pic — no receipt. New invoice (Aug 31–Sep 13) also due.",8053,"Owed, wire unconfirmed",date(2026,8,19),None,date(2026,9,17),"Send wire + confirmation; answer 'How much has been sent so far?'"),
 ("P0","ANGRY CLIENT","Essence","iMessage 'Essence Client'","9/14: 'every time we speak you promised me a bunch of things that never go through… I've just been waiting and waiting.' Also her own invoice may still be unpaid (confusion where to send, 8/24).",None,"Client meltdown",date(2026,8,24),None,date(2026,9,17),"Call today; fix promises list; sort her invoice"),
 ("P0","FINAL PAY","Michelle (Suto)","iMessage 'Michelle Queue'","Laid off 9/14. Claims paid $3,000/mo for 3 months vs agreed $3,500 → ~$1,500 short + final check. Unanswered.",1500,"Final-pay dispute",date(2026,9,14),None,date(2026,9,14),"Reconcile and pay final check"),
 ("P0","REFUND","Ethaniel Lebaron","WA group","Paid $1,500 deposit; asked for refund 8/31, chased 9/3, 9/8, 9/12 — nothing sent.",1500,"Refund owed",date(2026,8,31),None,date(2026,9,12),"Refund or deliver within 48h"),
 ("P0","REFUND","Carla Aish (Sarah H referral)","WA 'Carla Aish'","Deposit refund promised 8/9 if she didn't proceed; her account got recovered elsewhere. 8/27: 'could you send me the $1000?' — unanswered.",1000,"Refund owed",date(2026,8,27),None,date(2026,8,27),"Send $1,000"),
 ("P0","ANGRY CLIENT","Anllela (Sagra)","iMessage 'Anllela Client'","Paid $2,500 Snapchat verification never delivered — refund promised 5/4, she asked to credit invoice 6/15; NO evidence it was ever credited. FB broken ~3 months ('no one is working on my fb' 9/8). Last msg 9/11 unanswered.",2500,"Refund/credit + stalled work",date(2026,5,4),None,date(2026,9,11),"Credit $2.5k on next invoice; assign FB fix; answer her"),
 ("P0","ANGRY CLIENT","Mikayla @kkvsh","iMessage 'Kkvsh unban'","8M-class model; main case blocked ('someone paid a supervisor', price 2x'd). Chasing 'what's going on' 8/12→9/11 with no plan given.",None,"Stalled, angry",date(2026,8,12),None,date(2026,9,11),"Give honest plan/price or refund path"),
 ("P1","CHECK IN","Sarah H","WA 'Sarah H'","Snapchat verification pending ~6 MONTHS (promised 'done this week' on 5/22). 9/15: 'do you think my snapchat will ever actually be verified hahaha'. Also verify her $3.5k recovery was ever invoiced + August invoice went out late.",3500,"Longest-waiting promise",date(2026,3,29),None,date(2026,9,17),"Honest snap answer; audit her invoices"),
 ("P1","COLLECT","Kells / Kelsey","iMessage 'Holly Unban' grp","Account recovered 6/18 on $3,500 job; paid only $500 + $1,300 partial ('Crazy u only paid us half' 7/1). Balance ~$1,700–3,000.",1700,"Delivered, part-paid",date(2026,6,18),None,date(2026,7,19),"Invoice balance"),
 ("P1","QUOTE + PLAN","Holly (+1 352-710-7247)","iMessage 'Holly Unban' grp","Quoted $3,500; asked for payment plan 6/22 ('1k down, rest in a month') — NEVER ANSWERED. Waiting 88+ days total.",3500,"Needs payment-plan answer",date(2026,6,22),None,date(2026,7,8),"Answer payment plan; start case"),
 ("P1","REFUND?","Brendan / OFFMENU","iMessage 'OFFMENU CLAIM'","Paid $6,000 for @offmenu claim 6/8; never delivered; refund paid only partially by 7/14 ('hit daily limit'); chased balance 7/15–7/19 then silence.",3000,"Refund balance unverified",date(2026,7,14),None,date(2026,7,29),"Verify what was returned; pay remainder; re-engage when claims work"),
 ("P1","CHECK IN","Owen & Cole","iMessage group","$9,220 payout discussed 8/5–8/7; never confirmed received before group went quiet 8/8.",9220,"Payout unconfirmed",date(2026,8,5),None,date(2026,8,8),"Confirm wire landed / Zelle it"),
 ("P1","PAY PARTNER","Noah (BKAO LLC)","iMessage 'Noah x ALTR'","Aug balance $24,996 sent 8/7 OK; SEPTEMBER wire still pending (wire info re-sent 9/3; 'This is retatded wtf' 9/8; 9/14 'Wire ?').",None,"Wire pending",date(2026,9,3),None,date(2026,9,14),"Send September wire"),
 ("P1","START/REDO","Rosie Clarke","WA groups","Paid $2,500 via TransferWise 7/16; recovered account went straight back down 8/7; second account down 8/8. Silent since 8/20.",2500,"Paid, broken again",date(2026,7,16),None,date(2026,8,20),"Redo or refund"),
 ("P1","START WORK","Hunter Neely","iMessage + groups","Paid ~$2,000 Venmo 8/4; flags/trial reels still broken; chased 9/2, 9/7, 9/12–15.",2000,"Paid, partial delivery",date(2026,8,4),None,date(2026,9,15),"Finish flag/reach fixes"),
 ("P1","START WORK","Elliott Dermond (@freakfactorycoaching)","iMessage groups","Paid $6,000 crypto 7/21 for 2 accounts; new Sept case group active; 9/11 'just checking in' unanswered.",6000,"Verify delivery",date(2026,7,21),None,date(2026,9,16),"Confirm both accounts done; update him"),
 ("P1","START WORK","@tristanmedia.aus","WA group","Paid ~$4,200 for perm unban ('Yup ive paid derrick' 8/10); chased 8/15, 8/22, 9/6 with no updates.",4200,"Paid, stalled",date(2026,8,10),None,date(2026,9,7),"Deliver or refund"),
 ("P1","START WORK","Starchive client (+1 858-201-9609)","iMessage 14857","Paid 9/15 ('Sent $10 test… sent the rest') — confirm receipt, start case.",None,"Paid, confirm",date(2026,9,15),None,date(2026,9,17),"Confirm crypto; start"),
 ("P1","CHECK IN","Cam Concierge client","WA group","Paid for IG protection 8/8; repeated 'Any update' through 9/18; $800 deletion + $800 website agreed.",1600,"Paid, slow",date(2026,8,8),None,date(2026,9,18),"Status update + deliver"),
 ("P1","REFUND/REDO","MainmanfreakyT","WA","Paid ~$2,600 unban; account broke again 2.5 weeks later; 9/7 'can you fix this please' — pending 11d.",None,"Redo request",date(2026,9,7),None,date(2026,9,17),"Redo under warranty"),
 ("P1","REFUND","Zac New","iMessage 'Zac New'","$10k legacy verification (paid 3/19) failed; refund done in pieces; final Zelle portion (6/3) never confirmed. He threatened suit in May; now friendly — close it out cleanly.",None,"Verify refund completed",date(2026,5,16),None,date(2026,9,11),"Verify final refund piece landed"),
 ("P1","COLLECT","Corey Chute","AR/AP + Execs","'$11k owed — any progress?' (8/17). Invoicing for her was broken in May. No resolution visible.",11000,"Receivable",date(2026,8,17),None,date(2026,8,17),"Chase; use Owen client contact"),
 ("P1","COLLECT","Chey Mai","ALTR group (Stephski)","'Not paying her last 2 invoices till you hit her' (8/31).",None,"2 invoices held",date(2026,8,31),None,date(2026,8,31),"Derek personal call"),
 ("P1","COLLECT","Beiberr channel","iMessage 'Beiberr'","Beiberr owes $4,000 (Lambo fiasco, admitted 8/11+8/18); YT-unban client owes $8,000 balance after 15k deal delivered 8/20; verify Beiberr's 8/11 $3,000 wire landed.",12000,"Delivered, unpaid",date(2026,8,11),None,date(2026,9,13),"Collect via Beiberr; write off Lambo cash-in-mail"),
 ("P1","INVESTOR","Alex Baleno","iMessage 'Alex Baleno'","Investment ROI ~1 year late ('racking up interest' 7/14); crypto payment attempts stalled 8/4 ('Still nothing'). Last msg 9/15 unanswered.",None,"Investor unpaid",date(2026,7,14),None,date(2026,9,15),"Reconcile; schedule payout"),
 ("P1","INVESTOR","Des","iMessage 'Des'","Owed ~$18,150 from January payout (3/20); drip-paid since; balance never reconciled. 9/16: 'Wait wtf is going on'.",None,"Investor unreconciled",date(2026,3,20),None,date(2026,9,16),"Reconcile balance; payment schedule"),
 ("P1","ANGRY CLIENT","LA Client","iMessage 'LA Client'","Page not recommended for 5–6 weeks; 'Still NOTHING!' 8/24 + 9/14. Paying client ($7,222 invoice paid 8/10).",None,"Stalled fix",date(2026,8,13),None,date(2026,9,14),"Get Fonta/Mayson update today"),
 ("P1","ANGRY CLIENT","Alex Paige","WA chats","Account issue since July ('Hello?' x3); 'should be fixed by monday' 9/12; still open.",None,"Stalled",date(2026,7,3),None,date(2026,9,18),"Deliver fix"),
 ("P1","LEGAL RISK","Ayman @egyptianmade","WA group","8/27 blowup: partner's '$6,000' message read as extortion; client's lawyer has it in writing + recorded call; threatening charges. Derek claims $2k+ loss on case.",None,"Legal threat",date(2026,8,27),None,date(2026,8,27),"De-escalate carefully; document; no further payment demands"),
 ("P1","REFUND","Jon Gilman's artist","iMessage 'Jon Gilman'","Botched trending campaign; 'You need to refund her today. No excuses' (7/2). Thread ends 7/15 mid-refund-logistics.",None,"Verify refund sent",date(2026,7,2),None,date(2026,7,15),"Verify/pay; repair referral relationship"),
 ("P1","REFUND","Jerry M","iMessage 'Jerry M'","Trending refund: 'only owe us 3k, already refunded 1' (7/15) — claimed sent same day; never confirmed.",3000,"Verify refund",date(2026,7,15),None,date(2026,8,25),"Verify; then revive his X-unban mega-deal"),
 ("P1","REFUND","Chico Sway ('mexi')","iMessage 'Chico Sway'","$1,500 refund requested 6/2 and 6/19; no evidence sent; dormant 70d.",1500,"Refund owed",date(2026,6,2),None,date(2026,7,10),"Refund or deliver"),
 ("P1","REFUND","realkeylamarie","Kartik ledger + group","$4,000 refund for re-disabled unban; half ($2,000) paid 9/3 — other half status unknown.",2000,"Half refund open",date(2026,9,3),None,date(2026,9,3),"Confirm/pay remaining $2,000"),
 ("P1","REFUND","Jabran Khan (via Justin Woll)","WA groups","Paid Jan (via Beiberr $2.5k); demanding full refund since April; 'It's August'. Money held by Beiberr.",2500,"Refund demanded",date(2026,4,15),None,date(2026,9,4),"Force Beiberr to return or make good"),
 ("P2","CHECK IN","Trevor Morgan","iMessage 'Trevor Morgan'","Reseller: Bonnie Locket TikTok retry quote never given (7/30); his own socialdepot pages stuck ~2 months; music-promo cost never provided; FB unban status unclear.",None,"Multiple open quotes",date(2026,7,30),None,date(2026,9,16),"Send 3 quotes + page status"),
 ("P2","CHECK IN","Eric Payed (reseller)","iMessage 'Eric Unban client'","'How much integrity?' 8/7 — UNANSWERED 42 DAYS. Historic ~$500k/yr channel.",None,"Ignored reseller",date(2026,8,7),None,date(2026,9,17),"Send price list; revive"),
 ("P2","CHECK IN","Dani Banks (8M)","iMessage 'Dani Banks'","YouTube unban: $2,000 deposit agreed 8/26–27 via Venmo — verify received & case started. Trust eroding ('everything is promised never actually done' 9/9).",2000,"Deposit unverified",date(2026,8,27),None,date(2026,9,16),"Confirm deposit; start YT case"),
 ("P2","CHECK IN","Jaylietori","WA group","Paid for recovery; refused vendor refund — wants account; dormant 68d.",None,"Paid, limbo",date(2026,7,12),None,date(2026,7,12),"Deliver or force refund"),
 ("P2","CHECK IN","Emma IG unban","WA group","~$4,000 held since June for fraud-ban recovery; chose to wait instead of refund; dormant since 7/29.",4000,"Paid, limbo",date(2026,6,23),None,date(2026,7,29),"Deliver or refund"),
 ("P2","CHECK IN","Fit Donk","iMessage 'Fit Donk'","Paid $1,200 recovery; begged not to be refunded (5/18); NOTHING since 5/28 — 113 days.",1200,"Paid, abandoned",date(2026,4,23),None,date(2026,5,28),"Deliver or refund — longest forgotten case"),
 ("P2","CHECK IN","Lola Client","iMessage 'Lola'","Unban case from March; chased ~2 months ('I really need this handled asap'); silent since 5/18.",None,"Abandoned case",date(2026,3,18),None,date(2026,5,18),"Close out honestly"),
 ("P2","CHECK IN","Claudia Snap Client","iMessage 'Claudia'","Paid $2,000 (Zelle 6/6) for Snapstar; one check-in 6/16 then nothing — 94 days. Third pending Snapchat-verification case.",2000,"Paid, dormant",date(2026,6,6),None,date(2026,6,16),"Deliver or refund"),
 ("P2","CHECK IN","Kay (protection)","iMessage groups","Paid 8/4; copyright restores pending; chased through 9/7; Derek silent 18–33d.",None,"Paid, slow",date(2026,8,4),None,date(2026,9,7),"Finish restores"),
 ("P2","CHECK IN","Mikayla Gambles","WA group","Meta-verified/reach work; chased 8/25→9/12 ('Wtf is going on'); 9/16 'I sent it straight to derrek' — VERIFY that payment.",None,"Payment untracked",date(2026,8,25),None,date(2026,9,18),"Find payment; deliver"),
 ("P2","CHECK IN","IG-takeover client (wh#1405)","WA","Paid Zelle ~8/1 ($1,500–2,500 tier); Derek 8/3: 'when did you pay? which day?' — payment never located; case limbo 45d.",2000,"Payment untracked",date(2026,8,2),None,date(2026,8,4),"Find Zelle in statements; deliver"),
 ("P2","COLLECT","Grant Lockly channel","iMessage","'Ive still not been paid on the accounts we did a long time ago' (8/27); 9/7 his clients' paid unbans also waiting.",None,"Receivable + delivery",date(2026,8,27),None,date(2026,9,17),"Reconcile; deliver batch"),
 ("P2","COLLECT","Ronyrocket (via Lilia)","iMessage 'Lilia'","Ghosted after Derek prepaid $3,000+ for her unban (7/25).",3000,"Delivered, unpaid",date(2026,7,25),None,date(2026,9,7),"Collect or write off"),
 ("P2","COLLECT","David reseller batch","iMessage 'David'/portal","Sept pay-after batch: thesamplebeast $700–1,000 owed, ojrose_ $2,700, MrAndyHoops $700, Cole.mp4x $500, samobadtv $500, c4shdevi etc. 9/10: 'Any update on these payments'.",6000,"Pay-after receivables",date(2026,9,10),None,date(2026,9,17),"Invoice completed cases; chase"),
 ("P2","COLLECT","@whoisgeminibabyy","WA group","Recovered 8/13 on $3,200 half/half deal — collection state unclear; unanswered since 9/14.",3200,"Verify collected",date(2026,8,13),None,date(2026,9,14),"Verify payment; collect"),
 ("P2","COLLECT","Damien clients","iMessage","'Will have u paid today, confirm that was 1200' (8/17) — verify $1,200 arrived.",1200,"Verify",date(2026,8,17),None,date(2026,8,18),"Verify"),
 ("P2","COLLECT","Kaitlyn (departing model)","ALTR ops chats","Final invoices (~$16,970 lifetime figure, 8/28) — 9/8 'make sure she pays her final invoices'. Also owe Koda 2.5% referral $424 + $1,212.79.",None,"Final invoice",date(2026,9,8),None,date(2026,9,8),"Invoice + net Koda referral"),
 ("P2","PAY","Koda referrals","AR/AP chat","Owed referrals: $1,505 (May) + $1,283.90 (Jamie June) + $1,212.79 (Kaitlyn 9/11 request, unanswered).",4002,"Payable aging",date(2026,6,23),None,date(2026,9,11),"Pay Koda"),
 ("P2","PAY","Boring Social","WA group","Remainder $639.17 (7/20) + later invoices chased 8/11–9/7; they offered card link.",639,"Vendor payable",date(2026,7,20),None,date(2026,9,11),"Pay by card link"),
 ("P2","PAY","Remove.tech / RemoveLabs","WA billing groups","~5 × $149 subscription invoices open (card broken since June); active DMCA work ongoing (Sarah H leaks 9/13).",745,"Vendor payable",date(2026,7,22),None,date(2026,9,16),"Update card; clear invoices"),
 ("P2","PAY","Zeus Photographer","iMessage/Zeus Media","$500 ACH never received (5/23) + 'Invoice is still unpaid' 8/17 pattern.",500,"Vendor payable",date(2026,5,23),None,date(2026,9,16),"Confirm ACH; pay invoices on shoot"),
 ("P2","PAY","Stephski (staff)","iMessage 'Stephski'","Her own payroll $1,000 short last month (9/1) — unanswered.",1000,"Payroll short",date(2026,9,1),None,date(2026,9,18),"True-up payroll"),
 ("P2","PAY","Nick Granberry","iMessage 'Nick'","$1,500 'can we get it sent back' (7/3, 7/10) — unresolved.",1500,"Owed to partner",date(2026,7,3),None,date(2026,9,17),"Send it"),
 ("P2","QUOTE","Quote backlog (biggest first)","Various","Bijan: 10 accounts >4M followers (6/19, dropped). Walker: @rthms claim 'ready to go' + $10k 3-letter claim (9/6–15). Steffan: $5k 5-letter handle — 'should we say yes' 9/4 UNANSWERED. Djwrecky CSE quote (9/17). Lana Smalls $3.5k (refund landing). Krissy Taylor $2,700 re-offer. Nick 2mrw cost Q (8/21). Sharna $2,500 counter (9/3). Vivek's own asks: zoerhode YT (answered late), TikTok verification pricing (8/4), Mc_Phils X unban.",None,"Money on table",date(2026,9,4),None,date(2026,9,17),"One quote-clearing session"),
 ("P2","INTEL","Misdirected client money","Alex Camus/AR-AP/24273","Amber wired $4k + Haleigh Cox wired to OLD BofA (9/10); '$4,500 sitting' waiting a month; Zelle proofs that never hit (8/11); $4.5–6.7k stuck in PayPal (9/16 email deleted). Reconcile old accounts vs invoices.",None,"Trapped cash",date(2026,8,11),None,date(2026,9,17),"Bank sweep of old accounts + PayPal"),
]
ws = wb.active
headers = ["Priority","Bucket","Client / Party","Where","Case detail (dated evidence)","$ at stake","Status","Waiting since","Days waiting","Last activity","Next action"]
last = sheet_with(ws, "Priority Board", headers, [list(r) for r in pb], [7,13,22,18,60,11,16,12,9,12,34], prio_col=1, date_cols=(8,10), money_cols=(6,))
for r in range(4, last + 1):
    if ws.cell(row=r, column=8).value:
        ws.cell(row=r, column=9).value = f"=$C$1-H{r}"
        ws.cell(row=r, column=9).number_format = '0'
        ws.cell(row=r, column=9).font = BASE

# ---------------- TAB 2: MONEY OWED TO ALTR ----------------
recv = [
 ("Corey Chute","AR/AP 8/17 'any progress on corey chute 11k owed'",11000,"Aging since ≤Aug","Chase"),
 ("Elizabeth","Stephski 5/13: 'Elizabeth owes $9,800' (chargebacks); paying gradually in USDT",9800,"Payment plan","Track next commission"),
 ("Anllela","Stephski 5/13: 'Anllela owes $9,300 hasn't responded'; later invoices flowing — net vs $2.5k snap credit",9300,"Partially settled?","Audit her invoice history"),
 ("Beiberr YT-unban client","15k YouTube unban delivered 8/20; 'idk if that nigga's good for the other 8k'",8000,"Delivered, unpaid","Collect via Beiberr"),
 ("Warner Bros / Columbia","'$5,800 waiting' (8/12, 8/25); earlier '$5,000 from warner bros — did you ever get paid?' (7/20)",5800,"Unverified receipt","Check bank for wire"),
 ("Beiberr personally","'I owe you four bands for Lambo' (8/18) + verify his 8/11 $3,000 wire landed",4000,"Admitted debt","Collect"),
 ("Unnamed model ('her')","Noah onboarding 6/22: '$14K bill pending from her'; 8/19 'she owes my rep $1300'",14000,"Identify + collect","Identify client; invoice"),
 ("Kells/Kelsey","$3,500 job, ~$1,800 received ($500 credit + $1,300)",1700,"Delivered, part-paid","Invoice"),
 ("Ronyrocket (Lilia's girl)","Prepaid unban $3,000+, client ghosted (7/25)",3000,"Ghosted","Collect or write off"),
 ("David reseller Sept batch","thesamplebeast $700 'Owed', ojrose_ $2,700, MrAndyHoops $700, Cole.mp4x $500, samobadtv $500 + more pay-afters",5100,"As cases complete","Invoice on completion"),
 ("Vivek channel receivable","9/16 'We fixed his clients. He hasn't paid' (Z-side)",None,"Identify amount","Reconcile with Vivek"),
 ("@whoisgeminibabyy","$3,200 recovery delivered 8/13 — collection unclear",3200,"Verify","Verify/collect"),
 ("Grant Lockly channel","'still not been paid on the accounts we did a long time ago' (8/27)",None,"Unquantified","Reconcile"),
 ("Markuss","Scott owed $515 + page balance $1,265 (4/17); '$540 owed' (5/22)",1780,"Stale","Nudge or write off"),
 ("Kaitlyn","Final invoices on departure (9/8)",None,"Invoice now","Stephski to send"),
 ("Gwen","Chronic late payer; paused 8/15; partial $2k sent 8/16 — check remainder + Sept cycle",None,"Verify balance","Stephski follow-up"),
 ("Hailey","Says she paid Aug invoice 8/21; Derek couldn't see it — locate or re-invoice",None,"Payment untracked","Find payment"),
 ("Damien","$1,200 promised 8/17 'today'",1200,"Verify","Verify"),
 ("IG-takeover client","Zelle paid ~8/1 but never located — deliver after finding payment",2000,"Untracked","Bank sweep"),
]
ws2 = wb.create_sheet()
last2 = sheet_with(ws2, "Owed To ALTR", ["Who","Evidence","Amount ($)","Status","Action"], [list(r) for r in recv], [24,60,12,18,26], money_cols=(3,))
tot = ws2.cell(row=last2 + 2, column=2, value="TOTAL identified (excl. unquantified)")
tot.font = Font(name='Arial', bold=True)
c = ws2.cell(row=last2 + 2, column=3, value=f"=SUM(C4:C{last2})")
c.number_format = '$#,##0'; c.font = Font(name='Arial', bold=True)

# ---------------- TAB 3: REFUNDS & PAYABLES ----------------
pay = [
 ("REFUND","Adam (reseller)","Failed legacy verification; deposit ~half of $8,500; he already refunded his client (9/14)",4250,"OWED — highest urgency"),
 ("REFUND","Ethaniel Lebaron","$1,500 deposit; refund chased 4x since 8/31",1500,"OWED"),
 ("REFUND","Carla Aish","$1,000 deposit; promised back 8/9; asked 8/27",1000,"OWED"),
 ("REFUND","Chico Sway","$1,500 'mexi' unban; asked 6/2 & 6/19",1500,"OWED (verify)"),
 ("REFUND","realkeylamarie","$4,000 total; $2,000 paid 9/3","2000","Remaining half"),
 ("REFUND","Brendan / OFFMENU","$6,000 paid; partial refund 7/14; balance chased 7/15–19",3000,"Verify remainder"),
 ("REFUND","Zac New","$10k legacy: refund pieces sent May–June; final Zelle unconfirmed",None,"Verify closed"),
 ("REFUND","Jon Gilman's artist","Campaign refund demanded 7/2; logistics unresolved 7/15",None,"Verify sent"),
 ("REFUND","Jerry M","$3,000 trending refund 'sent' 7/15 — unconfirmed",3000,"Verify"),
 ("REFUND","Jabran Khan","Paid Jan via Beiberr ($2.5k); demanding since April",2500,"Held by Beiberr"),
 ("REFUND","Jordy/Akeyla","$4,500 double-unban dispute; refund requested 8/8; + 8/16 'satisfy the Zelle today' unanswered",None,"Negotiate partial"),
 ("REFUND","LILLIENUE client","7/29: 'you still owe us for accounts never created/never posted'",None,"Quantify & settle"),
 ("REFUND-RISK","Merewena","$3,200 job waiting since 8/25; refund offered 9/12",3200,"Deliver fast"),
 ("REFUND-RISK","IG Unbans Appealed (juli07)","$8k 2-account deal w/ 1-month guarantee; one re-disabled 7/13",None,"Honor guarantee"),
 ("VENDOR","Ollie / Kelliher Media","$8,052.74 shortfall + new biweekly invoice",8053,"Wire + confirm"),
 ("VENDOR","Boring Social","$639.17 remainder + later chases",639,"Pay via card link"),
 ("VENDOR","Remove.tech/RemoveLabs","~5 × $149 open; card broken",745,"Fix card"),
 ("VENDOR","Zeus Photographer","$500 lost ACH + open shoot invoices",500,"Confirm & pay"),
 ("STAFF","Michelle (Suto)","Final pay + $500×3 shortfall claim",1500,"Settle at offboarding"),
 ("STAFF","Stephski","$1,000 payroll short (9/1)",1000,"True-up"),
 ("PARTNER","Noah (BKAO)","September wire pending since 9/3",None,"Send wire"),
 ("PARTNER","Nick Granberry","$1,500 return asked 7/3 & 7/10",1500,"Send"),
 ("PARTNER","Kartik","$7,500 re-sent 9/16 after 10k wire failed — confirm received; disputed ~10k claim vs $12k refunds + $2.5k referrals he owes",None,"Confirm wire; settle-up doc"),
 ("REFERRAL","Koda","$1,505 + $1,283.90 + $1,212.79 referrals",4002,"Pay"),
 ("INVESTOR","Alex Baleno","ROI ~1 year late",None,"Schedule"),
 ("INVESTOR","Des","~$18,150 base owed since Jan (partially drip-paid)",None,"Reconcile"),
]
ws3 = wb.create_sheet()
rows3 = []
for r in pay:
    amt = r[3]
    if isinstance(amt, str): amt = int(amt)
    rows3.append([r[0], r[1], r[2], amt, r[4]])
last3 = sheet_with(ws3, "Refunds & Payables", ["Type","Who","Detail","Amount ($)","Status/Action"], rows3, [12,26,58,12,24], money_cols=(4,))
t = ws3.cell(row=last3 + 2, column=3, value="TOTAL identified (excl. unquantified)"); t.font = Font(name='Arial', bold=True)
c = ws3.cell(row=last3 + 2, column=4, value=f"=SUM(D4:D{last3})"); c.number_format = '$#,##0'; c.font = Font(name='Arial', bold=True)

# ---------------- TAB 4: VERIFIED DEPOSITS ----------------
dep = [
 (date(2026,6,8),"Michelle Suto","Zelle","BUS COMPLETE CHK …1915",2000,"Text receipt in Alex Camus chat (6/10)"),
 (date(2026,8,17),"Daniel Potts","Zelle",None,190,"Chase alert 24273"),
 (date(2026,8,17),"Maverick & Co LLC","Zelle",None,3500,"Chase alert 24273"),
 (date(2026,8,17),"Damien Torrez","Zelle",None,1200,"Chase alert 24273 — matches Damien's $1,200 case"),
 (date(2026,8,17),"Daniel Potts","Zelle",None,810,"Chase alert 24273"),
 (date(2026,8,17),"Abdul G Karim","Zelle",None,1000,"Chase alert 24273"),
 (date(2026,8,17),"Gem Mint Cardhouse LLC","Zelle",None,350,"Chase alert 24273"),
 (date(2026,8,18),"Nazarena Blanco","Zelle",None,713.17,"Chase alert 24273"),
 (date(2026,8,20),"Chase Irons Fitness LLC","Zelle",None,3500,"Chase alert 24273 — @chaseirons case"),
 (date(2026,8,20),"Renato R Dias","Zelle",None,1000,"Chase alert 24273"),
 (date(2026,9,5),"→ Kevin Gaje (outbound)","PayPal",None,-437,"'You've sent ₱24,652.41 PHP' (AR/AP)"),
 (date(2026,8,7),"→ Noah / BKAO (outbound)","Wire",None,-24996,"'Balance sent 24,996' (Alex Camus, Noah chat)"),
 (date(2026,9,15),"Zoe Rhode","Bank transfer","arrives ~Sat",2500,"Her msg 9/15 — UNCONFIRMED on our side"),
 (date(2026,9,15),"Zoe Rhode → Derrek","Bank transfer",None,2500,"Her msg 9/15 'says you should have received' — UNCONFIRMED"),
 (date(2026,7,16),"Rosie Clarke","TransferWise",None,2500,"Her msg 7/16 — verify landed"),
 (date(2026,8,13),"Beiberr (partial)","Wire",None,2000,"BofA wire 8/13 in Beiberr chat — verify"),
 (date(2026,8,11),"Beiberr","Wire",None,3000,"'Wire sent $3000' screenshot (missing from disk) — verify"),
]
ws4 = wb.create_sheet()
last4 = sheet_with(ws4, "Deposits Log", ["Date","Counterparty","Method","Account ref","Amount ($)","Source / verification"], [list(r) for r in dep], [12,26,12,18,12,52], date_cols=(1,), money_cols=(5,))
n = ws4.cell(row=last4 + 2, column=6, value="Note: pre-Aug WhatsApp media and most pre-Aug iMessage attachments are purged from disk, so older 'payment screenshots' can no longer be re-opened — bank statements are the ground truth for those.")
n.font = Font(name='Arial', italic=True, size=9)

# ---------------- TAB 5: TIMELINE ----------------
tl = [
 (date(2026,3,19),"Zac New pays $10,000 for legacy verification (never delivered → refund saga May–June)"),
 (date(2026,3,20),"Des owed $18,150 from January payout — start of drip repayments"),
 (date(2026,4,20),"Des confrontation: 'money you're collecting now should be money for the things owed'"),
 (date(2026,4,26),"petervincer3 Coachella scam: Derek + friends out $25,000"),
 (date(2026,5,4),"Anllela: Snapchat verification failed — 'I'll refund' (never credited)"),
 (date(2026,5,13),"Stephski ledger: Elizabeth owes $9,800; Anllela owes $9,300"),
 (date(2026,5,22),"Stephski: 'Rn were 24k owed' across client invoices"),
 (date(2026,5,28),"Zac refund partially wired; wire bounces 5/29; Zelle promised 6/3"),
 (date(2026,6,6),"Claudia pays $2,000 for Snapstar (still undelivered)"),
 (date(2026,6,8),"Brendan pays $6,000 for @offmenu claim (never delivered)"),
 (date(2026,6,18),"Kelsey's account recovered — only $500 of $3,500 collected"),
 (date(2026,6,22),"Holly asks for payment plan on $3,500 — never answered"),
 (date(2026,6,24),"Mercury bank shutdown fallout — Ollie chatters nearly quit over $1,500"),
 (date(2026,7,3),"Yuni dips — 'paid out yuni and got fucked 6k'"),
 (date(2026,7,8),"OFFMENU refund promised; partial 7/14; balance chased through 7/19"),
 (date(2026,7,15),"Aundy Crenshaw refund $3,500 instructed — verify sent"),
 (date(2026,7,16),"Rosie pays $2,500 TransferWise"),
 (date(2026,7,20),"Kartik fake-Revolut scam on KeekGrace ($4,500) — 'I'm out $4500'"),
 (date(2026,7,21),"Elliott Dermond pays $6,000 crypto"),
 (date(2026,7,26),"Unban wave re-bans overnight — '(clients) haven't paid me because the account was down by the time they woke up'"),
 (date(2026,7,29),"Kartik reconciliation: Derrek owes $29,373.50; split $44,166.50 each. Public split announced to all case groups"),
 (date(2026,8,4),"Adam pays legacy-verification deposit (~$4,250)"),
 (date(2026,8,7),"Alex sends Noah $24,996 balance"),
 (date(2026,8,11),"Zelle misdirect discovered: client payments not hitting any known account"),
 (date(2026,8,17),"Corey Chute $11k flagged again; no progress"),
 (date(2026,8,18),"Justin Woll's client wires YT-recovery payment — still undone"),
 (date(2026,8,19),"Ollie invoice wire bounces — start of $8,052.74 shortfall"),
 (date(2026,8,20),"Beiberr channel YT unban delivered — $8,000 balance never collected"),
 (date(2026,8,27),"Ayman legal-threat blowup ('extortion', lawyer involved)"),
 (date(2026,8,31),"Ethaniel requests refund on his $1,500 deposit"),
 (date(2026,9,4),"Daniel: '2 people wanted refunds today' — backlog crisis visible"),
 (date(2026,9,9),"Dillon summary: Fanbasis held over $500; $3,500 refund forced over $1,300; employees quitting; farm paused"),
 (date(2026,9,12),"JMB VA agency finally paid; 'we removed Alex from the company'"),
 (date(2026,9,14),"Michelle laid off — final-pay dispute opens. Adam refunds his own client; Derrek's refund still unpaid"),
 (date(2026,9,15),"Zoe pays $5,000 (2×$2,500) for 3 YouTube unbans — unconfirmed, unstarted"),
 (date(2026,9,16),"Partner meltdown: Alex Camus removed; hidden invoices; $6,700 stuck in PayPal; account email deleted"),
 (date(2026,9,17),"Ollie submits new invoice + still waiting on $7,216; Kartik $7,500 wire resent — unconfirmed"),
]
ws5 = wb.create_sheet()
sheet_with(ws5, "Timeline", ["Date","Money event"], [list(r) for r in tl], [12,95], date_cols=(1,))

wb.save(OUT)
print("saved", OUT)
