// ALTR Media Bundles — 2026 pricing deck (+15% applied to all bundle pricing)
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
pres.author = "ALTR Management";
pres.title = "ALTR Media Bundles — 2026 Pricing";

const W = 10, H = 5.625;
const C = {
  bg: "EBECDC", ink: "1D1D1B", mint: "B6F2E5", teal: "6BB6A3",
  sage: "BCCBC0", purple: "7C41F1", ivory: "FFFFF0", mute: "6F6F68",
};
const F = { head: "Bricolage Grotesque ExtraBold", body: "Space Mono" };
const RECT = pres.shapes.RECTANGLE, LINE = pres.shapes.LINE;

// ---------- pricing ----------
const UPLIFT_PCT = 15;
// exact integer math, then round to nearest $10
const up = (v) => (v == null ? null : Math.round((v * (100 + UPLIFT_PCT)) / 1000) * 10);
const money = (v) => "$" + v.toLocaleString("en-US");

// price / retail are the ORIGINAL sheet values; uplift is applied at render time.
const PACKAGES = [
  { name: "Beginner", blurb: "Entry-level placements for founders and brands establishing a first press footprint.",
    tiers: [
      { price: 1425, retail: 1550, outlets: ["Yahoo Finance", "California Business Journal", "Digital Journal"] },
      { price: 3250, retail: 3750, outlets: ["Yahoo Finance", "California Business Journal", "Digital Journal", "LA Weekly", "Haute Living"] },
      { price: 5750, retail: 6450, outlets: ["Digital Journal", "LA Weekly", "Haute Living", "Hollywood Life", "USA Today"] },
    ] },
  { name: "Influencer", blurb: "Lifestyle and entertainment coverage for creators building mainstream visibility.",
    tiers: [
      { price: 2400, retail: 2900, outlets: ["Cultr Magazine", "Flaunt Magazine", "Hollywood Life"] },
      { price: 5900, retail: 6600, outlets: ["Cultr Magazine", "Flaunt Magazine", "Hollywood Life", "Hollywood Unlocked", "OK! Magazine"] },
      { price: 11500, retail: 12700, outlets: ["Hollywood Life", "Hollywood Unlocked", "OK! Magazine", "Bustle", "US Weekly"] },
    ] },
  { name: "Crypto", blurb: "Sector-native outlets for Web3 projects, tokens, exchanges and founders.",
    tiers: [
      { price: 3900, retail: 4200, outlets: ["CryptoSlate", "Cryptopolitan", "CoinGape"] },
      { price: 8100, retail: 9200, outlets: ["CryptoSlate", "Cryptopolitan", "CoinGape", "Decrypt", "CoinCodex"] },
      { price: 10100, retail: 11700, outlets: ["Bitcoin.com (Sponsored)", "Decrypt", "CryptoSlate", "Cryptopolitan", "CoinCodex"] },
    ] },
  { name: "Corporate", blurb: "Business and finance press for executives and established companies.",
    tiers: [
      { price: null, retail: 1800, outlets: ["Financial Tech Times", "California Business Journal", "CEO World Biz"] },
      { price: null, retail: 2600, outlets: ["Financial Tech Times", "California Business Journal", "CEO World Biz", "Benzinga", "BizJournals.com"] },
      { price: null, retail: 8600, outlets: ["Financial Tech Times", "California Business Journal", "CEO World Biz", "Benzinga", "BizJournals.com", "Investing.com", "Digital Trends"] },
    ] },
  { name: "Entrepreneur", blurb: "Founder-focused features across business, lifestyle and regional press.",
    tiers: [
      { price: null, retail: 3250, outlets: ["CEO Weekly", "Digital Journal (Contributor)", "California Business Journal", "LA Magazine", "Miami Herald"] },
      { price: null, retail: 9250, outlets: ["CEO Weekly", "Digital Journal (Contributor)", "California Business Journal", "LA Magazine", "Miami Herald", "BizJournals.com", "Investing.com"] },
      { price: null, retail: 12750, outlets: ["CEO Weekly", "Digital Journal (Contributor)", "California Business Journal", "LA Magazine", "Miami Herald", "BizJournals.com", "Investing.com"] },
    ] },
  { name: "Musician", blurb: "Music and culture coverage for artists, releases and tours.",
    tiers: [
      { price: 1900, retail: 2100, outlets: ["The Source", "Notion Online", "Flaunt Magazine"] },
      { price: 3900, retail: 4600, outlets: ["The Source", "Notion Online", "Flaunt Magazine", "Galore Magazine", "Spin.com"] },
      { price: 7000, retail: 8200, outlets: ["Flaunt Magazine", "Galore Magazine", "Spin.com", "Paste Magazine", "Rolling Stone (MENA)"] },
    ] },
  { name: "Organic", sub: "No Disclaimers", blurb: "Editorial placements that run without sponsored or paid-content disclaimers.",
    tiers: [
      { price: 1900, retail: 2050, outlets: ["The Source", "Digital Journal", "Grit Daily"] },
      { price: null, retail: 4550, outlets: ["The Source", "Digital Journal", "Grit Daily", "Benzinga", "LA Magazine"] },
      { price: null, retail: 8050, outlets: ["The Source", "Digital Journal", "Grit Daily", "Benzinga", "LA Magazine", "Hollywood Life", "OK! Magazine"] },
    ] },
  { name: "Fashion", blurb: "Style and culture outlets for designers, labels and fashion creators.",
    tiers: [
      { price: 2000, retail: 2200, outlets: ["Broke & Chic", "Flaunt Magazine", "Galore Magazine"] },
      { price: 3900, retail: 4300, outlets: ["Broke & Chic", "Flaunt Magazine", "Galore Magazine", "Fashion Week Daily", "Wonderwall.com"] },
      { price: 10500, retail: 11600, outlets: ["Galore Magazine", "Fashion Week Daily", "Wonderwall.com", "Bustle", "WWD"] },
    ] },
];
const ACCENTS = [C.mint, C.teal, C.purple, C.sage];

