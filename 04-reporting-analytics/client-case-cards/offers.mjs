#!/usr/bin/env node
// Marketplace offer card generator: node offers.mjs offers/<offer>.json [more ...]
// 1080x1080 PNG per offer → output/offers/<name>.png
// Offer JSON: { platform?, service, tat, price, priceNote?, details?, notes? }

import { readFile, writeFile, mkdir, rm } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { chromium } from "playwright";

const ROOT = dirname(fileURLToPath(import.meta.url));
const brand = JSON.parse(await readFile(join(ROOT, "cards", "brand", "config.json"), "utf8"));

const esc = (s) =>
  String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

const asset = async (p) => `data:image/png;base64,${(await readFile(join(ROOT, p))).toString("base64")}`;
const wordmarkLight = await asset(brand.assets.wordmarkLight);
const wordmarkDark = await asset(brand.assets.wordmarkDark);
const monogramLight = await asset(brand.assets.monogramLight);
const monogramDark = await asset(brand.assets.monogramDark);

const GLYPHS = {
  youtube: `<svg class="glyph" width="640" height="640" viewBox="0 0 100 100"><rect x="6" y="22" width="88" height="60" rx="16" fill="none" stroke="#ff0033" stroke-width="3.5"/><path d="M42 38 L66 52 L42 66 Z" fill="#ff0033"/></svg>`,
  instagram: `<svg class="glyph" width="620" height="620" viewBox="0 0 100 100"><defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#f7b955"/><stop offset="0.5" stop-color="#e94b8a"/><stop offset="1" stop-color="#8a3ab9"/></linearGradient></defs><rect x="10" y="10" width="80" height="80" rx="24" fill="none" stroke="url(#ig)" stroke-width="4"/><circle cx="50" cy="50" r="19" fill="none" stroke="url(#ig)" stroke-width="4"/><circle cx="73" cy="27" r="5.5" fill="url(#ig)"/></svg>`,
  tiktok: `<svg class="glyph" width="560" height="560" viewBox="0 0 100 100"><path d="M60 12 v46 a16 16 0 1 1 -12 -15.5" fill="none" stroke="#25f4ee" stroke-width="7" stroke-linecap="round"/><path d="M64 16 v46 a16 16 0 1 1 -12 -15.5" fill="none" stroke="#fe2c55" stroke-width="7" stroke-linecap="round" opacity="0.9"/><path d="M62 14 c2 12 10 20 22 21 v11 c-9 0 -17 -3 -22 -8" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.85"/></svg>`,
  snapchat: `<svg class="glyph" width="560" height="560" viewBox="0 0 100 100"><path d="M50 12 c14 0 22 10 22 24 v8 c4 5 9 7 14 8 -3 6 -9 8 -13 9 3 8 10 12 17 13 -4 6 -12 7 -17 8 -5 6 -13 10 -23 10 s-18 -4 -23 -10 c-5 -1 -13 -2 -17 -8 7 -1 14 -5 17 -13 -4 -1 -10 -3 -13 -9 5 -1 10 -3 14 -8 v-8 c0 -14 8 -24 22 -24 z" fill="none" stroke="#0b0b0b" stroke-width="4" stroke-linejoin="round"/></svg>`,
  whatsapp: `<svg class="glyph" width="580" height="580" viewBox="0 0 100 100"><path d="M50 12 a37 37 0 1 1 -18.5 69 L14 86 l5.3 -17 A37 37 0 0 1 50 12 z" fill="none" stroke="#25d366" stroke-width="4" stroke-linejoin="round"/><path d="M36 34 c-2 0 -4 2 -4 5 c0 12 13 25 25 25 c3 0 5 -2 5 -4 l-1.5 -5 l-7 -2.5 l-3 3 c-4 -1.5 -8 -5.5 -9.5 -9.5 l3 -3 l-2.5 -7 z" fill="none" stroke="#25d366" stroke-width="3.5" stroke-linejoin="round"/></svg>`,
  wikipedia: `<svg class="glyph" width="620" height="620" viewBox="0 0 100 100"><text x="50" y="74" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="86" fill="none" stroke="#202122" stroke-width="1.6">W</text></svg>`,
  google: `<svg class="glyph" width="600" height="600" viewBox="0 0 100 100"><path d="M83 36 A38 38 0 1 0 88 50" fill="none" stroke="#4285F4" stroke-width="8" stroke-linecap="round"/><path d="M54 50 h34" fill="none" stroke="#34A853" stroke-width="8" stroke-linecap="round"/><path d="M62 22 l3.5 7.5 8 1 -6 5.5 1.5 8 -7 -4" fill="#FBBC05" opacity="0.9"/></svg>`,
  uber: `<svg class="glyph" width="560" height="560" viewBox="0 0 100 100"><path d="M50 14 c-16 0 -29 13 -29 29 c0 20 24 39 29 43 c5 -4 29 -23 29 -43 c0 -16 -13 -29 -29 -29 z" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round"/><circle cx="50" cy="43" r="11" fill="none" stroke="#ffffff" stroke-width="3.5"/></svg>`,
  house: `<img class="glyph" width="560" src="${monogramLight}">`,
};

