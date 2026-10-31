#!/usr/bin/env python3
"""Generate ALTR Case Board dashboard (brand-matched to ALTR Money Audit)."""
import json, datetime, importlib.util

spec = importlib.util.spec_from_file_location("bx", "/Users/locklyjailbreak/conductor/workspaces/lead-check-up/dakar/scratch/build_xlsx.py")
bx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bx)  # also rewrites the xlsx; harmless

def iso(d):
    return d.isoformat() if isinstance(d, (datetime.date,)) else d

PB = [{"p":r[0],"bucket":r[1],"who":r[2],"where":r[3],"case":r[4],"amt":r[5],"status":r[6],
      "since":iso(r[7]),"last":iso(r[9]),"action":r[10]} for r in bx.pb]
RECV = [{"who":r[0],"ev":r[1],"amt":r[2],"status":r[3],"action":r[4]} for r in bx.recv]
PAY = []
for r in bx.pay:
    amt = int(r[3]) if isinstance(r[3], str) else r[3]
    PAY.append({"type":r[0],"who":r[1],"detail":r[2],"amt":amt,"status":r[4]})
DEP = [{"date":iso(r[0]),"who":r[1],"method":r[2],"ref":r[3],"amt":r[4],"src":r[5]} for r in bx.dep]
TL = [{"date":iso(r[0]),"event":r[1]} for r in bx.tl]

