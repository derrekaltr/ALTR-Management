#!/usr/bin/env node
// Case card generator: node generate.mjs cases/<case>.json [more.json ...]
// Renders a branded 1080x1080 PNG (2x scale) into output/<case>.png

import { readFile, writeFile, mkdir, rm } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { chromium } from "playwright";

const ROOT = dirname(fileURLToPath(import.meta.url));
const PLATFORMS = ["youtube", "instagram", "tiktok", "snapchat"];

const esc = (s) =>
  String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

function statusClass(status) {
  const s = String(status).toLowerCase();
  if (/(done|complete|recovered|removed|verified|success|100)/.test(s)) return "st-done";
  if (/(progress|working|processing|escalat)/.test(s)) return "st-progress";
  if (/(submit|pending|review|queue|new)/.test(s)) return "st-pending";
  if (/(hold|issue|fail|denied|stuck)/.test(s)) return "st-issue";
  return "st-neutral";
}

function kvRows(obj) {
  return Object.entries(obj ?? {})
    .map(
      ([k, v]) =>
        `<div class="row"><span class="k">${esc(k)}</span><span class="v">${esc(v)}</span></div>`
    )
    .join("\n");
}

function credBlock(creds) {
  const entries = Object.entries(creds ?? {});
  if (!entries.length) return "";
  const lines = entries
    .map(
      ([k, v]) =>
        `<div class="cred-line"><span class="ck">${esc(k)}</span><span class="cv">${esc(v)}</span></div>`
    )
    .join("\n");
  return `<div class="creds"><div class="creds-label">Account Access</div>${lines}</div>`;
}

function linkLabel(url) {
  try {
    const h = new URL(url).hostname.replace(/^www\./, "");
    if (h.includes("instagram")) return "Instagram";
    if (h === "x.com" || h.includes("twitter")) return "X";
    if (h.includes("tiktok")) return "TikTok";
    if (h.includes("youtube") || h === "youtu.be") return "YouTube";
    if (h.includes("snapchat")) return "Snapchat";
    return h;
  } catch {
    return "Link";
  }
}

// display form: host + path, no protocol/query trackers (href keeps the full URL)
function linkDisplay(url) {
  try {
    const u = new URL(url);
    return (u.hostname.replace(/^www\./, "") + u.pathname).replace(/\/$/, "");
  } catch {
    return url;
  }
}

function linkRows(data) {
  const entries = [];
  if (data.link) entries.push(["Page", data.link]);
  if (Array.isArray(data.links)) {
    for (const url of data.links) entries.push([linkLabel(url), url]);
  } else if (data.links) {
    for (const [label, url] of Object.entries(data.links)) entries.push([label, url]);
  }
  return entries
    .map(
      ([label, url]) =>
        `<div class="row"><span class="k">${esc(label)}</span><a class="v handle" href="${esc(url)}">${esc(linkDisplay(url))}</a></div>`
    )
    .join("\n");
}

async function assetDataUri(path) {
  const buf = await readFile(join(ROOT, path));
  return `data:image/png;base64,${buf.toString("base64")}`;
}

