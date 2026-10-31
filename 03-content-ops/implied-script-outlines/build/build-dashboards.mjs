// ALTR creator dashboard generator
// Produces one self-contained, private HTML file per creator (only their own
// data + the scripts at their content level) plus a master internal index.
// Re-run any time to add/update creators or scripts:  node build/build-dashboards.mjs

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { createHash } from 'crypto';

// Stable unguessable slug per creator (same input → same slug on every build,
// so live links never break on regeneration).
const SLUG_SALT = 'altr-hub-2026-v1';
const slugOf = (c) => createHash('sha256').update(`${c.handle}|${SLUG_SALT}`).digest('hex').slice(0, 12);
const fileOf = (c) => `c-${slugOf(c)}.html`;

// When BASE_URL is set (after deploy), the internal index shows and links the
// live public URLs instead of local relative files.
const BASE = (process.env.BASE_URL || '').replace(/\/$/, '');

const __dir = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dir, '..');
const OUT = resolve(ROOT, 'dashboards');
mkdirSync(OUT, { recursive: true });

const b64 = (p) => readFileSync(resolve(ROOT, p)).toString('base64');
const LOGO_MINT = `data:image/png;base64,${b64('.context/attachments/1vezTj/18.png')}`;
const MONO_CREAM = `data:image/png;base64,${b64('.context/attachments/tAYW3n/20.png')}`;
const MONO_BLACK = `data:image/png;base64,${b64('.context/attachments/ilMQnA/19.png')}`;

// ————————————————————————————————————————————————————————————————
// CREATORS
// ————————————————————————————————————————————————————————————————
const CREATORS = [
  { name: 'Amber Rodriguez', handle: 'ambzy', level: 1 },

  { name: 'Elizabeth Kovalenko', handle: 'lizakovalenkoo', level: 2 },
  { name: 'Guadalupe', handle: 'mariapero', level: 2 },
  { name: 'Kirsten Bobbette', handle: 'amberhazexo', level: 2 },
  { name: 'Lauren Blake', handle: 'laurenblake', level: 2 },
  { name: 'Naza', handle: 'miamigirl26', level: 2 },
  { name: 'Sarah Henderson', handle: 'brunnettebaby', level: 2 },
  { name: 'Shayna Holt', handle: 'shaynaholt', level: 2 },
  { name: 'Jane Aubrun Mautin', handle: 'Jane.mautin', level: 2 },

  { name: 'Alanna Pow', handle: 'alannasworldxfree', level: 3 },
  { name: 'Alex Paige Moore', handle: 'alexpaigemoore', level: 3 },
  { name: 'Anllela Sagra', handle: 'anllelasagra', level: 3 },
  { name: 'Barbara Duarte', handle: 'barbarabarbiee', level: 3 },
  { name: 'Callander Bullough', stage: 'Mila Brooks', handle: 'Milaabrookss', level: 3 },
  { name: 'Essence Hoffman', handle: 'essencehoff', level: 3 },
  { name: 'Haleigh Cox', handle: 'haleighcox', level: 3 },
  { name: 'Lauryn Alease Williams', stage: 'LA', handle: 'lalovetheboss', level: 3 },
  { name: 'Lilia Culverwell', stage: 'Lilia Summers', handle: 'lilia_summers', level: 3 },
  { name: 'Lilly Milbourne', stage: 'Gwen', handle: 'gwensingervip', level: 3 },
  { name: 'Maja Metelko', stage: 'Celine', handle: 'renceline', level: 3 },
  { name: 'Mya Bernal', stage: 'Aly Main', handle: 'myabernal', level: 3 },
  { name: 'Sarah Lloyd', handle: 'Sarahlloyd', level: 3 },
  { name: 'Valerie Bragg', stage: 'Vale Rae', handle: 'valeraexo', level: 3 },
  { name: 'Isabella', handle: 'isabellakcups', level: 3 },
];

const LEVELS = {
  1: { name: 'Level 1', tag: 'Implied / Non-Nude', accent: '#b6f2e5', ink: '#1d1d1b' },
  2: { name: 'Level 2', tag: 'Topless', accent: '#ddc38a', ink: '#1d1d1b' },
  3: { name: 'Level 3', tag: 'Full / Explicit', accent: '#d98c86', ink: '#1d1d1b' },
};

// ————————————————————————————————————————————————————————————————
// SCRIPT LIBRARY  (Level 1 written out; Levels 2 & 3 = ready-to-fill slots)
// ————————————————————————————————————————————————————————————————
const GYM_FOLDERS = [
  { n: '01', label: 'Free Photos — Gym (Beats 4–5)', href: 'https://drive.google.com/drive/folders/14Dy6Rgsv8_Akt7Z4HWVeS_7_eNdVBQm2' },
  { n: '02', label: 'Free Photo + Video — Poolside (Beats 9–10)', href: 'https://drive.google.com/drive/folders/1wzmQxHU6W1Rr9TszLeDm9Iab34Qb19sh' },
  { n: '03', label: 'Locked PPV — Underwater Clip (Beat 13)', href: 'https://drive.google.com/drive/folders/18cPBPaSAj8p6C0zYbijNGUAiAFUjGlkH' },
  { n: '04', label: "Optional PPV 2 — Bonus (If He's Buying)", href: 'https://drive.google.com/drive/folders/1onHOloWk-FjxqKCTwWjjkOO6MSoc1LUs' },
];

