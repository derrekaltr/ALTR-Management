const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.33, height: 7.5 });
p.layout = "W";

// palette — matches the HTML report
const INK = "0D0D10", PAPER = "16161C", CARD = "1E1E27", LINE = "2C2C38";
const TEXT = "E8E6DF", DIM = "9B98A8", FAINT = "8D8A9C";
const SIGNAL = "FF5D3A", AMBER = "FFB340", MINT = "5EE0A0", SKY = "6DB3F2";
const HEAD = "Georgia", BODY = "Calibri", MONO = "Consolas";
const SS = "screenshots/";

const W = 13.33, H = 7.5;

function base(s) { s.background = { color: INK }; }

// small kicker label
function kicker(s, txt, x, y, color = SIGNAL) {
  s.addText(txt.toUpperCase(), { x, y, w: 8, h: 0.3, fontFace: MONO, fontSize: 10.5, color, charSpacing: 4, align: "left" });
}

// screenshot with thin border, ratio ~1152x578 (≈1.993)
function shot(s, file, x, y, w, ratio = 1.993) {
  const h = w / ratio;
  s.addShape("rect", { x: x - 0.03, y: y - 0.03, w: w + 0.06, h: h + 0.06, fill: { color: "000000" }, line: { color: LINE, width: 1 } });
  s.addImage({ path: SS + file, x, y, w, h });
  return h;
}

// ───────────────────────── 1 · TITLE
let s = p.addSlide(); base(s);
s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: INK } });
s.addShape("ellipse", { x: 9.2, y: -2.8, w: 7, h: 7, fill: { color: "1C1218" }, line: { type: "none" } });
kicker(s, "Field audit · wisfma.com · 26 Sept 2026", 0.9, 0.85);
s.addText([
  { text: "What Is Working,", options: { fontFace: HEAD, fontSize: 54, bold: true, color: TEXT, breakLine: true } },
  { text: "and what isn't.", options: { fontFace: HEAD, fontSize: 54, italic: true, color: DIM } },
], { x: 0.85, y: 1.35, w: 10.5, h: 2.3, align: "left", lineSpacing: 60 });
s.addText([
  { text: "A hands-on UX review of the WISFMA / Flow's CRM agency platform — every section used live, workflows exercised end-to-end, benchmarked against what full-service OF management agencies pay for. ", options: { color: DIM } },
  { text: "The engine is impressive. The cockpit needs work.", options: { color: TEXT, bold: true } },
], { x: 0.9, y: 3.75, w: 8.6, h: 1.3, fontFace: BODY, fontSize: 15, align: "left" });
const stats = [["15", "sections tested live", TEXT], ["6", "critical issues", SIGNAL], ["14", "friction points", AMBER], ["9", "standout strengths", MINT]];
stats.forEach((st, i) => {
  const x = 0.9 + i * 2.95;
  s.addShape("rect", { x, y: 5.45, w: 2.75, h: 1.35, fill: { color: PAPER }, line: { color: LINE, width: 1 } });
  s.addText(st[0], { x: x + 0.22, y: 5.6, w: 2.2, h: 0.7, fontFace: HEAD, fontSize: 34, bold: true, color: st[2] });
  s.addText(st[1].toUpperCase(), { x: x + 0.24, y: 6.3, w: 2.4, h: 0.32, fontFace: MONO, fontSize: 9, color: FAINT, charSpacing: 2 });
});

