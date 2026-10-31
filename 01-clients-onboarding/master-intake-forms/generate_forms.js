// ALTR Management — Master Model Intake Form generator
// Builds two .docx forms (full union + streamlined) and a CSV field schema
// from the merged question inventory of all six source intake forms.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak,
} = require("docx");

// ---------------------------------------------------------------------------
// Question inventory. core:true => included in the streamlined version.
// types: short | long | choice | yn
// Special blocks: checklist (Yes/No/Notes) and pricing (Offer/Price/Notes)
// ---------------------------------------------------------------------------
const CHECK = "☐ "; // empty checkbox

const SECTIONS = [
  {
    title: "1. Account & Platforms",
    items: [
      { q: "Model name (stage name)", type: "short", core: true },
      { q: "Full legal name", type: "short" },
      { q: "Name you go by in fan chats", type: "short", core: true },
      { q: "Name(s) the chat team can NEVER use", type: "short", core: true },
      { q: "Pronouns", type: "short", core: true },
      { q: "Main OnlyFans page (handle / URL)", type: "short", core: true },
      { q: "Other OnlyFans pages (VIP / free / etc.) and how they must be run", type: "long", core: true,
        note: "e.g. keep free and VIP pages fully separate; never cross-promote between them" },
      { q: "Other platforms (Fansly, Fanvue, MYM, etc.)", type: "short" },
      { q: "Account login email", type: "short",
        note: "SECURITY: credentials may also be shared via a secure channel instead of this form" },
      { q: "Account login password", type: "short" },
      { q: "Do you show your face in content?", type: "yn", core: true },
      { q: "Explicitness level", type: "choice", core: true, opts: [
        "X — Non-Nude / Implied: lingerie, teasing",
        "XX — Semi Nude / Topless: tits shown, no pussy, over-underwear / non-frontal masturbation",
        "XXX — Full Nude: everything shown",
        "XXXX — Explicit: everything shown, masturbation, sextapes etc.",
        "Other" ] },
      { q: "Explicit content collaboration types", type: "choice", core: true, multi: true,
        opts: ["Individual (solo only)", "Boy/Girl", "Girl/Girl", "Boy/Boy/Girl", "Boy/Girl/Girl", "Anything"] },
      { q: "Your niche / what you are known for on the platform", type: "short", core: true },
    ],
  },
  {
    title: "2. Personal & Identity",
    intro: "Answer based on how the account is marketed — the persona fans should see, not necessarily your private life.",
    items: [
      { q: "Age", type: "short", core: true },
      { q: "Birthday (DOB)", type: "short", core: true },
      { q: "Zodiac sign", type: "short", core: true },
      { q: "Born in / birthplace", type: "short", core: true },
      { q: "Where you actually live (private — never shared with fans)", type: "short" },
      { q: "Location to tell fans (persona location)", type: "short", core: true },
      { q: "Time zone", type: "short", core: true },
      { q: "Ethnicity", type: "short", core: true },
      { q: "Sexual orientation", type: "short", core: true },
      { q: "Languages spoken", type: "short", core: true },
      { q: "English skills", type: "choice", opts: ["Good", "Okay", "Bad"] },
      { q: "Public relationship status (what fans are told)", type: "choice", core: true,
        opts: ["Single", "In a Relationship", "Married", "Other"] },
      { q: "Real relationship status (private)", type: "short" },
      { q: "Do you have children?", type: "short", core: true },
      { q: "Family / siblings (and what is OK to mention)", type: "short" },
      { q: "Pets (type, breed, names)", type: "short", core: true },
      { q: "Car you drive", type: "short" },
      { q: "College / education (where, major)", type: "short" },
      { q: "Other work besides OnlyFans", type: "short" },
      { q: "What are you famous / known for?", type: "short" },
      { q: "Anything fans may know about you from before OnlyFans?", type: "long" },
    ],
  },
  {
    title: "3. Physical & Sizing",
    items: [
      { q: "Height", type: "short", core: true },
      { q: "Weight", type: "short" },
      { q: "Measurements (bust – waist – hips)", type: "short", core: true },
      { q: "Eye color", type: "short" },
      { q: "Hair color", type: "short" },
      { q: "Bra size (natural / enhanced details if any)", type: "short", core: true },
      { q: "Shoe size", type: "short", core: true },
      { q: "Panty / underwear size", type: "short", core: true },
      { q: "Shirt size", type: "short" },
      { q: "Dress size", type: "short" },
      { q: "Bikini size", type: "short" },
      { q: "Lingerie size", type: "short" },
      { q: "Tattoos (how many, of what, favorite)", type: "long", core: true },
      { q: "Piercings", type: "short", core: true },
      { q: "Surgeries / enhancements (what and when)", type: "long", core: true },
      { q: "Shaving / grooming style", type: "short" },
      { q: "Nails (style you always wear)", type: "short" },
      { q: "Signature scent / perfume", type: "short" },
      { q: "Hidden talents", type: "short" },
      { q: "Cock size (male models only — skip otherwise)", type: "short" },
    ],
  },
  {
    title: "4. Favorites & Lifestyle",
    items: [
      { q: "Favorite food", type: "short", core: true },
      { q: "Favorite drinks", type: "short", core: true },
      { q: "Favorite snacks / dessert", type: "short" },
      { q: "Food dislikes", type: "short" },
      { q: "Diet / allergies (vegan, gluten-free, etc.)", type: "short" },
      { q: "Favorite color", type: "short", core: true },
      { q: "Favorite animal", type: "short" },
      { q: "Favorite holiday", type: "short" },
      { q: "Favorite music (genres, artists, songs)", type: "short", core: true },
      { q: "Favorite TV shows", type: "short", core: true },
      { q: "Favorite movies", type: "short", core: true },
      { q: "Sports you play / favorite teams", type: "short" },
      { q: "Hobbies / favorite things to do", type: "long", core: true },
      { q: "What you do for fun on a weekend", type: "short" },
      { q: "Places you have traveled", type: "short" },
      { q: "Dream vacation / dream travel list", type: "short", core: true },
      { q: "Fitness routine", type: "short" },
      { q: "Daily routine (skincare, baths, massages, etc.)", type: "short" },
      { q: "Smoking / drinking (cigarettes, weed, vape, alcohol, sobriety)", type: "short", core: true },
      { q: "Guilty pleasures", type: "short" },
      { q: "Do you like to cook anything special?", type: "short" },
      { q: "Dream since you were little", type: "short" },
      { q: "Extracurriculars growing up (ballet, sports, etc.)", type: "short" },
      { q: "Something silly about yourself", type: "short" },
      { q: "Celebrity you would hook up with", type: "short" },
      { q: "Top 5 bucket list items", type: "long" },
      { q: "What does your dream date look like?", type: "short" },
      { q: "Pet peeves", type: "short", core: true },
    ],
  },
  {
    title: "5. Persona & Chat Voice",
    intro: "This is how the chat team captures your tone and represents you. The more detail, the better.",
    items: [
      { q: "Describe your online personality / persona", type: "long", core: true },
      { q: "How should we portray you?", type: "long", core: true },
      { q: "Vibe to give off", type: "choice", core: true, multi: true,
        opts: ["Submissive", "Dominant", "Switch", "Bratty", "Innocent", "Playful", "Gamer girl", "Luxury / rich-girl", "GFE (girlfriend experience)", "Other"] },
      { q: "Special nicknames for fans (love, babe, pookie...)", type: "short", core: true },
      { q: "Emojis you use most (should appear in chats)", type: "short", core: true },
      { q: "Signature words / phrases you actually say", type: "short", core: true },
      { q: "Words / phrases you would NEVER use", type: "short", core: true },
      { q: "Texting style", type: "choice", core: true, opts: ["Formal", "Slang", "Casual", "Other"] },
      { q: "Topics the chat team can NEVER mention", type: "long", core: true },
      { q: "Personal details that ARE okay to share with fans (city, pets, food...)", type: "long", core: true },
      { q: "What turns you on?", type: "short", core: true },
      { q: "What turns you off?", type: "short", core: true },
      { q: "Your ideal guy / type", type: "short" },
      { q: "Love language", type: "short" },
      { q: "How you view men / provider dynamic (e.g. men should always pay)", type: "short" },
    ],
  },
  {
    title: "6. Sexual Profile",
    intro: "Used only when conversation turns explicit — chatters mirror these exactly.",
    items: [
      { q: "Favorite sex position", type: "short", core: true },
      { q: "Fetishes / kinks you have", type: "long", core: true },
      { q: "Fetishes you ACCEPT from fans", type: "short", core: true },
      { q: "Fetishes you REJECT (never engage)", type: "short", core: true },
      { q: "Sexual fantasies", type: "long" },
      { q: "Oral or penetration — which do you enjoy more?", type: "short" },
      { q: "Favorite toy(s) and how many you own", type: "short", core: true },
      { q: "Are you vocal in bed?", type: "short" },
      { q: "Secret / most sensitive zones", type: "short" },
      { q: "Craziest place you have done it", type: "short" },
      { q: "Best sex you can imagine / how you like to be treated", type: "short" },
      { q: "Do you like being on top?", type: "short" },
      { q: "Hard turn-offs in bed", type: "long", core: true },
    ],
  },
  {
    title: "7. Content Menu — What You Offer",
    intro: "Mark YES or NO for every item. Add limits or details in Notes (e.g. “censored only”, “ask first”).",
    checklist: [
      { item: "Ass pictures / videos", core: true },
      { item: "Boob pictures / videos", core: true },
      { item: "Visible nipple pictures / videos", core: true },
      { item: "Full nudity — censored", core: true },
      { item: "Full nudity — uncensored", core: true },
      { item: "Masturbation pictures / videos", core: true },
      { item: "Solo fingering", core: true },
      { item: "Solo with toys", core: true },
      { item: "Solo anal play (plug)", core: true },
      { item: "Solo anal play (dildo)", core: true },
      { item: "Solo double penetration", core: true },
      { item: "Squirting", core: true },
      { item: "Boy/Girl content", core: true },
      { item: "Boy/Girl anal", core: true },
      { item: "Girl/Girl content", core: true },
      { item: "Girl/Girl with toys" },
      { item: "Blowjob content", core: true },
      { item: "JOI (jerk-off instructions)", core: true },
      { item: "CEI (cum eating instructions)", core: true },
      { item: "SPH (small penis humiliation)", core: true },
      { item: "Dick ratings", core: true },
      { item: "Domination", core: true },
      { item: "Submissive", core: true },
      { item: "Feet / foot content", core: true },
      { item: "Kissing / sucking toes" },
      { item: "Fetish / kink content", core: true },
      { item: "Twerk videos" },
      { item: "Fan signs / holding a sign", core: true },
      { item: "Writing fan's name on body", core: true },
      { item: "Video calls", core: true },
      { item: "Public play", core: true },
      { item: "Food play" },
      { item: "Fake cum eating / creampie" },
      { item: "Eating own cum" },
      { item: "Cum swap" },
      { item: "Edging" },
      { item: "Findom / money kink" },
      { item: "Giantess content" },
      { item: "Bondage" },
      { item: "Tickling" },
      { item: "Armpit play" },
      { item: "Bathing / showering content" },
      { item: "Using oils or lubes" },
      { item: "Smoking cigarettes on camera" },
      { item: "Smoking weed on camera" },
      { item: "Smoking vape on camera" },
      { item: "Singing" },
      { item: "Using the term BBC / black dildo content" },
      { item: "Winking asshole" },
      { item: "Panty stuffing" },
    ],
  },
  {
    title: "8. Customs & Pricing",
    intro: "Enter YES/NO and your price for each. Leave price blank if the team sets pricing.",
    items: [
      { q: "Who sets pricing?", type: "choice", core: true,
        opts: ["I set all prices (listed below)", "Team sets prices — be fair, never sell cheap", "Mix of both"] },
      { q: "Subscription price", type: "short", core: true },
      { q: "GFE (girlfriend experience) price", type: "short", core: true },
      { q: "BFE (boyfriend experience) price", type: "short" },
      { q: "MVP package price", type: "short" },
      { q: "VIP package price", type: "short", core: true },
      { q: "PPV price range (min – max)", type: "short", core: true },
    ],
    pricing: [
      { item: "Custom video — non-nude (under 5 min)", core: true },
      { item: "Custom video — non-nude (under 10 min)" },
      { item: "Custom video — solo fingering (5 min)", core: true },
      { item: "Custom video — solo fingering (10 min)" },
      { item: "Custom video — solo with toy (5 min)", core: true },
      { item: "Custom video — solo with toy (10 min)" },
      { item: "Custom video — solo anal with plug", core: true },
      { item: "Custom video — solo anal with dildo" },
      { item: "Custom video — solo double penetration" },
      { item: "Custom video — squirting", core: true },
      { item: "Custom video — sex tape (B/G)", core: true },
      { item: "Custom video — blowjob tape (B/G)", core: true },
      { item: "Custom video — Girl/Girl collaboration", core: true },
      { item: "Custom video — JOI", core: true },
      { item: "Custom video — dominating the fan" },
      { item: "Custom video — foot-focused", core: true },
      { item: "Custom video — food-focused" },
      { item: "Custom video — giantess niche" },
      { item: "Dick rating — video (under 3 min)", core: true },
      { item: "Dick rating — video (under 5 min)" },
      { item: "Dick rating — voice / audio", core: true },
      { item: "Dick rating — clothed" },
      { item: "Dick rating — nude" },
      { item: "Custom pictures — non-nude (per pic)", core: true },
      { item: "Custom pictures — nude (per pic)", core: true },
      { item: "Custom audio — saying fan's name", core: true },
      { item: "Custom audio — voice note", core: true },
      { item: "Video call — OnlyFans Live 1:1", core: true },
      { item: "Video call — on socials (IG, Snapchat, X)" },
      { item: "Voice call", core: true },
      { item: "Private Snapchat add / following fan on socials", core: true },
      { item: "Liking / commenting on fan's profile" },
      { item: "Used panties sent to fan", core: true },
      { item: "Used socks sent to fan" },
      { item: "Used tights / pantyhose sent to fan" },
      { item: "Toys used in content sold to fan" },
      { item: "Outfits / props used in content sold to fan" },
      { item: "Writing fan's name on body (add-on to custom)", core: true },
      { item: "Fan sign (photo holding fan's name)", core: true },
    ],
    itemsAfter: [
      { q: "Custom DOs and DON'Ts (dildo, self-play, anal, blowjob, B/G...)", type: "long", core: true },
      { q: "Toys you will NOT use in a custom", type: "short", core: true },
      { q: "Willing to send fans pictures of the toys you'd use in their custom?", type: "yn" },
      { q: "Accept customs WITHOUT prior approval?", type: "yn", core: true,
        note: "Waiting on approval can reduce buying interest and interrupt conversation flow" },
      { q: "Is there ANYTHING off limits for custom requests?", type: "long", core: true },
    ],
  },
  {
    title: "9. Vault, Fans & Chat Team Rules",
    items: [
      { q: "Any vault content we should NOT currently use?", type: "long", core: true },
      { q: "Any fans you do NOT want us to contact?", type: "long", core: true },
      { q: "VIPs / whales / special fans we need to know about (names + notes)", type: "long", core: true },
      { q: "How should we handle a fan upset about content they bought?", type: "long", core: true },
      { q: "Problems you've had with previous chat teams we should avoid", type: "long", core: true },
      { q: "Things you DISLIKE — chatters must never do these", type: "long", core: true },
      { q: "Your rules & guidelines for the chat team", type: "long", core: true },
      { q: "Anything else to help the chat team represent you", type: "long", core: true },
    ],
  },
  {
    title: "10. Career & Experience",
    items: [
      { q: "When did you start OnlyFans / the adult industry?", type: "short", core: true },
      { q: "Previous / active experience (cams, other platforms, studios)", type: "long", core: true },
      { q: "Represented by an agency or production company?", type: "short" },
      { q: "Awards from your career", type: "short" },
      { q: "Adult expos attended", type: "short" },
      { q: "Ever done a dance feature?", type: "short" },
      { q: "Favorite company to shoot for", type: "short" },
      { q: "Memorable released scenes (elaborate)", type: "long" },
      { q: "Favorite performances / performers you've worked with", type: "short" },
    ],
  },
  {
    title: "11. Marketing & Socials",
    socials: [
      { item: "Instagram", core: true },
      { item: "Twitter / X", core: true },
      { item: "TikTok", core: true },
      { item: "Snapchat", core: true },
      { item: "Reddit", core: true },
      { item: "YouTube" },
      { item: "Pornhub" },
      { item: "Linktree" },
      { item: "Amazon wishlist" },
      { item: "Third-party ad vendors" },
      { item: "Other" },
    ],
    items: [
      { q: "Which social accounts are linked on your OnlyFans page?", type: "short" },
      { q: "Any accounts banned / shadow-banned / restricted / deleted?", type: "long", core: true },
      { q: "Anything specific we should use or say in ads?", type: "long" },
    ],
  },
  {
    title: "12. Content Production Standards",
    intro: "All content submitted to the team must meet these standards. Initial each line to confirm.",
    ack: [
      "RAW videos in original format (no compression)",
      "No filters",
      "Good lighting",
      "Clean camera lens",
      "Vertical format for social media content",
      "Uploaded to Drive following the team's folder structure",
    ],
  },
  {
    title: "13. Final Notes",
    items: [
      { q: "Is there anything about you, your life, or your career that is completely OFF LIMITS?", type: "long", core: true },
      { q: "Anything specific you want fans to know, or how you want to be represented?", type: "long", core: true },
      { q: "Anything else you want the team to know?", type: "long", core: true },
    ],
  },
];

