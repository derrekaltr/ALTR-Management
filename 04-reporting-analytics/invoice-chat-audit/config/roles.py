"""Sender -> role mapping for the audit.

Roles:
  client        - the paying client / model-side principal in the chat
  staff_billing - agency staff who issue invoices and chase payment
  staff         - other agency staff (chat managers, DMCA, queue, etc.)

Anything not listed falls back to heuristics in role_of().
"""

CLIENTS = {
    "Amber Haze x ALTR": ["Kirsten (amber Haze)"],
    "Barbara x ALTR": ["Barb Brazil", "Barbara Silva"],
    "Haileigh Cox x ALTR": ["Hailey Client"],
    "Kaitlynn x ALTR": ["Kaitlynn Anderson Koda"],
    "Lauren Blake x ALTR": ["Lauren Blake"],
    "Lauryn x ALTR": ["LA Client"],
    "Lilia x ALTR": ["Lilia"],
    "Liza Kovalenko x ALTR": ["Eli"],
    "Mila x ALTR": ["Callie (Mila)"],
    "Sarah Lloyd x ALTR": ["Sarah Lloyd"],
    "Sarah x ALTR": ["Sarah H"],
    "Shayna x ALTR": ["Shayna Holt"],
    "Vale x ALTR": ["Vale", "Val Bragg"],
    "Vicky x ALTR": ["Valerie"],
}

STAFF_BILLING = [
    "Lauren Biz Assistant",
    "Stephski",
    "Michelle Queue",
    "Mica Vecco",
]

STAFF = [
    "Sophie Logan (Raw Agency)", "Mayson Chat", "Derrek", "Eric The Efficient",
    "Olivia", "Lissy", "Ollie Mckinlay", "FRED | OFM", "Jonasito", "Arlo",
    "Joshiepoo", "Nick Granberry", "Vivek", "smurf(offline)", "Alex Camus",
    "Joseph H", "Noah Chat", "Nate (Noah)", "Ronnie Chat", "Nick Scott",
    "Nick | DMCA", "Thon | Content Manager", "Rafael|Content Manager",
    "Ana M | General Manager", "Anne | Account Manager", "Alfred",
    "Masa | Account Executive", "Day | Account Executive",
    "Emmanuel | General Manager", "George", "Alex Chatting Team",
    "Lance | Chat Manager", "Tanya | Chat Manager",
    "Paulo Gutierrez | Chat Manager", "King Choy | Chat Manager",
    "Gelle | Chat Manager", "Isaac |Chat Manager", "Vladan | Chat Manager",
    "Martino | Chat Manager", "Updates", "Leak Scan Demo",
]


def role_of(chat, sender):
    if not sender:
        return "unknown"
    if sender in CLIENTS.get(chat, []):
        return "client"
    if sender in STAFF_BILLING:
        return "staff_billing"
    if sender in STAFF:
        return "staff"
    if "client" in sender.lower():
        return "client"
    if any(t in sender for t in ("| Chat", "|Chat", "Manager", "Executive")):
        return "staff"
    return "unknown"