// ---------- brand frame ----------
const FX = 0.12, FY = 0.12, FR = W - 0.12, FB = H - 0.12; // frame bounds
const RAIL = 0.5;                                         // left rail right edge
const CX = 0.78, CR = 9.62;                               // content x bounds

function frame(slide, dark) {
  const lc = dark ? C.ivory : C.ink;
  slide.background = { color: dark ? C.ink : C.bg };
  slide.addShape(RECT, { x: FX, y: FY, w: FR - FX, h: FB - FY, fill: { type: "none" }, line: { color: lc, width: 0.75 } });
  slide.addShape(LINE, { x: RAIL, y: FY, w: 0, h: FB - FY, line: { color: lc, width: 0.75 } });
  // rotated rail text
  const cx = (FX + RAIL) / 2, cy = H / 2, tw = 4.6, th = 0.3;
  slide.addText("ALTR   |   MEDIA BUNDLES   |   2026 PRICING", {
    x: cx - tw / 2, y: cy - th / 2, w: tw, h: th, rotate: 270,
    fontFace: F.body, fontSize: 6.5, color: lc, align: "center", valign: "middle", charSpacing: 3, margin: 0,
  });
}

function stripes(slide, x0, x1, color, count, len) {
  // parallel 45° bars, clipped later by masks
  const step = (x1 - x0) / count;
  for (let i = 0; i < count; i++) {
    const cx = x0 + step * (i + 0.5), cy = H / 2, bw = 0.16, bh = len;
    slide.addShape(RECT, { x: cx - bw / 2, y: cy - bh / 2, w: bw, h: bh, rotate: 45, fill: { color }, line: { color, width: 0 } });
  }
}
function maskOutsideFrame(slide, color) {
  slide.addShape(RECT, { x: 0, y: 0, w: W, h: FY, fill: { color }, line: { color, width: 0 } });
  slide.addShape(RECT, { x: 0, y: FB, w: W, h: H - FB, fill: { color }, line: { color, width: 0 } });
  slide.addShape(RECT, { x: FR, y: 0, w: W - FR, h: H, fill: { color }, line: { color, width: 0 } });
}