// ---------------------------------------------------------------------------
// docx rendering
// ---------------------------------------------------------------------------
const GOLD = "B08D3F";
const DARK = "1A1A1A";
const LIGHT = "F5F1E8";
const CONTENT_W = 9360;

const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

const t = (text, opts = {}) => new TextRun({ text, font: "Arial", ...opts });
const p = (children, opts = {}) => new Paragraph({ children, ...opts });

function labelCell(text, width, note) {
  const paras = [p([t(text, { bold: true, size: 20 })])];
  if (note) paras.push(p([t(note, { italics: true, size: 16, color: "666666" })]));
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: LIGHT, type: ShadingType.CLEAR },
    margins: cellMargins, verticalAlign: VerticalAlign.CENTER, children: paras,
  });
}
function blankCell(width, nLines = 1) {
  const paras = [];
  for (let i = 0; i < nLines; i++) paras.push(p([t("", { size: 20 })]));
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    margins: cellMargins, children: paras,
  });
}
function textCell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    margins: cellMargins, verticalAlign: VerticalAlign.CENTER,
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    children: [p([t(text, { size: 20, bold: !!opts.bold, color: opts.color })],
      opts.center ? { alignment: AlignmentType.CENTER } : {})],
  });
}

// group consecutive short/yn/choice items into one 2-column table
function renderItems(items, streamlined) {
  const out = [];
  let rows = [];
  const LW = 3900, RW = CONTENT_W - LW;
  const flush = () => {
    if (!rows.length) return;
    out.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [LW, RW], rows }));
    out.push(p([t("", { size: 8 })]));
    rows = [];
  };
  for (const it of items) {
    if (streamlined && !it.core) continue;
    if (it.type === "long") {
      flush();
      out.push(new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
        rows: [
          new TableRow({ children: [labelCell(it.q, CONTENT_W, it.note)] }),
          new TableRow({ children: [blankCell(CONTENT_W, 3)] }),
        ],
      }));
      out.push(p([t("", { size: 8 })]));
    } else if (it.type === "choice") {
      const optText = it.opts.map(o => CHECK + o);
      const cellParas = optText.map(o => p([t(o, { size: 20 })]));
      if (it.multi) cellParas.unshift(p([t("(select all that apply)", { italics: true, size: 16, color: "666666" })]));
      rows.push(new TableRow({
        children: [labelCell(it.q, LW, it.note),
          new TableCell({ borders, width: { size: RW, type: WidthType.DXA }, margins: cellMargins, children: cellParas })],
      }));
    } else if (it.type === "yn") {
      rows.push(new TableRow({
        children: [labelCell(it.q, LW, it.note),
          new TableCell({ borders, width: { size: RW, type: WidthType.DXA }, margins: cellMargins,
            verticalAlign: VerticalAlign.CENTER,
            children: [p([t(CHECK + "Yes      " + CHECK + "No", { size: 20 })])] })],
      }));
    } else {
      rows.push(new TableRow({ children: [labelCell(it.q, LW, it.note), blankCell(RW)] }));
    }
  }
  flush();
  return out;
}