const SCRIPTS = [
  {
    id: 'gym-pool', level: 1,
    title: 'Gym Crush to Poolside Tease',
    kicker: 'Sexting Set · Script 001',
    tagline: 'From casual gym check-in to first paywall — girlfriend energy, zero explicit content.',
    chips: ['Non-Nude / Implied', '15 Message Beats', '2 Free Visuals + 1 Clip', '1–2 Locked PPV', '20–45 Min Session'],
    phases: [
      { label: 'Phase 01', name: 'Warm Open', beats: [
        { no: '1–3', noLabel: 'Beats', fmt: 'Text Only', sub: '1–2 sentences each', desc: "Gym check-in. Casual, flirty but innocent — she's talking about her actual day, not performing.", purpose: 'Relationship building. Establish girlfriend-energy rapport before anything visual.' },
        { no: '4–5', noLabel: 'Beats', fmt: 'Free Photo', sub: 'Implied / non-nude', desc: 'Gym selfie or workout clip — leggings, sports bra. Fit, sweaty, confident. <strong>Zero explicit content.</strong>', purpose: 'Visual hook. Authentic to her real life; earns attention without spending anything.', upload: 1 },
      ]},
      { label: 'Phase 02', name: 'Building Heat', beats: [
        { no: '6–8', noLabel: 'Beats', fmt: 'Text Only', sub: 'Playful challenges', desc: 'Building heat through banter. <span class="q">"Bet you couldn\'t keep up with my cardio."</span>', purpose: 'Transition. Shift from friendly to charged without breaking her voice.' },
        { no: '9–10', noLabel: 'Beats', fmt: 'Free Photo / Video', sub: 'Implied / non-nude', desc: 'Poolside. Wet hair, bikini cover-up or one-piece. Water dripping, towel dropping, looking away from camera.', purpose: 'Tease escalation. Intimacy through suggestion — never exposure.', upload: 2 },
      ]},
      { label: 'Phase 03', name: 'Tension Peak', beats: [
        { no: '11–12', noLabel: 'Beats', fmt: 'Text Only', sub: 'Suggestive, never explicit', desc: 'Sexual tension at its peak. <span class="q">"This water\'s freezing but I\'m still burning up."</span>', purpose: 'Tension peak. Let the subtext do the work — the restraint is the product.' },
      ]},
      { label: 'Phase 04', name: 'The Paywall', beats: [
        { no: '13', noLabel: 'Beat', fmt: 'First Locked PPV', sub: 'Clip · 15–20 sec', ppv: true, desc: 'Underwater slow-mo — legs, silhouette, maybe adjusting bikini bottom with a quick smirk. Still non-nude, but intimate enough to feel exclusive.', purposeLabel: 'Paywall Test', purpose: 'First conversion point. Exclusivity is the sell, not explicitness.', upload: 3 },
        { no: '14–15', noLabel: 'Beats', fmt: 'Text Only', sub: 'Reactive', desc: "React to his unlock, keep momentum. If he buys, you know he's ready for more later.", purpose: "Gauge interest. The unlock is the signal — read it, don't chase it." },
      ]},
    ],
    summary: [
      { label: 'Text Messages', value: '12–15', note: 'Short, punchy. Spaced 1–2 minutes apart to feel live.' },
      { label: 'Free Visual Teases', value: '2', small: '+1 CLIP', note: '100% non-nude. Gym & pool — authentic to her life.' },
      { label: 'Locked PPV Pieces', value: '1–2', note: "15–20 seconds max. Implied only. Second piece optional if he's buying." },
      { label: 'Session Time', value: '20–45', small: 'MIN', note: 'Real-time. Depends on his response speed.' },
    ],
    psych: {
      paras: [
        'She gets to <em>actually talk about her day</em> and feel like herself. The fan gets girlfriend energy — not camgirl energy — and the tension builds organically from her real life rather than fake <em>"I\'m so horny"</em> scripts.',
        'If he wants more explicit later, <em>he</em> has to push for it. She\'s responding to him — never leading with it.',
      ],
      principles: [
        { b: 'For Her', t: 'Sustainable. She stays in her own voice and her own life — no persona fatigue, no scripts that feel fake to write.' },
        { b: 'For Him', t: 'The scarcity is real. Restraint reads as authenticity, and the unlock feels like his idea.' },
      ],
    },
    folders: GYM_FOLDERS,
  },

  {
    id: 'coffee-cozy', level: 1,
    title: 'Coffee Run to Cozy Night In',
    kicker: 'Sexting Set · Script 002',
    tagline: "A full day arc — morning coffee to bedtime — soft, domestic, girl-next-door. Implied only.",
    chips: ['Non-Nude / Implied', '15 Message Beats', '2 Free Visuals + 1 Clip', '1 Locked PPV', '25–50 Min Session'],
    phases: [
      { label: 'Phase 01', name: 'Morning Hello', beats: [
        { no: '1–3', noLabel: 'Beats', fmt: 'Text Only', sub: '1–2 sentences each', desc: 'Sleepy good-morning texts. Heading out for coffee, warm and unguarded — like he\'s the first person she talks to.', purpose: 'Relationship building. Wake up in his phone; own the start of his day.' },
        { no: '4–5', noLabel: 'Beats', fmt: 'Free Photo', sub: 'Implied / non-nude', desc: 'Coffee-shop mirror selfie — oversized sweater, bare legs implied, hair up, barely any makeup. <strong>Cozy, not staged.</strong> <span class="q">"no makeup, don\'t judge me 😅"</span>', purpose: 'Visual hook. The "real" look builds trust and intimacy fast.', upload: 1 },
      ]},
      { label: 'Phase 02', name: 'Afternoon Drift', beats: [
        { no: '6–8', noLabel: 'Beats', fmt: 'Text Only', sub: 'Playful, domestic', desc: 'Running errands, being cute. <span class="q">"wish you were here to carry my bags… and other things"</span>', purpose: 'Transition. Fold him into her day so home feels shared.' },
        { no: '9–10', noLabel: 'Beats', fmt: 'Free Photo / Video', sub: 'Implied / non-nude', desc: 'Back home, changed into an oversized tee on the couch under a blanket. Legs tucked, soft lamp light, looking up at the camera.', purpose: 'Tease escalation. The "his-shirt" energy is the whole play.', upload: 2 },
      ]},
      { label: 'Phase 03', name: 'Wind Down', beats: [
        { no: '11–12', noLabel: 'Beats', fmt: 'Text Only', sub: 'Suggestive, never explicit', desc: 'Getting into bed. <span class="q">"it\'s so cold in here… kinda wish I had some company"</span>', purpose: 'Tension peak. Loneliness-as-invitation without ever asking.' },
      ]},
      { label: 'Phase 04', name: 'The Paywall', beats: [
        { no: '13', noLabel: 'Beat', fmt: 'First Locked PPV', sub: 'Clip · 15–20 sec', ppv: true, desc: 'Lying in bed in the oversized tee, warm low light, sheets pulled up, a slow camera tilt and a bitten lip. Implied under the covers — still non-nude.', purposeLabel: 'Paywall Test', purpose: 'First conversion. The bedroom framing feels private and exclusive.', upload: 3 },
        { no: '14–15', noLabel: 'Beats', fmt: 'Text Only', sub: 'Reactive', desc: 'React to the unlock, then soft goodnight energy. <span class="q">"okay now I really can\'t sleep… goodnight 🙈"</span>', purpose: 'Gauge interest and leave the door open for tomorrow.' },
      ]},
    ],
    summary: [
      { label: 'Text Messages', value: '12–15', note: 'Warm and unhurried. Morning, afternoon, night beats.' },
      { label: 'Free Visual Teases', value: '2', small: '+1 CLIP', note: 'Non-nude. Coffee-shop selfie + couch/cozy clip.' },
      { label: 'Locked PPV Pieces', value: '1', note: '15–20 sec bedroom clip, implied only.' },
      { label: 'Session Time', value: '25–50', small: 'MIN', note: 'Drip across a "day" or run compressed in one sitting.' },
    ],
    psych: {
      paras: [
        'This one sells <em>domestic intimacy</em>. She\'s not a fantasy on a set — she\'s the girl he texts good morning. The oversized-tee, no-makeup framing reads as "you\'re seeing the real me," which is worth more than skin.',
        'The bedroom PPV lands because he\'s spent the whole day being let into her routine. By nighttime, the unlock feels like being invited in — not sold to.',
      ],
      principles: [
        { b: 'For Her', t: 'Low-effort, high-authenticity. Filmable on any ordinary day at home — no location, no glam team.' },
        { b: 'For Him', t: 'Girlfriend fantasy at its purest: routine, comfort, and the feeling that he\'s the one she winds down with.' },
      ],
    },
  },

  {
    id: 'beach-sunset', level: 1,
    title: 'Beach Day to Sunset Wind-Down',
    kicker: 'Sexting Set · Script 003',
    tagline: 'Vacation energy — arrival to golden hour. Travel FOMO plus one exclusive sunset clip. Implied only.',
    chips: ['Non-Nude / Implied', '15 Message Beats', '2 Free Visuals + 1 Clip', '1 Locked PPV', '30–60 Min Session'],
    phases: [
      { label: 'Phase 01', name: 'Morning Departure', beats: [
        { no: '1–3', noLabel: 'Beats', fmt: 'Text Only', sub: '1–2 sentences each', desc: 'Heading to the beach, buzzing. <span class="q">"the water\'s unreal today — you\'d never want to leave"</span>', purpose: 'Relationship building. Invite him along for the day in spirit.' },
        { no: '4–5', noLabel: 'Beats', fmt: 'Free Photo', sub: 'Implied / non-nude', desc: 'Arrival shot — sundress over swimwear, or a one-piece with sunglasses. Sun-drenched, candid, happy. <strong>Zero explicit content.</strong>', purpose: 'Visual hook. Aspirational and warm; makes him want in on the trip.', upload: 1 },
      ]},
      { label: 'Phase 02', name: 'Sun & Sand', beats: [
        { no: '6–8', noLabel: 'Beats', fmt: 'Text Only', sub: 'Playful challenges', desc: 'Teasing from the water. <span class="q">"I\'d dare you to join me but you couldn\'t handle it 😏"</span>', purpose: 'Transition. Turn distance into a dare and pull him closer.' },
        { no: '9–10', noLabel: 'Beats', fmt: 'Free Photo / Video', sub: 'Implied / non-nude', desc: 'Just out of the ocean — wrap or cover-up clinging, hair slicked back, water on skin, looking off camera.', purpose: 'Tease escalation. "Wet and unbothered" does all the work — no exposure.', upload: 2 },
      ]},
      { label: 'Phase 03', name: 'Golden Hour', beats: [
        { no: '11–12', noLabel: 'Beats', fmt: 'Text Only', sub: 'Suggestive, never explicit', desc: 'Sunset, glass of wine. <span class="q">"perfect view, perfect night… only thing missing is you"</span>', purpose: 'Tension peak. Romance and longing set up the unlock.' },
      ]},
      { label: 'Phase 04', name: 'The Paywall', beats: [
        { no: '13', noLabel: 'Beat', fmt: 'First Locked PPV', sub: 'Clip · 15–20 sec', ppv: true, desc: 'Golden-hour clip — silhouette against the sunset, cover-up slipping off one shoulder, a slow turn with her back to camera. Backlit and implied — still non-nude.', purposeLabel: 'Paywall Test', purpose: 'First conversion. The silhouette feels cinematic and exclusive.', upload: 3 },
        { no: '14–15', noLabel: 'Beats', fmt: 'Text Only', sub: 'Reactive', desc: 'React to the unlock and keep the vacation glow going. <span class="q">"glad you liked the view… stick around, the trip\'s just getting started"</span>', purpose: 'Gauge interest and tee up the rest of the "trip."' },
      ]},
    ],
    summary: [
      { label: 'Text Messages', value: '12–15', note: 'Sunrise-to-sunset arc. Vacation FOMO throughout.' },
      { label: 'Free Visual Teases', value: '2', small: '+1 CLIP', note: 'Non-nude. Beach arrival + post-swim cover-up.' },
      { label: 'Locked PPV Pieces', value: '1', note: '15–20 sec sunset silhouette, implied only.' },
      { label: 'Session Time', value: '30–60', small: 'MIN', note: 'Great as a real travel-day drip in real time.' },
    ],
    psych: {
      paras: [
        'Travel content prints money because it\'s <em>aspirational and time-boxed</em>. He\'s not just buying a clip — he\'s buying a seat on a trip he wishes he was on, and the "wish you were here" framing makes him feel chosen.',
        'The backlit sunset PPV is the safest possible "reveal": a silhouette shows almost nothing yet feels the most intimate. Cinematic quality justifies the price without a single explicit frame.',
      ],
      principles: [
        { b: 'For Her', t: 'Any beach day becomes a full monetized set. Golden hour does the lighting for free.' },
        { b: 'For Him', t: 'Escapism plus exclusivity: a beautiful place, a beautiful moment, and the sense that he\'s the one she\'s wishing was there.' },
      ],
    },
  },

  {
    id: 'date-night', level: 1,
    title: 'Date Night Getting Ready',
    kicker: 'Sexting Set · Script 004',
    tagline: "Getting ready to go out — then choosing to stay in with him instead. Jealousy tease, implied only.",
    chips: ['Non-Nude / Implied', '15 Message Beats', '2 Free Visuals + 1 Clip', '1 Locked PPV', '20–40 Min Session'],
    phases: [
      { label: 'Phase 01', name: 'The Invitation', beats: [
        { no: '1–3', noLabel: 'Beats', fmt: 'Text Only', sub: '1–2 sentences each', desc: 'Getting ready for a night out. <span class="q">"the girls are dragging me out tonight… kinda wish you were my date instead"</span>', purpose: 'Relationship building. Position him as the one she\'d rather be with.' },
        { no: '4–5', noLabel: 'Beats', fmt: 'Free Photo', sub: 'Implied / non-nude', desc: 'Getting-ready mirror selfie — silk robe, hair in a towel or rollers, doing makeup. Intimate backstage energy. <strong>Nothing on show.</strong>', purpose: 'Visual hook. Backstage access feels personal and exclusive.', upload: 1 },
      ]},
      { label: 'Phase 02', name: 'The Reveal', beats: [
        { no: '6–8', noLabel: 'Beats', fmt: 'Text Only', sub: 'Interactive, playful', desc: 'Pull him in on the decision. <span class="q">"black dress or red? be honest, you\'re dressing me tonight"</span>', purpose: 'Transition. Interactivity boosts replies and buy-in.' },
        { no: '9–10', noLabel: 'Beats', fmt: 'Free Photo / Video', sub: 'Implied / non-nude', desc: 'The final look — little black dress, heels, full-length mirror, an over-the-shoulder glance. Elegant and covered.', purpose: 'Tease escalation. "Look what you\'re missing tonight."', upload: 2 },
      ]},
      { label: 'Phase 03', name: 'Second Thoughts', beats: [
        { no: '11–12', noLabel: 'Beats', fmt: 'Text Only', sub: 'Suggestive, never explicit', desc: 'Home early, over it. <span class="q">"honestly? I\'d have rather stayed in with you all night"</span>', purpose: 'Tension peak. Rejects the crowd, chooses him — flattery + heat.' },
      ]},
      { label: 'Phase 04', name: 'The Paywall', beats: [
        { no: '13', noLabel: 'Beat', fmt: 'First Locked PPV', sub: 'Clip · 15–20 sec', ppv: true, desc: 'Back home — heels kicked off, still in the dress, sitting back on the bed, one strap slipping. <span class="q">"the night could\'ve ended so much better…"</span> Implied only — still non-nude.', purposeLabel: 'Paywall Test', purpose: 'First conversion. "The night we could\'ve had" is the fantasy he pays for.', upload: 3 },
        { no: '14–15', noLabel: 'Beats', fmt: 'Text Only', sub: 'Reactive', desc: 'React to the unlock and keep it warm. <span class="q">"mmm glad someone appreciates the effort… stay up with me?"</span>', purpose: 'Gauge interest and roll straight into a late-night conversation.' },
      ]},
    ],
    summary: [
      { label: 'Text Messages', value: '12–15', note: 'Interactive "help me pick" beats drive replies.' },
      { label: 'Free Visual Teases', value: '2', small: '+1 CLIP', note: 'Non-nude. Getting-ready selfie + final-look clip.' },
      { label: 'Locked PPV Pieces', value: '1', note: '15–20 sec "home early" clip, implied only.' },
      { label: 'Session Time', value: '20–40', small: 'MIN', note: 'Punchy. Works best on a real evening.' },
    ],
    psych: {
      paras: [
        'This runs on gentle <em>jealousy and being chosen</em>. She could be out with anyone, and she\'d rather be texting him — then she actually leaves early "for" him. That\'s an ego reward most fans will pay to feel.',
        'Letting him pick the dress makes him a participant, not a spectator. By the time the "home early" PPV lands, he\'s invested in the night as if it were theirs.',
      ],
      principles: [
        { b: 'For Her', t: 'Filmable in one evening at home. The getting-ready ritual is content she\'s doing anyway.' },
        { b: 'For Him', t: 'Chosen over a whole night out — the fantasy that he\'s the one she actually wants.' },
      ],
    },
  },

  // Level 2 — ready-to-fill slots
  { id: 'l2-01', level: 2, placeholder: true, title: 'Open Script Slot 01' },
  { id: 'l2-02', level: 2, placeholder: true, title: 'Open Script Slot 02' },
  { id: 'l2-03', level: 2, placeholder: true, title: 'Open Script Slot 03' },

  // Level 3 — ready-to-fill slots
  { id: 'l3-01', level: 3, placeholder: true, title: 'Open Script Slot 01' },
  { id: 'l3-02', level: 3, placeholder: true, title: 'Open Script Slot 02' },
  { id: 'l3-03', level: 3, placeholder: true, title: 'Open Script Slot 03' },
];

