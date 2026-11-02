#!/usr/bin/env node
/* Render README.md -> ALTR-Pitch-Deck-Review.pdf
 *
 * pandoc (md -> html fragment) -> branded template -> headless Chrome -> PDF.
 * Same HTML -> Chrome -> Skia route the pitch decks themselves were rendered with.
 * Fonts (Bricolage Grotesque, Space Mono) resolve from ~/Library/Fonts by family name.
 *
 *   node build.js
 */
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");
const { PDFDocument } = require("pdf-lib");

const DIR = __dirname;
const BUILD = path.join(DIR, ".build");
const OUT = path.join(DIR, "ALTR-Pitch-Deck-Review.pdf");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

fs.mkdirSync(BUILD, { recursive: true });

// 1. markdown -> html fragment
const body = execFileSync(
  "pandoc",
  [path.join(DIR, "README.md"), "--from=gfm", "--to=html5", "--wrap=none"],
  { encoding: "utf8" }
);

// 2. pull the section headings for the cover contents strip
const contents = [...body.matchAll(/<h2[^>]*>(?:<[^>]+>)*([^<]+)/g)]
  .map((m) => m[1].trim())
  .map((t) => `<li>${t}</li>`)
  .join("");

const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>ALTR · Pitch Deck Review 2026</title>
<link rel="stylesheet" href="../style.css">
</head><body>

<section class="cover">
  <span class="bracket tl"></span><span class="bracket br"></span>
  <div class="eyebrow">ALTR &nbsp;·&nbsp; INTERNAL REVIEW &nbsp;·&nbsp; 2026</div>
  <div class="mark">ALTR</div>
  <div class="rule-row">${"<i></i>".repeat(16)}</div>
  <h1>Pitch Deck Review.<br><em>Management &amp; Media.</em></h1>
  <p class="deck">A read-only critique of the two 13-slide 2026 pitch decks.
  <strong>All 26 slides inspected as rendered images.</strong> Neither deck file was
  modified, compressed, or committed.</p>
  <ol class="contents">${contents}</ol>
  <div class="stats">
    <div><b>26</b><span>slides reviewed</span></div>
    <div><b>5</b><span>ship-stoppers</span></div>
    <div><b>13</b><span>prioritized fixes</span></div>
  </div>
  <div class="meta"><span>ALTR Management HQ &nbsp;·&nbsp; 02 Outreach &amp; Sales</span><span>2026-11-02</span></div>
</section>

<main class="doc">
${body}
</main></body></html>`;

// the cover is printed full-bleed in its own pass so Chrome's running footer
// (which cannot be suppressed per-page) never lands on it
const COVER_OVERRIDE = '<style>@page { size: Letter; margin: 0; }</style>';
const split = html.indexOf("<main class=\"doc\">");
const head = html.slice(0, html.indexOf("</head>"));
const coverHtml =
  head + COVER_OVERRIDE + "</head><body>" +
  html.slice(html.indexOf("<section class=\"cover\">"), split) +
  "</body></html>";
const bodyHtml =
  head + "</head><body>" + html.slice(split) ;

const coverPath = path.join(BUILD, "cover.html");
const bodyPath = path.join(BUILD, "body.html");
fs.writeFileSync(coverPath, coverHtml);
fs.writeFileSync(bodyPath, bodyHtml);

// 3. print to PDF
const FOOT = `
<div style="width:100%;margin:0 16mm;padding-top:2.2mm;border-top:.5pt solid #D6D7C6;
            font-family:'Space Mono',monospace;font-size:6.6pt;letter-spacing:.16em;
            text-transform:uppercase;color:#6F6F68;display:flex;justify-content:space-between;">
  <span>ALTR &nbsp;|&nbsp; Pitch Deck Review &nbsp;·&nbsp; 2026</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>`;

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ["--no-sandbox", "--font-render-hinting=none"],
  });
  const print = async (src, out, footer) => {
    const page = await browser.newPage();
    await page.goto("file://" + src, { waitUntil: "networkidle0" });
    await page.evaluateHandle("document.fonts.ready");
    await page.pdf({
      path: out,
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: Boolean(footer),
      headerTemplate: "<div></div>",
      footerTemplate: footer || "<div></div>",
      tagged: true,
    });
    await page.close();
  };

  const coverPdf = path.join(BUILD, "cover.pdf");
  const bodyPdf = path.join(BUILD, "body.pdf");
  await print(coverPath, coverPdf, null);
  await print(bodyPath, bodyPdf, FOOT);
  await browser.close();

  // merge in-process so document metadata survives (pdfunite drops it)
  const merged = await PDFDocument.create();
  for (const src of [coverPdf, bodyPdf]) {
    const doc = await PDFDocument.load(fs.readFileSync(src));
    const pages = await merged.copyPages(doc, doc.getPageIndices());
    pages.forEach((pg) => merged.addPage(pg));
  }
  merged.setTitle("ALTR · Pitch Deck Review 2026");
  merged.setAuthor("ALTR Management");
  merged.setSubject("Review of the 2026 ALTR Management and ALTR Media pitch decks");
  merged.setCreator("ALTR Management HQ — 02-outreach-sales/pitch-deck-review/build.js");
  merged.setKeywords(["ALTR", "pitch deck", "review", "2026"]);
  fs.writeFileSync(OUT, await merged.save());
  const kb = (fs.statSync(OUT).size / 1024).toFixed(0);
  console.log(`wrote ${path.basename(OUT)} (${kb} KB)`);
})();
