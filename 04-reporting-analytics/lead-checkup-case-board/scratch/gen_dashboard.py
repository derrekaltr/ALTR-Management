#!/usr/bin/env python3
"""ALTR Case Board dashboard — brand-matched to the ALTR deck system
(charcoal / cream / mint / purple · Hanken Grotesk + JetBrains Mono · flat
square cards, hairlines, diamond bullets). Phone-first."""
import json, datetime, importlib.util, base64

spec = importlib.util.spec_from_file_location("bx", "/Users/locklyjailbreak/conductor/workspaces/lead-check-up/dakar/scratch/build_xlsx.py")
bx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bx)  # side effect: rewrites xlsx (re-fixed afterwards by caller)

WORDMARK = base64.b64encode(open("/Users/locklyjailbreak/conductor/workspaces/smm-panel-pricing/melbourne/altr-wordmark.png","rb").read()).decode()

def iso(d): return d.isoformat() if isinstance(d, datetime.date) else d
PB = [{"p":r[0],"bucket":r[1],"who":r[2],"where":r[3],"case":r[4],"amt":r[5],"status":r[6],
      "since":iso(r[7]),"last":iso(r[9]),"action":r[10]} for r in bx.pb]
RECV = [{"who":r[0],"ev":r[1],"amt":r[2],"status":r[3],"action":r[4]} for r in bx.recv]
PAY = [{"type":r[0],"who":r[1],"detail":r[2],"amt":(int(r[3]) if isinstance(r[3],str) else r[3]),"status":r[4]} for r in bx.pay]
DEP = [{"date":iso(r[0]),"who":r[1],"method":r[2],"ref":r[3],"amt":r[4],"src":r[5]} for r in bx.dep]
TL  = [{"date":iso(r[0]),"event":r[1]} for r in bx.tl]
DATA = json.dumps({"pb":PB,"recv":RECV,"pay":PAY,"dep":DEP,"tl":TL}, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#232220">
<title>ALTR — Case Board</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ================= ALTR BRAND TOKENS (swap here to re-skin) ================= */
:root{
  --bg:#232220;            /* page charcoal */
  --card:#2b2a26;          /* raised surface */
  --card-2:#31302b;        /* hover surface */
  --cream:#e9ebda;         /* primary ink */
  --body:#d5d7c6;          /* body ink */
  --muted:#c9cbba;         /* secondary ink */
  --dim:#8f9083;           /* tertiary ink */
  --mint:#aeebcb;          /* brand accent (labels, marks) */
  --purple:#8247e5;        /* featured blocks */
  --hairline:rgba(233,235,218,.16);
  --hairline-strong:rgba(233,235,218,.45);
  /* chart series — validated for dark surface + color-vision safety */
  --c1:#2fa574; --c2:#9468e0; --c3:#bc8332; --c4:#4a8dcc;
  /* status (always paired with a label, never color alone) */
  --alert:#ff8a76;         /* critical / money-out */
  --sand:#ecc069;          /* caution */
  --ok:#aeebcb;            /* good / money-in */
  --sans:'Hanken Grotesk',-apple-system,system-ui,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,monospace;
}
/* =========================================================================== */
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--body);font:16.5px/1.6 var(--sans)}
::selection{background:var(--mint);color:var(--bg)}
.wrap{max-width:1240px;margin:0 auto;padding:0 clamp(16px,4vw,44px)}

/* ---------- header ---------- */
.topbar{display:flex;justify-content:space-between;align-items:center;padding:20px 0 16px;border-bottom:1px solid var(--hairline)}
.topbar img{height:18px;width:auto;display:block}
.topbar .tag{font:700 12.5px/1.5 var(--mono);letter-spacing:.22em;text-transform:uppercase;color:var(--dim);text-align:right}
.hero{padding:clamp(26px,5vw,52px) 0 clamp(20px,3vw,34px)}
.eyebrow-row{display:flex;align-items:center;gap:12px}
.diamond{width:11px;height:11px;background:var(--mint);transform:rotate(45deg);flex:none}
.eyebrow{font:700 13px/1 var(--mono);letter-spacing:.32em;text-transform:uppercase;color:var(--mint)}
h1{font:300 clamp(34px,7vw,62px)/1.1 var(--sans);color:var(--cream);letter-spacing:.002em;margin-top:clamp(14px,2.5vw,26px);max-width:820px}
.hero .sub{color:var(--dim);font-size:clamp(15px,1.9vw,17.5px);max-width:680px;margin-top:14px}
.hero .sub b{color:var(--muted);font-weight:500}