function renderChecklist(rowsData, streamlined) {
  const W = [4600, 900, 900, 2960];
  const header = new TableRow({
    tableHeader: true,
    children: [
      textCell("Content type", W[0], { bold: true, fill: DARK, color: "FFFFFF" }),
      textCell("YES", W[1], { bold: true, fill: DARK, color: "FFFFFF", center: true }),
      textCell("NO", W[2], { bold: true, fill: DARK, color: "FFFFFF", center: true }),
      textCell("Notes / limits", W[3], { bold: true, fill: DARK, color: "FFFFFF" }),
    ],
  });
  const rows = [header];
  for (const r of rowsData) {
    if (streamlined && !r.core) continue;
    rows.push(new TableRow({
      children: [textCell(r.item, W[0]), blankCell(W[1]), blankCell(W[2]), blankCell(W[3])],
    }));
  }
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: W, rows }),
    p([t("", { size: 8 })])];
}

function renderPricing(rowsData, streamlined) {
  const W = [4300, 1100, 1400, 2560];
  const header = new TableRow({
    tableHeader: true,
    children: [
      textCell("Custom / item", W[0], { bold: true, fill: DARK, color: "FFFFFF" }),
      textCell("YES / NO", W[1], { bold: true, fill: DARK, color: "FFFFFF", center: true }),
      textCell("Price ($)", W[2], { bold: true, fill: DARK, color: "FFFFFF", center: true }),
      textCell("Notes", W[3], { bold: true, fill: DARK, color: "FFFFFF" }),
    ],
  });
  const rows = [header];
  for (const r of rowsData) {
    if (streamlined && !r.core) continue;
    rows.push(new TableRow({
      children: [textCell(r.item, W[0]), blankCell(W[1]), blankCell(W[2]), blankCell(W[3])],
    }));
  }
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: W, rows }),
    p([t("", { size: 8 })])];
}

