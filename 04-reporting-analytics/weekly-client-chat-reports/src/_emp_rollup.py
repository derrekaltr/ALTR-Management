"""Build _employees.json for a week from the per-client findings files.

Normalises the free-text `owner`/`who`/`employee` strings the client analysts
produce ("Michelle Queue", "Ollie Mckinlay / Mayson (chat)", "Stephski (invoicing)")
onto canonical roster names, drops client-side owners, and applies the
never-in-the-Team-tab exclusion list.

Usage:
    python3 src/_emp_rollup.py 2026-09-11 [--dump]
"""
import glob
import json
import re
import sys

import yaml

WEEK = sys.argv[1]
DUMP = "--dump" in sys.argv

# Derrek's standing request (2026-08-08): these never appear in the Team tab.
EXCLUDED = {"Derrek", "Nick (DMCA)", "Noah"}

team_cfg = yaml.safe_load(open("config/team.yaml"))
clients_cfg = yaml.safe_load(open("config/clients.yaml"))

ROLE = {m["name"]: m.get("role", "Team") for m in team_cfg["team"]}
for v in team_cfg.get("vendors", []):
    ROLE[v["name"]] = "Vendor chat team"

CANON = set(ROLE)

# Client-side names that show up as "owners" of client deliverables.
CLIENT_NAMES = set()
for c in clients_cfg["clients"]:
    CLIENT_NAMES.add(c["name"])
    CLIENT_NAMES.update(c.get("client_aliases", []))

ALIAS = {
    "michelle queue": "Michelle",
    "michelle (promo team)": "Michelle",
    "mayson chat": "Mayson",
    "ronnie chat": "Ronnie",
    "noah chat": "Noah",
    "nate (noah)": "Noah",
    "eric the efficient": "Eric",
    "nick | dmca": "Nick (DMCA)",
    "lauren biz assistant": "Lauren (Biz Assistant)",
    "fred | ofm": "Fred",
    "fred spitfire": "Fred",
    "ollie": "Ollie Mckinlay",
    "mica": "Mica Vecco",
}


def canonicalise(raw):
    """One free-text owner string -> set of canonical roster names."""
    if not raw:
        return set()
    out = set()
    for part in re.split(r"[/,;&]| and | or ", str(raw)):
        p = part.strip()
        # "Eric (original); Mayson (current)" / "Joseph H (departed); chat team":
        # the historical owner is not accountable for the open item.
        if re.search(r"depart|original|former|previous", p, flags=re.I):
            continue
        # strip trailing qualifiers: "(invoicing)", "(current)", "(client)"
        p = re.sub(r"\(.*?\)", "", p).strip()
        p = re.sub(r"^(unassigned|originally|current)\b[:\-\s]*", "", p, flags=re.I).strip()
        p = p.strip(" .-")
        if not p:
            continue
        low = p.lower()
        if low in ALIAS:
            p = ALIAS[low]
        if p in CLIENT_NAMES or p in EXCLUDED:
            continue
        if p in CANON:
            out.add(p)
    return out


