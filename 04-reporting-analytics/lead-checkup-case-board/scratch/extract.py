#!/usr/bin/env python3
"""Extract last-6-months messages from iMessage + WhatsApp copies into JSONL."""
import sqlite3, json, os, glob, re, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
APPLE_EPOCH = 978307200  # 2001-01-01 unix offset
CUTOFF_UNIX = int(datetime(2026, 3, 18, tzinfo=timezone.utc).timestamp())
CUTOFF_APPLE_NS = (CUTOFF_UNIX - APPLE_EPOCH) * 1_000_000_000
CUTOFF_APPLE_S = CUTOFF_UNIX - APPLE_EPOCH

def ts_apple_ns(v):
    return datetime.fromtimestamp(v / 1_000_000_000 + APPLE_EPOCH, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

def ts_apple_s(v):
    return datetime.fromtimestamp(v + APPLE_EPOCH, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

# ---------- contacts ----------
def load_contacts():
    contacts = {}  # normalized key -> name
    for db in glob.glob(os.path.expanduser("~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb")) + \
              glob.glob(os.path.expanduser("~/Library/Application Support/AddressBook/AddressBook-v22.abcddb")):
        try:
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            cur = con.cursor()
            recs = {}
            for pk, fn, ln, org in cur.execute(
                "SELECT Z_PK, ZFIRSTNAME, ZLASTNAME, ZORGANIZATION FROM ZABCDRECORD"):
                name = " ".join(x for x in (fn, ln) if x) or (org or "")
                if name:
                    recs[pk] = name.strip()
            for owner, num in cur.execute("SELECT ZOWNER, ZFULLNUMBER FROM ZABCDPHONENUMBER"):
                if owner in recs and num:
                    digits = re.sub(r"\D", "", num)
                    if len(digits) >= 7:
                        contacts[digits[-10:]] = recs[owner]
            for owner, addr in cur.execute("SELECT ZOWNER, ZADDRESS FROM ZABCDEMAILADDRESS"):
                if owner in recs and addr:
                    contacts[addr.lower()] = recs[owner]
            con.close()
        except Exception as e:
            print(f"contacts {db}: {e}", file=sys.stderr)
    return contacts

def resolve(handle, contacts):
    if not handle:
        return handle
    h = handle.lower()
    if "@" in h and not h.split("@")[0].isdigit():
        return contacts.get(h, handle)
    digits = re.sub(r"\D", "", h.split("@")[0])
    if len(digits) >= 7:
        return contacts.get(digits[-10:], handle)
    return handle

# ---------- iMessage attributedBody decode ----------
def decode_body(blob):
    if blob is None:
        return None
    try:
        idx = blob.find(b"NSString")
        if idx == -1:
            return None
        c = blob[idx + 8:]
        c = c[5:]  # skip \x01\x94\x84\x01\x2b control bytes
        if not c:
            return None
        ln = c[0]; start = 1
        if ln == 0x81:
            ln = int.from_bytes(c[1:3], "little"); start = 3
        elif ln == 0x82:
            ln = int.from_bytes(c[1:5], "little"); start = 5
        return c[start:start + ln].decode("utf-8", errors="replace")
    except Exception:
        return None

def extract_imessage(contacts, out_path):
    con = sqlite3.connect(f"file:{HERE}/chat.db?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # chat participants
    parts = {}
    for r in cur.execute("""SELECT chj.chat_id, h.id FROM chat_handle_join chj
                            JOIN handle h ON h.ROWID = chj.handle_id"""):
        parts.setdefault(r[0], []).append(resolve(r[1], contacts))
    chats = {}
    for r in cur.execute("SELECT ROWID, guid, display_name, chat_identifier, style FROM chat"):
        nm = r["display_name"] or ""
        if not nm:
            p = parts.get(r["ROWID"], [])
            nm = ", ".join(p[:4]) if p else (resolve(r["chat_identifier"], contacts) or r["chat_identifier"])
        chats[r["ROWID"]] = {"name": nm, "group": r["style"] == 43, "participants": parts.get(r["ROWID"], [])}
    # attachments per message
    atts = {}
    for r in cur.execute("""SELECT maj.message_id, a.filename, a.mime_type FROM message_attachment_join maj
                            JOIN attachment a ON a.ROWID = maj.attachment_id"""):
        atts.setdefault(r[0], []).append({"path": r[1], "mime": r[2]})
    n = 0
    with open(out_path, "w") as f:
        q = """SELECT m.ROWID, m.date, m.is_from_me, m.text, m.attributedBody, m.associated_message_type,
                      h.id AS sender, cmj.chat_id
               FROM message m
               JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
               LEFT JOIN handle h ON h.ROWID = m.handle_id
               WHERE m.date > ? ORDER BY m.date"""
        for r in cur.execute(q, (CUTOFF_APPLE_NS,)):
            text = r["text"] or decode_body(r["attributedBody"]) or ""
            a = atts.get(r["ROWID"], [])
            if not text and not a:
                continue
            ch = chats.get(r["chat_id"], {"name": "?", "group": False, "participants": []})
            rec = {
                "src": "imessage", "chat_id": r["chat_id"], "chat": ch["name"], "group": ch["group"],
                "ts": ts_apple_ns(r["date"]),
                "from_me": bool(r["is_from_me"]),
                "sender": "me" if r["is_from_me"] else resolve(r["sender"], contacts),
                "text": text,
                "react": r["associated_message_type"] or 0,
            }
            if a:
                rec["atts"] = a
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    con.close()
    print(f"imessage: {n} messages")

# ---------- WhatsApp ----------
def extract_whatsapp(contacts, out_path):
    con = sqlite3.connect(f"file:{HERE}/wa.sqlite?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    sessions = {}
    for r in cur.execute("SELECT Z_PK, ZCONTACTJID, ZPARTNERNAME, ZSESSIONTYPE FROM ZWACHATSESSION"):
        sessions[r["Z_PK"]] = {"jid": r["ZCONTACTJID"], "name": r["ZPARTNERNAME"] or resolve(r["ZCONTACTJID"], contacts),
                               "group": r["ZSESSIONTYPE"] == 1}
    members = {}
    for r in cur.execute("SELECT Z_PK, ZMEMBERJID, ZCONTACTNAME FROM ZWAGROUPMEMBER"):
        members[r["Z_PK"]] = r["ZCONTACTNAME"] or resolve(r["ZMEMBERJID"] or "", contacts)
    media = {}
    for r in cur.execute("SELECT ZMESSAGE, ZMEDIALOCALPATH, ZTITLE FROM ZWAMEDIAITEM WHERE ZMESSAGE IS NOT NULL"):
        if r["ZMEDIALOCALPATH"]:
            media[r["ZMESSAGE"]] = r["ZMEDIALOCALPATH"]
    n = 0
    with open(out_path, "w") as f:
        q = """SELECT Z_PK, ZCHATSESSION, ZISFROMME, ZMESSAGEDATE, ZTEXT, ZGROUPMEMBER, ZMESSAGETYPE, ZFROMJID
               FROM ZWAMESSAGE WHERE ZMESSAGEDATE > ? ORDER BY ZMESSAGEDATE"""
        for r in cur.execute(q, (CUTOFF_APPLE_S,)):
            s = sessions.get(r["ZCHATSESSION"])
            if s is None:
                continue
            text = r["ZTEXT"] or ""
            mp = media.get(r["Z_PK"])
            if not text and not mp:
                continue
            if r["ZISFROMME"]:
                sender = "me"
            elif r["ZGROUPMEMBER"] and r["ZGROUPMEMBER"] in members:
                sender = members[r["ZGROUPMEMBER"]]
            else:
                sender = resolve((r["ZFROMJID"] or s["jid"] or ""), contacts)
            rec = {"src": "whatsapp", "chat_id": r["ZCHATSESSION"], "chat": s["name"], "group": s["group"],
                   "ts": ts_apple_s(r["ZMESSAGEDATE"]), "from_me": bool(r["ZISFROMME"]),
                   "sender": sender, "text": text, "type": r["ZMESSAGETYPE"]}
            if mp:
                rec["atts"] = [{"path": mp}]
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    con.close()
    print(f"whatsapp: {n} messages")

if __name__ == "__main__":
    contacts = load_contacts()
    print(f"contacts loaded: {len(contacts)}")
    extract_imessage(contacts, os.path.join(HERE, "imessage.jsonl"))
    extract_whatsapp(contacts, os.path.join(HERE, "whatsapp.jsonl"))
