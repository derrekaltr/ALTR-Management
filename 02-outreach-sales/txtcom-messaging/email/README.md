# ALTR · TXT Line — creator promo email blast

Everything lives in this folder. Stdlib Python only — nothing to install.

## Files

| File | What it is |
|---|---|
| `promo-email.html` | The designed email (ALTR brand, email-safe tables/inline styles) |
| `promo-email.txt` | Plain-text version, sent alongside the HTML (helps deliverability) |
| `send.py` | The mass sender: CSV in, personalized sends out, throttled + logged |
| `config.example.env` | Copy to `config.env`, fill in SMTP + sender details |
| `creators.csv.example` | Copy to `creators.csv`, paste your list (`email,first_name`) |
| `sent_log.csv` | Created automatically; makes re-runs skip already-sent addresses |

## Setup (5 minutes)

```bash
cd email
cp config.example.env config.env     # fill in SMTP creds, subject, links, address
cp creators.csv.example creators.csv # paste your list
```

Placeholders available in the templates and subject line: `{{first_name}}`
(falls back to "there" if blank), `{{email}}`, `{{cta_url}}`,
`{{unsubscribe_url}}`, `{{company_address}}`, plus any extra column you add
to the CSV (a `handle` column becomes `{{handle}}`).

## Run order

```bash
python3 send.py --test you@yourdomain.com  # 1. send yourself a proof — check phone + desktop + spam
python3 send.py --dry-run                  # 2. validates every row renders cleanly, sends nothing
python3 send.py --limit 25                 # 3. first real batch, small
python3 send.py                            # 4. full run (resumes past already-sent)
```

Stop any time with Ctrl-C — `sent_log.csv` means the next run picks up where
you left off. Failures are logged with the error and retried on the next run
only if you delete their row from the log (deliberate: hard bounces usually
shouldn't be retried).

## Deliverability — read this before the full run

Cold volume from a fresh address gets spam-foldered. The cheap insurance:

1. **Send from a subdomain** (`outreach.yourdomain.com` or a lookalike domain),
   so your main domain's reputation is never at risk.
2. **Set up SPF, DKIM, and DMARC** on that sending domain. Without DKIM,
   Gmail will junk bulk sends on arrival. Your provider's docs cover it —
   it's three DNS records.
3. **Warm up**: ~25–50/day for the first week, then ramp. The `--limit` flag
   plus the built-in 20–45s random delay exists for exactly this.
4. **Gmail/Yahoo bulk-sender rules** require one-click unsubscribe — the
   script already sends `List-Unsubscribe` headers, but the URL in your
   config has to actually work.
5. At 1,000+ sends, consider an ESP SMTP relay (Postmark, SendGrid, Mailgun) —
   the script works unchanged, just point the SMTP config at the relay.
   Note: check the ESP's acceptable-use policy; some prohibit adult-industry
   senders, so pick one that allows your business before building on it.

## Compliance (CAN-SPAM, quick version)

This is commercial email to business contacts, which is legal in the US if:
a real physical mailing address is in the footer (config: `COMPANY_ADDRESS`),
there's a working opt-out honored within 10 days (`UNSUBSCRIBE_URL` — keep a
suppression list and remove unsubscribes from `creators.csv`), the From name
and subject aren't deceptive, and you keep sends to each address reasonable.
EU/UK recipients fall under stricter rules (PECR/GDPR) — if the list has many
EU creators, trim them or get advice first.

## Tweaking the design

`promo-email.html` is table-based with inline styles on purpose — email
clients (especially Outlook and Gmail) strip `<style>` blocks, CSS variables,
flexbox, and grid. Edit text freely; if you change layout, keep it tables.
Width is fixed at 600px, fonts are web-safe stacks (true Archivo/Spline Sans
Mono don't load reliably in email). Re-test with `--test` after any edit.