// ---------- 1. cover ----------
{
  const s = pres.addSlide();
  s.background = { color: C.ink };
  const SPLIT = 5.55;
  // stripes region (right of split), masked to frame
  s.addShape(RECT, { x: SPLIT, y: FY, w: FR - SPLIT, h: FB - FY, fill: { color: C.ink }, line: { color: C.ink, width: 0 } });
  stripes(s, SPLIT + 0.2, FR + 1.2, C.mint, 9, 7.5);
  s.addShape(RECT, { x: 0, y: 0, w: SPLIT, h: H, fill: { color: C.ink }, line: { color: C.ink, width: 0 } });
  maskOutsideFrame(s, C.ink);
  frame(s, true);
  s.addShape(LINE, { x: SPLIT, y: FY, w: 0, h: FB - FY, line: { color: C.ivory, width: 0.75 } });

  // top index cells
  const cells = [["01", "Overview"], ["02", "Packages"], ["03", "Summary"], ["04", "Contact"]];
  const cw = (SPLIT - RAIL) / 4;
  s.addShape(LINE, { x: RAIL, y: 1.55, w: SPLIT - RAIL, h: 0, line: { color: C.ivory, width: 0.75 } });
  cells.forEach(([n, t], i) => {
    const x = RAIL + cw * i;
    if (i > 0) s.addShape(LINE, { x, y: FY, w: 0, h: 1.55 - FY, line: { color: C.ivory, width: 0.75 } });
    s.addText(n, { x: x + 0.18, y: 0.72, w: cw - 0.3, h: 0.4, fontFace: F.head, fontSize: 20, color: C.bg, margin: 0 });
    s.addText(t.toUpperCase(), { x: x + 0.18, y: 1.12, w: cw - 0.3, h: 0.25, fontFace: F.body, fontSize: 7, color: C.bg, charSpacing: 2, margin: 0 });
  });

  s.addText("MEDIA PLACEMENT BUNDLES", { x: CX, y: 2.05, w: 4.5, h: 0.3, fontFace: F.body, fontSize: 8.5, color: C.mint, charSpacing: 3, margin: 0 });
  s.addText("2026 Pricing", { x: CX, y: 2.35, w: 4.5, h: 0.5, fontFace: F.body, fontSize: 12, color: C.bg, margin: 0 });
  s.addText("ALTR", { x: CX - 0.05, y: 3.25, w: 4.7, h: 1.9, fontFace: F.head, fontSize: 118, color: C.bg, margin: 0, valign: "bottom", charSpacing: -6 });
}

// ---------- 2. overview ----------
{
  const s = pres.addSlide();
  frame(s, false);
  s.addText("MEDIA BUNDLES", { x: CX, y: 0.3, w: 5.4, h: 0.95, fontFace: F.head, fontSize: 40, color: C.ink, margin: 0, valign: "middle", charSpacing: -2 });
  s.addText("Eight packages, three tiers each. Every bundle is a curated set of placements across the outlets your audience already reads — priced below the combined retail value of the individual placements.",
    { x: 6.2, y: 0.32, w: 3.35, h: 0.95, fontFace: F.body, fontSize: 7.5, color: C.ink, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });
  s.addShape(LINE, { x: RAIL, y: 1.4, w: FR - RAIL, h: 0, line: { color: C.ink, width: 0.75 } });

  // 4x2 index grid
  const gx = CX, gy = 1.7, gw = CR - CX, gh = 2.75, cols = 4, rows = 2;
  const cw = gw / cols, ch = gh / rows;
  PACKAGES.forEach((p, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = gx + c * cw, y = gy + r * ch;
    s.addShape(RECT, { x, y, w: cw, h: ch, fill: { type: "none" }, line: { color: C.ink, width: 0.75 } });
    s.addShape(RECT, { x: x + 0.18, y: y + 0.18, w: 0.32, h: 0.32, fill: { color: ACCENTS[i % 4] }, line: { color: C.ink, width: 0.5 } });
    s.addText(String(i + 1).padStart(2, "0") + (p.sub ? "  ·  " + p.sub.toUpperCase() : ""),
      { x: x + 0.58, y: y + 0.18, w: cw - 0.62, h: 0.32, fontFace: F.body, fontSize: p.sub ? 6.5 : 9, color: C.ink, margin: 0, valign: "middle", wrap: false });
    s.addText(p.name.toUpperCase(), { x: x + 0.18, y: y + ch - 0.72, w: cw - 0.3, h: 0.36, fontFace: F.head, fontSize: 15, color: C.ink, margin: 0, valign: "bottom", charSpacing: -1 });
    const from = p.tiers.map((t) => up(t.price)).filter((v) => v != null);
    s.addText(from.length ? "FROM " + money(Math.min(...from)) : "PRICING ON REQUEST",
      { x: x + 0.18, y: y + ch - 0.36, w: cw - 0.3, h: 0.22, fontFace: F.body, fontSize: 6.5, color: C.mute, charSpacing: 1.5, margin: 0 });
  });

  // stat strip — number with label beneath, one third each
  const stats = [["3,000+", "INSTAGRAM THEME PAGES"], ["55M", "COMBINED FOLLOWERS"], ["15B", "ORGANIC MONTHLY VIEWS"]];
  const sy = 4.66, sw = (CR - CX) / 3;
  stats.forEach(([n, l], i) => {
    const x = CX + sw * i;
    if (i > 0) s.addShape(LINE, { x: x - 0.25, y: sy + 0.02, w: 0, h: 0.6, line: { color: C.sage, width: 0.75 } });
    s.addText(n, { x, y: sy, w: sw - 0.5, h: 0.38, fontFace: F.head, fontSize: 22, color: C.ink, margin: 0, valign: "middle" });
    s.addText(l, { x, y: sy + 0.4, w: sw - 0.5, h: 0.2, fontFace: F.body, fontSize: 6.5, color: C.mute, charSpacing: 1.5, margin: 0, valign: "middle" });
  });
}

