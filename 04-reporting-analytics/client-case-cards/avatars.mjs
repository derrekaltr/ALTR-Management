#!/usr/bin/env node
// Group-chat avatar generator: node avatars.mjs  →  output/avatars/*.png
// 1024x1024, designed to survive the circular crop chat apps apply.

import { readFile, writeFile, mkdir, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { chromium } from "playwright";

const ROOT = dirname(fileURLToPath(import.meta.url));
const brand = JSON.parse(await readFile(join(ROOT, "cards", "brand", "config.json"), "utf8"));

const asset = async (p) =>
  `data:image/png;base64,${(await readFile(join(ROOT, p))).toString("base64")}`;

const monogram = {
  mint: await asset("cards/brand/assets/monogram-mint-trim.png"),
  cream: await asset("cards/brand/assets/monogram-cream-trim.png"),
  charcoal: await asset("cards/brand/assets/monogram-black-trim.png"),
};

// bg / monogram tint / SERVICES color / ring color(s)
const VARIANTS = {
  "altr-services-dark":  { bg: "#1D1D1B", mono: "mint",     text: "#EBECDC", ring: "#B6F2E5" },
  "altr-services-mint":  { bg: "#B6F2E5", mono: "charcoal", text: "#1D1D1B", ring: "#1D1D1B" },
  "altr-services-cream": { bg: "#EBECDC", mono: "charcoal", text: "#1D1D1B", ring: "#1D1D1B" },
  "altr-services-youtube":   { bg: "#141416", mono: "mint", text: "#EBECDC", ring: "#FF0033" },
  "altr-services-instagram": { bg: "#16101f", mono: "mint", text: "#EBECDC", ring: "linear-gradient(135deg,#f7b955,#e94b8a,#8a3ab9)" },
  "altr-services-tiktok":    { bg: "#050507", mono: "mint", text: "#EBECDC", ring: "linear-gradient(135deg,#25f4ee,#fe2c55)" },
  "altr-services-snapchat":  { bg: "#FFFC00", mono: "charcoal", text: "#1D1D1B", ring: "#1D1D1B" },
};

function html(v) {
  const ringIsGradient = v.ring.startsWith("linear-gradient");
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
<style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1024px; height: 1024px; overflow: hidden; }
  .avatar {
    width: 1024px; height: 1024px;
    background:
      radial-gradient(700px 700px at 30% 20%, rgba(255,255,255,0.07), transparent 60%),
      ${v.bg};
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 52px; position: relative;
  }
  /* grain, same as the cards */
  .avatar::after {
    content: ""; position: absolute; inset: 0; opacity: 0.45; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.05 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  /* ring sits inside the circle crop */
  .ring {
    position: absolute; inset: 56px; border-radius: 50%;
    ${ringIsGradient
      ? `background: ${v.ring}; -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 14px), #000 calc(100% - 13px)); mask: radial-gradient(farthest-side, transparent calc(100% - 14px), #000 calc(100% - 13px));`
      : `border: 13px solid ${v.ring};`}
  }
  .mono { height: 380px; width: auto; position: relative; z-index: 2; }
  .services {
    position: relative; z-index: 2;
    font-family: "JetBrains Mono", monospace;
    font-weight: 800; font-size: 74px;
    letter-spacing: 0.46em; text-indent: 0.46em;
    color: ${v.text}; text-transform: uppercase;
  }
</style></head>
<body><div class="avatar">
  <div class="ring"></div>
  <img class="mono" src="${monogram[v.mono]}">
  <div class="services">Services</div>
</div></body></html>`;
}

await mkdir(join(ROOT, "output", "avatars"), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 2 });
try {
  for (const [name, v] of Object.entries(VARIANTS)) {
    const tmp = join(tmpdir(), `avatar-${name}.html`);
    await writeFile(tmp, html(v));
    await page.goto(`file://${tmp}`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    const out = join(ROOT, "output", "avatars", `${name}.png`);
    await page.screenshot({ path: out });
    await rm(tmp, { force: true });
    console.log(`✓ ${out}`);
  }
} finally {
  await browser.close();
}