// ————————————————————————————————————————————————————————————————
// CSS (shared)
// ————————————————————————————————————————————————————————————————
const CSS = `
  :root{
    --ink:#1d1d1b;--ink-raise:#242422;--ink-line:rgba(235,236,220,.14);--ink-line-soft:rgba(235,236,220,.08);
    --bone:#ebecdc;--bone-dim:rgba(235,236,220,.62);--bone-faint:rgba(235,236,220,.38);
    --mint:#b6f2e5;--mint-wash:rgba(182,242,229,.06);
    --accent:#b6f2e5;--accent-wash:rgba(182,242,229,.07);
    --sans:"Archivo","Helvetica Neue",sans-serif;--mono:"Spline Sans Mono","SF Mono",monospace;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{background:var(--ink);color:var(--bone);font-family:var(--sans);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;position:relative}
  body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:999;opacity:.6;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 250 250' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E")}
  .page{max-width:1060px;margin:0 auto;padding:0 48px 110px;position:relative}
  @keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  .rise{animation:rise .7s cubic-bezier(.22,1,.36,1) both}
  .d1{animation-delay:.06s}.d2{animation-delay:.14s}.d3{animation-delay:.24s}.d4{animation-delay:.36s}
  header{display:flex;align-items:center;justify-content:space-between;padding:32px 0 26px;border-bottom:1px solid var(--ink-line);gap:20px;flex-wrap:wrap}
  .logo img{height:26px;display:block}
  .masthead-meta{display:flex;align-items:center;gap:24px;flex-wrap:wrap}
  .dept{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--bone-faint)}
  .badge{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--mint);border:1px solid rgba(182,242,229,.5);padding:7px 14px 6px;border-radius:999px;white-space:nowrap}
  .back{display:inline-flex;align-items:center;gap:9px;font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--bone-dim);text-decoration:none;margin:34px 0 -8px;transition:color .2s}
  .back:hover{color:var(--mint)}
  .hero{padding:70px 0 40px;position:relative}
  .hero .ghost{position:absolute;top:10px;right:-140px;width:520px;opacity:.045;pointer-events:none;user-select:none}
  .kicker{font-family:var(--mono);font-size:11.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);display:flex;align-items:center;gap:16px;margin-bottom:28px}
  .kicker::before{content:"";display:block;width:44px;height:1px;background:var(--accent)}
  h1{font-weight:800;font-stretch:118%;font-size:clamp(40px,6.4vw,74px);line-height:1;letter-spacing:-.015em;text-transform:uppercase;max-width:16ch;position:relative}
  h1 .alt{color:var(--accent)}
  .lede{margin-top:26px;font-size:16px;color:var(--bone-dim);max-width:60ch}
  .hero-foot{margin-top:38px;display:flex;flex-wrap:wrap;gap:12px;position:relative}
  .chip{font-family:var(--mono);font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;padding:8px 16px 7px;border:1px solid var(--ink-line);border-radius:999px;color:var(--bone-dim)}
  .chip.accent{border-color:var(--accent);color:var(--accent);background:var(--accent-wash)}
  section{margin-top:70px}
  .sec-head{display:flex;align-items:baseline;gap:20px;margin-bottom:10px}
  .sec-num{font-family:var(--mono);font-size:12px;letter-spacing:.12em;color:var(--accent)}
  h2{font-weight:800;font-stretch:118%;font-size:clamp(22px,3vw,31px);letter-spacing:-.005em;text-transform:uppercase}
  .sec-sub{color:var(--bone-faint);font-size:14.5px;max-width:64ch;margin-bottom:34px}
  /* level rail */
  .level-rail{font-family:var(--mono);font-size:10px;letter-spacing:.26em;text-transform:uppercase;color:var(--bone-faint);padding:34px 0 14px;display:flex;align-items:center;gap:14px}
  .level-rail::after{content:"";flex:1;height:1px;background:var(--ink-line-soft)}
  .level-rail .lv{font-weight:800;font-stretch:118%;font-family:var(--sans);font-size:12px;letter-spacing:.08em}
  /* creator + script cards */
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  .card{position:relative;display:flex;flex-direction:column;justify-content:space-between;min-height:190px;padding:24px 24px 22px;border:1px solid var(--ink-line);border-radius:4px;background:var(--ink-raise);text-decoration:none;color:var(--bone);transition:transform .2s,border-color .2s,background .2s;overflow:hidden}
  .card:hover{transform:translateY(-3px);border-color:var(--accent);background:#2a2a27}
  .card .lvpill{align-self:flex-start;font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;padding:5px 11px 4px;border-radius:999px;color:var(--ink);font-weight:600}
  .card .cname{font-weight:800;font-stretch:112%;font-size:22px;line-height:1.08;letter-spacing:-.01em;margin-top:20px}
  .card .cstage{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:var(--bone-faint);margin-top:8px}
  .card .chandle{font-family:var(--mono);font-size:12px;letter-spacing:.04em;color:var(--accent);margin-top:6px}
  .card .cgo{margin-top:18px;font-family:var(--mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--bone-dim)}
  .card.script .cname{font-size:20px}
  .card.script .ctag{font-size:13px;color:var(--bone-dim);margin-top:12px;line-height:1.5}
  .card.slot{opacity:.6;pointer-events:none;border-style:dashed}
  .card.slot .cname{color:var(--bone-faint)}
  .card.slot .cgo{color:var(--bone-faint)}
  /* beat sheet */
  .sheet{border-top:1px solid var(--bone)}
  .beat{display:grid;grid-template-columns:92px 172px 1fr 232px;gap:28px;padding:26px 8px 25px;border-bottom:1px solid var(--ink-line);align-items:baseline}
  .beat.is-ppv{background:var(--accent-wash);border-left:3px solid var(--accent);padding-left:20px;margin-left:-23px}
  .beat-no{font-weight:800;font-stretch:118%;font-size:27px;line-height:1;white-space:nowrap}
  .beat-no small{display:block;font-family:var(--mono);font-weight:400;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:var(--bone-faint);margin-top:8px}
  .beat-type{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;line-height:1.8;color:var(--bone-dim)}
  .beat-type .fmt{display:inline-block;padding:3px 10px 2px;border-radius:999px;border:1px solid var(--ink-line);margin-bottom:8px}
  .beat.is-ppv .beat-type .fmt{border-color:var(--accent);color:var(--ink);background:var(--accent);font-weight:500}
  .beat-desc{font-size:15.5px;color:var(--bone-dim);max-width:52ch}
  .beat-desc strong{color:var(--bone);font-weight:700}
  .beat-desc .q{font-style:italic;color:var(--accent)}
  .upload-link{display:inline-block;margin-top:10px;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(182,242,229,.4);padding-bottom:2px}
  .upload-link:hover{border-color:var(--accent)}
  .beat-purpose{font-size:13.5px;color:var(--bone-faint);line-height:1.6}
  .beat-purpose b{display:block;font-family:var(--mono);font-weight:500;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:5px}
  .phase-label{font-family:var(--mono);font-size:10px;letter-spacing:.26em;text-transform:uppercase;color:var(--bone-faint);padding:30px 8px 12px;display:flex;align-items:center;gap:14px}
  .phase-label::after{content:"";flex:1;height:1px;background:var(--ink-line-soft)}
  .phase-label .roman{font-weight:800;font-stretch:118%;font-family:var(--sans);font-size:12px;letter-spacing:.1em;color:var(--accent)}
  .summary-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--bone);border-left:1px solid var(--ink-line)}
  .sum-cell{border-right:1px solid var(--ink-line);border-bottom:1px solid var(--ink-line);padding:30px 26px 34px;background:var(--ink-raise)}
  .sum-cell .label{font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--bone-faint);margin-bottom:20px}
  .sum-cell .value{font-weight:800;font-stretch:118%;font-size:40px;line-height:1;letter-spacing:-.01em}
  .sum-cell .value small{font-size:15px;font-weight:500;font-stretch:100%;color:var(--accent);letter-spacing:.02em}
  .sum-cell .note{margin-top:14px;font-size:13px;color:var(--bone-faint);line-height:1.55}
  .submit{margin-top:40px;border-top:1px solid var(--bone)}
  .folder-row{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;padding:20px 8px;border-bottom:1px solid var(--ink-line);text-decoration:none;transition:background .2s}
  .folder-row:hover{background:var(--accent-wash)}
  .folder-row .f-name{font-family:var(--mono);font-size:12.5px;letter-spacing:.08em;color:var(--bone)}
  .folder-row .f-open{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);white-space:nowrap}
  .submit-note{margin-top:18px;font-size:13px;color:var(--bone-faint);font-family:var(--mono);letter-spacing:.04em;line-height:1.7}
  .psych{margin-top:70px;background:var(--accent);color:var(--ink);border-radius:4px;padding:60px 60px 54px;position:relative;overflow:hidden}
  .psych .mono-mark{position:absolute;bottom:-70px;right:-50px;width:360px;opacity:.1;pointer-events:none}
  .psych .label{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--ink);display:flex;align-items:center;gap:16px;margin-bottom:30px}
  .psych .label::before{content:"";width:44px;height:1px;background:var(--ink)}
  .psych p{font-weight:500;font-size:clamp(18px,2.3vw,24px);line-height:1.45;max-width:40ch;letter-spacing:-.005em;position:relative}
  .psych p+p{margin-top:22px}
  .psych em{font-style:italic;font-weight:700}
  .psych .principle{margin-top:40px;padding-top:30px;border-top:1px solid rgba(29,29,27,.25);display:grid;grid-template-columns:repeat(2,1fr);gap:26px 46px;position:relative}
  .psych .principle div{font-size:13.5px;line-height:1.6;color:rgba(29,29,27,.78)}
  .psych .principle b{display:block;font-family:var(--mono);font-weight:500;font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--ink);margin-bottom:8px}
  footer{margin-top:90px;border-top:1px solid var(--ink-line);padding-top:30px;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap}
  footer .fm img{height:16px;display:block;opacity:.9}
  footer .legal{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--bone-faint);text-align:right;line-height:2}
  .hidden{display:none}
  @media(max-width:880px){
    .page{padding:0 24px 70px}
    .grid{grid-template-columns:1fr}
    .beat{grid-template-columns:64px 1fr;gap:14px 20px}
    .beat-desc,.beat-purpose{grid-column:1/-1}
    .beat.is-ppv{margin-left:-12px;padding-left:9px}
    .summary-grid{grid-template-columns:repeat(2,1fr)}
    .psych{padding:44px 28px 40px}.psych .principle{grid-template-columns:1fr}
    .hero .ghost{width:340px;right:-110px}.dept{display:none}
  }
  @media print{body::before{display:none}.rise{animation:none}body,.psych{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
`;