// ───────────────────────── 2 · VERDICT
s = p.addSlide(); base(s);
kicker(s, "Executive summary", 0.9, 0.5);
s.addText("A power tool that hides its power.", { x: 0.85, y: 0.85, w: 11.5, h: 0.75, fontFace: HEAD, fontSize: 32, bold: true, color: TEXT });
const keep = [
  ["Shadowban alerts with evidence", "“1.1k views vs 5.4k normally” — no competitor shows this"],
  ["AI niche strategy + insights", "full per-creator playbooks with next moves for the team"],
  ["White-label client reports", "branded PDF per client — a retention weapon"],
  ["Trials + hook library", "mining proven reels to re-post, done well"],
  ["Pulse", "“is the work getting done” per account & employee"],
];
const fix = [
  ["Revenue is invisible", "the #1 agency number never reaches the dashboard"],
  ["Instagram has no section", "65% of views, 52 accounts — no nav entry"],
  ["Employees page is hidden", "team accountability buried inside a Pulse tab"],
  ["Same client, four pickers", "every section restarts client selection"],
  ["Expenses = a different app", "money-out lives on another domain"],
];
function vcol(title, items, x, accent, marker) {
  s.addShape("rect", { x, y: 1.85, w: 5.75, h: 5.05, fill: { color: PAPER }, line: { color: LINE, width: 1 } });
  s.addText(title.toUpperCase(), { x: x + 0.3, y: 2.05, w: 5, h: 0.35, fontFace: MONO, fontSize: 11, color: accent, charSpacing: 3 });
  items.forEach((it, i) => {
    const y = 2.55 + i * 0.88;
    s.addText(marker, { x: x + 0.3, y, w: 0.3, h: 0.4, fontFace: MONO, fontSize: 14, bold: true, color: accent });
    s.addText([
      { text: it[0], options: { bold: true, color: TEXT, breakLine: true } },
      { text: it[1], options: { color: DIM, fontSize: 11.5 } },
    ], { x: x + 0.62, y: y - 0.04, w: 4.95, h: 0.85, fontFace: BODY, fontSize: 13, lineSpacingMultiple: 1.05 });
  });
}
vcol("Keep — genuinely differentiated", keep, 0.9, MINT, "+");
vcol("Fix — blocks daily flow", fix, 6.85, SIGNAL, "!");

// ───────────────────────── helper for critical slides
function critical(num, area, title, body, fixTxt, img, ratio) {
  const s = p.addSlide(); base(s);
  // left: media
  const iw = 6.55; const ihh = iw / (ratio || 1.993); const iy = 1.35 + (5.9 - ihh) / 2; const ih = shot(s, img, 0.55, iy, iw, ratio);
  // badges
  s.addShape("rect", { x: 0.9, y: 0.55, w: 1.75, h: 0.38, fill: { color: INK }, line: { color: SIGNAL, width: 1 } });
  s.addText(("critical 0" + num).toUpperCase(), { x: 0.9, y: 0.55, w: 1.75, h: 0.38, fontFace: MONO, fontSize: 10, color: SIGNAL, align: "center", charSpacing: 2 });
  s.addShape("rect", { x: 2.8, y: 0.55, w: 1.9, h: 0.38, fill: { color: INK }, line: { color: LINE, width: 1 } });
  s.addText(area.toUpperCase(), { x: 2.8, y: 0.55, w: 1.9, h: 0.38, fontFace: MONO, fontSize: 10, color: FAINT, align: "center", charSpacing: 2 });
  // right: text
  s.addText(title, { x: 7.5, y: 1.35, w: 5.35, h: 1.5, fontFace: HEAD, fontSize: 25, bold: true, color: TEXT, lineSpacingMultiple: 1.02 });
  s.addText(body, { x: 7.55, y: 2.95, w: 5.25, h: 2.3, fontFace: BODY, fontSize: 13.5, color: DIM, lineSpacingMultiple: 1.12 });
  s.addShape("rect", { x: 7.55, y: 5.45, w: 5.25, h: 1.5, fill: { color: CARD }, line: { type: "none" } });
  s.addShape("rect", { x: 7.55, y: 5.45, w: 0.045, h: 1.5, fill: { color: MINT }, line: { type: "none" } });
  s.addText("SUGGESTED CHANGE", { x: 7.8, y: 5.58, w: 4.8, h: 0.28, fontFace: MONO, fontSize: 9.5, color: MINT, charSpacing: 3 });
  s.addText(fixTxt, { x: 7.8, y: 5.88, w: 4.85, h: 1, fontFace: BODY, fontSize: 12.5, color: TEXT, lineSpacingMultiple: 1.08 });
  return s;
}

