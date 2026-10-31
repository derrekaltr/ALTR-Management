#!/usr/bin/env node
// ALTR weekly content-outline site generator. Zero dependencies.
// content/<model>/<YYYY-MM-DD>/<level>/idea-N.md  ->  dist/

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CONTENT = path.join(ROOT, 'content');
const DIST = path.join(ROOT, 'dist');
const ASSETS = path.join(__dirname, 'assets');

const LEVELS = {
  'level-1-implied': { n: 1, name: 'Non-Nude / Implied', rule: 'Never nude. Hand bra, strategic covering, implied framing only.' },
  'level-2-topless': { n: 2, name: 'Topless', rule: 'Topless allowed. Nothing below the waist, ever.' },
  'level-3-full-nude': { n: 3, name: 'Full Nude', rule: 'Full nude allowed.' },
};

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

const titleCase = (slug) => slug.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');

function splitTitle(title) {
  // Second half of the title gets the mint accent, like the reference doc.
  const words = title.split(/\s+/);
  if (words.length < 2) return { plain: title, alt: '' };
  const cut = Math.ceil(words.length / 2);
  return { plain: words.slice(0, cut).join(' '), alt: words.slice(cut).join(' ') };
}

function weekLabel(iso) {
  const d = new Date(iso + 'T00:00:00');
  const fmt = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  return fmt.format(d);
}