function renderSocials(rowsData, streamlined) {
  const W = [2200, 4800, 2360];
  const header = new TableRow({
    tableHeader: true,
    children: [
      textCell("Platform", W[0], { bold: true, fill: DARK, color: "FFFFFF" }),
      textCell("Handle / link", W[1], { bold: true, fill: DARK, color: "FFFFFF" }),
      textCell("Do you sell on it?", W[2], { bold: true, fill: DARK, color: "FFFFFF" }),
    ],
  });
  const rows = [header];
  for (const r of rowsData) {
    if (streamlined && !r.core) continue;
    rows.push(new TableRow({ children: [textCell(r.item, W[0]), blankCell(W[1]), blankCell(W[2])] }));
  }
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: W, rows }),
    p([t("", { size: 8 })])];
}

function renderAck(lines) {
  const W = [7860, 1500];
  const rows = lines.map(l => new TableRow({
    children: [textCell(CHECK + l, W[0]), blankCell(W[1])],
  }));
  rows.unshift(new TableRow({
    tableHeader: true,
    children: [
      textCell("Standard", W[0], { bold: true, fill: DARK, color: "FFFFFF" }),
      textCell("Initials", W[1], { bold: true, fill: DARK, color: "FFFFFF", center: true }),
    ],
  }));
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: W, rows }),
    p([t("", { size: 8 })])];
}