/* ---------- stat strip ---------- */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--hairline);border:1px solid var(--hairline);margin-bottom:clamp(18px,3vw,30px)}
.tile{background:var(--card);padding:clamp(14px,2.4vw,22px) clamp(14px,2vw,24px)}
.tile .lbl{font:700 12px/1.45 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--dim)}
.tile .val{font:300 clamp(30px,5vw,46px)/1.15 var(--sans);color:var(--cream);margin-top:8px;white-space:nowrap}
.tile .note{font-size:13.5px;color:var(--dim);margin-top:6px}
.tile.alert .val{color:var(--alert)} .tile.sand .val{color:var(--sand)}
.tile.mint .val{color:var(--mint)} .tile.purple .val{color:#b795f2}
@media(max-width:740px){.tiles{grid-template-columns:1fr 1fr}.tile .val{white-space:normal}.tile:last-child{grid-column:1/-1}}

/* ---------- nav ---------- */
nav{position:sticky;top:0;z-index:9;background:rgba(35,34,32,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--hairline)}
nav .wrap{display:flex;gap:clamp(14px,3vw,30px);overflow-x:auto;scrollbar-width:none}
nav .wrap::-webkit-scrollbar{display:none}
nav button{appearance:none;background:none;border:none;border-bottom:2px solid transparent;padding:16px 2px 14px;font:700 12.5px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--dim);cursor:pointer;white-space:nowrap}
nav button .n{color:var(--dim);margin-left:6px;font-weight:400}
nav button.on{color:var(--mint);border-bottom-color:var(--mint)}
nav button.on .n{color:var(--mint)}

main{padding:clamp(20px,3.5vw,36px) 0 20px}
.tab{display:none}.tab.on{display:block}

/* ---------- cards / sections ---------- */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:clamp(14px,2vw,24px);margin-bottom:clamp(14px,2vw,24px)}
@media(max-width:980px){.cards{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--hairline);padding:clamp(16px,2.6vw,28px)}
.card .clabel{font:700 12px/1 var(--mono);letter-spacing:.24em;text-transform:uppercase;color:var(--mint)}
.card h3{font:300 clamp(22px,3vw,30px)/1.25 var(--sans);color:var(--cream);margin:10px 0 4px}
.card .csub{color:var(--dim);font-size:14px;margin-bottom:14px;max-width:560px}

/* featured block — charcoal with a thin purple accent, no purple wall */
.featured{background:var(--card);border:1px solid var(--hairline);border-top:3px solid var(--purple)}
.featured ol{list-style:none;counter-reset:n;margin-top:8px}
.featured li{counter-increment:n;display:flex;gap:16px;align-items:baseline;padding:12px 0;border-top:1px solid var(--hairline);font-size:16px;line-height:1.55;color:var(--body)}
.featured li::before{content:counter(n,decimal-leading-zero);font:700 13px var(--mono);color:var(--mint);flex:none}
.featured li b{color:var(--cream);font-weight:600}
.featured li .small{color:var(--dim)}

/* ---------- charts ---------- */
svg{display:block}
svg text{font:12.5px var(--mono);fill:var(--dim)}
svg .lab{font:500 13.5px var(--sans);fill:var(--muted)}
svg .vlab{font:500 12.5px var(--mono);fill:var(--cream)}
svg .idx{font:700 11.5px var(--mono);fill:var(--mint)}
.gridline{stroke:var(--hairline)}

/* ---------- controls ---------- */
.controls{display:flex;gap:8px;margin:0 0 16px;flex-wrap:wrap;align-items:center}
.chip{appearance:none;border:1px solid var(--hairline-strong);background:none;color:var(--muted);padding:10px 15px;font:700 12px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;cursor:pointer}
.chip.on{background:var(--mint);border-color:var(--mint);color:var(--bg)}
input[type=search]{background:var(--card);border:1px solid var(--hairline-strong);color:var(--cream);padding:11px 13px;font:15px var(--sans);min-width:200px;flex:1;max-width:340px}
input[type=search]::placeholder{color:var(--dim)}
input[type=search]:focus{outline:none;border-color:var(--mint)}
.hint{font:400 13px var(--sans);color:var(--dim)}

