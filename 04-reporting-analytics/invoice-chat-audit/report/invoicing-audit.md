# ALTR Invoicing Audit — Telegram Group Chats

**Source:** 14 `<Model> x ALTR` Telegram group chats (Jul 2025 → Aug 8, 2026, ~9,500 messages).
**Scope:** every invoicing-related message anywhere in each chat, not just the Invoicing topic.
**Method:** automated parse/extract/cycle-reconstruction pipeline (see README) + full human-level read of every extracted transcript. All message IDs (`#N`) are traceable to the source chats.

---

## 1. Executive summary

**~130 invoice cycles** were issued across 13 active chats (Kaitlynn onboarded Aug 7, 2026 — no invoicing yet). The single most important finding:

> **Your clients pay. Your rails don't.**

Virtually every client in the book pays willingly within 0.5–5 days of receiving a *correct invoice with working payment details*. Almost all collection delay — conservatively **250+ cycle-days of avoidable lag across the year** — was caused on the agency side by three things:

1. **Payment-rail churn.** Clients were asked to change where/how they pay **at least 6 times in ~10 months**: Chase/"Social Depot LLC" (Sep 27 '25) → Revolut added (Oct 13 '25) → FanBasis card links (Nov '25) → card processor freezes *all* payments for two pay periods (Feb 14–Mar 5 '26) → unnamed new bank (Apr 15 '26) → aborted Stripe rollout (May 1 '26, retracted same day) → Mercury pay links (Jun 15 '26, **retracted Jun 22 because payments bounce**) → Bank of America "last change I promise!" (Jul 1 '26) → 5% CC surcharge (Jul 15 '26) → Commas checkout (Jul 31 '26). Every single major collection stall in the data maps onto one of these transitions.
2. **No receivables reconciliation.** Nobody watching the bank account is connected to the people chasing invoices. Staff chased invoices that were already paid (Vale, Liza ×2), declared a received wire "missing" for 12 days (Sarah, Oct '25), took 10 days + 3 internal escalations to locate two wires (Liza, Jul '26), and never noticed a client's bank fraud-flag silently cancel a payment (Mila, Aug '26). Clients run test payments ($10, $100) because they don't trust the details — and they've been right to.
3. **Off-book side payments to Derrek.** Payments went to Derrek personally — Apple Pay to a personal number (Lauryn, Feb '26), USDT to "Derek's wallet" (Liza ×3), "I sent to Derrek" (Vale) — with billing staff finding out only when the client told them. This desynchronizes the ledger and caused duplicate chases.

**Drop-off:** zero clients are demonstrated non-payers. At the data cutoff (Aug 7–8, 2026) **7 invoices were genuinely open**, clustered in the Jul 15–31 period, and most were blocked by the agency's own rails (broken BofA Zelle, failed Zelle email on a first invoice, an unanswered overpayment-credit request). The Lauryn chat literally ends with the client trying to pay and failing: *"That Zelle email isn't working"* (#1524, Aug 7) — unanswered.

**Time lost per cycle:** clean cycles collect in **1–5 days**. Friction cycles ran **7–24 days**, and the worst stretches (Feb '26 processor freeze, Jun–Jul '26 Mercury/BofA churn) pushed individual invoices to 15–24 days with balances rolling into the next period for the first time in the dataset.

**Employees:** one person — **Stephski** — issues ~95% of all invoices for 12+ clients, batch-style. Her punctuality is excellent (near-perfect 1st/15th issuance). Her failure modes are accuracy (wrong commission rate twice, missing contractual deductions, wrong revenue total, wrong wire address, wrong crypto network) and latency (payment links up to 12 days after clients asked to pay; receipt confirmations that never come). Details in §4.

---

## 2. Methodology & caveats

- **Payment evidence is a flag, not a verdict.** Wire/Zelle/crypto payments can complete with zero chat trace. Cycles labeled "silent/off-chat" mean *no visible signal*, not non-payment. Where later messages imply settlement (e.g. staff praising on-time payment), we say so.
- The automated cycle scaffold (`data/cycles/cycles.csv`) undercounts payments — clients confirm with screenshots and phrases like "Wire sent!!", "First half xx", "Complete ✅" that pattern-matching misses. **Every cycle table in §6 was corrected by a full read of the transcript.** Corrected numbers supersede the CSV.
- All bank account numbers, routing numbers, personal phone numbers, and non-agency emails are redacted from this report and from all extracts.

---

## 3. The systemic timeline (what happened agency-wide)

| Date | Event | Evidence across chats |
|---|---|---|
| Sep 27, 2025 | **Bank change #1** → JPMorgan Chase / "Social Depot LLC"; Zelle moves to trevor@altrmgmt.com | Lauryn #629, Sarah #586, Liza #204, Haileigh #179 |
| Oct 13, 2025 | Revolut @socialdepot added as method | Sarah #710, Lauryn #846, Liza #295 |
| Nov 6–17, 2025 | FanBasis card links become default rail; **billing handoff Lauren → Stephski** — never announced to clients; in two chats Stephski invoiced before introducing herself | Liza #417/#453, Lauryn #896 vs #899, Sarah #877 |
| Feb 14 – Mar 5, 2026 | **Card processor freezes all agency payments for two pay periods** → "only Wire, Zelle, or Apple Pay"; ad-hoc USDT accepted; Apple Pay routed to a personal phone number | Liza #765, Lauryn #1087/#1103/#1120, Haileigh #374 |
| Apr 15, 2026 | **Bank change #2** ("we recently changed banks") — payee later identified as "Altr platforms," acct …1915; one client wired to the *old* account and it was caught 5 days later | Sarah #1351, Lauryn #1255, Haileigh #547/#590, Vale #135, Liza #849 |
| May 1, 2026 | **Stripe rollout launched and retracted the same day** | Haileigh #570→#572 |
| Jun 15–22, 2026 | **Mercury pay-link system launched, then retracted — "your transaction will bounce."** A 7-day window existed where paying clients were paying into a dead end. Invoicing delayed agency-wide ("technical difficulties") | Lauryn #1440–1442, Sarah #1497/#1518, Liza #905, Vale #331, Shayna #427, Lilia #330/#370, Sarah Lloyd #316/#376, Amber #532 |
| Jun 17–29, 2026 | Staff exodus from group chats (Ana, Lance, Paulo, Gelle, Anne et al. removed) — concurrent with the worst collection period | Lauryn service msgs |
| Jul 1, 2026 | **Bank change #4 → Bank of America, "last change I promise!"** — shipped with a wrong wire address in one chat (fixed next day), Zelle not yet activated in another, and BofA Zelle receiving failure by Aug 7 | all chats; Haileigh #712, Lilia #501, Lauryn #1524 |
| Jul 15, 2026 | **5% credit-card surcharge** introduced — right as multiple clients were requesting split payments | Lauryn #1492, Liza #949, Sarah Lloyd/Amber templates |
| Jul 31, 2026 | Processor swap FanBasis → Commas | Lauryn #1513–1515 |
| Aug 1, 2026 | **First-ever payment due dates** ("within the next 7 days") appear in all invoice templates simultaneously; Derrek's agency-wide IG/"Phone Farm" broadcast ($40k, 200+ devices) | all chats, batch-sent 15:40–15:50 |

Until Aug 1, 2026, **invoices carried no due date at all** ("at your earliest convenience"). A dunning policy existed on paper since Oct '25 — reminder at day 2, chat pause at day 5 (Lauryn #786) — but was applied exactly once (the Nov 20 '25 pause-chatting warning, Lauryn #919, which skipped the day-2 reminder entirely).

---

## 4. Employee findings

**Stephski** — billing owner since Nov 13, 2025; issued ~105+ of ~130 cycles, alone, batch-style (invoices across 12 chats land within minutes of each other).
- ✅ Near-perfect calendar punctuality (16/16 on-time in Vale+Shayna; only slips: Amber Jun 20 +5d during Mercury chaos, Sarah Lloyd Jul 5 +4d, Sarah Aug 3 +2d, two +1d weekend slips). Persistent, polite follow-ups (16+ in Lauryn alone). Proactive OF-withdrawal reminders before every cycle. Accommodated every split-payment request.
- ❌ **Accuracy** — wrong commission rate billed twice (35% vs contracted 30%: Amber #259, Sarah Lloyd #628); contractual deductions omitted until clients caught them ($100/wk OFTV editor: Sarah Lloyd #559; agreed deductions: Sarah #1520); wrong revenue total (Amber #448, caught by Derrek); premature invoice rescinded by Derrek (Lilia #132–137); wrong wire address on the first BofA invoice (Haileigh #712); **wrong-network crypto address** that could have permanently lost funds — client caught it (Vicky #246–249); invoice re-issues in at least 6 chats. *The clients are functioning as invoice QA.*
- ❌ **Latency** — payment links delivered days after clients said "ready to pay": 12 days worst case (Lauryn #1497→#1513), 5 days (Lauryn #1450→#1464), ~20h repeatedly; referral-credit figures took 11 days with two client bumps (Sarah #1592→#1659); receipt confirmations frequently promised ("Checking! 🙏") and never delivered (Haileigh #600/#648/#716, Vicky #407, Mila #116/#130, Liza #918); client questions needing 2–6 days and internal @-pings to get answered (Liza Jul '26: 3 escalations).
- ❌ Professionalism in money comms: typos ("paymebnt", "Hope you're having a good weed", "had to dick a bit" — Mila #100), wrong client name on a corrected invoice ("Here you go Sofia" in Vale's chat #665).

**Lauren Biz Assistant** — billing owner Aug–Nov 2025.
- ✅ The best-run stretch in the dataset: pre-reminder before *every* cycle including holiday bank-closure advice, ~2-day payment lags, fast troubleshooting (17 min on a Zelle failure), asked for confirmations "for my records."
- ❌ **Dropped receipt collection when clients went quiet**: chased a ~$15k boyfriend-wire twice then let the thread die with no receipt ever produced (Liza #44–54, Aug '25); three consecutive Liza cycles with zero ack/receipt/chase. **The Oct '25 "lost wire"** (Sarah #726–782): collected the client's wire proof Oct 20, went silent 8 days, told the client "we have not received it" — then found it in 3 minutes once Derrek was asked. Departed with **no handoff announcement** in any chat.
- Era comparison (Lauryn chat): avg lag ~2.6 days under Lauren vs ~9.5 days after — though the drivers are the 2026 rail churn more than the person.

**Derrek (owner)** — the involuntary single point of truth.
- Only person who can see the bank account; receipt verification bottlenecks on "checking with Derrek." Accepts side payments (personal Apple Pay, USDT wallet, "sent to D") that billing staff learn about after chasing already-paid invoices. Terse partial answers that generate more client follow-ups (Sarah #1543 "the one ending in 1915"). Catches real errors (Amber #448, referral credit #644) but also left his own Aug 8 ping to Stephski unanswered at data end (Sarah Lloyd #642).

**Michelle Queue & Mica Vecco** — carry billing-adjacent titles but **do zero invoicing work in any chat**; both perform well in their real lanes (DMCA/promo, social). Role labels vs reality mismatch confused at least one client. Mica: quoted ad-hoc, shifting IG-unban fees rolled into invoices ($1,680 → $2,275 → $1,785 + $840, Sarah #822–941); also posted a login+password in plaintext in a group chat (Shayna #243).
**Noah Chat / Nate** — misdiagnosed a client's IRS levy as a chargeback (Haileigh #193–196); fatalistic on the $7.5k chargeback event ("email OF support").
**Alex Camus** — fastest responder measured (1–4 min, GBP conversion + full bank details, Mila #73–75) but his promise "we will make sure the exchange is on the next invoice" was broken the very next cycle (#76 vs #112).

---

## 5. The four questions, answered

### Where were the holes?
1. **No due dates until Aug 1, 2026** — 11 months of "at your earliest convenience."
2. **No receivables visibility** — chasing paid invoices, losing received wires, missing failed payments, manual amount-matching that breaks on transit fees (Mila took 6 days to locate a wire because "there was a fee deducted so the total didnt match").
3. **No receipt-confirmation loop** — clients beg "did you get it?" and get silence or "checking!"; they invented their own test-payment protocol ($10/$100 probes) in three chats.
4. **Contract terms not encoded in billing** — rates, deductions, referral credits, currency handled from memory; every new client's first cycles required corrections.
5. **Payment instructions not verified before sending** — broken Zelle email printed on a first invoice (Barbara), wrong wire address (Haileigh), wrong crypto network (Vicky), dead Mercury links (everyone), BofA Zelle not activated / later broken.
6. **Off-chat payments to the owner with no ledger sync.**
7. **Handoffs and onboarding** — Lauren→Stephski never announced; Lauren Blake got zero billing contact for 28 days until the invoice itself; Barbara was invoiced for ~11 days predating her chat with no earnings statement; Lilia was invoiced prematurely against negotiated start terms Derrek then had to rescind with a one-word "disregard."
8. **A missing billing period** — Liza May 1–14, 2026: no invoice, reminder, or payment trace at all.
9. **Client finance questions dropped** — Sarah's GST/per-country revenue question (Jan 2, #1045): never answered in 8 months. Lauren Blake's request to see the 5% Meta ad-spend reports: open at data end. Chargebacks not itemized on invoices (Sarah's May audit found systematic small over-billing vs dashboard net, explained only verbally).

### Where were the problems?
The incident list is dominated by the rail churn in §3. Chat-specific highlights: the Oct '25 lost-wire scare (Sarah); the Feb '26 processor freeze forcing Apple-Pay-to-a-personal-phone and USDT improvisation; the Mercury bounce window (Jun '26); the broken first-invoice Zelle + 47-hour silence (Barbara, Aug '26); three invoice-amount errors in one client's six cycles (Amber); the $7.5k OF chargeback with no meaningful response playbook (Haileigh); Zelle daily caps ($1k/day, $500/day new-recipient) turning single invoices into week-long installment plans with hand-tracked balances (Shayna, Lilia); third-party payer names breaking reconciliation (Liza: boyfriend, Leticia Linss, Jose Munoz, EDGARDO R CANALES).

### Were there specific employee problems?
Yes — see §4. Summary: **Stephski** = punctual but error-prone and slow to confirm/answer (and she is a single point of failure doing 12+ clients' billing alone); **Lauren** = strong process, weak follow-through on receipts, silent exit; **Derrek** = side-payment channel and verification bottleneck; **Michelle/Mica** = mislabeled as billing; **Noah/Nate** = weak on payment-adjacent incidents. No evidence anywhere of dishonesty or client-hostile conduct — tone across all staff is consistently warm.

### What was the overall drop-off and time lost?
- **True non-payment: none demonstrated.** Every client with history pays; several apologize for 2-day delays; one paid 3 minutes after issuance (Haileigh #546).
- **Open at data cutoff (Aug 7–8, 2026): ~7 invoices**, almost all Jul 15–31 cycle, mostly blocked by agency rails: Lauryn ×2 (broken BofA Zelle, unanswered — 23+ and 6+ days old), Barbara (failed Zelle email on first invoice, dangling 4+ days), Sarah Lloyd (awaiting corrected-rate payment + unanswered overpayment credit), Mila (fraud-flag redo never confirmed), Vicky (silent but within the new 7-day terms), Lilia (claimed "I'll get that paid" same day as cutoff).
- **Time lost:** clean cycles 1–5 days; friction cycles 7–24. Worst stretches: Lauryn Jun 1–14 '26 (~21–24 days, Mercury), Sarah Jul 1–14 '26 (12 days, 11 of them waiting on the agency's own referral-credit math), Liza Jul 1–14 '26 (~16 days, lost-wire reconciliation), Lilia's combined first invoice (~15 days, Mercury→Chase→Zelle-cap), Shayna Jun 15–30 '26 (12 days, Zelle cap + new-bank verification pause), Haileigh Jun 15–30 '26 (8 days, ~2 lost to the wrong wire address).
- **Aggregate:** roughly 250–300 avoidable cycle-days of delay across the year, ~80% attributable to agency-side causes (rail churn, invoice errors, link/confirmation latency), ~20% client-side (bank caps, travel, cash-flow — including the legitimate splits Lauryn requested citing "money is beyond low").
- **Trendline worth flagging:** Lauryn — the longest-tenured client — went from 1–2-day payments (fall '25) to split requests in 6 of the last 12 cycles, unpaid balance carried across periods for the first time (Aug 1), and a failed payment attempt as the chat's last billing event. That is a collections risk building in plain sight, and most of the friction pushing her there was self-inflicted rail churn plus the new 5% surcharge.

---

## 6. Per-chat detail

### Lauryn x ALTR (client "LA Client") — 23 cycles, Sep '25–Aug '26 · 2 open
The stress case. ~14 of 23 cycles had friction. Absorbed ≥6 method changes including Apple-Pay-to-owner during the Feb freeze. Client pays within minutes when a working link exists (#1199: 3 min) but staff link latency ran to 12 days. Only true escalation in the dataset: Nov 20 '25 pause-chatting warning (#919) — which skipped the promised day-2 reminder. 5% CC surcharge landed (Jul 15) exactly as she requested splits. Chat ends Aug 7 with a failed Zelle attempt, unanswered; two invoices open. Watch this account.

### Sarah x ALTR (client "Sarah H") — 21 cycles, Sep '25–Aug '26 · 0 open
Model payer; splits wires only because of a 50k AUD/day cap. All 16 auto-flagged "unpaid" cycles were regex misses. Friction: Oct '25 lost-wire scare (12 days, money was there all along); Jun '26 Mercury churn (15–17 days); Jul '26 referral-credit delay (12 days — client chased *them*). Open items of a different kind: GST question never answered; her May audit showing invoices systematically above dashboard net (post-period chargebacks never credited).

### Liza Kovalenko x ALTR (client "Eli") — 24 periods, Jul '25–Aug '26 · 1 period never invoiced
Most complex payer (Mexican banks, third-party senders, crypto). Holes: ~$15k paid with no receipt ever collected (Aug '25); three silent cycles under Lauren; May 1–14 '26 never invoiced; USDT side payments to Derrek causing duplicate chases; Jul '26 two-wire reconciliation took 10 days + 3 internal escalations. Only hard payment demand in 13 months: #937.

### Haileigh Cox x ALTR (client "Hailey Client") — 23 cycles, Aug '25–Aug '26 · 0 unpaid, 2 receipt-unconfirmed
Pays in ~2 days median with screenshots; zero real escalations. All friction agency-side after Apr '26: paid the old account post-bank-change, wrong BofA wire address (+2 days), Stripe same-day retraction, and three receipt questions answered with silence or a ❤️. Client-side event: IRS levy on OF withdrawals (Sep–Oct '25) handled gracefully — she offered to pay a late fee. Red flag on service generally: "every time i reach out it's either super delayed or just no response at all" (#415).

### Amber Haze x ALTR (client "Kirsten") — 6 cycles, May–Aug '26 · 0 open
Pays in 0.5–1.6 days once the invoice is *correct* — but 3 of 6 cycles had amount errors (35% vs 30% + unsettled $4.7k pre-existing balance; wrong revenue total Derrek caught; chargeback delta requiring live explanation). One invoice 5 days late and delivered as a photo. Payment acks took up to 10 days.

### Vale x ALTR — 9 cycles, Mar–Aug '26 · 0 open
Perfect issuance punctuality. Friction: Jul 3–6 rail failure (Zelle rejected, ACH failed, $1k/day cap, BofA initially failed — ~3 days); staff chased a payment 4 days after it was made (no receivables view); first-cycle payment went to Derrek personally; $5,720 referral credit ordered *after* issuance forced a reissue.

### Shayna x ALTR — 7 cycles, Apr–Aug '26 · 0 open
Fast, communicative payer who disputed one billing start-date (resolved same day with evidence — good save). Structural issue: chose Zelle to avoid wire fees → $1k/day cap → invoices paid in hand-tracked installments over 4–12 days; she had to ask staff to confirm receipt mid-stream during the bank switch before sending more.

### Lilia x ALTR — 5 cycles, Jun–Aug '26 · 1 open
Rockiest onboarding: premature invoice rescinded by Derrek ("disregard"); first real invoice = Mercury link that later bounced (7-day dead-end window); $500/day new-recipient Zelle cap → five tranches with one silent failure; ~15 days to substantially collect. Jul 15–31 cycle open at cutoff ("Whoops no I didn't! I'll get that paid 🩵").

### Sarah Lloyd x ALTR — 4 cycles, Jun–Aug '26 · 1 open + credit
**Zero clean first-pass cycles.** Broken wire details at onboarding (her $10 test was refunded); Jul 1 invoice simply never sent until she asked; $100/wk OFTV deduction omitted since signing; 35% vs 30% rate error; overpayment credit request unanswered 4+ days incl. an ignored Derrek ping.

### Vicky x ALTR (client "Valerie") — 3 cycles, Jun–Aug '26 · 1–2 open
Crypto payer. Wrong-network USDT address sent (client caught it — funds-loss near-miss); 2.6 days to confirm her test transaction; Jul 1–14 payment claimed with screenshot but never confirmed received.

### Mila x ALTR (client "Callie") — 3 cycles, Jun–Aug '26 · 1 open
GBP client whose currency needs were never systematized (promised "exchange on the next invoice," then not delivered); 12 days to confirmed receipt on cycle 1 (fee-deduction amount mismatch); her bank's fraud flag stopped a payment and **ALTR never noticed** — she self-reported and asked them to check for double payment; unconfirmed at cutoff.

### Barbara x ALTR — 1 cycle, Aug '26 · open
First invoice carried a broken Zelle email that Stephski confirmed as correct hours before it failed. Client attempted payment within ~2 hours of the invoice; error report → 7h first response → **47-hour silence** → workaround (Zelle request to client's own info) → no confirmation by data end. 100% of delay after the error report is agency-attributable.

### Lauren Blake x ALTR — 1 cycle, Aug '26 · paid, unacknowledged
Paid by wire in ~3 days with screenshot — which no staff member ever acknowledged. No billing contact existed for her entire first month until the invoice itself. Open: her request to see Meta ad-spend reports behind the 5% fee. Also raised: 13 of 24 whales ghosted (59% of revenue) and a $27k spender blocked by the chat team.

### Kaitlynn x ALTR — onboarded Aug 7, 2026
No invoicing activity yet; first invoice due on the Aug 15 cadence.

---

## 7. Recommendations

1. **Freeze the payment rails.** One bank, one processor, published on every invoice, tested with a real transaction before any client sees it. The "last change I promise" line has been sent to every client — credibility is spent.
2. **Build a receivables loop:** whoever can see the bank account posts received-payment confirmations within 24h, matched by invoice reference numbers (put a reference code on every invoice so transit-fee deltas and third-party sender names stop breaking matching).
3. **Ban side-channel payments** to personal Apple Pay/wallets — or at minimum require Derrek to post them to the billing thread same-day.
4. **Encode contract terms** (rate, deductions, referral credits, currency, chargeback credits) into invoice generation. Every one of the five newest clients caught an invoice error the agency should have caught.
5. **Keep the 7-day terms** (good Aug 1 change) and actually run the stated dunning ladder: day-2 reminder, day-5 escalation — automatically, every cycle, every client.
6. **Confirm receipts proactively** — "received, thank you" within one business day, always. Three chats invented test-payment protocols purely from lack of trust in confirmation.
7. **Fix the Zelle-cap workflow:** for clients on daily caps, offer a no-fee high-limit rail (wire fee credit, or split-invoice links generated *with* the invoice, not 5–12 days later on request).
8. **Staff the function.** One person batch-billing 12+ clients with no backup produced exactly the error/latency profile you'd predict. Add a second trained biller and a handoff checklist (announced handoffs, intro-before-invoice, client acknowledgment state carried over).
9. **Answer the open items now:** Lauryn's broken Zelle + two open invoices; Barbara's dangling first invoice; Sarah Lloyd's overpayment credit; Sarah's GST/per-country question and chargeback-credit methodology; Lauren Blake's ad-spend reports; Mila's double-payment check.