function buildDoc(streamlined) {
  const children = [];

  // Title block
  children.push(p([t("ALTR MANAGEMENT", { bold: true, size: 22, color: GOLD, allCaps: true })],
    { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 60 } }));
  children.push(p([t(streamlined ? "Model Intake Form" : "Master Model Intake Form", { bold: true, size: 48 })],
    { alignment: AlignmentType.CENTER, spacing: { after: 60 } }));
  children.push(p([t(streamlined ? "Streamlined Edition" : "Complete Edition", { italics: true, size: 22, color: "666666" })],
    { alignment: AlignmentType.CENTER, spacing: { after: 200 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: GOLD, space: 8 } } }));

  const intro = [
    "This form helps our management and chat teams understand you, your boundaries, and how you want to be represented to fans. It replaces all previous intake forms — completed once and used as the reference document for everyone who works on your account.",
    "Answer everything based on how your account is MARKETED, not your personal life. If a fan asks something not covered here, the chat team will deflect or ask you — they will never make it up.",
    "The more detail you provide, the better we can capture your tone, personality, and preferences. If you don't want to answer something, write a dash ( – ). If anything is unclear, ask before submitting.",
  ];
  for (const line of intro) {
    children.push(p([t(line, { size: 20 })], { spacing: { after: 120 } }));
  }
  children.push(p([t("Never share passwords over unsecured channels. Login details can be provided separately through a secure channel if you prefer.",
    { italics: true, size: 18, color: "8B0000" })], { spacing: { after: 240 } }));

  for (const sec of SECTIONS) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 320, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 2 } },
      children: [t(sec.title, { bold: true, size: 30 })],
    }));
    if (sec.intro) {
      children.push(p([t(sec.intro, { italics: true, size: 18, color: "555555" })], { spacing: { after: 120 } }));
    }
    if (sec.items) children.push(...renderItems(sec.items, streamlined));
    if (sec.checklist) children.push(...renderChecklist(sec.checklist, streamlined));
    if (sec.pricing) children.push(...renderPricing(sec.pricing, streamlined));
    if (sec.itemsAfter) children.push(...renderItems(sec.itemsAfter, streamlined));
    if (sec.socials) children.push(...renderSocials(sec.socials, streamlined));
    if (sec.ack) children.push(...renderAck(sec.ack));
  }

  // Signature block
  children.push(p([t("Confirmation", { bold: true, size: 26 })],
    { spacing: { before: 400, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 2 } } }));
  children.push(p([t("I confirm the information above is accurate and I am comfortable with the boundaries and offerings listed.", { size: 20 })], { spacing: { after: 240 } }));
  children.push(p([t("Model signature: ______________________________          Date: ______________", { size: 20 })], { spacing: { after: 120 } }));

  return new Document({
    styles: {
      default: { document: { run: { font: "Arial", size: 20 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: "Arial", color: DARK },
          paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0 } },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1080, right: 1440, bottom: 1080, left: 1440 },
        },
      },
      headers: {
        default: new Header({ children: [p([
          t("ALTR MANAGEMENT", { bold: true, size: 16, color: GOLD }),
          t("   •   Model Intake — Confidential", { size: 16, color: "999999" }),
        ])] }),
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            t("Confidential — for internal ALTR Management use only    |    Page ", { size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999", font: "Arial" }),
          ],
        })] }),
      },
      children,
    }],
  });
}