/* ---------- tables (desktop) / case cards (mobile) ---------- */
.tablewrap{background:var(--card);border:1px solid var(--hairline)}
table{width:100%;border-collapse:collapse;font-size:15px}
th{text-align:left;font:700 11.5px var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--dim);padding:12px 12px;border-bottom:1px solid var(--hairline);cursor:pointer;user-select:none;white-space:nowrap}
th .arr{color:var(--mint)}
td{padding:14px 12px;border-bottom:1px solid var(--hairline);vertical-align:top;color:var(--body)}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--card-2)}
td.num,th.num{text-align:right;font-family:var(--mono);font-size:14px;white-space:nowrap}
td .who{color:var(--cream);font-weight:600}
td .where{font:400 12.5px var(--mono);color:var(--dim);margin-top:2px}
.bucket{display:block;font:700 11px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--mint);margin-top:7px}
.act{color:var(--cream);font-weight:500}
.amt{color:var(--cream)}
.evi{max-width:430px}
td.evi, td .evi{color:var(--muted);font-size:14px}

.pill{display:inline-block;font:700 11.5px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;padding:6px 9px;white-space:nowrap}
.pill.p0{background:rgba(255,138,118,.16);color:var(--alert)}
.pill.p1{background:rgba(236,192,105,.14);color:var(--sand)}
.pill.p2{background:rgba(174,235,203,.12);color:var(--mint)}
.pill.gray{background:rgba(233,235,218,.10);color:var(--muted)}
.pill.in{background:rgba(174,235,203,.14);color:var(--mint)}
.pill.out{background:rgba(255,138,118,.16);color:var(--alert)}
.days{font-family:var(--mono);font-weight:700;color:var(--muted)}
.days.hot{color:var(--alert)} .days.warm{color:var(--sand)}
.small{font-size:13px;color:var(--dim)}

@media(max-width:740px){
  .tablewrap{background:none;border:none}
  table,tbody,tr,td{display:block;width:100%}
  thead{display:none}
  tr{background:var(--card);border:1px solid var(--hairline);margin-bottom:10px;padding:14px 14px 6px}
  tr:hover td{background:none}
  td{border:none;padding:0 0 10px}
  td.num{text-align:left}
  td[data-l]::before{content:attr(data-l);display:block;font:700 10.5px var(--mono);letter-spacing:.22em;text-transform:uppercase;color:var(--dim);margin-bottom:3px}
  td:empty{display:none}
  .evi{max-width:none}
}