// ---------- 3–10. package slides ----------
function card(s, x, y, w, h, tierIdx, tier, dark, accent) {
  const fill = dark ? C.ink : C.ivory;
  const fg = dark ? C.bg : C.ink;
  const price = up(tier.price), retail = up(tier.retail);
  s.addShape(RECT, { x, y, w, h, fill: { color: fill }, line: { color: C.ink, width: 0.75 } });
  const px = x + 0.22, pw = w - 0.44;
  s.addText(`BUNDLE ${String(tierIdx + 1).padStart(2, "0")}`, { x: px, y: y + 0.2, w: pw, h: 0.22, fontFace: F.body, fontSize: 7.5, color: dark ? C.mint : C.mute, charSpacing: 2.5, margin: 0 });
  if (price != null) {
    s.addText(money(price), { x: px, y: y + 0.44, w: pw, h: 0.62, fontFace: F.head, fontSize: 30, color: fg, margin: 0, valign: "middle", charSpacing: -1 });
    s.addText([
      { text: "RETAIL VALUE  ", options: { color: dark ? C.sage : C.mute } },
      { text: money(retail), options: { color: fg, strike: true } },
    ], { x: px, y: y + 1.1, w: pw, h: 0.22, fontFace: F.body, fontSize: 7.5, charSpacing: 1, margin: 0 });
    const save = retail - price;
    const pillW = 1.35;
    s.addShape(RECT, { x: px, y: y + 1.42, w: pillW, h: 0.28, fill: { color: accent }, line: { color: dark ? accent : C.ink, width: 0.5 } });
    s.addText(`YOU SAVE ${money(save)}`, { x: px, y: y + 1.42, w: pillW, h: 0.28, fontFace: F.body, fontSize: 7, color: accent === C.purple ? C.ivory : C.ink, charSpacing: 1, margin: 0, align: "center", valign: "middle", bold: true });
  } else {
    s.addText("Pricing on request", { x: px, y: y + 0.44, w: pw, h: 0.62, fontFace: F.head, fontSize: 17, color: fg, margin: 0, valign: "middle" });
    s.addText([
      { text: "RETAIL VALUE  ", options: { color: dark ? C.sage : C.mute } },
      { text: money(retail), options: { color: fg } },
    ], { x: px, y: y + 1.1, w: pw, h: 0.22, fontFace: F.body, fontSize: 7.5, charSpacing: 1, margin: 0 });
    s.addShape(RECT, { x: px, y: y + 1.42, w: 1.35, h: 0.28, fill: { type: "none" }, line: { color: dark ? C.sage : C.ink, width: 0.5 } });
    s.addText("CONTACT ALTR", { x: px, y: y + 1.42, w: 1.35, h: 0.28, fontFace: F.body, fontSize: 7, color: fg, charSpacing: 1, margin: 0, align: "center", valign: "middle" });
  }
  s.addShape(LINE, { x: px, y: y + 1.92, w: pw, h: 0, line: { color: dark ? C.sage : C.ink, width: 0.5 } });
  s.addText("INCLUDED PLACEMENTS", { x: px, y: y + 2.02, w: pw, h: 0.2, fontFace: F.body, fontSize: 6.5, color: dark ? C.sage : C.mute, charSpacing: 2, margin: 0 });
  s.addText(tier.outlets.map((o, i) => ({ text: o, options: { breakLine: i < tier.outlets.length - 1 } })),
    { x: px, y: y + 2.26, w: pw, h: h - 2.36, fontFace: F.body, fontSize: 8.5, color: fg, margin: 0, valign: "top", paraSpaceAfter: 2.5 });
}