// ---------------------------------------------------------------------------
// CSV field schema for the dashboard build
// ---------------------------------------------------------------------------
function csvEscape(s) {
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}
function buildCsv() {
  const lines = ["section,field_label,field_type,options,in_streamlined"];
  const push = (sec, label, type, opts, core) =>
    lines.push([sec, label, type, opts || "", core ? "yes" : "no"].map(csvEscape).join(","));
  for (const sec of SECTIONS) {
    const name = sec.title.replace(/^\d+\.\s*/, "");
    for (const it of sec.items || []) {
      const type = it.type === "yn" ? "yes_no" : it.type === "choice" ? (it.multi ? "multi_select" : "single_select") : it.type === "long" ? "textarea" : "text";
      push(name, it.q, type, (it.opts || []).join(" | "), !!it.core);
    }
    for (const r of sec.checklist || []) push(name, r.item, "yes_no_with_notes", "", !!r.core);
    for (const r of sec.pricing || []) push(name, r.item, "yes_no_with_price", "", !!r.core);
    for (const it of sec.itemsAfter || []) {
      const type = it.type === "yn" ? "yes_no" : it.type === "long" ? "textarea" : "text";
      push(name, it.q, type, (it.opts || []).join(" | "), !!it.core);
    }
    for (const r of sec.socials || []) push(name, r.item + " (handle/link + sells on it?)", "text", "", !!r.core);
    for (const a of sec.ack || []) push(name, a, "acknowledgement", "", true);
  }
  return lines.join("\n") + "\n";
}