// 3 · C1
critical(1, "Dashboard", "“At a glance” — with zero dollars on it",
  [{ text: "The company dashboard is 100% views: 69M tracked, platform splits, publishing chart. But agencies run on revenue — and the platform already has it: $101,853/30d sits on the Revenues page, and every client card shows OnlyFans earnings.\n\nViews are the input. Money is the output. The glance page only shows the input.", options: {} }],
  "Add a revenue strip to the dashboard hero (24h / 7d / 30d, top-3 earners, biggest mover). The data already exists — it's a layout change, not a feature.",
  "01-dashboard.jpg", 2.147);

// 4 · C2
critical(2, "Navigation", "Instagram is the business — and has no home",
  "Sidebar: Twitter ✓ Facebook ✓ TikTok ✓ … Instagram ✗. Yet Instagram is 52 accounts and 65% of all selected views, and the entire Content Studio is built around Instagram filming plans.\n\nThe three platform pages that do exist use three different layouts — an operator learns three UIs to do one job.",
  "One shared platform-page template (health → creators → accounts → top content), instantiated for all four platforms. Instagram gets a first-class sidebar entry.",
  "02-dashboard-scroll-trap.jpg", 2.147);

// 5 · C3
critical(3, "Team ops", "The team page is a secret",
  "A full Employee Pulse exists — who owns each account, what got posted, 29 accounts needing assignment, per-employee CSV export. It is not in the sidebar; the only way in is a small tab inside Pulse.\n\nMeanwhile the dashboard flags “29 accounts need an employee” every day — and the workflow to fix it is hidden two levels deep.",
  "Promote Employees to the sidebar under a “Team” group; dashboard card links straight into an assignment view with bulk assign.",
  "21-employee-pulse.jpg");

// 6 · C4
critical(4, "Repetitiveness", "Four sections, four client pickers",
  "Working one model: Niche → dropdown + View. Insights → another dropdown + View. Results → dropdown + Apply. Content plans → find her card in a grid. The app never remembers which client you're working on.\n\nClient-page tabs jump to global pages and the breadcrumb switches section — “back to my client” is never one click. (Recorded as a GIF in the full report.)",
  "Make the client the unit of navigation: persistent client switcher in the top bar; stable client sub-pages for plans / niche / results.",
  "22-insights.jpg");

// 7 · C5
critical(5, "Core actions", "Core operations live inside a chat box",
  "The dashboard's own help text: “Ask chat ‘Refresh Instagram analytics’ to pull new data.” Adding accounts and refreshing data route through an admin-only chat whose fine print says “additions save immediately” — instant CRM writes, no confirm, invisible to new users, unavailable to employees.",
  "Every chat-only operation gets a real button in the UI; chat additions show a preview + confirm before saving.",
  "24-crm-chat.jpg");

// 8 · C6
critical(6, "Money ops", "Money-in and money-out live in different worlds",
  "Revenues is a proper page. Expenses is an external link into a separate app on another domain (flow-crm-private.vercel.app) with separate access.\n\nSo the platform can never answer the owner's real question: profit per model — revenue minus chatting labor, traffic spend and tools.",
  "Bring expenses in-app (categorized ledger), then ship per-client P&L: OF revenue − attributed costs = margin per model. No competitor offers this.",
  "19-revenues.jpg");

// ───────────────────────── 9 · FRICTION
s = p.addSlide(); base(s);
kicker(s, "Priority two", 0.9, 0.5, AMBER);
s.addText("Friction & repetition in the daily loop", { x: 0.85, y: 0.85, w: 11.5, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: TEXT });
const fr = [
  ["07", "154 accounts, no compact view", "every account is a huge card; no table view, no bulk assign/refresh"],
  ["08", "“Fix Ban” is a phone number × 10", "no recovery pipeline — no contacted / quoted / recovered status"],
  ["09", "The scroll fights back", "scroll traps + a frozen page; night-mode toggle does nothing"],
  ["10", "Onboarding is a wall of zeros", "the real setup path exists across 5 sections but is never shown"],
  ["11", "Search only knows accounts", "no way to jump to a client, plan or report from the keyboard"],
  ["12", "404s with no way home", "/feed dead-ends unbranded; Benchmark anchor lands at page top"],
  ["13", "Cloned control clusters", "same 4 buttons repeated on every plan card; 10 identical ban cards"],
];
fr.forEach((f, i) => {
  const y = 1.75 + i * 0.73;
  s.addText(f[0], { x: 0.9, y: y - 0.06, w: 0.7, h: 0.6, fontFace: HEAD, fontSize: 21, italic: true, color: AMBER });
  s.addText([
    { text: f[1] + "   ", options: { bold: true, color: TEXT } },
    { text: "— " + f[2], options: { color: DIM } },
  ], { x: 1.65, y, w: 6.35, h: 0.6, fontFace: BODY, fontSize: 13.5 });
  if (i < fr.length - 1) s.addShape("line", { x: 0.9, y: y + 0.62, w: 7.1, h: 0, line: { color: "20202A", width: 0.75, dashType: "dash" } });
});
shot(s, "06-accounts-cards.jpg", 8.45, 1.8, 4.3);
shot(s, "27-fix-ban.jpg", 8.45, 4.5, 4.3);
s.addText("EVIDENCE: OVERSIZED CARDS · BAN TRIAGE BY SMS", { x: 8.45, y: 6.85, w: 4.3, h: 0.28, fontFace: MONO, fontSize: 9, color: DIM, charSpacing: 1 });