// ————————————————————————————————————————————————————————————————
// Render helpers
// ————————————————————————————————————————————————————————————————
const esc = (s) => String(s);

function renderScriptDetail(sc, creator) {
  const uploadLink = (idx) => {
    if (!sc.folders) return '';
    const f = sc.folders[idx];
    return f ? `<br><a class="upload-link" href="${f.href}" target="_blank" rel="noopener">Upload to Folder ${f.n} ↗</a>` : '';
  };
  const beatsHtml = sc.phases.map((ph) => {
    const rows = ph.beats.map((b) => `
      <div class="beat${b.ppv ? ' is-ppv' : ''}">
        <div class="beat-no">${b.no}<small>${b.noLabel}</small></div>
        <div class="beat-type"><span class="fmt">${b.fmt}</span><br>${b.sub}</div>
        <div class="beat-desc">${b.desc}${b.upload ? uploadLink(b.upload - 1) : ''}</div>
        <div class="beat-purpose"><b>${b.purposeLabel || 'Purpose'}</b>${b.purpose}</div>
      </div>`).join('');
    return `<div class="phase-label"><span class="roman">${ph.label}</span> ${ph.name}</div>${rows}`;
  }).join('');

  const summaryHtml = sc.summary.map((s) => `
    <div class="sum-cell">
      <div class="label">${s.label}</div>
      <div class="value">${s.value}${s.small ? ` <small>${s.small}</small>` : ''}</div>
      <div class="note">${s.note}</div>
    </div>`).join('');

  let submitHtml;
  if (sc.folders) {
    submitHtml = `
    <section>
      <div class="sec-head"><span class="sec-num">03</span><h2>Submit Your Content</h2></div>
      <p class="sec-sub">Every deliverable has a matching numbered folder in your private shared Drive. Shoot it, name it, drop it in its folder — same numbers as the beats above.</p>
      <div class="submit">
        ${sc.folders.map((f) => `<a class="folder-row" href="${f.href}" target="_blank" rel="noopener"><span class="f-name">${f.n} — ${f.label}</span><span class="f-open">Open ↗</span></a>`).join('')}
      </div>
    </section>`;
  } else {
    submitHtml = `
    <section>
      <div class="sec-head"><span class="sec-num">03</span><h2>Submit Your Content</h2></div>
      <p class="sec-sub">When you pick this script, your ALTR manager activates a private upload folder for each beat and drops the links right here.</p>
      <div class="submit-note">Upload folders — activated on selection · Message your ALTR manager to start this script.</div>
    </section>`;
  }

  return `
  <div id="view-${sc.id}" class="script-view hidden">
    <a class="back" href="#" data-home>← All ${creator.name.split(' ')[0]}'s scripts</a>
    <div class="hero">
      <img class="ghost" src="${MONO_CREAM}" alt="" aria-hidden="true">
      <div class="kicker">${sc.kicker}</div>
      <h1>${sc.title}</h1>
      <p class="lede">${sc.tagline}</p>
      <div class="hero-foot">${sc.chips.map((c, i) => `<span class="chip${i === 0 ? ' accent' : ''}">${c}</span>`).join('')}</div>
    </div>
    <section>
      <div class="sec-head"><span class="sec-num">01</span><h2>Message Flow</h2></div>
      <p class="sec-sub">Sequenced beats from casual open to first paywall. Space texts 1–2 minutes apart. Every visual stays non-nude — the escalation lives in tone, not exposure.</p>
      <div class="sheet">${beatsHtml}</div>
    </section>
    <section>
      <div class="sec-head"><span class="sec-num">02</span><h2>Content Length Summary</h2></div>
      <p class="sec-sub">Everything the shoot and chat session need to produce, at a glance.</p>
      <div class="summary-grid">${summaryHtml}</div>
    </section>
    ${submitHtml}
    <div class="psych">
      <img class="mono-mark" src="${MONO_BLACK}" alt="" aria-hidden="true">
      <div class="label">The Psychology</div>
      ${sc.psych.paras.map((p) => `<p>${p}</p>`).join('')}
      <div class="principle">${sc.psych.principles.map((pr) => `<div><b>${pr.b}</b>${pr.t}</div>`).join('')}</div>
    </div>
  </div>`;
}

