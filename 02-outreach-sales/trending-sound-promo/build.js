#!/usr/bin/env node
/* ALTR · IG Trending Sound Promo — one-pagers
 *
 * Builds two Letter one-pagers (wholesale/reseller + artist/label) from one
 * shared spec, so the sheets cannot drift apart. HTML -> headless Chrome ->
 * PDF, the same route the 2026 pitch decks were rendered with.
 *
 *   node build.js
 */
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");

const DIR = __dirname;
const BUILD = path.join(DIR, ".build");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
fs.mkdirSync(BUILD, { recursive: true });

/* ---------- contact: change in one place, both sheets follow ---------- */
const CONTACT = { email: "derrek@altrmgmt.com", url: "quote.altrservices.com" };

/* ---------- deliverables are identical across both audiences ---------- */
const SPEC = [
  {
    rank: "Top 20 Guaranteed",
    items: ["<b>3,000</b> Reels", "<b>500</b> story reposts of the artist's video", "<b>500</b> story notes · 24 hrs"],
  },
  {
    rank: "Top 10 Guaranteed",
    items: ["<b>5,000</b> Reels", "<b>All pages</b> story reposts", "<b>All</b> story notes · 24 hrs"],
  },
  {
    rank: "Top 5 Guaranteed",
    items: ["<b>7,000</b> Reels, run across 5 days", "<b>All pages</b> story reposts", "<b>All</b> story notes · 24 hrs"],
    flag: true,
    tag: "The full network, five days",
  },
];

const SHEETS = [
  {
    file: "ALTR-Trending-Sound-Promo-Wholesale.pdf",
    chip: "Wholesale · Resellers",
    rate: "Wholesale & reseller rates",
    prices: ["$2,000", "$3,000", "$4,000"],
  },
  {
    file: "ALTR-Trending-Sound-Promo-Artists.pdf",
    chip: "Artists · Labels",
    rate: "Artist & label rates",
    prices: ["$3,000", "$4,000", "$5,500"],
  },
];

const RUN = [
  ["01", "Sound locked", "You bring the track. Tier and start date set."],
  ["02", "Days 1–5", "Reels roll across the network. Story reposts and notes run in the first 24 hrs."],
  ["03", "Day 3+", "Chart position becomes visible — Instagram's trending data runs about three days behind."],
  ["04", "On delivery", "Proof pack plus a reel-by-reel report, verified in Chartmetric."],
];

const KNOW = [
  ["The chart runs three days behind",
   "Instagram's trending data is roughly 72 hours late, so a placement will not appear before day three of a five-day run — the push is working before the chart says so."],
  ["Audio level is set per theme",
   "The sound goes under content on thousands of built-up theme pages. Where the original audio carries the video — a comedy page where the joke has to land — the music sits lower. Forcing it up kills the reel, and a dead reel does not chart."],
  ["There is more than one US chart",
   "Instagram serves several trending charts in the States, so a placement may not show on the one you see. Proof is supplied either way."],
  ["Every run is reported",
   "A reel-by-reel report on every placement delivered, with results verified independently in <em>Chartmetric</em>."],
];

const esc = (s) => s;

const page = (sheet) => `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>ALTR Media · IG Trending Sound Promo · ${sheet.chip}</title>
<link rel="stylesheet" href="../style.css">
</head><body>
<div class="bg"><span class="orbit a"></span><span class="orbit b"></span></div>
<span class="bracket tl"></span><span class="bracket tr"></span>
<span class="bracket bl"></span><span class="bracket br"></span>

<header>
  <div class="id">
    <div class="dot"><span>A</span></div>
    <div class="t">
      <span class="one">ALTR &nbsp;|&nbsp; Media</span>
      <span class="two">IG Trending Sound Promo &nbsp;·&nbsp; 2026</span>
    </div>
  </div>
  <div class="chip">${sheet.chip}</div>
</header>

<section class="hero">
  <h1>Guaranteed placement.<br><em>On pages we own.</em></h1>
  <p>Top 20, Top 10 or Top 5 on Instagram's Trending Sound chart — pushed across thousands of
  built-up theme pages in the ALTR network. <b>No ad spend, no rented inventory.</b></p>
</section>

<div class="stats">
  <div class="stat"><b>2,000+</b><span>owned pages</span></div>
  <div class="stat"><b>5 days</b><span>full run</span></div>
  <div class="stat"><b>Guaranteed</b><span>chart placement</span></div>
  <div class="stat"><b>Chartmetric</b><span>verified reporting</span></div>
</div>

<div class="lbl"><span>Pricing</span><b>${sheet.rate}</b></div>
<div class="tiers">
${SPEC.map((t, i) => `  <div class="tier${t.flag ? " flag" : ""}">
    <div class="rank">${t.rank}</div>
    <div class="price">${sheet.prices[i]}</div>
    <div class="per">per campaign</div>
    <ul>${t.items.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    ${t.tag ? `<div class="tag">${t.tag}</div>` : ""}
  </div>`).join("\n")}
</div>

<div class="lbl" style="margin-top:8mm"><span>How the push runs</span><b>~5 days end to end</b></div>
<div class="run">
${RUN.map(([n, h, p]) => `  <div class="step"><div class="n">${n}</div><h3>${h}</h3><p>${p}</p></div>`).join("\n")}
</div>

<div class="lbl" style="margin-top:8mm"><span>What to know before you book</span><b>Set expectations once</b></div>
<div class="know">
${KNOW.map(([h, p]) => `  <div><h3>${h}</h3><p>${p}</p></div>`).join("\n")}
</div>

<div class="close">
  <div class="cta">
    <div class="btn">${CONTACT.email}</div>
    <div class="alt">${CONTACT.url}</div>
  </div>
  <div class="foot">
    <div>ALTR &nbsp;|&nbsp; Media &nbsp;·&nbsp; ${sheet.chip}</div>
    <div class="hatch">//////</div>
  </div>
</div>
</body></html>`;

let overflow = false;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ["--no-sandbox", "--font-render-hinting=none"],
  });
  for (const sheet of SHEETS) {
    const src = path.join(BUILD, sheet.file.replace(/\.pdf$/, ".html"));
    fs.writeFileSync(src, page(sheet));
    const tab = await browser.newPage();
    await tab.setCacheEnabled(false);
    await tab.goto("file://" + src, { waitUntil: "networkidle0" });
    await tab.evaluateHandle("document.fonts.ready");
    await tab.emulateMediaType("print");
    const fit = await tab.evaluate(() => {
      const know = document.querySelector(".know").getBoundingClientRect();
      const close = document.querySelector(".close").getBoundingClientRect();
      return {
        content: document.documentElement.scrollHeight,
        page: document.body.getBoundingClientRect().height,
        slack: Math.round(close.top - know.bottom),
      };
    });
    if (fit.content > fit.page + 1) {
      console.error(
        `  !! ${sheet.file}: content is ${fit.content - fit.page}px taller than the page ` +
        `(${fit.content} vs ${fit.page}). Chrome will shrink-to-fit — tighten style.css.`
      );
      overflow = true;
    }
    await tab.pdf({
      path: path.join(DIR, sheet.file),
      printBackground: true, preferCSSPageSize: true, tagged: true,
    });
    await tab.close();
    const kb = (fs.statSync(path.join(DIR, sheet.file)).size / 1024).toFixed(0);
    console.log(`wrote ${sheet.file} (${kb} KB) — ${fit.slack}px slack above the footer`);
  }
  await browser.close();
  if (overflow) process.exitCode = 1;
  else console.log("both sheets fit one page at 1:1");
})();