PACKAGES.forEach((p, i) => {
  const s = pres.addSlide();
  frame(s, false);
  const accent = ACCENTS[i % 4];
  const num = String(i + 1).padStart(2, "0");
  // header
  s.addShape(RECT, { x: CX, y: 0.36, w: 0.5, h: 0.5, fill: { color: accent }, line: { color: C.ink, width: 0.5 } });
  s.addText(num, { x: CX, y: 0.36, w: 0.5, h: 0.5, fontFace: F.body, fontSize: 9, color: accent === C.purple ? C.ivory : C.ink, margin: 0, align: "center", valign: "middle", bold: true });
  s.addText(p.name.toUpperCase(), { x: CX + 0.68, y: 0.3, w: 4.6, h: 0.62, fontFace: F.head, fontSize: 34, color: C.ink, margin: 0, valign: "middle", charSpacing: -2 });
  if (p.sub) s.addText(p.sub.toUpperCase(), { x: CX + 0.68, y: 0.92, w: 4.6, h: 0.22, fontFace: F.body, fontSize: 7.5, color: C.mute, charSpacing: 2.5, margin: 0 });
  s.addText(p.blurb, { x: 6.35, y: 0.32, w: 3.2, h: 0.85, fontFace: F.body, fontSize: 7.5, color: C.ink, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });
  s.addShape(LINE, { x: RAIL, y: 1.28, w: FR - RAIL, h: 0, line: { color: C.ink, width: 0.75 } });

  // three tier cards — bundle 3 is the dark flagship
  const gap = 0.18, cy = 1.52, ch = 3.68;
  const cw = (CR - CX - gap * 2) / 3;
  p.tiers.forEach((t, k) => card(s, CX + k * (cw + gap), cy, cw, ch, k, t, k === 2, accent));

  s.addText("All prices USD. Retail value reflects the combined individual rate of the included placements.", { x: CX, y: 5.26, w: 6.5, h: 0.2, fontFace: F.body, fontSize: 6, color: C.mute, margin: 0, valign: "middle" });
  s.addText(`${num} / ${String(PACKAGES.length).padStart(2, "0")}`, { x: CR - 1.2, y: 5.26, w: 1.2, h: 0.2, fontFace: F.body, fontSize: 6, color: C.mute, margin: 0, align: "right", valign: "middle" });
});