# Authored per-person read for this week. Counts come from the findings files;
# these are the judgement calls that sit on top of them.
NARRATIVE = {
    "Ollie Mckinlay": {
        "trend": "down",
        "summary": (
            "The single largest source of client damage this fortnight, and the gap widened "
            "(43 open issues on 08-28, 61 now). He owns six accounts and closed nothing on any "
            "of them — zero commitments kept against 35 overdue. He sent no messages at all in "
            "Alanna's chat for the full 14 days while the page management she pays for produced "
            "nothing, and his entire output on Vale was 14 words across four messages, each "
            "arriving only after Mayson @-tagged him. Three of the five clients ALTR lost or is "
            "losing this window (Vicky, Kaitlynn, Alanna at risk) are his."
        ),
        "strengths": [],
        "coaching_flags": [
            "Zero commitments closed across six accounts in fourteen days (0 kept / 35 overdue).",
            "Only responds after an internal @-tag — 5th time on Vale since Jul 28, also the pattern on Amber Haze.",
            "Answers substantive client questions with bare acknowledgements ('Thank you', 'Will look into this for you') and never posts the outcome.",
            "Holds the two largest fan-money liabilities on the book (Vale ~$5,300, Vicky $1,700) and has not actioned either.",
        ],
    },
    "Mayson": {
        "trend": "down",
        "summary": (
            "Carries the widest surface of anyone — 17 of 18 accounts — and is the only working "
            "routing mechanism in the agency: on Barbara, Liza and Vale nothing moves until he "
            "tags an owner. That is also the problem. Open issues nearly tripled (17 → 48) "
            "because he converts client questions into tags rather than answers, and because he "
            "opened a large number of new workstreams this window (a 7-reels-a-week quota across "
            "at least six clients, a Snapchat team, trial-reel calls) while closing one "
            "commitment. He proposed a Monday 09-07 trial-reels call to at least six clients and "
            "booked none of them."
        ),
        "strengths": [
            "The de facto escalation layer — repeatedly the only person who gets Vivek, Olivia or Stephski to respond to a client.",
            "Closed a 331-day-old Google Drive upload failure for Alex Paige Moore in 24 minutes on Sep 4, with an unprompted apology.",
        ],
        "coaching_flags": [
            "Proposed the same Monday 09-07 call to six-plus clients (Alanna, Alex Paige Moore, Liza, Mila, Sarah Lloyd, Vale) and booked zero.",
            "Imposed an identical 7-reels/week quota across the book without checking client circumstances — including on Alex Paige Moore four days after she disclosed surgery, and on Amber Haze, who had already refused it.",
            "Routes rather than owns: 5 escalation tags on Kaitlynn alone in one window, in place of answering her.",
            "Asked Sarah for her Snapchat handle on Sep 9 — she had supplied it unprompted on 2026-02-04.",
        ],
    },
    "Stephski": {
        "trend": "down",
        "summary": (
            "Touches every account (18 of 18) and is the only function still reliably reaching "
            "clients — which is exactly why the failures here are so costly. She is invoicing on "
            "cadence, but reconciliation has collapsed: payments from Vale (25 days), Mila, "
            "Haileigh, Alex Paige Moore and Lauryn sit unconfirmed, and on Liza she under-credited "
            "the client by $5,000 and only corrected it after Liza produced her own wire receipts. "
            "Chasing has also become the agency's default client contact — on Paige she sent a "
            "work-pause threat seven days after the client had resigned, and on Chey Mai the "
            "chasing simply stopped when the client was quietly offboarded mid-window."
        ),
        "strengths": [
            "Only person with contact on all 18 accounts; invoices went out on cadence across the book.",
            "Handled Amber Haze's UK bank block well when the client flagged it proactively.",
            "Turned around a payment link for Kaitlynn in 37 minutes once it was finally asked for.",
        ],
        "coaching_flags": [
            "Under-credited Liza Kovalenko by $5,000; the client had to disprove ALTR's own number with receipts (6th consecutive cycle she has had to audit us).",
            "Payments acknowledged with pleasantries ('Perf thank you love', 'Appreciate you!') instead of confirmed receipt — two consecutive unreconciled cycles on Vale, Mila and Haileigh against a bank account number that changed on Aug 15.",
            "'To avoid any pausing of work' language now being used on clients with perfect payment records (Haileigh 26/26 cycles) and on clients who have already quit (Paige).",
            "Stopped chasing Shayna and Alanna entirely once their invoices went past the 7-day term she herself set.",
        ],
    },
    "Vivek": {
        "trend": "flat",
        "summary": (
            "Flat at 36 open issues, but flat here means twelve accounts' worth of Meta problems "
            "sitting untouched. He went the entire fourteen days without a single message on "
            "Lauryn (through four direct chases and an internal tag), Liza (11 days after being "
            "handed credentials for three deleted accounts) and Paige. His lifetime output on "
            "Lilia is six messages. The pattern is consistent: he asks for a credential in the "
            "group chat, receives it, and then goes silent — which is both a service failure and "
            "the source of the plaintext-password problem now spanning at least six client chats."
        ),
        "strengths": [
            "Closed Amber Haze's Instagram restriction in ~27 hours on Sep 6-7, shutting a thread open since Jul 21 — she replied 'amazing thank you.'",
            "Responded fast on Sarah Lloyd's 08-28 account compromise once bumped, and correctly took it to DM.",
        ],
        "coaching_flags": [
            "Zero messages in 14 days on Lauryn, Liza Kovalenko and Paige despite direct client chases and internal tags.",
            "Collects logins and passwords in client group chats and does not report back — Liza (3 accounts, 11 days), Sarah (36 days), Haileigh (44 days), Barbara (18 days).",
            "Never engaged Barbara's own root-cause lead (the .vip domain restricting her main IG), the strongest diagnostic on that account, 18 days old.",
            "Asks for credentials without specifying which account ('send the password for suspended account' to a client with two down).",
        ],
    },
    "Fred": {
        "trend": "down",
        "summary": (
            "Only two accounts, but 32 reminders on them — the highest reminder density of anyone "
            "on the team. Lilia repeated the same three instructions (communicate before acting, "
            "hold the $200 price floor, sell only new content from the high-spender folder) six, "
            "six and four times respectively; the price-floor and new-content instructions are "
            "now on their tenth-plus repetition across the relationship. Her Aug 29 lost $300 "
            "spender went 13 days unanswered through three Mayson escalations. On Shayna he did "
            "the best operational work on that account all quarter and simultaneously let a 4th "
            "'stop selling private lives' instruction go past."
        ),
        "strengths": [
            "Shayna's Sep 9 fan-by-fan live availability sweep was the best operational output on that account this quarter, and it surfaced $1,600 of previously invisible fan-money exposure.",
            "Sought client approval and pricing before selling twice on Shayna (Sep 8 $500, Sep 10 $400).",
        ],
        "coaching_flags": [
            "Same instructions re-issued by clients 4-6 times per window; Lilia's price floor and new-content rules are on their 10th+ repetition.",
            "Client CRM notes failing within 48 hours — Lilia gave Fred a fan's car-crash backstory Sep 2, chatters were 'acting shocked' about it Sep 4.",
            "Lilia's Aug 29 lost high spender ('we lost out on 300') went 13 days and 3 escalations with no reply — the second identical loss in a month.",
            "Shayna has now said 'stop selling private 1:1 lives' four times (7/27, 8/3, 9/1, 9/9).",
        ],
    },
    "Michelle": {
        "trend": "flat",
        "summary": (
            "The most reliable delivery function in the agency and, at the same time, the person "
            "most often sent to chase content that should never have been chased. DMCA is the one "
            "workstream clients consistently praise: 11 consecutive on-time leak reports for "
            "Shayna, on-cadence reports for Vale and Barbara, and the first-ever leak report for "
            "Alanna on 9/8. Against that, she was sent on Sep 10 to chase Liza for uploads to an "
            "Instagram account whose three predecessors ALTR had just let get deleted, and to "
            "chase Lilia for a Reels account Lilia did not know existed. Paige's DMCA takedown — "
            "the last thing that client ever asked for — has been dead 11 days."
        ),
        "strengths": [
            "11 consecutive on-time weekly leak reports for Shayna; on-cadence delivery for Vale and Barbara; first-ever leak report delivered for Alanna on 9/8.",
            "Answered Vale's leak surge within twelve hours of it being raised.",
            "Carries promo, DMCA and social single-handedly on Alanna.",
        ],
        "coaching_flags": [
            "Sent to chase content for management-run Instagram accounts that are dead, empty or unknown to the client — Liza (9/10, all three accounts deleted), Lilia (9/10, 'Wait u guys have an account for me?'), Amber Haze (9/10, same abandoned Drive link re-sent with her objection still unanswered).",
            "Paige's leak takedown: claimed on Aug 31, exact URL supplied Sep 1, silent 11 days — the client's final request before resigning.",
            "Sarah's ~20 hand-collected leak URLs answered after 47 days with 'their being worked on babes' and no count, site list or date; now 55 days old.",
            "Second person chasing the same content on a different thread from Mayson — no consolidated intake (Haileigh, Alex Paige Moore).",
        ],
    },
    "Mica Vecco": {
        "trend": "down",
        "summary": (
            "Numerically flat (12 → 13) but qualitatively the sharpest decline on the team. The "
            "weekly reel-inspo drop — the deliverable clients actually valued — has largely "
            "stopped; four weekly drops missed on Amber Haze since Aug 13, nothing on Shayna in "
            "29 days, nothing on Vale in 11 days. What replaced it was a generic 'post more "
            "consistently' nudge sent to Alex Paige Moore six days after her surgery disclosure, "
            "to Mila whose main account is suspended, and to Haileigh as literally the only "
            "non-billing message ALTR sent her all fortnight. The one piece of genuinely good "
            "work — diagnosing Vale's Instagram reach collapse and handing her a three-variant "
            "hook test — was then never followed up."
        ),
        "strengths": [
            "Diagnosed Vale's Instagram reach collapse (200k+ to under 3k) the same evening it was raised and handed her a concrete three-variant hook test.",
            "Restored Barbara's weekly inspo drop on Sep 9 after a 27-day gap.",
        ],
        "coaching_flags": [
            "Weekly inspo drop replaced by generic consistency lectures across at least four accounts.",
            "Advice sent without account context — told Alex Paige Moore to post more six days after she disclosed surgery, and Mila to post more while her main account is suspended.",
            "Never collected the results of the hook test she designed for Vale; silent 11 days after the client ran it herself.",
            "No written content-safety guidance for Barbara, 24 days after a 'will this get flagged?' question went unanswered and she deleted her own post out of anxiety.",
        ],
    },
    "Ronnie": {
        "trend": "down",
        "summary": (
            "Low volume, but what there is has gone quiet at the wrong moments. He has not posted "
            "in Sarah's chat since 08-14 (28 days) while nominally owning her 34-day-old earnings "
            "and ranking drop, which has still never received a plan, a date or a named owner. "
            "Same pattern on Sarah Lloyd (silent since 08-26) where the customs-in-the-PPV-queue "
            "issue she caught herself never got a mechanical safeguard. The bright spot is Alex "
            "Paige Moore, where he turned a fan-stalling voice note around in 3h24m."
        ),
        "strengths": [
            "Turned around Alex Paige Moore's fan-facing stall voice note in 3 hours 24 minutes.",
        ],
        "coaching_flags": [
            "Owns Sarah's earnings/ranking drop (34 days) with no plan, date or owner, and has not posted in her chat in 28 days.",
            "No mechanical safeguard built after customs leaked into the PPV/MM queue on Sarah Lloyd; silent there 16 days.",
        ],
    },
    "Olivia": {
        "trend": "flat",
        "summary": (
            "Delivered the single best client outcome of the fortnight and is carrying two "
            "accounts largely alone, which is why her open-issue count rose (2 → 7) despite good "
            "work. She closed Barbara's OFTV loop end to end — chased five times, delivered Sep 2 "
            "— producing the warmest client response anywhere in this report ('These are too good "
            "Liv!!!!!'). She is effectively the entire service on Barbara right now. The gap is "
            "follow-through after delivery: the missing fourth OFTV video is 6 days unanswered, "
            "and Sarah's AI voice-clone accent problem has had no word in 13 days after a 'I'll "
            "try to fix it if possible'."
        ),
        "strengths": [
            "Closed Barbara's OFTV loop end-to-end after five chases — the best-received deliverable in this report ('These are too good Liv!!!!!', 'thank you super star!!!!!!!!').",
            "Two of the three commitments closed on Barbara in fourteen days were hers.",
        ],
        "coaching_flags": [
            "Stops short of the last step — Barbara's missing 4th OFTV video (6 days) and the YouTube repurposing question (11 days) both unanswered after the main delivery landed.",
            "Sarah's AI voice clone: she flagged the wrong accent four times on Aug 29 and explained the brand risk; 13 days of silence since 'I'll try to fix it if possible'.",
        ],
    },
    "Sarah Lloyd chat team": {
        "trend": "flat",
        "summary": (
            "One open item, but it is 90 days old and has never once received a reply. Sexting "
            "sessions are still being built from multiple sets instead of one set per session — "
            "asked 2026-06-13, acknowledged once by the vendor, asked again verbatim 2026-08-19, "
            "bumped internally by Mayson 08-20, and answered by nobody on either occasion. Third "
            "consecutive reporting period carrying it unchanged."
        ),
        "strengths": [],
        "coaching_flags": [
            "A 90-day-old, twice-asked, internally-bumped client instruction has never received a reply from any vendor member.",
        ],
    },
}