/* ---------- tooltip ---------- */
.tooltip{position:fixed;pointer-events:none;background:var(--cream);color:var(--bg);font:13.5px/1.5 var(--sans);padding:10px 12px;max-width:340px;z-index:30;display:none;box-shadow:0 6px 22px rgba(0,0,0,.45)}
.tooltip b{font-weight:600}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--hairline);margin-top:clamp(24px,4vw,44px)}
footer .wrap{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding-top:16px;padding-bottom:26px}
footer span{font:500 11px var(--mono);letter-spacing:.28em;text-transform:uppercase;color:var(--dim)}
@media print{ nav{position:static} body{background:#232220} .tab{display:block!important} }
</style></head>
<body data-palette="#2fa574,#9468e0,#bc8332,#4a8dcc">

<div class="wrap topbar">
  <img src="data:image/png;base64,__WORDMARK__" alt="ALTR">
  <div class="tag">Internal · Week of Sep 18 2026</div>
</div>

<div class="wrap hero">
  <div class="eyebrow-row"><span class="diamond"></span><span class="eyebrow">Case Dashboard</span></div>
  <h1>Where the money is.</h1>
  <div class="sub">Every open case, debt, refund and deposit pulled from <b>316k messages</b> across iMessage + WhatsApp, Mar 18 – Sep 18. Each row carries its message date — pull the thread to verify. <b>Local file, updates weekly.</b></div>
</div>

<div class="wrap"><div class="tiles" id="heroTiles"></div></div>

<nav><div class="wrap" id="nav"></div></nav>
<div class="wrap"><main id="main"></main></div>
<div class="tooltip" id="tip"></div>

<footer><div class="wrap">
  <span>ALTR — Case Board</span>
  <span>Sources · chat.db + ChatStorage + Chase alerts</span>
  <span>As of Sep 18 2026</span>
</div></footer>

<script>
const DATA = __DATA__;
const ASOF = new Date("2026-09-18T00:00:00");
const $ = s => document.querySelector(s);
const esc = s => String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const fmt$ = v => v==null||v===""?"—":"$"+Math.abs(v).toLocaleString(undefined,{maximumFractionDigits:0});
const days = d => d?Math.round((ASOF-new Date(d+"T00:00:00"))/864e5):null;
const fdate = d => d? new Date(d+"T00:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric"}) : "—";
const CS = ["#2fa574","#9468e0","#bc8332","#4a8dcc"];

/* tooltip */
const tip = $("#tip");
function showTip(ev,html){tip.innerHTML=html;tip.style.display="block";moveTip(ev)}
function moveTip(ev){const w=tip.offsetWidth,h=tip.offsetHeight;
 tip.style.left=Math.min(ev.clientX+14,innerWidth-w-8)+"px";
 tip.style.top=Math.min(ev.clientY+14,innerHeight-h-8)+"px"}
function hideTip(){tip.style.display="none"}

/* charts */
function hbar(el,rows,{color=CS[0],h=36,label=r=>r.l,val=r=>r.v,tipHtml=null,colorOf=null,money=true,numbered=false}={}){
 const W=el.clientWidth||600, narrow=W<520, LW=narrow?Math.min(135,W*.36):Math.min(215,W*.33),
  max=Math.max(...rows.map(val),1), H=rows.length*h+4;
 let s=`<svg width="${W}" height="${H}" role="img">`;
 rows.forEach((r,i)=>{const y=i*h+2,bw=Math.max(3,(W-LW-(narrow?58:80))*(val(r)/max)),c=colorOf?colorOf(r):color;
  if(numbered) s+=`<text x="0" y="${y+h/2+4}" class="idx">${String(i+1).padStart(2,"0")}</text>`;
  s+=`<text x="${LW-8}" y="${y+h/2+4}" text-anchor="end" class="lab">${esc(label(r)).slice(0,narrow?14:24)}</text>`;
  s+=`<rect data-i="${i}" x="${LW}" y="${y+6}" width="${bw}" height="${h-14}" rx="1" fill="${c}"></rect>`;
  s+=`<text x="${LW+bw+7}" y="${y+h/2+4}" class="vlab">${money?fmt$(val(r)):val(r)}</text>`;});
 s+="</svg>"; el.innerHTML=s;
 if(tipHtml) el.querySelectorAll("rect").forEach(rc=>{const r=rows[+rc.dataset.i];
  rc.addEventListener("mousemove",ev=>showTip(ev,tipHtml(r)));
  rc.addEventListener("mouseleave",hideTip);});
}
function colbar(el,rows,{color=CS[0],label=r=>r.l,val=r=>r.v,tipHtml=null,H=200}={}){
 const W=el.clientWidth||600,n=rows.length,slot=(W-44)/n,bw=Math.max(8,Math.min(44,slot-6)),
  max=Math.max(...rows.map(val),1),base=H-26,top=16;
 let s=`<svg width="${W}" height="${H}" role="img">`;
 [0,.5,1].forEach(f=>{const y=base-(base-top)*f;
  s+=`<line class="gridline" x1="36" x2="${W-4}" y1="${y}" y2="${y}"/>`;
  s+=`<text x="30" y="${y+4}" text-anchor="end">${Math.round(max*f/100)/10}k</text>`;});
 rows.forEach((r,i)=>{const x=42+i*slot,bh=Math.max(2,(base-top)*(val(r)/max));
  s+=`<rect data-i="${i}" x="${x}" y="${base-bh}" width="${bw}" height="${bh}" rx="1" fill="${color}"></rect>`;
  if(!(rows.length>9&&i%2)) s+=`<text x="${x+bw/2}" y="${H-8}" text-anchor="middle">${esc(label(r))}</text>`;});
 s+="</svg>"; el.innerHTML=s;
 if(tipHtml) el.querySelectorAll("rect").forEach(rc=>{const r=rows[+rc.dataset.i];
  rc.addEventListener("mousemove",ev=>showTip(ev,tipHtml(r)));
  rc.addEventListener("mouseleave",hideTip);});
}
function colbarCount(el,rows,opts){ // counts on y-axis
 const W=el.clientWidth||600,n=rows.length,slot=(W-44)/n,bw=Math.max(8,Math.min(44,slot-6)),
  max=Math.max(...rows.map(opts.val),1),H=opts.H||200,base=H-26,top=16;
 let s=`<svg width="${W}" height="${H}">`;
 [0,.5,1].forEach(f=>{const y=base-(base-top)*f;
  s+=`<line class="gridline" x1="36" x2="${W-4}" y1="${y}" y2="${y}"/>`;
  s+=`<text x="30" y="${y+4}" text-anchor="end">${Math.round(max*f)}</text>`;});
 rows.forEach((r,i)=>{const x=42+i*slot,bh=Math.max(2,(base-top)*(opts.val(r)/max));
  s+=`<rect data-i="${i}" x="${x}" y="${base-bh}" width="${bw}" height="${bh}" rx="1" fill="${opts.color||CS[1]}"></rect>`;
  s+=`<text x="${x+bw/2}" y="${base-bh-5}" text-anchor="middle" class="vlab">${opts.val(r)}</text>`;
  s+=`<text x="${x+bw/2}" y="${H-8}" text-anchor="middle">${esc(opts.label(r))}</text>`;});
 s+="</svg>"; el.innerHTML=s;
 if(opts.tipHtml) el.querySelectorAll("rect").forEach(rc=>{const r=rows[+rc.dataset.i];
  rc.addEventListener("mousemove",ev=>showTip(ev,opts.tipHtml(r)));
  rc.addEventListener("mouseleave",hideTip);});
}

/* table helper */
function tableHTML(id,cols,rows,rowHTML){
 return `<div class="tablewrap"><table id="${id}"><thead><tr>${cols.map((c,i)=>`<th data-k="${i}" class="${c.num?'num':''}">${c.h}<span class="arr"></span></th>`).join("")}</tr></thead><tbody>${rows.map(rowHTML).join("")}</tbody></table></div>`;
}
function makeSortable(tblId,rows,keyFns,rerender){
 const tbl=document.getElementById(tblId); if(!tbl) return;
 let cur={k:-1,dir:-1};
 tbl.querySelectorAll("th").forEach(th=>{th.onclick=()=>{
  const k=+th.dataset.k; cur={k,dir:cur.k===k?-cur.dir:-1};
  rows.sort((a,b)=>{const va=keyFns[k](a),vb=keyFns[k](b);
   const na=va==null||va==="",nb=vb==null||vb==="";
   if(na&&nb)return 0; if(na)return 1; if(nb)return -1;
   return (va<vb?-1:va>vb?1:0)*cur.dir;});
  rerender();
  const t2=document.getElementById(tblId);
  t2.querySelectorAll("th .arr").forEach(a=>a.textContent="");
  t2.querySelector(`th[data-k="${k}"] .arr`).textContent=cur.dir<0?" ▼":" ▲";};});
}

const P_ORDER={P0:0,P1:1,P2:2};
const pillP=p=>`<span class="pill ${p.toLowerCase()}">${p==="P0"?"P0 · today":p==="P1"?"P1 · this week":"P2 · queue"}</span>`;
const daysCell=d=>d==null?"—":`<span class="days ${d>=60?"hot":d>=21?"warm":""}">${d}d</span>`;

/* hero tiles */
const recvTot=DATA.recv.reduce((a,r)=>a+(r.amt||0),0), payTot=DATA.pay.reduce((a,r)=>a+(r.amt||0),0);
$("#heroTiles").innerHTML=`
 <div class="tile mint"><div class="lbl">Owed to ALTR</div><div class="val">${fmt$(recvTot)}</div><div class="note">${DATA.recv.filter(r=>r.amt).length} identified receivables</div></div>
 <div class="tile alert"><div class="lbl">ALTR owes out</div><div class="val">${fmt$(payTot)}</div><div class="note">refunds · vendors · staff</div></div>
 <div class="tile sand"><div class="lbl">Trapped cash</div><div class="val">~$15–20k</div><div class="note">old accounts · PayPal · lost Zelles</div></div>
 <div class="tile"><div class="lbl">Open cases</div><div class="val">${DATA.pb.length}</div><div class="note">${DATA.pb.filter(r=>r.p==="P0").length} today · ${DATA.pb.filter(r=>r.p==="P1").length} this week</div></div>
 <div class="tile purple"><div class="lbl">Waiting 60+ days</div><div class="val">${DATA.pb.filter(r=>days(r.since)>=60).length}</div><div class="note">longest ≈ 6 months (Sarah H)</div></div>`;

/* ---------- tabs ---------- */
function card(label,h3,sub,body){return `<div class="card"><div class="clabel">${label}</div><h3>${h3}</h3><div class="csub">${sub}</div>${body}</div>`}

function renderOverview(el){
 el.innerHTML=`
  <div class="card featured" style="margin-bottom:clamp(14px,2vw,24px)">
    <div class="clabel">Do today</div>
    <h3>Clear the refunds. Confirm the payments.</h3>
    <div class="csub">The moves that calm the most people and money — ranked. Every one is a send, a confirmation, or a call.</div>
    <ol>${DATA.pb.filter(r=>r.p==="P0").map(r=>`<li><span><b>${esc(r.who)}</b> — ${esc(r.action)} <span class="small">${r.amt?fmt$(r.amt):""}</span></span></li>`).join("")}</ol>
  </div>
  <div class="cards">
   ${card("Where it's stuck","One chart, three piles","Money sitting behind each problem. Hover a bar for detail.",'<div id="ch-block"></div>')}
   ${card("Board mix","Open cases by action needed","What kind of move each of the '+DATA.pb.length+' cases is waiting on.",'<div id="ch-bucket"></div>')}
   ${card("Collect list","Top money owed to ALTR","Largest identified receivables — full ledger in Owed.",'<div id="ch-recv"></div>')}
   ${card("Out list","Refunds &amp; payables by type","What ALTR owes out — full ledger in Owed by us.",'<div id="ch-pay"></div>')}
  </div>`;
 hbar($("#ch-block"),[
  {l:"Collections idle",v:DATA.recv.reduce((a,r)=>a+(r.amt||0),0),note:"identified receivables with nobody chasing"},
  {l:"Refund backlog",v:23250,note:"Adam, Ethaniel, Carla, Chico, OFFMENU, realkeylamarie…"},
  {l:"Trapped cash",v:18000,note:"old-BofA wires · $6.7k PayPal hold · unmatched Zelles"},
 ],{color:CS[1],tipHtml:r=>`<b>${esc(r.l)}</b><br>${esc(r.note)}`});
 const b={}; DATA.pb.forEach(r=>{const k=r.bucket.trim();b[k]=(b[k]||0)+1});
 hbar($("#ch-bucket"),Object.entries(b).map(([l,v])=>({l,v})).sort((a,x)=>x.v-a.v).slice(0,9),
  {color:CS[0],money:false,tipHtml:r=>`<b>${esc(r.l)}</b><br>${r.v} open case(s)`});
 hbar($("#ch-recv"),DATA.recv.filter(r=>r.amt).sort((a,x)=>x.amt-a.amt).slice(0,10).map(r=>({l:r.who,v:r.amt,ev:r.ev})),
  {color:CS[3],numbered:true,tipHtml:r=>`<b>${esc(r.l)}</b><br>${esc(r.ev)}`});
 const pt={}; DATA.pay.forEach(r=>{const t=r.type.replace("REFUND-RISK","REFUND RISK");pt[t]=(pt[t]||0)+(r.amt||0)});
 const pc={"REFUND":CS[1],"REFUND RISK":CS[2],"VENDOR":CS[3],"STAFF":CS[0],"PARTNER":"#8f9083","REFERRAL":"#c9cbba","INVESTOR":CS[2]};
 hbar($("#ch-pay"),Object.entries(pt).filter(([,v])=>v>0).map(([l,v])=>({l,v})).sort((a,x)=>x.v-a.v),
  {colorOf:r=>pc[r.l]||CS[3],tipHtml:r=>`<b>${esc(r.l)}</b><br>${fmt$(r.v)} identified`});
}

let pbFilter="ALL",pbQ="";
function renderBoard(el){
 el.innerHTML=`<div class="controls">
   <button class="chip ${pbFilter==="ALL"?"on":""}" data-f="ALL">All ${DATA.pb.length}</button>
   <button class="chip ${pbFilter==="P0"?"on":""}" data-f="P0">P0 ${DATA.pb.filter(r=>r.p==="P0").length}</button>
   <button class="chip ${pbFilter==="P1"?"on":""}" data-f="P1">P1 ${DATA.pb.filter(r=>r.p==="P1").length}</button>
   <button class="chip ${pbFilter==="P2"?"on":""}" data-f="P2">P2 ${DATA.pb.filter(r=>r.p==="P2").length}</button>
   <input type="search" id="pbq" placeholder="Search client, case, action…" value="${esc(pbQ)}">
   <span class="hint">tap headers to sort</span></div><div id="pbtbl"></div>`;
 const draw=()=>{
  let rows=DATA.pb.filter(r=>(pbFilter==="ALL"||r.p===pbFilter)&&(!pbQ||(r.who+" "+r.case+" "+r.action+" "+r.bucket).toLowerCase().includes(pbQ.toLowerCase())));
  $("#pbtbl").innerHTML=tableHTML("pbt",
   [{h:"Priority"},{h:"Client / party"},{h:"Case (dated evidence)"},{h:"At stake",num:1},{h:"Days",num:1},{h:"Next action"}],
   rows,r=>`<tr><td data-l="Priority">${pillP(r.p)} <span class="bucket">${esc(r.bucket)}</span></td>
    <td data-l="Client"><span class="who">${esc(r.who)}</span><div class="where">${esc(r.where)}</div></td>
    <td class="evi" data-l="Case">${esc(r.case)}</td>
    <td class="num amt" data-l="At stake">${fmt$(r.amt)}</td>
    <td class="num" data-l="Waiting">${daysCell(days(r.since))} <span class="small">since ${fdate(r.since)}</span></td>
    <td data-l="Next action" class="act">${esc(r.action)}</td></tr>`);
  makeSortable("pbt",rows,[r=>P_ORDER[r.p],r=>r.who.toLowerCase(),r=>r.case,r=>r.amt??-1,r=>days(r.since)??-1,r=>r.action],draw);};
 draw();
 el.querySelectorAll(".chip").forEach(c=>c.onclick=()=>{pbFilter=c.dataset.f;renderBoard(el)});
 $("#pbq").oninput=e=>{pbQ=e.target.value;draw()};
}

function renderRecv(el){
 const rows=[...DATA.recv].sort((a,b)=>(b.amt||0)-(a.amt||0));
 el.innerHTML=card("Collect",fmt$(rows.reduce((a,r)=>a+(r.amt||0),0))+" identified","Who owes ALTR, with the message evidence. Sort any column.",'<div id="rtbl"></div>');
 const draw=()=>{$("#rtbl").innerHTML=tableHTML("rt",
  [{h:"Who"},{h:"Evidence (dated)"},{h:"Amount",num:1},{h:"Status"},{h:"Action"}],
  rows,r=>`<tr><td data-l="Who"><span class="who">${esc(r.who)}</span></td>
   <td class="evi" data-l="Evidence">${esc(r.ev)}</td>
   <td class="num amt" data-l="Amount">${fmt$(r.amt)}</td>
   <td data-l="Status"><span class="pill gray">${esc(r.status)}</span></td>
   <td data-l="Action" class="act">${esc(r.action)}</td></tr>`);
  makeSortable("rt",rows,[r=>r.who.toLowerCase(),r=>r.ev,r=>r.amt??-1,r=>r.status,r=>r.action],draw);};
 draw();
}

function renderPay(el){
 const order={VENDOR:0,REFUND:1,"REFUND-RISK":2,STAFF:3,PARTNER:4,REFERRAL:5,INVESTOR:6};
 const rows=[...DATA.pay].sort((a,b)=>(order[a.type]??9)-(order[b.type]??9)||(b.amt||0)-(a.amt||0));
 const pillT=t=>({VENDOR:'<span class="pill p2">Vendor</span>',REFUND:'<span class="pill p0">Refund</span>',"REFUND-RISK":'<span class="pill p1">Refund risk</span>',STAFF:'<span class="pill in">Staff</span>',PARTNER:'<span class="pill gray">Partner</span>',REFERRAL:'<span class="pill gray">Referral</span>',INVESTOR:'<span class="pill p1">Investor</span>'}[t]||esc(t));
 el.innerHTML=card("Owed by us",fmt$(rows.reduce((a,r)=>a+(r.amt||0),0))+" identified","Refunds first — they're the trust killers. Then Ollie's wire and the small stuff that keeps relationships warm.",'<div id="ptbl"></div>');
 const draw=()=>{$("#ptbl").innerHTML=tableHTML("pt",
  [{h:"Type"},{h:"Who"},{h:"Detail"},{h:"Amount",num:1},{h:"Status / action"}],
  rows,r=>`<tr><td data-l="Type">${pillT(r.type)}</td>
   <td data-l="Who"><span class="who">${esc(r.who)}</span></td>
   <td class="evi" data-l="Detail">${esc(r.detail)}</td>
   <td class="num amt" data-l="Amount">${fmt$(r.amt)}</td>
   <td data-l="Status" class="act">${esc(r.status)}</td></tr>`);
  makeSortable("pt",rows,[r=>order[r.type]??9,r=>r.who.toLowerCase(),r=>r.detail,r=>r.amt??-1,r=>r.status],draw);};
 draw();
}

function renderDep(el){
 const isVer=r=>!/UNCONFIRMED|verify/i.test(r.src||"");
 const ver=DATA.dep.filter(r=>r.amt>0&&isVer(r));
 const inflow=ver.reduce((a,r)=>a+r.amt,0);
 el.innerHTML=`
  ${card("Ground truth",fmt$(Math.round(inflow))+" verified in","Chase Zelle alerts + hard receipts, Jun 8 – Sep 17. “Sent” claims that never showed a receipt are badged UNCONFIRMED and excluded. Campus Phone Repair deposits (separate business) are excluded. Pre-Aug chat screenshots are purged from disk — bank statements decide those.",'<div id="ch-dep"></div>')}
  ${card("Log","Deposit &amp; transfer log","Sorted newest first. Includes outbound transfers and the four unconfirmed claims to check at the bank.",'<div id="dtbl"></div>')}`;
 const byday={};
 ver.forEach(r=>{byday[r.date]=byday[r.date]||{v:0,who:[]};byday[r.date].v+=r.amt;byday[r.date].who.push(r.who+" "+fmt$(r.amt))});
 colbar($("#ch-dep"),Object.entries(byday).sort().map(([d,o])=>({l:fdate(d),v:Math.round(o.v),who:o.who})),
  {color:CS[0],tipHtml:r=>`<b>${esc(r.l)}</b><br>${r.who.map(esc).join("<br>")}`});
 const drows=[...DATA.dep].sort((a,b)=>a.date<b.date?1:-1);
 const draw=()=>{$("#dtbl").innerHTML=tableHTML("dt",
  [{h:"Date"},{h:"Counterparty"},{h:"Method"},{h:"Amount",num:1},{h:"Source / verification"}],
  drows,r=>`<tr><td data-l="Date" class="num" style="text-align:left">${fdate(r.date)}</td>
   <td data-l="Counterparty"><span class="who">${esc(r.who)}</span></td>
   <td data-l="Method">${esc(r.method)}</td>
   <td class="num" data-l="Amount">${!isVer(r)?'<span class="pill gray">Unconfirmed</span> ':""}<span class="pill ${r.amt>0?"in":"out"}">${r.amt>0?"In":"Out"}</span> <span class="amt">${fmt$(Math.abs(r.amt))}</span></td>
   <td data-l="Source" class="evi">${esc(r.src)}</td></tr>`);
  makeSortable("dt",drows,[r=>r.date,r=>r.who.toLowerCase(),r=>r.method,r=>r.amt,r=>r.src],draw);};
 draw();
}

function renderTL(el){
 const M={}; DATA.tl.forEach(r=>{const m=r.date.slice(0,7);(M[m]=M[m]||[]).push(r.event)});
 el.innerHTML=`
  ${card("How it built up","Money events per month","Hover a bar for that month's events.",'<div id="ch-tl"></div>')}
  ${card("The record","Date-ordered money timeline","Every significant money event found in the chats.",'<div id="ttbl"></div>')}`;
 colbarCount($("#ch-tl"),Object.entries(M).sort().map(([m,evs])=>({l:new Date(m+"-01T00:00:00").toLocaleDateString("en-US",{month:"short"}),v:evs.length,evs})),
  {color:CS[1],label:r=>r.l,val:r=>r.v,tipHtml:r=>`<b>${r.v} events</b><br>${r.evs.slice(0,8).map(esc).join("<br>")}${r.evs.length>8?"<br>…":""}`});
 $("#ttbl").innerHTML=tableHTML("tt",[{h:"Date"},{h:"Event"}],
  DATA.tl,r=>`<tr><td data-l="Date" style="white-space:nowrap;font-family:var(--mono);font-size:12px">${fdate(r.date)}</td><td data-l="Event" class="evi">${esc(r.event)}</td></tr>`);
}

const TABS=[
 ["Overview",renderOverview,""],
 ["Board",renderBoard,DATA.pb.length],
 ["Owed",renderRecv,DATA.recv.length],
 ["Owed by us",renderPay,DATA.pay.length],
 ["Deposits",renderDep,DATA.dep.length],
 ["Timeline",renderTL,DATA.tl.length],
];
const nav=$("#nav"),main=$("#main");
TABS.forEach(([name,fn,count],i)=>{
 const b=document.createElement("button");
 b.innerHTML=esc(name)+(count!==""?` <span class="n">${count}</span>`:"");
 b.onclick=()=>show(i); nav.appendChild(b);
 const d=document.createElement("div");d.className="tab";d.id="tab"+i;main.appendChild(d);});
function show(i){
 nav.querySelectorAll("button").forEach((b,j)=>b.classList.toggle("on",i===j));
 main.querySelectorAll(".tab").forEach((t,j)=>t.classList.toggle("on",i===j));
 const el=$("#tab"+i); if(!el.dataset.done){TABS[i][1](el);el.dataset.done=1;}}
show(0);
let rT; addEventListener("resize",()=>{clearTimeout(rT);rT=setTimeout(()=>{
 main.querySelectorAll(".tab").forEach(t=>t.dataset.done="");
 const on=[...main.querySelectorAll(".tab")].findIndex(t=>t.classList.contains("on"));
 show(on<0?0:on);},200)});
</script>
</body></html>"""

out = "/Users/locklyjailbreak/conductor/workspaces/lead-check-up/dakar/ALTR_Case_Board_Dashboard.html"
html = HTML.replace("__DATA__", DATA).replace("__WORDMARK__", WORDMARK)
open(out, "w").write(html)
print("saved", out, len(html)//1024, "KB")