function parseIdea(file) {
  const md = fs.readFileSync(file, 'utf8');
  const lines = md.split('\n');
  const idea = { title: path.basename(file, '.md'), theme: '', pairs: '', beats: [], totals: '', notes: '', drive: '' };
  for (const line of lines) {
    const t = line.trim();
    if (t.startsWith('# ')) idea.title = t.slice(2).trim();
    else if (/^\*\*Theme:\*\*/i.test(t)) idea.theme = t.replace(/^\*\*Theme:\*\*/i, '').trim();
    else if (/^\*\*Pairs with script:\*\*/i.test(t)) idea.pairs = t.replace(/^\*\*Pairs with script:\*\*/i, '').trim();
    else if (/^\*\*Totals:\*\*/i.test(t)) idea.totals = t.replace(/^\*\*Totals:\*\*/i, '').trim();
    else if (/^\*\*Filming notes:\*\*/i.test(t)) idea.notes = t.replace(/^\*\*Filming notes:\*\*/i, '').trim();
    else if (/^\*\*Drive folder:\*\*/i.test(t)) idea.drive = t.replace(/^\*\*Drive folder:\*\*/i, '').trim();
    else if (t.startsWith('|')) {
      const cells = t.split('|').slice(1, -1).map((c) => c.trim());
      if (cells.length < 5) continue;
      if (/^#$/.test(cells[0]) || /^-+$/.test(cells[0].replace(/[: ]/g, '-'))) continue; // header/divider
      idea.beats.push({ no: cells[0], type: cells[1], length: cells[2], desc: cells[3], purpose: cells[4] });
    }
  }
  // Derived counts (photos / videos / voice notes / total video minutes)
  const stat = { photos: 0, videos: 0, voice: 0, secs: 0 };
  for (const b of idea.beats) {
    const type = b.type.toLowerCase();
    const m = b.length.match(/(\d+):(\d\d)/);
    const secs = m ? Number(m[1]) * 60 + Number(m[2]) : 0;
    if (type.includes('photo')) stat.photos += 1;
    else if (type.includes('voice')) stat.voice += 1;
    else if (type.includes('video') || type.includes('clip')) { stat.videos += 1; stat.secs += secs; }
  }
  stat.mins = Math.round(stat.secs / 60);
  if (!/^https?:\/\//.test(idea.drive)) idea.drive = ''; // TBD / blank = no folder yet
  idea.stat = stat;
  return idea;
}

function scan() {
  const models = [];
  for (const slug of fs.readdirSync(CONTENT).sort()) {
    const dir = path.join(CONTENT, slug);
    if (!fs.statSync(dir).isDirectory()) continue;
    const model = { slug, name: titleCase(slug), handle: '', weeks: [] };
    const profile = path.join(dir, 'profile.md');
    if (fs.existsSync(profile)) {
      const h1 = fs.readFileSync(profile, 'utf8').match(/^# (.+?)(\s*\((@[^)]+)\))?\s*$/m);
      if (h1) { model.name = h1[1].trim(); model.handle = h1[3] || ''; }
    }
    for (const wk of fs.readdirSync(dir).sort().reverse()) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(wk)) continue;
      const week = { date: wk, label: weekLabel(wk), levels: [] };
      week.pdf = fs.readdirSync(path.join(dir, wk)).find((f) => f.endsWith('.pdf')) || null;
      week.drive = '';
      const driveFile = path.join(dir, wk, 'drive-folder.txt');
      if (fs.existsSync(driveFile)) {
        const v = fs.readFileSync(driveFile, 'utf8').trim();
        if (/^https?:\/\//.test(v)) week.drive = v;
      }
      for (const lv of Object.keys(LEVELS)) {
        const lvDir = path.join(dir, wk, lv);
        if (!fs.existsSync(lvDir)) continue;
        const ideas = fs.readdirSync(lvDir).filter((f) => f.endsWith('.md')).sort()
          .map((f) => ({ file: path.basename(f, '.md'), ...parseIdea(path.join(lvDir, f)) }));
        if (ideas.length) week.levels.push({ key: lv, ...LEVELS[lv], ideas });
      }
      if (week.levels.length) model.weeks.push(week);
    }
    models.push(model);
  }
  return models;
}

/* ---------- templates ---------- */

function page({ title, depth, crumbs, body }) {
  const p = '../'.repeat(depth);
  const crumbHtml = crumbs?.length
    ? `<nav class="crumbs rise">${crumbs.map((c, i) => {
        const sep = i ? '<span class="sep">/</span>' : '';
        return c.href != null ? `${sep}<a href="${c.href}">${esc(c.label)}</a>` : `${sep}<span class="here">${esc(c.label)}</span>`;
      }).join('')}</nav>`
    : '';
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>${esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="${p}assets/style.css">
</head>
<body>
<div class="page">
  <header class="rise">
    <div class="logo"><a href="${p}index.html"><img src="${p}assets/altr-logo.png" alt="ALTR"></a></div>
    <div class="masthead-meta">
      <span class="dept">Talent Development · Content Direction</span>
      <span class="badge">Confidential · Internal</span>
    </div>
  </header>
  ${crumbHtml}
  ${body}
  <footer>
    <div class="fm"><img src="${p}assets/altr-logo.png" alt="ALTR"></div>
    <div class="legal">
      Prepared by ALTR Talent Development<br>
      Confidential · For assigned creator only · Not for distribution
    </div>
  </footer>
</div>
</body>
</html>`;
}

function hero({ kicker, title, chips = [], indexNo = [], ghost, compact }) {
  const t = splitTitle(title);
  return `<div class="hero${compact ? ' compact' : ''}">
    ${ghost ? `<img class="ghost" src="${ghost}" alt="" aria-hidden="true">` : ''}
    <div class="kicker rise d1">${esc(kicker)}</div>
    <h1 class="rise d2">${esc(t.plain)}${t.alt ? ` <span class="alt">${esc(t.alt)}</span>` : ''}</h1>
    ${indexNo.length ? `<div class="index-no rise d3">${indexNo.map(esc).join('<br>')}</div>` : ''}
    ${chips.length ? `<div class="hero-foot rise d3">${chips.map((c) => `<span class="chip${c.accent ? ' accent' : ''}">${esc(c.label)}</span>`).join('')}</div>` : ''}
  </div>`;
}

function rows(items) {
  return `<div class="folder-map">${items.map((it) => `
    <a class="folder-row" href="${it.href}">
      <span class="f-name">${esc(it.name)}<small>${esc(it.sub)}</small></span>
      <span class="f-open">Open ↗</span>
    </a>`).join('')}
  </div>`;
}

/* ---------- pages ---------- */

function ideaPage(model, week, level, idea, n) {
  const s = idea.stat;
  const chips = [
    { label: `Level ${level.n} · ${level.name}`, accent: true },
    { label: `${idea.beats.length} Assets In Sequence` },
    { label: `${s.photos} Photos` },
    { label: `${s.videos} Videos · ${s.mins} Min` },
    { label: `${s.voice} Voice Note${s.voice === 1 ? '' : 's'}` },
  ];
  const beats = idea.beats.map((b, i) => {
    const main = /main/i.test(b.purpose);
    return `<div class="beat${main ? ' is-ppv' : ''}">
      <div class="beat-no">${esc(b.no)}<small>Asset</small></div>
      <div class="beat-type"><span class="fmt">${esc(b.type)}</span><br>${esc(b.length === '—' || !b.length ? 'Still' : b.length)}</div>
      <div class="beat-desc">${esc(b.desc)}</div>
      <div class="beat-purpose"><b>${esc(b.purpose)}</b>${main ? 'The centerpiece of the drip — everything before it builds here.' : ''}</div>
    </div>`;
  }).join('\n');

  const body = `
  ${hero({
    kicker: `${model.name} · Week of ${week.label}`,
    title: idea.title,
    chips,
    indexNo: [`Idea № ${String(n).padStart(2, '0')}`, `Level ${level.n} · ${level.name}`],
    ghost: '../../../assets/altr-ghost.png',
  })}
  <section class="rise d4">
    <div class="sec-head"><span class="sec-num">01</span><h2>The Concept</h2></div>
    <p class="sec-sub">${esc(idea.theme)}${idea.pairs && idea.pairs !== 'TBD' ? ` — pairs with <strong>${esc(idea.pairs)}</strong>.` : ''}
    Level rule for every asset: ${esc(level.rule)}</p>
    <div class="sheet">${beats}</div>
  </section>
  <section>
    <div class="sec-head"><span class="sec-num">02</span><h2>Content Summary</h2></div>
    <p class="sec-sub">Everything the shoot needs to produce, at a glance.</p>
    <div class="summary-grid">
      <div class="sum-cell"><div class="label">Photos</div><div class="value">${s.photos}</div><div class="note">Stills in the drip sequence.</div></div>
      <div class="sum-cell"><div class="label">Videos</div><div class="value">${s.videos} <small>${s.mins} MIN</small></div><div class="note">Total runtime across all clips.</div></div>
      <div class="sum-cell"><div class="label">Voice Notes</div><div class="value">${s.voice}</div><div class="note">Placed between visuals to keep it live.</div></div>
      <div class="sum-cell"><div class="label">Content Level</div><div class="value">L${level.n}</div><div class="note">${esc(level.name)}. ${esc(level.rule)}</div></div>
    </div>
  </section>
  ${(idea.drive || week.drive) ? `<section>
    <div class="sec-head"><span class="sec-num">03</span><h2>Submit Your Content</h2></div>
    <p class="sec-sub">Shoot it, name each file by its asset number (01-photo, 05-video…), and drop everything for this idea into its folder.</p>
    <div class="submit-cta">
      <a class="cta-main" href="${idea.drive || week.drive}" target="_blank" rel="noopener">Open Upload Folder <span class="arrow">↗</span></a>
      <p class="cta-note">${idea.drive ? 'This folder is for this idea only.' : "This week's shared folder — make a subfolder named after the idea."} The Drive app works best for video.</p>
    </div>
  </section>` : ''}
  <div class="notes-panel">
    <img class="mono-mark" src="../../../assets/altr-mark-dark.png" alt="" aria-hidden="true">
    <div class="label">Filming Notes</div>
    <p>${esc(idea.notes)}</p>
  </div>`;

  return page({
    title: `ALTR · ${model.name} · ${idea.title}`,
    depth: 3,
    crumbs: [
      { label: 'Models', href: '../../../index.html' },
      { label: model.name, href: '../../index.html' },
      { label: `Week of ${week.label}`, href: '../index.html' },
      { label: idea.title },
    ],
    body,
  });
}

function weekPage(model, week) {
  const totalIdeas = week.levels.reduce((a, l) => a + l.ideas.length, 0);
  const sections = week.levels.map((level, i) => `
  <section class="${i === 0 ? 'rise d4' : ''}">
    <div class="sec-head"><span class="sec-num">0${i + 1}</span><h2>Level ${level.n} · ${esc(level.name)}</h2></div>
    <p class="sec-sub">${esc(level.rule)}</p>
    ${rows(level.ideas.map((idea, j) => ({
      href: `${level.key}/${idea.file}.html`,
      name: `${String(j + 1).padStart(2, '0')} · ${idea.title}`,
      sub: `${idea.stat.photos} photo${idea.stat.photos === 1 ? '' : 's'} · ${idea.stat.videos} video${idea.stat.videos === 1 ? '' : 's'} (${idea.stat.mins} min) · ${idea.stat.voice} voice note${idea.stat.voice === 1 ? '' : 's'}`,
    })))}
  </section>`).join('\n');

  const body = `
  ${hero({
    kicker: `${model.name} · Weekly Content Pack`,
    title: `Week of ${week.label}`,
    chips: [
      { label: `${totalIdeas} New Ideas`, accent: true },
      ...week.levels.map((l) => ({ label: `Level ${l.n} · ${l.ideas.length} Ideas` })),
    ],
    ghost: '../../assets/altr-ghost.png',
    compact: true,
  })}
  ${week.pdf ? `<div class="folder-map flush rise d4"><a class="folder-row" href="${week.pdf}">
    <span class="f-name">Weekly Pack PDF<small>Hand-off copy for the creator · all ${totalIdeas} briefs, one file</small></span>
    <span class="f-open">Download ↗</span></a></div>` : ''}
  ${sections}
  ${(week.drive || week.levels.some((l) => l.ideas.some((i) => i.drive))) ? `<section>
    <div class="sec-head"><span class="sec-num">0${week.levels.length + 1}</span><h2>Upload Folders</h2></div>
    <p class="sec-sub">Every idea has a matching Drive folder. Shoot it, name it by asset number, drop it in.</p>
    ${rows([
      ...(week.drive ? [{ href: week.drive, name: '00 · Week Root Folder', sub: 'All idea folders live inside' }] : []),
      ...week.levels.flatMap((l) => l.ideas.filter((i) => i.drive).map((i, j) => ({
        href: i.drive, name: `L${l.n} · ${i.title}`, sub: 'Upload folder for this idea' })))
    ])}
  </section>` : ''}`;

  return page({
    title: `ALTR · ${model.name} · Week of ${week.label}`,
    depth: 2,
    crumbs: [
      { label: 'Models', href: '../../index.html' },
      { label: model.name, href: '../index.html' },
      { label: `Week of ${week.label}` },
    ],
    body,
  });
}

function modelPage(model) {
  const body = `
  ${hero({
    kicker: 'Content Direction · Weekly Packs',
    title: model.name,
    chips: [
      ...(model.handle ? [{ label: model.handle, accent: true }] : []),
      { label: `${model.weeks.length} Week${model.weeks.length === 1 ? '' : 's'} Published` },
    ],
    ghost: '../assets/altr-ghost.png',
    compact: true,
  })}
  <section class="tight rise d4">
    <div class="sec-head"><span class="sec-num">01</span><h2>Weekly Packs</h2></div>
    <p class="sec-sub">Newest first. Each pack holds this week's ideas at every content level.</p>
    ${model.weeks.length ? rows(model.weeks.map((w) => ({
      href: `${w.date}/index.html`,
      name: `Week of ${w.label}`,
      sub: w.levels.map((l) => `L${l.n} × ${l.ideas.length}`).join(' · '),
    }))) : '<p class="sec-sub">No packs published yet.</p>'}
  </section>`;

  return page({
    title: `ALTR · ${model.name}`,
    depth: 1,
    crumbs: [{ label: 'Models', href: '../index.html' }, { label: model.name }],
    body,
  });
}

function indexPage(models) {
  const body = `
  ${hero({
    kicker: 'Talent Development · Content Direction',
    title: 'Weekly Content Outlines',
    chips: [
      { label: `${models.length} Models`, accent: true },
      { label: 'New Pack Every Monday' },
      { label: '3 Content Levels' },
    ],
    ghost: 'assets/altr-ghost.png',
  })}
  <section class="rise d4">
    <div class="sec-head"><span class="sec-num">01</span><h2>Models</h2></div>
    <p class="sec-sub">One folder per model. Inside: dated weekly packs, each broken down by content level with three fresh ideas per level.</p>
    ${rows(models.map((m) => ({
      href: `${m.slug}/index.html`,
      name: m.name + (m.handle ? ` · ${m.handle}` : ''),
      sub: m.weeks.length
        ? `${m.weeks.length} week${m.weeks.length === 1 ? '' : 's'} · latest ${m.weeks[0].label}`
        : 'No packs yet',
    })))}
  </section>`;

  return page({ title: 'ALTR · Weekly Content Outlines', depth: 0, crumbs: [], body });
}

/* ---------- printable weekly pack (rendered to PDF by scripts/make-pdfs.sh) ---------- */

function packPage(model, week) {
  const ideaBlock = (level, idea, n) => {
    const s = idea.stat;
    const rows = idea.beats.map((b) => `
      <tr class="${/main/i.test(b.purpose) ? 'is-main' : ''}">
        <td class="c-no">${esc(b.no)}</td>
        <td class="c-type">${esc(b.type)}<span>${esc(!b.length || b.length === '—' ? 'Still' : b.length)}</span></td>
        <td class="c-desc">${esc(b.desc)}</td>
        <td class="c-purp">${esc(b.purpose)}</td>
      </tr>`).join('');
    return `<section class="pdf-page${idea.beats.length >= 7 ? ' dense' : ''}">
      <div class="p-head">
        <img src="../../assets/altr-logo.png" alt="ALTR">
        <div class="p-meta">${esc(model.name)} · Week of ${week.label} · Confidential</div>
      </div>
      <div class="p-kicker">Level ${level.n} · ${esc(level.name)} — Idea ${String(n).padStart(2, '0')}</div>
      <h1>${esc(idea.title)}</h1>
      <p class="p-theme">${esc(idea.theme)}. <em>Level rule: ${esc(level.rule)}</em></p>
      <table class="p-sheet">
        <thead><tr><th>#</th><th>Asset</th><th>Direction</th><th>Purpose</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="p-totals">
        <div><b>${s.photos}</b>Photos</div>
        <div><b>${s.videos}</b>Videos · ${s.mins} min</div>
        <div><b>${s.voice}</b>Voice notes</div>
        <div><b>L${level.n}</b>${esc(level.name)}</div>
      </div>
      <div class="p-notes"><span>Filming notes</span>${esc(idea.notes)}</div>
      ${(idea.drive || week.drive) ? `<div class="p-submit">Upload finished assets → <a href="${idea.drive || week.drive}">${(idea.drive || week.drive).replace('https://', '')}</a></div>` : ''}
    </section>`;
  };

  const total = week.levels.reduce((a, l) => a + l.ideas.length, 0);
  const toc = week.levels.map((l) => `
    <div class="cv-level">
      <div class="cv-lvl-name">Level ${l.n} · ${esc(l.name)}</div>
      ${l.ideas.map((idea, j) => `<div class="cv-idea"><i>${String(j + 1).padStart(2, '0')}</i>${esc(idea.title)}</div>`).join('')}
    </div>`).join('');

  const body = week.levels
    .flatMap((level) => level.ideas.map((idea, j) => ideaBlock(level, idea, j + 1)))
    .join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ALTR · ${esc(model.name)} · Week of ${week.label}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --ink:#1d1d1b; --raise:#242422; --line:rgba(235,236,220,0.16); --bone:#ebecdc; --faint:rgba(235,236,220,0.85);
          --mint:#b6f2e5; --wash:rgba(182,242,229,0.08); --sans:"Archivo","Helvetica Neue",sans-serif; --mono:"Spline Sans Mono","SF Mono",monospace; }
  * { margin:0; padding:0; box-sizing:border-box; }
  @page { size: A4; margin: 0; }
  body { background: var(--ink); color: var(--bone); font-family: var(--sans);
         -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .pdf-page { width: 210mm; min-height: 297mm; padding: 13mm 15mm 11mm; page-break-after: always;
              background: var(--ink); display: flex; flex-direction: column; }
  .p-head { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); padding-bottom:5mm; }
  .p-head img { height: 7mm; }
  .p-meta, .p-kicker, .cv-lvl-name { font-family: var(--mono); font-size: 8.5pt; letter-spacing: 0.18em; text-transform: uppercase; }
  .p-meta { color: var(--faint); }
  .p-kicker { color: var(--mint); margin: 7mm 0 2.5mm; }
  h1 { font-weight: 800; font-stretch: 118%; font-size: 23pt; line-height: 1.02; text-transform: uppercase; letter-spacing: -0.01em; }
  .p-theme { margin: 3mm 0 4.5mm; font-size: 10pt; line-height: 1.5; color: var(--faint); max-width: 165mm; }
  .p-theme em { color: var(--mint); font-style: normal; }
  .p-sheet { width: 100%; border-collapse: collapse; border-top: 1.5px solid var(--bone); }
  .p-sheet th { font-family: var(--mono); font-size: 7.5pt; letter-spacing: 0.2em; text-transform: uppercase;
                color: var(--faint); text-align: left; padding: 2.5mm 2mm; border-bottom: 1px solid var(--line); }
  .p-sheet td { padding: 2.4mm 2mm; border-bottom: 1px solid var(--line); vertical-align: top; font-size: 9pt; line-height: 1.45; }
  .c-no { font-weight: 800; font-stretch: 118%; font-size: 13pt; width: 8mm; }
  .c-type { font-family: var(--mono); font-size: 7.5pt; letter-spacing: 0.12em; text-transform: uppercase; width: 26mm; }
  .c-type span { display: block; color: var(--faint); margin-top: 1.5mm; }
  .c-desc { color: var(--bone); }
  .c-purp { font-family: var(--mono); font-size: 7.5pt; letter-spacing: 0.16em; text-transform: uppercase; color: var(--mint); width: 18mm; }
  tr.is-main td { background: var(--wash); }
  tr.is-main .c-no { color: var(--mint); }
  .p-totals { display: grid; grid-template-columns: repeat(4,1fr); margin-top: 4.5mm; page-break-inside: avoid; border: 1px solid var(--line); }
  .p-totals div { padding: 3.2mm; border-right: 1px solid var(--line); font-family: var(--mono); font-size: 7.5pt;
                  letter-spacing: 0.18em; text-transform: uppercase; color: var(--faint); background: var(--raise); }
  .p-totals div:last-child { border-right: none; }
  .p-totals b { display: block; font-family: var(--sans); font-weight: 800; font-stretch: 118%; font-size: 17pt; color: var(--bone); margin-bottom: 1.5mm; }
  .p-notes { margin-top: 4.5mm; background: var(--mint); color: var(--ink); border-radius: 2mm; padding: 5mm 6mm; font-size: 9pt; page-break-inside: avoid; line-height: 1.55; }
  .p-notes span { display: block; font-family: var(--mono); font-size: 7.5pt; letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 2.5mm; }
  .p-foot { margin-top: auto; padding-top: 4mm; border-top: 1px solid var(--line); font-family: var(--mono);
            font-size: 7pt; letter-spacing: 0.16em; text-transform: uppercase; color: var(--faint); }
  .p-submit { margin-top: 3.5mm; font-family: var(--mono); font-size: 8pt; letter-spacing: 0.1em;
              text-transform: uppercase; color: var(--faint); }
  .p-submit a { color: var(--mint); text-decoration: none; border-bottom: 1px solid var(--mint); text-transform: none; letter-spacing: 0.04em; }
  /* dense mode for briefs with 7+ assets */
  .pdf-page.dense h1 { font-size: 19pt; }
  .pdf-page.dense .p-kicker { margin: 5mm 0 2mm; }
  .pdf-page.dense .p-theme { margin: 2.5mm 0 3.5mm; font-size: 9pt; }
  .pdf-page.dense .p-sheet td { padding: 1.9mm 2mm; font-size: 8.5pt; line-height: 1.35; }
  .pdf-page.dense .c-no { font-size: 11pt; }
  .pdf-page.dense .p-totals { margin-top: 3.5mm; }
  .pdf-page.dense .p-totals div { padding: 2.6mm; }
  .pdf-page.dense .p-totals b { font-size: 14pt; margin-bottom: 1mm; }
  .pdf-page.dense .p-notes { margin-top: 3.5mm; padding: 4mm 5mm; font-size: 8.5pt; line-height: 1.45; }
  .pdf-page.dense .p-submit { margin-top: 2.5mm; font-size: 7.5pt; }
  /* cover */
  .cover .cv-kicker { font-family: var(--mono); font-size: 9.5pt; letter-spacing: 0.3em; text-transform: uppercase; color: var(--mint); margin: 24mm 0 8mm; }
  .cover h1 { font-size: 40pt; max-width: 160mm; }
  .cover h1 .alt { color: var(--mint); }
  .cover .cv-sub { margin-top: 8mm; font-size: 11pt; color: var(--faint); max-width: 140mm; line-height: 1.6; }
  .cv-level { margin-top: 10mm; }
  .cv-lvl-name { color: var(--mint); border-bottom: 1px solid var(--line); padding-bottom: 2.5mm; margin-bottom: 2.5mm; }
  .cv-idea { font-size: 11pt; padding: 2mm 0; border-bottom: 1px solid var(--line); }
  .cv-idea i { font-family: var(--mono); font-style: normal; font-size: 8pt; color: var(--faint); margin-right: 5mm; }
</style>
</head>
<body>
  <section class="pdf-page cover">
    <div class="p-head">
      <img src="../../assets/altr-logo.png" alt="ALTR">
      <div class="p-meta">Talent Development · Confidential</div>
    </div>
    <div class="cv-kicker">Weekly Content Pack · ${total} Ideas · ${week.levels.length} Level${week.levels.length === 1 ? '' : 's'}</div>
    <h1>${esc(model.name)}<br><span class="alt">Week of ${week.label}</span></h1>
    <p class="cv-sub">Each idea is a complete filming brief: the asset drip in send order, durations,
    voice-note placement, and filming notes. Shoot only the ideas at or above your comfort level.</p>
    ${toc}
    ${week.drive ? `<div class="p-submit">Submit all content → <a href="${week.drive}">${week.drive.replace('https://', '')}</a></div>` : ''}
    <div class="p-foot">Prepared by ALTR Talent Development · For assigned creator only · Not for distribution</div>
  </section>
  ${body}
</body>
</html>`;
}

/* ---------- build ---------- */

function build() {
  fs.rmSync(DIST, { recursive: true, force: true });
  fs.mkdirSync(path.join(DIST, 'assets'), { recursive: true });
  for (const f of fs.readdirSync(ASSETS)) {
    fs.copyFileSync(path.join(ASSETS, f), path.join(DIST, 'assets', f));
  }

  // publish the brand kit at /brand/
  const DESIGN = path.join(ROOT, 'design');
  if (fs.existsSync(DESIGN)) {
    fs.mkdirSync(path.join(DIST, 'brand'), { recursive: true });
    for (const f of ['altr-report-template.html', 'altr-tokens.css', 'altr-brand-kit.zip']) {
      const src = path.join(DESIGN, f);
      if (fs.existsSync(src)) fs.copyFileSync(src, path.join(DIST, 'brand', f));
    }
    const dAssets = path.join(DESIGN, 'assets');
    if (fs.existsSync(dAssets)) {
      for (const f of fs.readdirSync(dAssets)) {
        fs.copyFileSync(path.join(dAssets, f), path.join(DIST, 'brand', f));
      }
    }
  }

  const models = scan();
  fs.writeFileSync(path.join(DIST, 'index.html'), indexPage(models));

  let pages = 1;
  for (const model of models) {
    fs.mkdirSync(path.join(DIST, model.slug), { recursive: true });
    fs.writeFileSync(path.join(DIST, model.slug, 'index.html'), modelPage(model));
    pages += 1;
    for (const week of model.weeks) {
      const wkDir = path.join(DIST, model.slug, week.date);
      fs.mkdirSync(wkDir, { recursive: true });
      fs.writeFileSync(path.join(wkDir, 'index.html'), weekPage(model, week));
      fs.writeFileSync(path.join(wkDir, 'pack.html'), packPage(model, week));
      if (week.pdf) {
        fs.copyFileSync(path.join(CONTENT, model.slug, week.date, week.pdf), path.join(wkDir, week.pdf));
      }
      pages += 1;
      for (const level of week.levels) {
        const lvDir = path.join(wkDir, level.key);
        fs.mkdirSync(lvDir, { recursive: true });
        level.ideas.forEach((idea, j) => {
          fs.writeFileSync(path.join(lvDir, `${idea.file}.html`), ideaPage(model, week, level, idea, j + 1));
          pages += 1;
        });
      }
    }
  }
  console.log(`Built ${pages} pages for ${models.length} models → dist/`);
}

build();