def main():
    people = {}

    def slot(name, client):
        e = people.setdefault(name, {
            "name": name, "role": ROLE.get(name, "Team"),
            "open_issues": 0, "clients": {},
            "quotes": [], "_topics": [],
        })
        return e, e["clients"].setdefault(client, {
            "client": client, "reminders": 0, "complaints_owned": 0,
            "commitments_kept": 0, "commitments_overdue": 0,
            "commitments_pending": 0, "notes": [],
        })

    for path in sorted(glob.glob(f"data/weeks/{WEEK}/*.json")):
        if path.endswith("_employees.json"):
            continue
        d = json.load(open(path))
        client = d["client"]

        for r in d.get("reminders", []):
            for name in canonicalise(r.get("employee")):
                e, row = slot(name, client)
                row["reminders"] += r.get("count", 1)
                topic = (r.get("topic") or "").strip()
                if topic:
                    e["_topics"].append(topic)
                    row["notes"].append(f"reminded {r.get('count', 1)}x: {topic}")

        for c in d.get("complaints", []):
            for name in canonicalise(c.get("owner")):
                e, row = slot(name, client)
                row["complaints_owned"] += 1
                if c.get("status") in ("new", "in_progress", "recurring"):
                    e["open_issues"] += 1
                issue = (c.get("issue") or "").strip()
                if issue:
                    row["notes"].append(f"[{c.get('status')}] {issue}")
                for ev in (c.get("evidence") or [])[:1]:
                    # analysts emit either {"quote":..,"date":..} or a bare string
                    q = ev.get("quote") if isinstance(ev, dict) else ev
                    if q:
                        e["quotes"].append({
                            "quote": q, "client": client,
                            "date": ev.get("date", "") if isinstance(ev, dict) else "",
                        })

        for c in d.get("commitments", []):
            for name in canonicalise(c.get("who")):
                e, row = slot(name, client)
                st = c.get("status")
                if st == "done":
                    row["commitments_kept"] += 1
                elif st == "overdue":
                    row["commitments_overdue"] += 1
                    e["open_issues"] += 1
                elif st == "pending":
                    row["commitments_pending"] += 1

    # finalise
    for e in people.values():
        e["clients"] = sorted(e["clients"].values(), key=lambda r: -(
            r["reminders"] + r["complaints_owned"] + r["commitments_overdue"]))
        for row in e["clients"]:
            row["notes"] = " | ".join(row["notes"][:4])
        e["quotes"] = e["quotes"][:6]
        n = NARRATIVE.get(e["name"], {})
        e["summary"] = n.get("summary", "")
        e["trend"] = n.get("trend", "flat")
        e["strengths"] = n.get("strengths", [])
        e["coaching_flags"] = n.get("coaching_flags", [])
        e["totals"] = {
            "clients": len(e["clients"]),
            "reminders": sum(r["reminders"] for r in e["clients"]),
            "complaints": sum(r["complaints_owned"] for r in e["clients"]),
            "kept": sum(r["commitments_kept"] for r in e["clients"]),
            "pending": sum(r["commitments_pending"] for r in e["clients"]),
            "overdue": sum(r["commitments_overdue"] for r in e["clients"]),
        }

    ordered = sorted(people.values(), key=lambda e: -e["open_issues"])

    if DUMP:
        for e in ordered:
            t = e["totals"]
            print(f"\n===== {e['name']} ({e['role']}) open_issues={e['open_issues']} "
                  f"clients={t['clients']} rem={t['reminders']} comp={t['complaints']} "
                  f"kept={t['kept']} pend={t['pending']} over={t['overdue']}")
            for row in e["clients"]:
                print(f"   {row['client']}: rem={row['reminders']} comp={row['complaints_owned']} "
                      f"kept={row['commitments_kept']} pend={row['commitments_pending']} "
                      f"over={row['commitments_overdue']}")
                if row["notes"]:
                    print(f"      {row['notes'][:400]}")
        return

    json.dump({"week_ending": WEEK, "employees": ordered},
              open(f"data/weeks/{WEEK}/_employees.json", "w"), indent=1)
    print(f"wrote data/weeks/{WEEK}/_employees.json ({len(ordered)} employees)")


main()