const THEMES = {
  youtube: { tag: "YouTube", bg: `radial-gradient(1100px 700px at 88% -10%, rgba(255,0,51,0.22), transparent 60%), #0d0d0f`, accent: "#ff0033", ink: "#f4f2ee", muted: "rgba(244,242,238,0.55)", line: "rgba(255,255,255,0.13)", dark: false },
  instagram: { tag: "Instagram", bg: `radial-gradient(1000px 760px at 100% 0%, rgba(188,42,141,0.30), transparent 58%), radial-gradient(900px 700px at 0% 100%, rgba(247,185,85,0.16), transparent 55%), #16101f`, accent: "#e94b8a", ink: "#f4f2ee", muted: "rgba(244,242,238,0.55)", line: "rgba(255,255,255,0.14)", dark: false, gradientText: "linear-gradient(100deg,#f7b955 0%,#e94b8a 45%,#8a3ab9 100%)" },
  tiktok: { tag: "TikTok", bg: `radial-gradient(900px 640px at 108% 4%, rgba(254,44,85,0.20), transparent 55%), radial-gradient(900px 720px at -8% 100%, rgba(37,244,238,0.14), transparent 55%), #050507`, accent: "#25f4ee", ink: "#ffffff", muted: "rgba(244,242,238,0.55)", line: "rgba(255,255,255,0.13)", dark: false },
  snapchat: { tag: "Snapchat", bg: `#fffc00`, accent: "#0b0b0b", ink: "#0b0b0b", muted: "rgba(11,11,11,0.55)", line: "rgba(11,11,11,0.3)", dark: true },
  whatsapp: { tag: "WhatsApp", bg: `radial-gradient(1000px 700px at 92% -8%, rgba(37,211,102,0.20), transparent 58%), radial-gradient(800px 700px at -5% 105%, rgba(37,211,102,0.08), transparent 55%), #0b141a`, accent: "#25D366", ink: "#f4f2ee", muted: "rgba(244,242,238,0.55)", line: "rgba(255,255,255,0.13)", dark: false },
  wikipedia: { tag: "Wikipedia", bg: `#f8f7f2`, accent: "#3366cc", ink: "#202122", muted: "rgba(32,33,34,0.55)", line: "rgba(32,33,34,0.28)", dark: true, priceColor: "#3366cc" },
  google: { tag: "Google", bg: `radial-gradient(1000px 700px at 92% -8%, rgba(66,133,244,0.10), transparent 58%), #f8f9fa`, accent: "#4285F4", ink: "#202124", muted: "rgba(32,33,36,0.55)", line: "rgba(32,33,36,0.22)", dark: true, priceColor: "#4285F4" },
  uber: { tag: "Uber", bg: `radial-gradient(1000px 700px at 90% -8%, rgba(255,255,255,0.06), transparent 58%), #000000`, accent: "#ffffff", ink: "#ffffff", muted: "rgba(255,255,255,0.5)", line: "rgba(255,255,255,0.16)", dark: false },
  house: { tag: "ALTR Services", bg: `radial-gradient(1000px 700px at 90% -5%, rgba(182,242,229,0.14), transparent 60%), #1D1D1B`, accent: "#B6F2E5", ink: "#EBECDC", muted: "rgba(235,236,220,0.55)", line: "rgba(255,255,255,0.13)", dark: false },
};