// ---------------------------------------------------------------------------
// HTML rendering (used to produce the PDFs via headless Chrome)
// ---------------------------------------------------------------------------
function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

function htmlItems(items, streamlined) {
  let h = "";
  let rows = "";
  const flush = () => { if (rows) { h += `<table class="qa">${rows}</table>`; rows = ""; } };
  for (const it of items || []) {
    if (streamlined && !it.core) continue;
    const note = it.note ? `<div class="note">${esc(it.note)}</div>` : "";
    if (it.type === "long") {
      flush();
      h += `<table class="qa"><tr><td class="label" colspan="2">${esc(it.q)}${note}</td></tr>
            <tr><td class="blank tall" colspan="2">&nbsp;</td></tr></table>`;
    } else if (it.type === "choice") {
      const multi = it.multi ? `<div class="note">(select all that apply)</div>` : "";
      const opts = it.opts.map(o => `<div class="opt">☐ ${esc(o)}</div>`).join("");
      rows += `<tr><td class="label">${esc(it.q)}${note}</td><td>${multi}${opts}</td></tr>`;
    } else if (it.type === "yn") {
      rows += `<tr><td class="label">${esc(it.q)}${note}</td><td>☐ Yes &nbsp;&nbsp;&nbsp; ☐ No</td></tr>`;
    } else {
      rows += `<tr><td class="label">${esc(it.q)}${note}</td><td class="blank">&nbsp;</td></tr>`;
    }
  }
  flush();
  return h;
}