// ───────────────────────── 10 · MARKET
s = p.addSlide(); base(s);
kicker(s, "Research · what agencies pay for", 0.9, 0.5, SKY);
s.addText("Where WISFMA sits in the market", { x: 0.85, y: 0.85, w: 11.5, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: TEXT });
const rows = [
  [{ text: "Agency need", options: { bold: true } }, "WISFMA", "Infloww", "Supercreator", "OnlyMonster"],
  ["Traffic-account health (bans / shadowbans / cadence)", ["Best in class", MINT], ["Partial", AMBER], ["—", "55525F"], ["Partial", AMBER]],
  ["AI content strategy per creator (niche, hooks, 30-day plan)", ["Yes — unique", MINT], ["—", "55525F"], ["—", "55525F"], ["—", "55525F"]],
  ["White-label client reporting", ["Yes", MINT], ["—", "55525F"], ["—", "55525F"], ["Exports", AMBER]],
  ["Unified fan inbox / chatting", ["No", SIGNAL], ["Core", MINT], ["Core", MINT], ["Core", MINT]],
  ["Chatter shifts, performance & commission math", ["No", SIGNAL], ["Yes", MINT], ["Yes", MINT], ["Yes", MINT]],
  ["AI chat assist (the 2026 battleground)", ["No", SIGNAL], ["Beta", AMBER], ["“Izzy”", MINT], ["Suggest", AMBER]],
  ["Profit per model (revenue − costs)", ["Nearly — expenses off-platform", AMBER], ["—", "55525F"], ["—", "55525F"], ["—", "55525F"]],
  ["Team roles & permissions", ["Owner only", SIGNAL], ["Yes", MINT], ["Basic", AMBER], ["Yes", MINT]],
  ["Compliance vault (2257 / releases)", ["No — nobody has it", AMBER], ["—", "55525F"], ["—", "55525F"], ["—", "55525F"]],
];
const tableRows = rows.map((r, ri) => r.map((c, ci) => {
  if (ri === 0) return { text: (typeof c === "object" ? c.text : c), options: { fontFace: MONO, fontSize: 9.5, color: FAINT, bold: false, fill: { color: INK }, align: ci === 0 ? "left" : "center", valign: "middle" } };
  if (ci === 0) return { text: c, options: { fontFace: BODY, fontSize: 11.5, color: TEXT, fill: { color: PAPER }, align: "left", valign: "middle" } };
  return { text: c[0], options: { fontFace: BODY, fontSize: 11, color: c[1], fill: { color: PAPER }, align: "center", valign: "middle" } };
}));
s.addTable(tableRows, { x: 0.9, y: 1.7, w: 11.5, colW: [4.35, 2.35, 1.6, 1.7, 1.5], border: { color: "23232E", pt: 0.75 }, rowH: 0.42 });
s.addText([
  { text: "Strategic read: ", options: { bold: true, color: TEXT } },
  { text: "don't chase Infloww's inbox first. The uncontested wins: per-model P&L, employee logins with roles, and a compliance vault no competitor ships. Today the niche playbooks tell staff to use Metricool, Notion & Dropbox — feature gaps wearing other logos.", options: { color: DIM } },
], { x: 0.9, y: 6.55, w: 11.5, h: 0.75, fontFace: BODY, fontSize: 12.5, lineSpacingMultiple: 1.1 });