function renderCreatorPage(creator) {
  const lv = LEVELS[creator.level];
  const scripts = SCRIPTS.filter((s) => s.level === creator.level);
  const first = creator.name.split(' ')[0];

  const cards = scripts.map((sc) => {
    if (sc.placeholder) {
      return `<div class="card script slot"><span class="lvpill" style="background:${lv.accent}">${lv.name}</span><div class="cname">${sc.title}</div><div class="ctag">Brief added by your ALTR manager.</div><div class="cgo">Coming soon</div></div>`;
    }
    return `<a class="card script" href="#${sc.id}" data-script="${sc.id}"><span class="lvpill" style="background:${lv.accent}">${lv.name}</span><div class="cname">${sc.title}</div><div class="ctag">${sc.tagline}</div><div class="cgo">Open script →</div></a>`;
  }).join('');

  const details = scripts.filter((s) => !s.placeholder).map((sc) => renderScriptDetail(sc, creator)).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>ALTR — ${creator.name} · Content Hub</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>${CSS}
  :root{--accent:${lv.accent};--accent-wash:${hexWash(lv.accent)}}
</style>
</head>
<body>
<div class="page">
  <header class="rise">
    <div class="logo"><img src="${LOGO_MINT}" alt="ALTR"></div>
    <div class="masthead-meta">
      <span class="dept">Creator Content Hub</span>
      <span class="badge">Private · ${lv.name}</span>
    </div>
  </header>

  <div id="view-home">
    <div class="hero rise d1">
      <img class="ghost" src="${MONO_CREAM}" alt="" aria-hidden="true">
      <div class="kicker">Welcome, ${first}</div>
      <h1>Your <span class="alt">Script</span> Hub</h1>
      <p class="lede">Here are the content scripts ready for you at your level. Pick the one you want to shoot, follow the beat sheet, and submit straight to your private folders. New scripts drop here as they're built.</p>
      <div class="hero-foot">
        <span class="chip accent">${lv.tag}</span>
        <span class="chip">@${creator.handle}</span>
        <span class="chip">${scripts.filter((s) => !s.placeholder).length} Script${scripts.filter((s) => !s.placeholder).length === 1 ? '' : 's'} Ready</span>
      </div>
    </div>
    <section class="rise d2">
      <div class="sec-head"><span class="sec-num">01</span><h2>Choose a Script</h2></div>
      <p class="sec-sub">Tap any script to open its full message flow, shot list, and submission folders.</p>
      <div class="grid">${cards}</div>
    </section>
  </div>

  ${details}

  <footer>
    <div class="fm"><img src="${LOGO_MINT}" alt="ALTR"></div>
    <div class="legal">Prepared by ALTR Talent Development<br>Private — For ${creator.name} only · Not for distribution</div>
  </footer>
</div>
<script>
  var scripts=${JSON.stringify(scripts.filter((s) => !s.placeholder).map((s) => s.id))};
  function show(id){
    document.getElementById('view-home').classList.toggle('hidden', !!id);
    scripts.forEach(function(s){var el=document.getElementById('view-'+s);if(el)el.classList.toggle('hidden', s!==id);});
    window.scrollTo(0,0);
  }
  function route(){var h=(location.hash||'').replace('#','');show(scripts.indexOf(h)>=0?h:null);}
  document.addEventListener('click',function(e){var a=e.target.closest('[data-home]');if(a){e.preventDefault();location.hash='';}});
  window.addEventListener('hashchange',route);
  route();
</script>
</body>
</html>`;
}

function hexWash(hex) {
  const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},.07)`;
}