async function renderCase(browser, caseFile, baseCss, brand) {
  const data = JSON.parse(await readFile(caseFile, "utf8"));
  const platform = String(data.platform ?? "").toLowerCase();
  if (!PLATFORMS.includes(platform)) {
    throw new Error(`${caseFile}: unknown platform "${data.platform}" (expected ${PLATFORMS.join(", ")})`);
  }
  const category = String(data.category ?? "recovery").toLowerCase() === "removal" ? "removal" : "recovery";
  let portrait = data.size === "portrait";

  const template = await readFile(join(ROOT, "cards", "templates", `${platform}.html`), "utf8");
  // snapchat is the light card — it takes the dark (charcoal) marks
  const dark = platform === "snapchat";
  const fills = {
    BASE_CSS: baseCss.replace("{{BRAND_ACCENT}}", brand.accent || "#B6F2E5"),
    BRAND_NAME: esc(brand.name || ""),
    BRAND_TAGLINE: esc(brand.tagline || ""),
    WORDMARK_SRC: await assetDataUri(dark ? brand.assets.wordmarkDark : brand.assets.wordmarkLight),
    MONOGRAM_SRC: await assetDataUri(dark ? brand.assets.monogramDark : brand.assets.monogramLight),
    CATEGORY: esc(category),
    CATEGORY_LABEL: category === "removal" ? "Removal Division" : "Recovery Division",
    CATEGORY_CLASS: `category-${category}`,
    SERVICE: esc(data.service ?? ""),
    CASE_TYPE: esc(data.caseType ?? ""),
    STATUS: esc(data.status ?? "New"),
    STATUS_CLASS: statusClass(data.status ?? "new"),
    CLIENT: esc(data.client ?? ""),
    HANDLE: esc(data.handle ?? ""),
    LINK_ROW: linkRows(data),
    DETAIL_ROWS: kvRows(data.details),
    CRED_BLOCK: credBlock(data.credentials),
    NOTES_BLOCK: data.notes ? `<div class="notes"><strong>Notes.</strong> ${esc(data.notes)}</div>` : "",
  };
  const buildHtml = (isPortrait) => {
    let html = template;
    const all = { ...fills, SIZE_CLASS: isPortrait ? "portrait" : "" };
    for (const [key, value] of Object.entries(all)) html = html.replaceAll(`{{${key}}}`, value);
    return html;
  };

  // fit pass: compact the layout if content overflows, shrink long titles,
  // and clamp notes to the whole lines that actually fit. Reports how many
  // notes lines were shown vs. needed so the caller can retry in portrait.
  const fitPage = (page) =>
    page.evaluate(() => {
      const main = document.querySelector("main");
      const overflows = () => main.scrollHeight > main.clientHeight;
      if (overflows()) document.body.classList.add("compact");
      if (overflows()) document.body.classList.add("compact-2");
      const h1 = document.querySelector(".service");
      let fs = parseFloat(getComputedStyle(h1).fontSize);
      while (h1.scrollWidth > h1.clientWidth && fs > 38) {
        fs -= 4;
        h1.style.fontSize = `${fs}px`;
      }
      let notesShown = null;
      let notesNeeded = null;
      const notes = document.querySelector(".notes");
      if (notes) {
        const lh = parseFloat(getComputedStyle(notes).lineHeight) || 36;
        const bottomPad = parseFloat(getComputedStyle(main).paddingBottom) || 0;
        const avail = main.clientHeight - bottomPad - notes.offsetTop;
        notesShown = Math.max(1, Math.min(6, Math.floor(avail / lh)));
        notesNeeded = Math.ceil(notes.scrollHeight / lh);
        notes.style.webkitLineClamp = String(notesShown);
      }
      return { notesShown, notesNeeded };
    });

  const tmp = join(tmpdir(), `card-${Date.now()}-${Math.random().toString(36).slice(2)}.html`);
  const page = await browser.newPage({
    viewport: { width: 1080, height: portrait ? 1350 : 1080 },
    deviceScaleFactor: 2,
  });
  try {
    await writeFile(tmp, buildHtml(portrait));
    await page.goto(`file://${tmp}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    let fit = await fitPage(page);
    // not enough room for the notes on a square card → retry as portrait
    if (!portrait && !data.size && fit.notesNeeded && fit.notesShown < Math.min(fit.notesNeeded, 2)) {
      portrait = true;
      await page.setViewportSize({ width: 1080, height: 1350 });
      await writeFile(tmp, buildHtml(true));
      await page.goto(`file://${tmp}`, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await fitPage(page);
    }
    const stem = basename(caseFile).replace(/\.json$/i, "");
    const outPath = join(ROOT, "output", `${stem}.png`);
    await page.screenshot({ path: outPath });
    // matching PDF — same design, but any `link` on the card is clickable
    await page.emulateMedia({ media: "screen" });
    await page.pdf({
      path: join(ROOT, "output", `${stem}.pdf`),
      width: "1080px",
      height: portrait ? "1350px" : "1080px",
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      pageRanges: "1",
    });
    return outPath;
  } finally {
    await page.close();
    await rm(tmp, { force: true });
  }
}

const files = process.argv.slice(2);
if (!files.length) {
  console.error("Usage: node generate.mjs cases/<case>.json [more.json ...]");
  process.exit(1);
}

const baseCss = await readFile(join(ROOT, "cards", "templates", "base.css"), "utf8");
const brand = JSON.parse(await readFile(join(ROOT, "cards", "brand", "config.json"), "utf8"));
await mkdir(join(ROOT, "output"), { recursive: true });

const browser = await chromium.launch();
try {
  for (const file of files) {
    const out = await renderCase(browser, resolve(file), baseCss, brand);
    console.log(`✓ ${out}`);
  }
} finally {
  await browser.close();
}