// ───────────────────────── 11 · ROADMAP
s = p.addSlide(); base(s);
kicker(s, "Recommendation", 0.9, 0.5);
s.addText("Suggested order of attack", { x: 0.85, y: 0.85, w: 11.5, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: TEXT });
const cols = [
  ["THIS WEEK — LAYOUT & BUGS", "Now", SIGNAL, [
    "Revenue strip on the dashboard (data exists)",
    "Sidebar: add Instagram + Employees",
    "Fix theme toggle, scroll trap, /feed 404, anchors",
    "Plain-language errors (no HikerAPI / Apify strings)",
    "Confirm-guard the OnlyFans “unlink”",
  ]],
  ["THIS MONTH — FLOW", "Next", AMBER, [
    "Persistent client switcher + stable client tabs",
    "Accounts table view + bulk actions",
    "Ban-recovery pipeline with statuses",
    "Onboarding checklist on empty clients",
    "⌘K global search; buttons for every chat-only op",
  ]],
  ["THIS QUARTER — MOAT", "Later", SKY, [
    "Per-model P&L (bring expenses in-app)",
    "Employee accounts with roles",
    "Compliance vault (2257 / releases / IDs)",
    "Data export everywhere + simple API",
    "Only then: chatting module or Infloww integration",
  ]],
];
cols.forEach((c, i) => {
  const x = 0.75 + i * 4.02;
  s.addShape("rect", { x, y: 1.75, w: 3.72, h: 5.1, fill: { color: PAPER }, line: { color: LINE, width: 1 } });
  s.addText(c[0], { x: x + 0.28, y: 2.0, w: 3.3, h: 0.3, fontFace: MONO, fontSize: 9, color: FAINT, charSpacing: 2 });
  s.addText(c[1], { x: x + 0.26, y: 2.3, w: 3, h: 0.6, fontFace: HEAD, fontSize: 27, bold: true, color: c[2] });
  c[3].forEach((li, j) => {
    const y = 3.1 + j * 0.72;
    s.addText("—", { x: x + 0.28, y, w: 0.3, h: 0.4, fontFace: MONO, fontSize: 11, color: c[2] });
    s.addText(li, { x: x + 0.6, y: y - 0.02, w: 3.0, h: 0.72, fontFace: BODY, fontSize: 12, color: DIM, lineSpacingMultiple: 1.05, valign: "top" });
  });
});

// ───────────────────────── 12 · CLOSE
s = p.addSlide(); base(s);
s.addShape("ellipse", { x: 10.2, y: -3.4, w: 7, h: 7, fill: { color: "10161A" }, line: { type: "none" } });
kicker(s, "Bottom line", 0.9, 1.1);
s.addText([
  { text: "The intelligence layer is already ahead of the market.\n", options: { color: TEXT } },
  { text: "Now make it flow.", options: { italic: true, color: SIGNAL } },
], { x: 0.85, y: 1.55, w: 11.6, h: 2.2, fontFace: HEAD, fontSize: 40, bold: true, lineSpacingMultiple: 1.05 });
s.addText("Shadowban evidence, AI niche playbooks, white-label reports and Pulse are genuinely differentiated — competitors charging $40+/creator don't have them. The fixes in this deck are mostly navigation, layout and copy: put money on the dashboard, give Instagram and the team a home, remember the selected client, and retire the chat box as the only path to core actions.", { x: 0.9, y: 3.9, w: 10.8, h: 1.6, fontFace: BODY, fontSize: 15, color: DIM, lineSpacingMultiple: 1.2 });
s.addText("Full interactive report: wisfma-ux-review.html — 29 annotated screenshots, live-recorded GIF evidence, complete polish list & method notes.", { x: 0.9, y: 6.4, w: 10.8, h: 0.6, fontFace: MONO, fontSize: 10.5, color: DIM, charSpacing: 1 });

p.writeFile({ fileName: "wisfma-ux-review.pptx" }).then(() => console.log("deck written"));
