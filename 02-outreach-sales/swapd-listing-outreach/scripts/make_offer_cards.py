#!/usr/bin/env python3
"""
make_offer_cards.py — bridge SWAPD-discovered services into the card project's offer cards.

For each NEW + QUALIFIED social-media service (a service ALTR doesn't sell yet, with a
>60% provider), compute an ALTR sell price = provider cost + inverse-scaled markup
(pricing.json), and write an offer-card JSON into the chiang-mai card project's offers/.
Then `node offers.mjs` there renders the branded PNGs.

  python3 scripts/make_offer_cards.py            # write JSONs + print pricing table
  python3 scripts/make_offer_cards.py --render   # also render PNGs via offers.mjs

Cards are prefixed 'swapd-' so they never clobber ALTR's hand-authored catalog offers.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CARD_PROJECT = Path(
    "/Users/locklyjailbreak/conductor/workspaces/sauce-the-brown-carpet-riders/chiang-mai"
)
OFFERS_DIR = CARD_PROJECT / "offers"

CARD_PLATFORMS = {"instagram", "tiktok", "youtube", "snapchat", "whatsapp", "wikipedia"}
SOCIAL_ACTIONS = {"unban", "removal", "verification", "monetization", "shielding",
                  "username_claim", "followers", "recovery"}
SOCIAL_PLATFORMS = {"instagram", "tiktok", "youtube", "facebook", "twitter", "snapchat",
                    "telegram", "threads", "linkedin", "whatsapp", "google", "reddit"}
DESCRIPTIONS = {
    "removal": "Content / account takedown",
    "unban": "Account recovery & unban",
    "verification": "Verification service",
    "username_claim": "Handle / username claim",
    "monetization": "Monetization enablement",
    "shielding": "Account protection",
    "followers": "Audience growth",
    "recovery": "Account recovery",
}


def relevant(sid):
    if sid.split("_")[0] in SOCIAL_PLATFORMS:
        return True
    return any(sid == a or sid.startswith(a + "_") or sid.endswith("_" + a)
               for a in SOCIAL_ACTIONS)


def load_pricing():
    return json.loads((ROOT / "pricing.json").read_text())


def sell_price(cost, cfg):
    mult = cfg["bands"][-1][1]
    for max_cost, m in cfg["bands"]:
        if cost <= max_cost:
            mult = m
            break
    raw = max(cost * mult, cost + cfg["min_margin"])
    r = cfg["round_to"]
    step = r["small_step"] if raw < r["below"] else r["large_step"]
    return int(round(raw / step) * step), mult


def money(n):
    return f"${n:,.0f}"


def fmt_tat(t):
    if not t:
        return None
    t = re.sub(r"\s*-\s*", "–", str(t).strip())
    return t[:1].upper() + t[1:]


def platform_of(sid, catalog_display):
    p = sid.split("_")[0]
    return p if p in CARD_PLATFORMS else "house"


def action_of(sid):
    for a in SOCIAL_ACTIONS:
        if sid.endswith("_" + a) or sid == a:
            return a
    return None


def build():
    services = json.loads((DATA / "services.json").read_text()).get("services", {})
    cfg = load_pricing()
    overrides = cfg.get("overrides", {})
    titles = cfg.get("card_titles", {})
    OFFERS_DIR.mkdir(parents=True, exist_ok=True)
    out_png_dir = CARD_PROJECT / "output" / "offers"
    for stale in list(OFFERS_DIR.glob("swapd-*.json")) + list(out_png_dir.glob("swapd-*.png")):
        stale.unlink()  # rebuild cleanly each run (filenames track the card title)

    rows, written = [], []
    for sid, svc in sorted(services.items()):
        if not svc.get("is_new") or not svc.get("qualified_count") or not relevant(sid):
            continue
        if sid.endswith("_service"):  # platform known but no real action = not a card
            continue
        best = next((p for p in svc["providers"] if p.get("is_best_price")), None)
        cost = best.get("price") if best else None

        if sid in overrides:
            price_str, note = overrides[sid], "override"
        elif cost:
            sp, mult = sell_price(cost, cfg)
            price_str, note = money(sp), f"{money(cost)} cost ×{mult:g}"
        else:
            price_str, note = "Custom Quote", "no provider price"

        offer = {
            "platform": platform_of(sid, svc["display"]),
            "service": titles.get(sid, svc["display"]),
            "description": DESCRIPTIONS.get(action_of(sid), "ALTR marketplace service"),
            "price": price_str,
        }
        tat = fmt_tat(best.get("turnaround") if best else None)
        if tat:
            offer["tat"] = tat

        slug = "swapd-" + re.sub(r"[^a-z0-9]+", "-", offer["service"].lower()).strip("-")
        (OFFERS_DIR / f"{slug}.json").write_text(json.dumps(offer, indent=2))
        written.append(f"offers/{slug}.json")
        rows.append((offer["service"], money(cost) if cost else "—", price_str, note,
                     offer["platform"]))

    print(f"Wrote {len(written)} offer cards to {OFFERS_DIR}\n")
    print(f"{'SERVICE':<34}{'COST':>10}{'SELL':>12}   {'BASIS':<22}PLATFORM")
    print("-" * 92)
    for disp, cost, sell, note, plat in rows:
        print(f"{disp[:33]:<34}{cost:>10}{sell:>12}   {note:<22}{plat}")

    if "--render" in sys.argv and written:
        print("\nRendering PNGs via offers.mjs …")
        res = subprocess.run(["node", "offers.mjs", *written], cwd=CARD_PROJECT,
                             capture_output=True, text=True)
        print(res.stdout or res.stderr)
    else:
        print(f"\nDry run — rerun with --render to build PNGs "
              f"(-> {CARD_PROJECT / 'output' / 'offers'}).")


if __name__ == "__main__":
    build()