// ---------- 11. summary table ----------
{
  const s = pres.addSlide();
  frame(s, false);
  s.addText("PRICING SUMMARY", { x: CX, y: 0.3, w: 5.4, h: 0.95, fontFace: F.head, fontSize: 40, color: C.ink, margin: 0, valign: "middle", charSpacing: -2 });
  s.addText("Bundle price shown bold; combined retail value of the included placements shown beneath. All prices USD.",
    { x: 6.35, y: 0.32, w: 3.2, h: 0.85, fontFace: F.body, fontSize: 7.5, color: C.ink, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });
  s.addShape(LINE, { x: RAIL, y: 1.4, w: FR - RAIL, h: 0, line: { color: C.ink, width: 0.75 } });

  const hdr = (t) => ({ text: t, options: { fontFace: F.body, fontSize: 7, color: C.bg, fill: { color: C.ink }, charSpacing: 2, bold: true, align: t === "PACKAGE" ? "left" : "center", valign: "middle" } });
  const rows = [[hdr("PACKAGE"), hdr("BUNDLE 01"), hdr("BUNDLE 02"), hdr("BUNDLE 03")]];
  PACKAGES.forEach((p, i) => {
    const name = { text: [
      { text: `${String(i + 1).padStart(2, "0")}  `, options: { fontFace: F.body, fontSize: 7, color: C.mute } },
      { text: p.name + (p.sub ? ` (${p.sub})` : ""), options: { fontFace: F.head, fontSize: 10.5, color: C.ink } },
    ], options: { align: "left", valign: "middle" } };
    const cells = p.tiers.map((t) => {
      const price = up(t.price), retail = up(t.retail);
      return { text: [
        { text: price != null ? money(price) : "On request", options: { fontFace: F.head, fontSize: 11.5, color: C.ink, breakLine: true } },
        { text: `RETAIL ${money(retail)}`, options: { fontFace: F.body, fontSize: 6.5, color: C.mute, charSpacing: 1 } },
      ], options: { align: "center", valign: "middle" } };
    });
    rows.push([name, ...cells]);
  });
  s.addTable(rows, {
    x: CX, y: 1.62, w: CR - CX, colW: [2.9, 1.98, 1.98, 1.98], rowH: [0.3, ...Array(8).fill(0.4)],
    border: { type: "solid", pt: 0.5, color: C.ink }, fill: { color: C.ivory }, margin: [0.03, 0.1, 0.03, 0.1],
  });
}

// ---------- 12. closing ----------
{
  const s = pres.addSlide();
  s.background = { color: C.ink };
  const SPLIT = 5.55;
  s.addShape(RECT, { x: SPLIT, y: FY, w: FR - SPLIT, h: FB - FY, fill: { color: C.ink }, line: { color: C.ink, width: 0 } });
  stripes(s, SPLIT + 0.2, FR + 1.2, C.purple, 9, 7.5);
  s.addShape(RECT, { x: 0, y: 0, w: SPLIT, h: H, fill: { color: C.ink }, line: { color: C.ink, width: 0 } });
  maskOutsideFrame(s, C.ink);
  frame(s, true);
  s.addShape(LINE, { x: SPLIT, y: FY, w: 0, h: FB - FY, line: { color: C.ivory, width: 0.75 } });

  s.addText("LET'S TALK", { x: CX, y: 0.5, w: 4.5, h: 0.3, fontFace: F.body, fontSize: 8.5, color: C.mint, charSpacing: 3, margin: 0 });
  s.addText("Ready to engineer your moment.", { x: CX, y: 0.85, w: 4.55, h: 1.6, fontFace: F.head, fontSize: 34, color: C.bg, margin: 0, valign: "top", charSpacing: -1.5, lineSpacingMultiple: 0.95 });
  const lines = [["EMAIL", "hi@altrmanagement.com"], ["WEB", "altrmanagement.com"], ["INSTAGRAM", "@altrmanagement"]];
  lines.forEach(([k, v], i) => {
    const y = 3.2 + i * 0.5;
    s.addShape(LINE, { x: CX, y, w: 4.5, h: 0, line: { color: C.sage, width: 0.5 } });
    s.addText(k, { x: CX, y: y + 0.08, w: 1.3, h: 0.3, fontFace: F.body, fontSize: 6.5, color: C.sage, charSpacing: 2, margin: 0, valign: "middle" });
    s.addText(v, { x: CX + 1.3, y: y + 0.08, w: 3.2, h: 0.3, fontFace: F.body, fontSize: 9.5, color: C.bg, margin: 0, valign: "middle" });
  });
  s.addText("ALTR", { x: CX - 0.03, y: 4.6, w: 3, h: 0.7, fontFace: F.head, fontSize: 40, color: C.bg, margin: 0, valign: "bottom", charSpacing: -2 });
}

const OUT = process.argv[2] || "ALTR-Media-Bundles-2026.pptx";
pres.writeFile({ fileName: OUT }).then(() => {
  console.log("wrote", OUT);
  // print pricing table for the summary
  console.log("\nPackage | Tier | Old price -> New price | Old retail -> New retail");
  PACKAGES.forEach((p) => p.tiers.forEach((t, k) =>
    console.log(`${p.name} | B${k + 1} | ${t.price == null ? "—" : money(t.price) + " -> " + money(up(t.price))} | ${money(t.retail)} -> ${money(up(t.retail))}`)));
});