DATA = json.dumps({"pb":PB,"recv":RECV,"pay":PAY,"dep":DEP,"tl":TL}, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ALTR Case Board — Interactive</title>
<style>
body { color-scheme:light;
  --page:#f9f9f7; --surface-1:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e;
  --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,.10);
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#d03b3b;
  margin:0; background:var(--page); color:var(--ink);
  font:14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
* { box-sizing:border-box; }
header { padding:18px 26px 0; display:flex; justify-content:space-between; align-items:flex-start; gap:14px; flex-wrap:wrap; }
h1 { font-size:21px; margin:0; font-weight:700; }
.sub { color:var(--ink-2); font-size:12px; margin-top:3px; max-width:860px; }
.hbtns { display:flex; gap:8px; }
.btn { border:1px solid var(--axis); background:var(--surface-1); border-radius:8px; padding:7px 13px; font:600 12.5px system-ui,sans-serif; cursor:pointer; color:var(--ink-2); }
.btn:hover { border-color:var(--ink); color:var(--ink); }
nav { display:flex; gap:4px; padding:12px 26px 0; border-bottom:1px solid var(--grid); background:var(--page); position:sticky; top:0; z-index:5; overflow-x:auto; }
nav button { border:1px solid transparent; border-bottom:none; background:none; font:600 13.5px system-ui,sans-serif; color:var(--ink-2); padding:9px 15px; cursor:pointer; border-radius:8px 8px 0 0; white-space:nowrap; }
nav button.on { background:var(--surface-1); color:var(--ink); border-color:var(--grid); position:relative; top:1px; }
nav button .n { font-size:10px; color:var(--muted); margin-left:4px; }
main { padding:18px 26px 60px; max-width:1400px; margin:0 auto; }
.tab { display:none; } .tab.on { display:block; }
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin-bottom:16px; }
.tile { background:var(--surface-1); border:1px solid var(--ring); border-radius:10px; padding:13px 15px; }
.tile .lbl { font-size:11.5px; color:var(--ink-2); font-weight:600; }
.tile .val { font-size:24px; font-weight:700; margin-top:2px; }
.tile .note { font-size:11px; color:var(--muted); margin-top:2px; }
.tile.warn .val { color:var(--serious); }
.tile.crit .val { color:var(--critical); }
.tile.good .val { color:#006300; }
.cards { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
@media (max-width:980px){ .cards{grid-template-columns:1fr} }
.card { background:var(--surface-1); border:1px solid var(--ring); border-radius:10px; padding:15px; }
.card h3 { margin:0 0 3px; font-size:14px; }
.card .csub { color:var(--muted); font-size:11.5px; margin-bottom:9px; }
.legend { display:flex; gap:14px; font-size:12px; color:var(--ink-2); margin:2px 0 8px; flex-wrap:wrap; }
.legend i { display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:5px; vertical-align:-1px; }
svg text { font:11px system-ui,sans-serif; fill:var(--muted); }
svg .vlab { font:600 11px system-ui,sans-serif; fill:var(--ink-2); }
.tooltip { position:fixed; pointer-events:none; background:var(--ink); color:#fff; font:12px system-ui,sans-serif; padding:7px 10px; border-radius:8px; max-width:340px; z-index:20; display:none; box-shadow:0 4px 14px rgba(0,0,0,.25); }
.tooltip b { color:#fff; }
.controls { display:flex; gap:8px; margin:0 0 12px; flex-wrap:wrap; align-items:center; }
.chip { border:1px solid var(--axis); background:var(--surface-1); border-radius:999px; padding:5px 12px; font:600 12px system-ui,sans-serif; color:var(--ink-2); cursor:pointer; }
.chip.on { background:var(--ink); color:#fff; border-color:var(--ink); }
input[type=search] { border:1px solid var(--axis); border-radius:8px; padding:7px 11px; font:13px system-ui,sans-serif; background:var(--surface-1); min-width:220px; color:var(--ink); }
table { width:100%; border-collapse:collapse; font-size:12.5px; }
th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); padding:8px 9px; border-bottom:1px solid var(--grid); cursor:pointer; user-select:none; white-space:nowrap; position:sticky; top:47px; background:var(--surface-1); }
th .arr { font-size:9px; }
td { padding:8px 9px; border-bottom:1px solid var(--grid); vertical-align:top; }
tr:hover td { background:#f4f4f1; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
.pill { display:inline-block; font:700 10.5px system-ui,sans-serif; border-radius:999px; padding:2px 9px; white-space:nowrap; }
.pill.p0 { background:#fbeaea; color:var(--critical); }
.pill.p1 { background:#fdf3df; color:#8a5a00; }
.pill.p2 { background:#eef4fc; color:#1d5da8; }
.pill.gray { background:#e9e9e5; color:var(--ink-2); }
.pill.money-in { background:#e7f6ec; color:#006300; }
.pill.money-out { background:#fbeaea; color:var(--critical); }
.days { font-weight:700; }
.days.hot { color:var(--critical); } .days.warm { color:#8a5a00; }
.small { font-size:11.5px; color:var(--ink-2); }
.mono { font-variant-numeric:tabular-nums; }
.footer { margin-top:26px; color:var(--muted); font-size:11px; }
.tablewrap { overflow:visible; }
@media (max-width:900px){ .tablewrap{overflow-x:auto} th{position:static} }
.bucket { font-weight:700; font-size:11px; color:var(--ink-2); text-transform:uppercase; letter-spacing:.03em; }
</style></head>
<body data-palette="#2a78d6,#eb6834,#1baf7a,#eda100">
<header>
  <div>
    <h1>ALTR Case Board — Interactive</h1>
    <div class="sub">iMessage + WhatsApp audit · Mar 18 – Sep 18 2026 · 316k messages · 471 business chats read · every row carries its message date so you can pull the thread. Local file — nothing leaves this machine.</div>
  </div>
  <div class="hbtns">
    <button class="btn" onclick="window.print()">Print / PDF</button>
    <button class="btn" id="asof">As of Sep 18, 2026</button>
  </div>
</header>
<nav id="nav"></nav>
<main id="main"></main>
<div class="tooltip" id="tip"></div>
<script>
const DATA = __DATA__;
const ASOF = new Date("2026-09-18T00:00:00");
const $ = s => document.querySelector(s);
const esc = s => String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const fmt$ = v => v==null||v===""?"—":(v<0?"(" : "")+"$"+Math.abs(v).toLocaleString(undefined,{maximumFractionDigits:0})+(v<0?")":"");
const days = d => d?Math.round((ASOF-new Date(d+"T00:00:00"))/864e5):null;
const fdate = d => d? new Date(d+"T00:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric"}) : "—";

/* ---------- tooltip ---------- */
const tip = $("#tip");
function showTip(ev, html){ tip.innerHTML = html; tip.style.display="block"; moveTip(ev); }
function moveTip(ev){ const w=tip.offsetWidth,h=tip.offsetHeight;
  tip.style.left = Math.min(ev.clientX+14, innerWidth-w-10)+"px";
  tip.style.top  = Math.min(ev.clientY+14, innerHeight-h-10)+"px"; }
function hideTip(){ tip.style.display="none"; }

/* ---------- chart helpers (brand marks: 4px rounded data-ends, 2px gaps) ---------- */
function hbar(el, rows, {color="#2a78d6", h=26, label=r=>r.l, val=r=>r.v, tipHtml=null, colorOf=null}={}){
  const W = el.clientWidth||600, LW = Math.min(210, W*0.34), max = Math.max(...rows.map(val),1);
  const H = rows.length*h+6;
  let s = `<svg width="${W}" height="${H}" role="img">`;
  rows.forEach((r,i)=>{
    const y=i*h+3, bw=Math.max(3,(W-LW-86)*(val(r)/max)), c=colorOf?colorOf(r):color;
    s+=`<text x="${LW-8}" y="${y+h/2+3}" text-anchor="end" class="vlab">${esc(label(r)).slice(0,30)}</text>`;
    s+=`<rect data-i="${i}" x="${LW}" y="${y+4}" width="${bw}" height="${h-11}" rx="4" fill="${c}"></rect>`;
    s+=`<text x="${LW+bw+7}" y="${y+h/2+3}" class="vlab">${fmt$(val(r))}</text>`;
  });
  s+="</svg>";
  el.innerHTML = s;
  if(tipHtml){ el.querySelectorAll("rect").forEach(rc=>{
    const r = rows[+rc.dataset.i];
    rc.addEventListener("mousemove",ev=>showTip(ev,tipHtml(r)));
    rc.addEventListener("mouseleave",hideTip);});}
}
function colbar(el, rows, {color="#2a78d6", label=r=>r.l, val=r=>r.v, tipHtml=null, H=190}={}){
  const W = el.clientWidth||600, n=rows.length, bw=Math.max(8,Math.min(46,(W-40)/n-4)), max=Math.max(...rows.map(val),1);
  let s = `<svg width="${W}" height="${H}" role="img">`;
  const base=H-26, top=14;
  [0,.5,1].forEach(f=>{ const y=base-(base-top)*f;
    s+=`<line x1="34" x2="${W-6}" y1="${y}" y2="${y}" stroke="var(--grid)"/>`;
    s+=`<text x="30" y="${y+3}" text-anchor="end">${Math.round(max*f)}</text>`;});
  rows.forEach((r,i)=>{
    const x=40+i*((W-46)/n), bh=Math.max(2,(base-top)*(val(r)/max));
    s+=`<rect data-i="${i}" x="${x}" y="${base-bh}" width="${bw}" height="${bh}" rx="4" fill="${color}"></rect>`;
    s+=`<text x="${x+bw/2}" y="${base-bh-4}" text-anchor="middle" class="vlab">${val(r)||""}</text>`;
    s+=`<text x="${x+bw/2}" y="${H-8}" text-anchor="middle">${esc(label(r))}</text>`;});
  s+="</svg>";
  el.innerHTML = s;
  if(tipHtml){ el.querySelectorAll("rect").forEach(rc=>{
    const r=rows[+rc.dataset.i];
    rc.addEventListener("mousemove",ev=>showTip(ev,tipHtml(r)));
    rc.addEventListener("mouseleave",hideTip);});}
}

/* ---------- generic sortable/filterable table ---------- */
function tableHTML(id, cols, rows, rowHTML){
  return `<div class="tablewrap"><table id="${id}"><thead><tr>${cols.map((c,i)=>`<th data-k="${i}" class="${c.num?'num':''}">${c.h}<span class="arr"></span></th>`).join("")}</tr></thead><tbody>${rows.map(rowHTML).join("")}</tbody></table></div>`;
}
function makeSortable(tblId, rows, keyFns, rerender){
  const tbl = document.getElementById(tblId); if(!tbl) return;
  let cur = {k:-1, dir:-1};
  tbl.querySelectorAll("th").forEach(th=>{ th.onclick = ()=>{
    const k=+th.dataset.k; cur = {k, dir: cur.k===k? -cur.dir : -1};
    rows.sort((a,b)=>{ const va=keyFns[k](a), vb=keyFns[k](b);
      const na = va==null||va==="", nb = vb==null||vb==="";
      if(na&&nb) return 0; if(na) return 1; if(nb) return -1;
      return (va<vb?-1:va>vb?1:0)*cur.dir; });
    rerender();
    tbl.querySelectorAll("th .arr").forEach(a=>a.textContent="");
    th.querySelector(".arr").textContent = cur.dir<0?" ▼":" ▲";
  };});
}

/* ---------- tabs ---------- */
const P_ORDER = {P0:0,P1:1,P2:2};
const PCOLOR = {P0:"var(--critical)",P1:"var(--serious)",P2:"var(--s1)"};
function pillP(p){ return `<span class="pill ${p.toLowerCase()}">${p==="P0"?"🔴 P0 — today":p==="P1"?"🟠 P1 — this week":"🟡 P2 — queue"}</span>`; }
function daysCell(d){ if(d==null) return "—";
  return `<span class="days ${d>=60?"hot":d>=21?"warm":""}">${d}d</span>`; }

/* Overview */
function renderOverview(el){
  const pb = DATA.pb;
  const owedTot = DATA.recv.reduce((a,r)=>a+(r.amt||0),0) - (DATA.recv.find(r=>String(r.who).startsWith("TOTAL"))?0:0);
  const payTot  = DATA.pay.reduce((a,r)=>a+(r.amt||0),0);
  const p0 = pb.filter(r=>r.p==="P0").length, p1=pb.filter(r=>r.p==="P1").length, p2=pb.filter(r=>r.p==="P2").length;
  const stale = pb.filter(r=>days(r.since)>=60).length;
  el.innerHTML = `
  <div class="tiles">
    <div class="tile crit"><div class="lbl">Owed TO ALTR (identified)</div><div class="val">$104,000</div><div class="note">22 receivables · several more unquantified</div></div>
    <div class="tile warn"><div class="lbl">Refunds + payables owed BY ALTR</div><div class="val">$47,889</div><div class="note">refunds, vendors, staff, referrals</div></div>
    <div class="tile warn"><div class="lbl">Trapped / untracked cash</div><div class="val">~$15–20k</div><div class="note">old BofA wires · $6.7k PayPal · lost Zelles · Fanbasis</div></div>
    <div class="tile"><div class="lbl">Open cases on the board</div><div class="val">${pb.length}</div><div class="note">${p0} do-today · ${p1} this-week · ${p2} queued</div></div>
    <div class="tile warn"><div class="lbl">Waiting 60+ days</div><div class="val">${stale}</div><div class="note">longest: Sarah H Snapchat ≈ 6 months</div></div>
  </div>
  <div class="cards">
    <div class="card"><h3>The bottleneck, in one chart</h3>
      <div class="csub">Money at stake behind each blocker — pay Vivek first and most of the board moves (Daniel 9/16: “we're waiting on Vivek for more than half”).</div>
      <div id="ch-block"></div></div>
    <div class="card"><h3>Open cases by bucket</h3>
      <div class="csub">What kind of action each open case needs right now.</div>
      <div id="ch-bucket"></div></div>
    <div class="card"><h3>Top money owed to ALTR</h3>
      <div class="csub">Largest identified receivables. Full list in “Owed to ALTR”.</div>
      <div id="ch-recv"></div></div>
    <div class="card"><h3>Refunds &amp; payables by type</h3>
      <div class="csub">What ALTR owes out, grouped. Full list in “Refunds &amp; Payables”.</div>
      <div id="ch-pay"></div></div>
  </div>
  <div class="card"><h3>Do these today (P0)</h3><div class="csub">The twelve moves that calm the most people and money, ranked.</div>
    <ol style="margin:6px 0 2px 18px; font-size:13px; line-height:1.7">
      ${pb.filter(r=>r.p==="P0").map(r=>`<li><b>${esc(r.who)}</b> — ${esc(r.action)} <span class="small">(${esc(r.bucket.toLowerCase())}${r.amt?", "+fmt$(r.amt):""})</span></li>`).join("")}
    </ol></div>`;
  hbar($("#ch-block"), [
    {l:"Vivek unpaid → cases frozen", v:45000, note:"~$45k of prepaid client work paused behind ~$8k vendor arrears"},
    {l:"Old-account / PayPal / Zelle", v:18000, note:"Amber $4k + Haleigh wires to old BofA · $6.7k PayPal hold · lost Zelles"},
    {l:"Refund backlog", v:23250, note:"Adam, Ethaniel, Carla, Chico, OFFMENU, realkeylamarie…"},
    {l:"Collections idle", v:104000, note:"$104k identified receivables, no one chasing"},
  ], {color:"#2a78d6", label:r=>r.l, val:r=>r.v, tipHtml:r=>`<b>${esc(r.l)}</b><br>${esc(r.note)}`});
  const buckets = {};
  DATA.pb.forEach(r=>{ const b=r.bucket.replace(/ .*—.*/,"").trim(); buckets[b]=(buckets[b]||0)+1; });
  const brows = Object.entries(buckets).map(([l,v])=>({l,v})).sort((a,b)=>b.v-a.v).slice(0,9);
  hbar($("#ch-bucket"), brows, {color:"#1baf7a", label:r=>r.l, val:r=>r.v, tipHtml:r=>`<b>${esc(r.l)}</b><br>${r.v} open case(s)`});
  $("#ch-bucket").querySelectorAll("svg text.vlab").forEach(t=>{ if(t.textContent.startsWith("$")) t.textContent=t.textContent.replace("$",""); });
  const recvTop = DATA.recv.filter(r=>r.amt).sort((a,b)=>b.amt-a.amt).slice(0,12).map(r=>({l:r.who,v:r.amt,ev:r.ev}));
  hbar($("#ch-recv"), recvTop, {color:"#2a78d6", label:r=>r.l, val:r=>r.v, tipHtml:r=>`<b>${esc(r.l)}</b><br>${esc(r.ev)}`});
  const ptypes = {};
  DATA.pay.forEach(r=>{ const t=r.type.replace("REFUND-RISK","REFUND RISK"); ptypes[t]=(ptypes[t]||0)+(r.amt||0); });
  const pcolors = {"REFUND":"#eb6834","REFUND RISK":"#eda100","VENDOR":"#2a78d6","STAFF":"#1baf7a","PARTNER":"#52514e","REFERRAL":"#898781","INVESTOR":"#eda100"};
  const prows = Object.entries(ptypes).filter(([,v])=>v>0).map(([l,v])=>({l,v})).sort((a,b)=>b.v-a.v);
  hbar($("#ch-pay"), prows, {label:r=>r.l, val:r=>r.v, colorOf:r=>pcolors[r.l]||"#2a78d6", tipHtml:r=>`<b>${esc(r.l)}</b><br>${fmt$(r.v)} identified`});
}

/* Priority board */
let pbFilter = "ALL", pbQ = "";
function renderBoard(el){
  el.innerHTML = `
   <div class="controls">
     <span class="chip ${pbFilter==="ALL"?"on":""}" data-f="ALL">All (${DATA.pb.length})</span>
     <span class="chip ${pbFilter==="P0"?"on":""}" data-f="P0">🔴 P0 (${DATA.pb.filter(r=>r.p==="P0").length})</span>
     <span class="chip ${pbFilter==="P1"?"on":""}" data-f="P1">🟠 P1 (${DATA.pb.filter(r=>r.p==="P1").length})</span>
     <span class="chip ${pbFilter==="P2"?"on":""}" data-f="P2">🟡 P2 (${DATA.pb.filter(r=>r.p==="P2").length})</span>
     <input type="search" id="pbq" placeholder="Search client, case, action…" value="${esc(pbQ)}">
     <span class="small">Sort by clicking headers · hover a row for the full case text</span>
   </div><div id="pbtbl"></div>`;
  const draw = ()=>{
    let rows = DATA.pb.filter(r=> (pbFilter==="ALL"||r.p===pbFilter) &&
      (!pbQ || (r.who+" "+r.case+" "+r.action+" "+r.bucket).toLowerCase().includes(pbQ.toLowerCase())));
    $("#pbtbl").innerHTML = tableHTML("pbt",
      [{h:"Priority"},{h:"Bucket"},{h:"Client / party"},{h:"Case (dated evidence)"},{h:"$ at stake",num:1},{h:"Waiting"},{h:"Days",num:1},{h:"Next action"}],
      rows, r=>`<tr title="${esc(r.case)}"><td>${pillP(r.p)}</td><td class="bucket">${esc(r.bucket)}</td>
        <td><b>${esc(r.who)}</b><div class="small">${esc(r.where)}</div></td>
        <td style="max-width:420px">${esc(r.case)}</td>
        <td class="num">${fmt$(r.amt)}</td>
        <td>${fdate(r.since)}</td><td class="num">${daysCell(days(r.since))}</td>
        <td style="max-width:240px"><b>${esc(r.action)}</b></td></tr>`);
    makeSortable("pbt", rows, [r=>P_ORDER[r.p], r=>r.bucket, r=>r.who.toLowerCase(), r=>r.case, r=>r.amt??-1, r=>r.since||"", r=>days(r.since)??-1, r=>r.action], draw);
  };
  draw();
  el.querySelectorAll(".chip").forEach(c=>c.onclick=()=>{ pbFilter=c.dataset.f; renderBoard(el); });
  $("#pbq").oninput = e=>{ pbQ=e.target.value; draw(); };
}

/* Receivables */
function renderRecv(el){
  const tot = DATA.recv.reduce((a,r)=>a+(r.amt||0),0);
  el.innerHTML = `<div class="tiles">
    <div class="tile crit"><div class="lbl">Identified total</div><div class="val">${fmt$(tot)}</div><div class="note">excludes rows with no stated amount</div></div>
    <div class="tile"><div class="lbl">Line items</div><div class="val">${DATA.recv.length}</div><div class="note">sorted biggest-first below</div></div>
    <div class="tile warn"><div class="lbl">Ground truth</div><div class="val">Bank sweep</div><div class="note">pre-Aug screenshots purged — statements decide the “verify” rows</div></div></div>
   <div class="card"><h3>All receivables</h3><div class="csub">Who owes ALTR, with the message evidence.</div><div id="rtbl"></div></div>`;
  const rows = [...DATA.recv].sort((a,b)=>(b.amt||0)-(a.amt||0));
  const draw = ()=>{ $("#rtbl").innerHTML = tableHTML("rt",
    [{h:"Who"},{h:"Evidence (dated)"},{h:"Amount",num:1},{h:"Status"},{h:"Action"}],
    rows, r=>`<tr><td><b>${esc(r.who)}</b></td><td style="max-width:520px">${esc(r.ev)}</td>
      <td class="num"><b>${fmt$(r.amt)}</b></td><td>${esc(r.status)}</td><td>${esc(r.action)}</td></tr>`);
    makeSortable("rt", rows, [r=>r.who.toLowerCase(), r=>r.ev, r=>r.amt??-1, r=>r.status, r=>r.action], draw); };
  draw();
}

/* Payables */
function renderPay(el){
  const tot = DATA.pay.reduce((a,r)=>a+(r.amt||0),0);
  el.innerHTML = `<div class="tiles">
    <div class="tile warn"><div class="lbl">Identified total</div><div class="val">${fmt$(tot)}</div><div class="note">refunds + vendors + staff + referrals</div></div>
    <div class="tile crit"><div class="lbl">Most urgent</div><div class="val">Vivek $8k</div><div class="note">then Adam $4,250 · Ollie $8,053 · VA invoice</div></div>
    <div class="tile"><div class="lbl">Refund requests being chased</div><div class="val">${DATA.pay.filter(r=>r.type.startsWith("REFUND")).length}</div><div class="note">4 chased multiple times in Sept</div></div></div>
   <div class="card"><h3>Everything ALTR owes out</h3><div class="csub">Type-tagged; sorted by urgency then size.</div><div id="ptbl"></div></div>`;
  const order = {VENDOR:0, REFUND:1, "REFUND-RISK":2, STAFF:3, PARTNER:4, REFERRAL:5, INVESTOR:6};
  const rows = [...DATA.pay].sort((a,b)=>(order[a.type]??9)-(order[b.type]??9) || (b.amt||0)-(a.amt||0));
  const pillT = t=>({VENDOR:'<span class="pill p2">VENDOR</span>',REFUND:'<span class="pill p0">REFUND</span>',"REFUND-RISK":'<span class="pill p1">REFUND RISK</span>',STAFF:'<span class="pill money-in">STAFF</span>',PARTNER:'<span class="pill gray">PARTNER</span>',REFERRAL:'<span class="pill gray">REFERRAL</span>',INVESTOR:'<span class="pill p1">INVESTOR</span>'}[t]||esc(t));
  const draw = ()=>{ $("#ptbl").innerHTML = tableHTML("pt",
    [{h:"Type"},{h:"Who"},{h:"Detail"},{h:"Amount",num:1},{h:"Status / action"}],
    rows, r=>`<tr><td>${pillT(r.type)}</td><td><b>${esc(r.who)}</b></td><td style="max-width:520px">${esc(r.detail)}</td>
      <td class="num"><b>${fmt$(r.amt)}</b></td><td>${esc(r.status)}</td></tr>`);
    makeSortable("pt", rows, [r=>order[r.type]??9, r=>r.who.toLowerCase(), r=>r.detail, r=>r.amt??-1, r=>r.status], draw); };
  draw();
}

/* Deposits */
function renderDep(el){
  const isVer = r => !/UNCONFIRMED|verify/i.test(r.src||"");
  const ver = DATA.dep.filter(r=>r.amt>0 && isVer(r));
  const inflow = ver.reduce((a,r)=>a+r.amt,0);
  el.innerHTML = `<div class="tiles">
    <div class="tile good"><div class="lbl">Verified inflows (Jun 8 – Sep 17)</div><div class="val">${fmt$(Math.round(inflow))}</div><div class="note">Chase Zelle alerts + text receipts · unconfirmed “sent” claims excluded</div></div>
    <div class="tile"><div class="lbl">Why this tab exists</div><div class="val" style="font-size:15px">Ground truth</div><div class="note">pre-Aug WhatsApp/iMessage payment screenshots are purged from disk — this is what actually landed</div></div></div>
   <div class="card"><h3>Verified inflows by day</h3><div class="csub">Positive = money in. Hover for the payer.</div><div id="ch-dep"></div></div>
   <div class="card"><h3>Deposit &amp; transfer log</h3><div class="csub">Includes two verified outbound transfers and four “sent but unconfirmed” items to check at the bank.</div><div id="dtbl"></div></div>`;
  const byday = {};
  ver.forEach(r=>{ byday[r.date]=(byday[r.date]||{v:0,who:[]}); byday[r.date].v+=r.amt; byday[r.date].who.push(r.who+" "+fmt$(r.amt)); });
  const rows = Object.entries(byday).sort((a,b)=>a[0]<b[0]?-1:1).map(([d,o])=>({l:fdate(d),v:Math.round(o.v),who:o.who}));
  colbar($("#ch-dep"), rows, {color:"#1baf7a", label:r=>r.l, val:r=>r.v, tipHtml:r=>`<b>${esc(r.l)}</b><br>${r.who.map(esc).join("<br>")}`});
  const drows = [...DATA.dep].sort((a,b)=>a.date<b.date?1:-1);
  const draw = ()=>{ $("#dtbl").innerHTML = tableHTML("dt",
    [{h:"Date"},{h:"Counterparty"},{h:"Method"},{h:"Amount",num:1},{h:"Source / verification"}],
    drows, r=>`<tr><td class="mono">${fdate(r.date)}</td><td><b>${esc(r.who)}</b></td><td>${esc(r.method)}</td>
      <td class="num">${!isVer(r)?'<span class="pill gray">UNCONFIRMED</span> ':""}${r.amt>0?'<span class="pill money-in">IN</span> ':'<span class="pill money-out">OUT</span> '}<b>${fmt$(Math.abs(r.amt))}</b></td>
      <td style="max-width:480px" class="small">${esc(r.src)}</td></tr>`);
    makeSortable("dt", drows, [r=>r.date, r=>r.who.toLowerCase(), r=>r.method, r=>r.amt, r=>r.src], draw); };
  draw();
}

/* Timeline */
function renderTL(el){
  el.innerHTML = `<div class="card"><h3>Money events per month</h3><div class="csub">How the situation built up. Hover a bar for that month's events.</div><div id="ch-tl"></div></div>
    <div class="card"><h3>Date-ordered money timeline</h3><div class="csub">Every significant money event found in the chats.</div><div id="ttbl"></div></div>`;
  const M={};
  DATA.tl.forEach(r=>{ const m=r.date.slice(0,7); (M[m]=M[m]||[]).push(r.event); });
  const rows = Object.entries(M).sort().map(([m,evs])=>({l:new Date(m+"-01T00:00:00").toLocaleDateString("en-US",{month:"short"}), v:evs.length, evs}));
  colbar($("#ch-tl"), rows, {color:"#2a78d6", label:r=>r.l, val:r=>r.v, tipHtml:r=>`<b>${r.v} events</b><br>${r.evs.slice(0,8).map(esc).join("<br>")}${r.evs.length>8?"<br>…":""}`});
  $("#ttbl").innerHTML = tableHTML("tt", [{h:"Date"},{h:"Event"}],
    DATA.tl, r=>`<tr><td class="mono" style="white-space:nowrap">${fdate(r.date)}</td><td>${esc(r.event)}</td></tr>`);
}

const TABS = [
  ["Overview", renderOverview, ()=> ""],
  ["Priority Board", renderBoard, ()=>DATA.pb.length],
  ["Owed to ALTR", renderRecv, ()=>DATA.recv.length],
  ["Refunds & Payables", renderPay, ()=>DATA.pay.length],
  ["Deposits Log", renderDep, ()=>DATA.dep.length],
  ["Timeline", renderTL, ()=>DATA.tl.length],
];
const nav = $("#nav"), main = $("#main");
TABS.forEach(([name,fn,count],i)=>{
  const b=document.createElement("button");
  b.innerHTML = esc(name)+(count()!==""?` <span class="n">${count()}</span>`:"");
  b.onclick=()=>show(i); nav.appendChild(b);
  const d=document.createElement("div"); d.className="tab"; d.id="tab"+i; main.appendChild(d);
});
function show(i){
  nav.querySelectorAll("button").forEach((b,j)=>b.classList.toggle("on",i===j));
  main.querySelectorAll(".tab").forEach((t,j)=>t.classList.toggle("on",i===j));
  const el=$("#tab"+i); if(!el.dataset.done){ TABS[i][1](el); el.dataset.done=1; }
}
show(0);
addEventListener("resize", ()=>{ main.querySelectorAll(".tab").forEach(t=>t.dataset.done=""); const on=[...main.querySelectorAll(".tab")].findIndex(t=>t.classList.contains("on")); show(on<0?0:on); });
document.body.insertAdjacentHTML("beforeend", `<div class="footer" style="padding:0 26px 30px; max-width:1400px; margin:0 auto">Sources: iMessage chat.db + WhatsApp ChatStorage.sqlite (read-only copies) · contact names via macOS AddressBook · deposits from Chase Zelle alert thread + verified screenshots. Companion files: ALTR_Case_Board.xlsx / ALTR_LEAD_CHECKUP_REPORT.md. Series palette validated for color-vision safety (dataviz checks passed; green/amber contrast relieved by direct labels + tables).</div>`);
</script>
</body></html>"""

out = "/Users/locklyjailbreak/conductor/workspaces/lead-check-up/dakar/ALTR_Case_Board_Dashboard.html"
open(out, "w").write(HTML.replace("__DATA__", DATA))
print("saved", out, len(HTML.replace('__DATA__', DATA))//1024, "KB")
