"""Redaction of PII from extracted transcripts before they leave data/parsed.

Everything committed to the repo (report/) or fed to analysis must pass
through redact(). Raw exports and data/parsed stay local and gitignored.
"""
import re

# Known live values seen in the exports (bank account, routing, personal phone)
LITERALS = [
    ("968329703", "[REDACTED:acct]"),
    ("021000021", "[REDACTED:routing]"),
    ("5618011087", "[REDACTED:phone]"),
    ("561-801-1087", "[REDACTED:phone]"),
    ("(561) 801-1087", "[REDACTED:phone]"),
]

GENERIC = [
    # 8-17 digit numbers near account/routing/wire context
    (re.compile(r"(?i)((?:account|acct|routing|aba|wire)[^\n]{0,60}?)\b\d{8,17}\b"),
     r"\1[REDACTED:number]"),
    # SWIFT/BIC codes explicitly labelled
    (re.compile(r"(?i)\b(swift|bic)\b(\s*(?:code|number)?\s*[:\-]?\s*)[A-Z0-9]{8,11}\b"),
     r"\1\2[REDACTED:swift]"),
    # US phone shapes
    (re.compile(r"\b\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"), "[REDACTED:phone]"),
    # tel: links
    (re.compile(r"tel:\+?\d+"), "tel:[REDACTED:phone]"),
    # emails except the agency domain
    (re.compile(r"\b[\w.+-]+@(?!altrmgmt\.com)[\w-]+\.[\w.]+\b"), "[REDACTED:email]"),
]


def redact(text):
    if not text:
        return text
    for lit, repl in LITERALS:
        text = text.replace(lit, repl)
    for pat, repl in GENERIC:
        text = pat.sub(repl, text)
    return text