function offerHtml(o) {
  const platform = String(o.platform ?? "house").toLowerCase();
  const t = THEMES[platform] ?? THEMES.house;
  const rows = Object.entries(o.details ?? {})
    .map(([k, v]) => `<div class="row"><span class="k">${esc(k)}</span><span class="v">${esc(v)}</span></div>`)
    .join("\n");
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;800&family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<style>
* { margin: 0; box-sizing: border-box; }
body { width: 1080px; height: 1080px; overflow: hidden; font-family: "Archivo", sans-serif; -webkit-font-smoothing: antialiased; }
.card { position: relative; width: 1080px; height: 1080px; display: flex; flex-direction: column; overflow: hidden; background: ${t.bg}; color: ${t.ink}; }
.card::after { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: 0.5; z-index: 6;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.05 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E"); }
.glyph { position: absolute; right: -110px; bottom: -120px; opacity: ${["snapchat", "wikipedia"].includes(platform) ? 0.14 : 0.18}; z-index: 0; }
.brand-band { position: relative; z-index: 4; display: flex; align-items: center; padding: 30px 54px; border-bottom: ${t.dark ? "3px solid #0b0b0b" : `1px solid ${t.line}`}; }
.brand-wordmark { height: 46px; display: block; }
.brand-division { margin-left: auto; font-family: "JetBrains Mono", monospace; font-size: 21px; font-weight: 700; letter-spacing: 0.28em; color: ${t.muted}; text-transform: uppercase; }
main { position: relative; z-index: 4; flex: 1; display: flex; flex-direction: column; padding: 48px 54px 30px; overflow: hidden; }
main > * { flex-shrink: 0; }
.platform-tag { display: flex; align-items: center; gap: 16px; font-family: "JetBrains Mono", monospace; font-size: 24px; font-weight: 800; letter-spacing: 0.42em; text-transform: uppercase; color: ${t.accent}; }
.platform-tag .tick { flex: 0 0 44px; height: 3px; background: ${t.accent}; }
.service { margin-top: 20px; font-family: "Unbounded", sans-serif; font-weight: 800; font-size: 84px; line-height: 1.0; text-transform: uppercase;
  ${t.gradientText ? `background: ${t.gradientText}; -webkit-background-clip: text; background-clip: text; color: transparent;` : ""} }
.desc { margin-top: 18px; font-size: 30px; font-weight: 500; color: ${t.muted}; }
.hero { margin-top: 44px; display: flex; align-items: flex-end; gap: 44px; width: 100%; }
.price-block { flex: 1 1 auto; min-width: 0; overflow: hidden; }
.tat-block { flex: 0 0 auto; }
.price-block .label, .tat-block .label { font-family: "JetBrains Mono", monospace; font-size: 20px; font-weight: 800; letter-spacing: 0.34em; text-transform: uppercase; color: ${t.muted}; margin-bottom: 10px; }
.price { font-family: "Unbounded", sans-serif; font-weight: 800; font-size: 120px; line-height: 1; color: ${t.priceColor ?? (t.dark ? "#0b0b0b" : t.accent)}; white-space: nowrap; }
.price small { font-size: 44px; font-weight: 700; color: ${t.muted}; margin-left: 8px; }
.tat-block { padding-bottom: 8px; }
.tat { display: inline-flex; align-items: center; gap: 14px; padding: 14px 28px; border-radius: 999px; border: 3px solid ${t.dark ? "#0b0b0b" : t.accent}; font-family: "Unbounded", sans-serif; font-weight: 700; font-size: 34px; text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
.tat .dot { width: 16px; height: 16px; border-radius: 50%; background: ${t.dark ? "#0b0b0b" : t.accent}; box-shadow: 0 0 18px ${t.dark ? "transparent" : t.accent}; }
.tiers { margin-top: 44px; display: flex; gap: 32px; width: 100%; }
.tier { flex: 1 1 0; min-width: 0; overflow: hidden; border: 1.5px solid ${t.line}; border-radius: 24px; padding: 30px 34px 34px; background: rgba(255,255,255,${t.dark ? "0.35" : "0.03"}); }
.tier .label { font-family: "JetBrains Mono", monospace; font-size: 20px; font-weight: 800; letter-spacing: 0.34em; text-transform: uppercase; color: ${t.dark ? "#0b0b0b" : t.accent}; margin-bottom: 14px; }
.tier .tier-price { font-family: "Unbounded", sans-serif; font-weight: 800; font-size: 84px; line-height: 1; color: ${t.dark ? "#0b0b0b" : t.ink}; white-space: nowrap; }
.tier .tat { margin-top: 22px; font-size: 27px; padding: 10px 22px; border-width: 2.5px; }
.rows { margin-top: 44px; border-top: 1px solid ${t.line}; }
.row { display: flex; align-items: baseline; gap: 30px; padding: 16px 0; border-bottom: 1px solid ${t.line}; }
.row .k { flex: 0 0 260px; font-family: "JetBrains Mono", monospace; font-size: 21px; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: ${t.muted}; }
.row .v { font-size: 31px; font-weight: 600; }
.notes { margin-top: 26px; font-size: 26px; line-height: 1.45; color: ${t.muted}; }
.notes strong { color: ${t.ink}; }
.brand-foot { position: relative; z-index: 4; display: flex; align-items: center; justify-content: space-between; padding: 24px 54px; border-top: ${t.dark ? "3px solid #0b0b0b" : `1px solid ${t.line}`}; font-family: "JetBrains Mono", monospace; font-size: 20px; font-weight: 700; letter-spacing: 0.26em; text-transform: uppercase; color: ${t.muted}; }
.foot-brand { display: flex; align-items: center; gap: 18px; }
.foot-monogram { height: 32px; opacity: 0.92; }
</style></head>
<body><div class="card">
  ${GLYPHS[platform] ?? GLYPHS.house}
  <header class="brand-band">
    <img class="brand-wordmark" src="${t.dark ? wordmarkDark : wordmarkLight}">
    <div class="brand-division">${esc(o.division ?? "Marketplace")}</div>
  </header>
  <main>
    <div class="platform-tag"><span class="tick"></span>${esc(t.tag)}</div>
    <h1 class="service">${esc(o.service ?? "")}</h1>
    ${o.description ? `<div class="desc">${esc(o.description)}</div>` : ""}
    ${Array.isArray(o.tiers) && o.tiers.length
      ? `<div class="tiers">${o.tiers
          .map(
            (tier) => `<div class="tier">
              <div class="label">${esc(tier.label ?? "")}</div>
              <div class="tier-price">${esc(tier.price ?? "")}${tier.priceNote ? `<small>${esc(tier.priceNote)}</small>` : ""}</div>
              <div class="tat"><span class="dot"></span>${esc(tier.tat ?? "")}</div>
            </div>`
          )
          .join("")}</div>`
      : `<div class="hero">
      <div class="price-block">
        <div class="label">${esc(o.priceLabel || "Price")}</div>
        <div class="price">${esc(o.price ?? "")}${o.priceNote ? `<small>${esc(o.priceNote)}</small>` : ""}</div>
      </div>
      <div class="tat-block">
        <div class="label">Turnaround</div>
        <div class="tat"><span class="dot"></span>${esc(o.tat ?? "")}</div>
      </div>
    </div>`}
    ${rows ? `<div class="rows">${rows}</div>` : ""}
    ${o.notes ? `<div class="notes"><strong>Note.</strong> ${esc(o.notes)}</div>` : ""}
  </main>
  <footer class="brand-foot">
    <span class="foot-brand"><img class="foot-monogram" src="${t.dark ? monogramDark : monogramLight}">${esc(brand.tagline)}</span>
    <span>${esc(o.footRight ?? "Offer")}</span>
  </footer>
</div></body></html>`;
}

const files = process.argv.slice(2);
if (!files.length) {
  console.error("Usage: node offers.mjs offers/<offer>.json [more.json ...]");
  process.exit(1);
}
await mkdir(join(ROOT, "output", "offers"), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 2 });
try {
  for (const file of files) {
    const offer = JSON.parse(await readFile(resolve(file), "utf8"));
    const tmp = join(tmpdir(), `offer-${Date.now()}-${Math.random().toString(36).slice(2)}.html`);
    await writeFile(tmp, offerHtml(offer));
    await page.goto(`file://${tmp}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    // shrink long titles/prices to fit
    await page.evaluate(() => {
      for (const el of document.querySelectorAll(".service, .price, .tier-price")) {
        let fs = parseFloat(getComputedStyle(el).fontSize);
        while (el.scrollWidth > el.clientWidth && fs > 36) {
          fs -= 4;
          el.style.fontSize = `${fs}px`;
        }
      }
    });
    const out = join(ROOT, "output", "offers", basename(file).replace(/\.json$/i, "") + ".png");
    await page.screenshot({ path: out });
    console.log(`✓ ${out}`);
    if (offer.pdf) {
      await page.emulateMedia({ media: "screen" });
      const pdfOut = out.replace(/\.png$/, ".pdf");
      await page.pdf({ path: pdfOut, width: "1080px", height: "1080px", printBackground: true, pageRanges: "1" });
      console.log(`✓ ${pdfOut}`);
    }
    await rm(tmp, { force: true });
  }
} finally {
  await browser.close();
}