// ————————————————————————————————————————————————————————————————
// Master internal index
// ————————————————————————————————————————————————————————————————
function renderIndex() {
  const byLevel = (lvl) => CREATORS.filter((c) => c.level === lvl);
  const section = (lvl) => {
    const lv = LEVELS[lvl];
    const rows = byLevel(lvl).map((c) => {
      const href = BASE ? `${BASE}/${fileOf(c)}` : fileOf(c);
      return `
      <a class="card" href="${href}"${BASE ? ' target="_blank" rel="noopener"' : ''}>
        <span class="lvpill" style="background:${lv.accent}">${lv.name} · ${lv.tag}</span>
        <div class="cname">${c.name}</div>
        ${c.stage ? `<div class="cstage">aka ${c.stage}</div>` : ''}
        <div class="chandle">@${c.handle}</div>
        ${BASE ? `<div class="cstage" style="word-break:break-all;margin-top:10px">${href}</div>` : ''}
        <div class="cgo">Open private hub →</div>
      </a>`;
    }).join('');
    return `<div class="level-rail"><span class="lv" style="color:${lv.accent}">${lv.name}</span> ${lv.tag} — ${byLevel(lvl).length} creator${byLevel(lvl).length === 1 ? '' : 's'}</div><div class="grid">${rows}</div>`;
  };

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="robots" content="noindex, nofollow">
<title>ALTR — Roster & Script Control</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>${CSS}</style>
</head>
<body>
<div class="page">
  <header class="rise">
    <div class="logo"><img src="${LOGO_MINT}" alt="ALTR"></div>
    <div class="masthead-meta"><span class="dept">Talent Development — Roster Control</span><span class="badge">Confidential · Internal</span></div>
  </header>
  <div class="hero rise d1">
    <img class="ghost" src="${MONO_CREAM}" alt="" aria-hidden="true">
    <div class="kicker">Internal Dashboard</div>
    <h1>Roster &amp; <span class="alt">Script</span> Control</h1>
    <p class="lede">${CREATORS.length} creators across three content tiers. Each creator has a private hub link — open it, copy the URL, and send it to that creator only. They see nothing but their own scripts.</p>
    <div class="hero-foot">
      <span class="chip accent">${CREATORS.length} Creators</span>
      <span class="chip">${byLevel(1).length} · Level 1</span>
      <span class="chip">${byLevel(2).length} · Level 2</span>
      <span class="chip">${byLevel(3).length} · Level 3</span>
    </div>
  </div>
  <section class="rise d2">
    <div class="sec-head"><span class="sec-num">01</span><h2>Creators</h2></div>
    <p class="sec-sub">Each card opens that creator's private, standalone hub file. This index is for internal use — do not share it with creators.</p>
    ${section(1)}${section(2)}${section(3)}
  </section>
  <footer>
    <div class="fm"><img src="${LOGO_MINT}" alt="ALTR"></div>
    <div class="legal">Prepared by ALTR Talent Development<br>Confidential — Internal roster · Not for distribution</div>
  </footer>
</div>
</body>
</html>`;
}

// ————————————————————————————————————————————————————————————————
// Write files
// ————————————————————————————————————————————————————————————————
let count = 0;
for (const c of CREATORS) {
  writeFileSync(resolve(OUT, fileOf(c)), renderCreatorPage(c));
  count++;
}
writeFileSync(resolve(OUT, 'altr-roster-index.html'), renderIndex());

// Minimal public root page — deliberately contains no roster info and no links.
writeFileSync(resolve(OUT, 'index.html'), `<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow"><title>ALTR</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#1d1d1b;color:#ebecdc;font-family:Helvetica,Arial,sans-serif}
.w{text-align:center}.w b{font-size:34px;letter-spacing:.3em;margin-right:-.3em}.w b i{color:#b6f2e5;font-style:normal}
.w p{margin-top:14px;font-size:11px;letter-spacing:.25em;text-transform:uppercase;color:rgba(235,236,220,.4)}</style>
</head><body><div class="w"><b>ALTR<i>.</i></b><p>Private access only</p></div></body></html>`);

console.log(`Wrote ${count} creator files (slugged) + altr-roster-index.html + index.html to ${OUT}`);
for (const c of CREATORS) console.log(`  ${c.name.padEnd(26)} @${c.handle.padEnd(20)} → ${fileOf(c)}`);
