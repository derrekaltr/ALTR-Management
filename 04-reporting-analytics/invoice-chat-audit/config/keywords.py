"""Keyword/regex sets for invoicing-relevance extraction and event classification.

Two tiers:
- PRIMARY: any single hit marks a message invoicing-relevant (high precision).
- SECONDARY: context-only; never trigger inclusion on their own (they get swept
  into segments via the context window around primary hits). This is what keeps
  "paid ads" / "OF account" / "bank holiday" out of the extract.
"""
import re

_flags = re.IGNORECASE

PRIMARY = [re.compile(p, _flags) for p in [
    r"invoic",                       # invoice, invoicing, invoiced
    r"\bzelle\b",
    r"\bwire\b",
    r"fan\s?basis|agency-checkout",
    r"apple\s?pay",
    r"\brevolut\b",
    r"\brouting\b",
    r"\bswift\b",
    r"\bbilling\b",
    r"\breceipt\b",
    r"overdue|past\s+due",
    r"pause\s+chatting",
    r"haven'?t\s+(received|heard\s+back).{0,60}payment",
    r"payment.{0,40}haven'?t\s+(been\s+)?(received|sent)",
    r"checking\s+in\s+on.{0,40}(invoice|payment)",
    r"follow(ing)?\s+up.{0,40}(invoice|payment)",
    r"payment\s+(link|method|processor|plan)",
    r"send\s+(the\s+)?payment",
    r"sent\s+(the\s+)?payment",
    r"make\s+(the\s+)?payment",
    r"invoice\s+complete",
    r"split.{0,25}invoice",
    r"bank\s+(details|info|account|change)",
    r"\bwithdraw(al)?\b",
    r"\bpayout\b",
    r"\bremittance\b",
    r"\bchargeback\b",
    r"\brefund\b",
]]

SECONDARY = [re.compile(p, _flags) for p in [
    r"\bpaid\b",
    r"\bpay(ing|ment)?\b",
    r"\bbalance\b",
    r"\bowe[sd]?\b",
    r"\bfunds?\b",
    r"\bbank\b",
    r"\bmoney\b",
    r"\btransfer\b",
]]

# Invoice PDF attachment: "<legal name> <Mon> <d>-<d>[th].pdf" and variants
INVOICE_PDF = re.compile(
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\.?\s*"
    r"(\d{1,2})(?:st|nd|rd|th)?\s*[-–]\s*"
    r"(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*)?"
    r"(\d{1,2})(?:st|nd|rd|th)?.*\.pdf$",
    _flags,
)

# Billing period in prose: "invoice for January 1-14", "September 1st to the 14th"
PERIOD_TEXT = re.compile(
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+"
    r"(\d{1,2})(?:st|nd|rd|th)?\s*(?:-|–|—|to|through|thru)\s*(?:the\s+)?"
    r"(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?"
    r"(\d{1,2})(?:st|nd|rd|th)?",
    _flags,
)

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def is_primary(text):
    return any(p.search(text) for p in PRIMARY)


def is_secondary(text):
    return any(p.search(text) for p in SECONDARY)


def is_invoice_pdf(name):
    return bool(name and INVOICE_PDF.search(name))


# ---------------------------------------------------------------------------
# Event classification patterns (used by build_cycles.py). Order matters:
# first match wins within a role class.
# ---------------------------------------------------------------------------
EVENT_PATTERNS = {
    # staff-side, high reliability
    "INVOICE_ISSUED_TEXT": re.compile(
        r"(here\s+is|attached|below.{0,30}invoice|invoice\s+for|sent\s+over.{0,30}invoice)", _flags),
    "PRE_REMINDER": re.compile(
        r"invoic(es?|ing)\s+(will\s+(be\s+sent|go)|go(es)?\s+out|going\s+out)", _flags),
    "PAYMENT_LINK": re.compile(r"fanbasis\.com|agency-checkout|payment\s+link", _flags),
    "FOLLOW_UP": re.compile(
        r"(follow(ing)?\s+up|checking\s+in|circle\s+back|touch(ing)?\s+base"
        r"|able\s+to\s+(send|shoot|make).{0,30}(payment|that\s+over)"
        r"|when\s+(will|can|do)\s+you.{0,40}(pay|send|payment)"
        r"|any\s+update.{0,30}(payment|invoice)"
        r"|send\s+payment\s+today|get\s+(that|the\s+invoice)\s+(paid|settled))", _flags),
    "ESCALATION": re.compile(
        r"(pause\s+chatting|past\s+due|overdue"
        r"|haven'?t\s+(received|heard\s+back).{0,60}payment"
        r"|we\s+will\s+have\s+to|final\s+(notice|reminder))", _flags),
    # client-side payment signals, medium reliability
    "PAYMENT_CLAIMED": re.compile(
        r"(invoice\s+complete|just\s+(sent|paid|wired|zelled)"
        r"|i\s+(sent|paid|wired|zelled)|payment\s+(was\s+)?sent"
        r"|sent\s+(it|the\s+payment|payment)|will\s+pay|i'?ll\s+(pay|send)"
        r"|paid\s+(it|both|the\s+invoice|this\s+morning|today|yesterday)"
        r"|already\s+paid|\bpaid\s+out\b"
        r"|via\s+(apple\s?pay|zelle|wire|revolut)|done\s*✅?|\bcomplete[d]?\b)", _flags),
    # staff acknowledgement, low reliability
    "PAYMENT_CONFIRMED": re.compile(
        r"(received|got\s+it|all\s+set|confirmed|we\s+see\s+it|came\s+through|thank\s+you)", _flags),
}
