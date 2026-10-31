#!/usr/bin/env python3
"""Reconstruct invoice cycles (issued -> follow-ups -> payment signal) per chat.

Usage: python3 scripts/build_cycles.py [--extract data/invoicing] [--out data/cycles]

Outputs:
  data/cycles/<chat>.json  - full event detail per cycle (traceable msg ids)
  data/cycles/cycles.csv   - one row per cycle, all chats

Payment detection is an EVIDENCE FLAG, not a verdict: wire/Zelle payments can
complete with zero chat trace. 'none' means no visible signal in chat.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.keywords import (EVENT_PATTERNS, INVOICE_PDF, MONTHS, PERIOD_TEXT,
                             is_primary, is_secondary)
from config.roles import role_of


def parse_dt(ts):
    return datetime.fromisoformat(ts) if ts else None


def month_num(tok):
    return MONTHS.get(tok[:3].lower()) if tok else None


def infer_period(m1, d1, m2, d2, ts):
    """Return (period_start_date, label). Year chosen to minimize |start - ts|."""
    mo1 = month_num(m1)
    mo2 = month_num(m2) or mo1
    if not mo1:
        return None, None
    best = None
    for y in (ts.year - 1, ts.year, ts.year + 1):
        try:
            start = datetime(y, mo1, int(d1), tzinfo=ts.tzinfo)
        except ValueError:
            continue
        if best is None or abs((start - ts).total_seconds()) < abs((best - ts).total_seconds()):
            best = start
    if best is None:
        return None, None
    label = f"{best.year}-{mo1:02d}-{int(d1):02d}..{mo2:02d}-{int(d2):02d}"
    return best, label


def period_from_message(m, ts):
    media = m.get("media") or {}
    name = media.get("name") or ""
    pm = INVOICE_PDF.search(name)
    if pm:
        return infer_period(pm.group(1), pm.group(2), pm.group(3), pm.group(4), ts)
    text = m.get("text") or ""
    if EVENT_PATTERNS["INVOICE_ISSUED_TEXT"].search(text) and "invoic" in text.lower():
        tm = PERIOD_TEXT.search(text)
        if tm:
            return infer_period(tm.group(1), tm.group(2), tm.group(3), tm.group(4), ts)
    return None, None


def classify(chat, m):
    """Return list of event types for this message."""
    role = role_of(chat, m.get("sender"))
    text = m.get("text") or ""
    media = m.get("media") or {}
    events = []
    is_invoice_pdf_msg = bool(media.get("name") and INVOICE_PDF.search(media["name"]))
    if is_invoice_pdf_msg:
        events.append("INVOICE_ISSUED")
    if role in ("staff_billing", "staff") and text:
        if not is_invoice_pdf_msg and EVENT_PATTERNS["INVOICE_ISSUED_TEXT"].search(text) \
                and "invoic" in text.lower() and PERIOD_TEXT.search(text):
            events.append("INVOICE_ISSUED")
        if EVENT_PATTERNS["PRE_REMINDER"].search(text):
            events.append("PRE_REMINDER")
        if EVENT_PATTERNS["PAYMENT_LINK"].search(text):
            events.append("PAYMENT_LINK")
        if EVENT_PATTERNS["ESCALATION"].search(text):
            events.append("ESCALATION")
        elif EVENT_PATTERNS["FOLLOW_UP"].search(text) and (is_primary(text) or is_secondary(text)):
            events.append("FOLLOW_UP")
    if role == "client" and text:
        contextual = (is_primary(text) or is_secondary(text)
                      or m.get("topic") == "Invoicing")
        if EVENT_PATTERNS["PAYMENT_CLAIMED"].search(text) and contextual:
            events.append("PAYMENT_CLAIMED")
    if role in ("staff_billing", "staff") and text and EVENT_PATTERNS["PAYMENT_CONFIRMED"].search(text):
        events.append("PAYMENT_CONFIRMED_CAND")  # only counts right after a claim
    return events


def build_chat_cycles(chat, msgs):
    cycles = []          # list of dicts, in issuance order
    open_cycles = []     # refs into cycles
    last_claim = None    # (cycle, ts, msg_id) awaiting staff confirmation
    events_log = []

    for m in msgs:
        ts = parse_dt(m.get("ts"))
        if ts is None:
            continue
        evs = classify(chat, m)
        for ev in evs:
            events_log.append({"event": ev, "id": m["id"], "ts": m["ts"],
                               "sender": m.get("sender")})
        if "INVOICE_ISSUED" in evs:
            start, label = period_from_message(m, ts)
            # dedupe on period START (text label and PDF filename can disagree
            # on the end day of the same invoice, e.g. "Dec 1-14" vs "Dec 1-15")
            key = start.date().isoformat() if start else f"unlabeled@{m['id']}"
            existing = next((c for c in cycles if c["period_key"] == key), None)
            if existing:
                existing["issue_msg_ids"].append(m["id"])
            else:
                cyc = {
                    "chat": chat, "period_key": key, "period": label or key,
                    "period_start": start.isoformat() if start else None,
                    "issued_ts": m["ts"], "issued_by": m.get("sender"),
                    "issue_msg_ids": [m["id"]],
                    "followups": [], "escalations": [], "payment_links": [],
                    "payment_claimed_ts": None, "payment_claim_msg": None,
                    "payment_confirmed": False,
                    "evidence": "none", "lag_days": None,
                }
                cycles.append(cyc)
                open_cycles.append(cyc)
        if open_cycles:
            # attach chasing activity to the most recently issued open cycle —
            # that is the invoice under discussion (older open cycles are
            # usually already settled off-chat)
            if "FOLLOW_UP" in evs:
                open_cycles[-1]["followups"].append(m["id"])
            if "ESCALATION" in evs:
                open_cycles[-1]["escalations"].append(m["id"])
            if "PAYMENT_LINK" in evs:
                open_cycles[-1]["payment_links"].append(m["id"])
        if "PAYMENT_CLAIMED" in evs and open_cycles:
            text = (m.get("text") or "").lower()
            # attach to the cycle the claim replies to, if it replies to an
            # issuance message; otherwise the MOST RECENT open cycle (clients
            # settle the invoice under discussion — older open cycles were
            # often paid off-chat, so pinning claims to them fabricates lag)
            reply_cyc = None
            if m.get("reply_to") is not None:
                reply_cyc = next((c for c in open_cycles
                                  if m["reply_to"] in c["issue_msg_ids"]), None)
            if "both" in text or "all" in text or "everything" in text:
                targets = [c for c in open_cycles
                           if (ts - parse_dt(c["issued_ts"])).days <= 60]
                if not targets:
                    targets = [open_cycles[-1]]
            else:
                targets = [reply_cyc or open_cycles[-1]]
            for cyc in targets:
                cyc["payment_claimed_ts"] = m["ts"]
                cyc["payment_claim_msg"] = m["id"]
                cyc["evidence"] = "claimed_only"
                issued = parse_dt(cyc["issued_ts"])
                cyc["lag_days"] = round((ts - issued).total_seconds() / 86400, 1)
                open_cycles.remove(cyc)
                last_claim = (cyc, ts, m["id"])
        elif "PAYMENT_CONFIRMED_CAND" in evs and last_claim:
            cyc, claim_ts, _ = last_claim
            if ts - claim_ts <= timedelta(days=3):
                cyc["payment_confirmed"] = True
                cyc["evidence"] = "strong"
            last_claim = None

    return cycles, events_log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", default="data/invoicing")
    ap.add_argument("--out", default="data/cycles")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for path in sorted(Path(args.extract).glob("*.jsonl")):
        chat = path.stem
        msgs = [json.loads(ln) for ln in path.open(encoding="utf-8")]
        cycles, events_log = build_chat_cycles(chat, msgs)
        (out_dir / f"{chat}.json").write_text(
            json.dumps({"cycles": cycles, "events": events_log},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        for c in cycles:
            all_rows.append({
                "chat": c["chat"], "period": c["period"],
                "issued_ts": c["issued_ts"], "issued_by": c["issued_by"],
                "n_followups": len(c["followups"]),
                "n_escalations": len(c["escalations"]),
                "payment_evidence": c["evidence"],
                "first_payment_signal_ts": c["payment_claimed_ts"] or "",
                "lag_days": c["lag_days"] if c["lag_days"] is not None else "",
                "issue_msg_ids": ";".join(map(str, c["issue_msg_ids"])),
                "followup_msg_ids": ";".join(map(str, c["followups"])),
                "escalation_msg_ids": ";".join(map(str, c["escalations"])),
                "claim_msg_id": c["payment_claim_msg"] or "",
            })
        n_open = sum(1 for c in cycles if c["evidence"] == "none")
        lags = [c["lag_days"] for c in cycles if c["lag_days"] is not None]
        med = sorted(lags)[len(lags) // 2] if lags else "-"
        print(f"{chat}: {len(cycles)} cycles, {n_open} no-payment-signal, median lag {med}d")

    with (out_dir / "cycles.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    print(f"\n{len(all_rows)} cycles total -> {out_dir/'cycles.csv'}")


if __name__ == "__main__":
    main()