function htmlGrid(rowsData, streamlined, headers, widths) {
  const head = headers.map((x, i) => `<th style="width:${widths[i]}">${esc(x)}</th>`).join("");
  let body = "";
  for (const r of rowsData) {
    if (streamlined && !r.core) continue;
    const cells = headers.slice(1).map(() => `<td class="blank">&nbsp;</td>`).join("");
    body += `<tr><td>${esc(r.item)}</td>${cells}</tr>`;
  }
  return `<table class="grid"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function buildHtml(streamlined) {
  let body = "";
  for (const sec of SECTIONS) {
    body += `<h2>${esc(sec.title)}</h2>`;
    if (sec.intro) body += `<p class="intro">${esc(sec.intro)}</p>`;
    body += htmlItems(sec.items, streamlined);
    if (sec.checklist) body += htmlGrid(sec.checklist, streamlined,
      ["Content type", "YES", "NO", "Notes / limits"], ["44%", "8%", "8%", "40%"]);
    if (sec.pricing) body += htmlGrid(sec.pricing, streamlined,
      ["Custom / item", "YES / NO", "Price ($)", "Notes"], ["42%", "12%", "14%", "32%"]);
    body += htmlItems(sec.itemsAfter, streamlined);
    if (sec.socials) body += htmlGrid(sec.socials, streamlined,
      ["Platform", "Handle / link", "Do you sell on it?"], ["22%", "50%", "28%"]);
    if (sec.ack) body += htmlGrid(sec.ack.map(a => ({ item: "☐ " + a, core: true })), false,
      ["Standard", "Initials"], ["84%", "16%"]);
  }
  const title = streamlined ? "Model Intake Form — Streamlined Edition" : "Master Model Intake Form — Complete Edition";
  return `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title><style>
  @page { size: letter; margin: 0.75in 1in; }
  body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #1a1a1a; }
  .brand { text-align:center; color:#B08D3F; font-weight:bold; letter-spacing:3px; font-size:11pt; }
  h1 { text-align:center; font-size:24pt; margin:4px 0 2px; }
  .edition { text-align:center; font-style:italic; color:#666; border-bottom:2px solid #B08D3F; padding-bottom:12px; margin-bottom:14px; }
  .secwarn { color:#8B0000; font-style:italic; font-size:9pt; }
  h2 { font-size:14pt; border-bottom:2px solid #B08D3F; padding-bottom:3px; margin:22px 0 8px; page-break-after:avoid; }
  .intro { font-style:italic; color:#555; font-size:9pt; margin:4px 0 8px; }
  .note { font-style:italic; color:#666; font-size:8pt; font-weight:normal; }
  table { width:100%; border-collapse:collapse; margin-bottom:10px; }
  td, th { border:1px solid #bbb; padding:5px 8px; vertical-align:top; }
  td.label { background:#F5F1E8; font-weight:bold; width:42%; }
  td.blank { min-width:60px; }
  td.tall { height:52px; }
  .opt { margin:1px 0; }
  th { background:#1a1a1a; color:#fff; text-align:left; font-size:9pt; }
  tr { page-break-inside:avoid; }
  .sig { margin-top:28px; }
  .confirm-title { font-size:14pt; font-weight:bold; border-bottom:2px solid #B08D3F; padding-bottom:3px; }
  </style></head><body>
  <div class="brand">ALTR MANAGEMENT</div>
  <h1>${streamlined ? "Model Intake Form" : "Master Model Intake Form"}</h1>
  <div class="edition">${streamlined ? "Streamlined Edition" : "Complete Edition"}</div>
  <p>This form helps our management and chat teams understand you, your boundaries, and how you want to be represented to fans. It replaces all previous intake forms — completed once and used as the reference document for everyone who works on your account.</p>
  <p>Answer everything based on how your account is <b>MARKETED</b>, not your personal life. If a fan asks something not covered here, the chat team will deflect or ask you — they will never make it up.</p>
  <p>The more detail you provide, the better we can capture your tone, personality, and preferences. If you don't want to answer something, write a dash ( – ). If anything is unclear, ask before submitting.</p>
  <p class="secwarn">Never share passwords over unsecured channels. Login details can be provided separately through a secure channel if you prefer.</p>
  ${body}
  <div class="sig">
    <div class="confirm-title">Confirmation</div>
    <p>I confirm the information above is accurate and I am comfortable with the boundaries and offerings listed.</p>
    <p style="margin-top:24px">Model signature: ______________________________ &nbsp;&nbsp;&nbsp;&nbsp; Date: ______________</p>
  </div>
  </body></html>`;
}

// ---------------------------------------------------------------------------
(async () => {
  fs.writeFileSync("ALTR-Master-Intake-Form.docx", await Packer.toBuffer(buildDoc(false)));
  fs.writeFileSync("ALTR-Master-Intake-Form-Streamlined.docx", await Packer.toBuffer(buildDoc(true)));
  fs.writeFileSync("master-intake-fields.csv", buildCsv());
  fs.writeFileSync("ALTR-Master-Intake-Form.html", buildHtml(false));
  fs.writeFileSync("ALTR-Master-Intake-Form-Streamlined.html", buildHtml(true));

  // question counts
  let full = 0, slim = 0;
  for (const sec of SECTIONS) {
    for (const arr of [sec.items, sec.itemsAfter, sec.checklist, sec.pricing, sec.socials]) {
      for (const it of arr || []) { full++; if (it.core) slim++; }
    }
    full += (sec.ack || []).length; slim += (sec.ack || []).length;
  }
  console.log(`Done. Full form: ${full} fields. Streamlined: ${slim} fields.`);
})();
