"""
QG — gera o centro de operações (constelação) a partir da varredura do repositório.

    python tools/qg/build.py     -> escreve docs/qg/index.html + state.json

A geometria e os números saem todos do repo. Rode de novo quando ele mudar;
o painel nunca inventa nem envelhece em silêncio — o carimbo diz a hora da varredura.
"""
from __future__ import annotations

import json
from pathlib import Path

from scan import ROOT, build_state

OUT = ROOT / "docs" / "qg" / "index.html"


def payload(st: dict) -> dict:
    """Reduz o estado ao que a constelação precisa desenhar."""
    status = {}
    for b in st["state"]["blocks"]:
        if b.get("agente"):
            status[b["agente"]] = {"st": "warn", "note": b.get("motivo", "")}
    for f in st["state"]["findings"]:
        if f.get("agente"):
            status.setdefault(f["agente"], {"st": "ok", "note": f.get("desc", "")})

    squads = [{
        "id": s["id"], "icon": s["icon"],
        "agents": [{
            "p": a["persona"], "id": a["id"], "lead": a["is_lead"],
            "cf": a["clones_formal"], "cp": a["clones_prose_only"], "d": a["docs"],
            "st": status.get(a["id"], {}).get("st"),
            "note": status.get(a["id"], {}).get("note", ""),
        } for a in s["agents"]],
    } for s in st["squads"]]

    feeds = {c["id"]: [] for c in st["clones"]}
    for s in st["squads"]:
        for a in s["agents"]:
            for c in a["clones"]:
                feeds.setdefault(c, []).append(a["id"])

    clones = [{"id": c["id"], "prim": c["depth"] == "primária",
               "docs": c["source_docs"], "feeds": feeds.get(c["id"], [])}
              for c in st["clones"]]

    t = st["totals"]
    att = []
    if t["prose_only_links"]:
        att.append([str(t["prose_only_links"]), "ligações só em prosa",
                    "funcionam, mas escapam do campo knowledge_sources — arrumação", "idle"])
    if t["consultive_clones"]:
        att.append([f'{t["consultive_clones"]}/{t["clones"]}', "clones consultivos",
                    "sem fonte primária ingerida", "warn"])
    if t["orphan_clones"]:
        att.append([str(len(t["orphan_clones"])), "clones órfãos",
                    ", ".join(t["orphan_clones"]), "crit"])
    sem_fonte = t["agents"] - t["agents_with_sources"]
    if sem_fonte:
        att.append([str(sem_fonte), "agentes sem fonte alguma",
                    "nem clone nem documento — operam só com a própria persona", "crit"])
    att.append([f'{t["agents_without_clone"]}/{t["agents"]}', "agentes sem clone",
                "têm material da casa, mas nenhum especialista ligado", "idle"])
    for b in st["state"]["blocks"]:
        att.append(["⏸", b.get("quem", "bloqueio"), b.get("motivo", ""), "warn"])

    return {
        "stamp": st["generated_at"][:16].replace("T", " "),
        "rev": f'{st["branch"]}@{st["head"]}',
        "squads": squads, "clones": clones, "att": att,
        "totals": {"sq": t["squads"], "ag": t["agents"], "cl": t["clones"],
                   "lk": t["links"], "orf": len(t["orphan_clones"])},
        "activity": st["activity"][:6],
    }


TPL = r"""<title>ARVEX · QG</title>
<style>
:root{--bg:#070d15;--bg2:#0b1420;--panel:#0f1c2b;--edge:#1b3145;--edge2:#142434;
--ink:#dce9f5;--ink2:#8dabc6;--ink3:#54748f;--ink4:#33506a;
--gold:#e8b657;--cyan:#5ad6da;--ok:#4ec48f;--warn:#e0a83f;--crit:#e56d58;
--mono:ui-monospace,"Cascadia Mono","SF Mono",Menlo,Consolas,monospace;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--r:3px}
@media(prefers-color-scheme:light){:root{--bg:#eaeff5;--bg2:#e0e8f0;--panel:#f6f9fc;--edge:#c0d0df;--edge2:#d4dfea;
--ink:#0c2035;--ink2:#3b5b79;--ink3:#6f8da8;--ink4:#9db3c8;
--gold:#8b5c07;--cyan:#0d6f72;--ok:#1d6f52;--warn:#8a6413;--crit:#a53c2c}}
:root[data-theme=dark]{--bg:#070d15;--bg2:#0b1420;--panel:#0f1c2b;--edge:#1b3145;--edge2:#142434;
--ink:#dce9f5;--ink2:#8dabc6;--ink3:#54748f;--ink4:#33506a;
--gold:#e8b657;--cyan:#5ad6da;--ok:#4ec48f;--warn:#e0a83f;--crit:#e56d58}
:root[data-theme=light]{--bg:#eaeff5;--bg2:#e0e8f0;--panel:#f6f9fc;--edge:#c0d0df;--edge2:#d4dfea;
--ink:#0c2035;--ink2:#3b5b79;--ink3:#6f8da8;--ink4:#9db3c8;
--gold:#8b5c07;--cyan:#0d6f72;--ok:#1d6f52;--warn:#8a6413;--crit:#a53c2c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:13.5px;line-height:1.5;-webkit-font-smoothing:antialiased}
.sh{max-width:1440px;margin:0 auto;padding:clamp(.8rem,2.2vw,1.6rem)}
.bar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:1rem;
border-bottom:1px solid var(--edge);padding-bottom:.75rem;margin-bottom:.85rem}
h1{margin:0;font-family:var(--mono);font-size:1.1rem;font-weight:600;letter-spacing:-.01em}
.stamp{font-family:var(--mono);font-size:.61rem;color:var(--ink3);margin-top:.18rem;letter-spacing:.04em}
.stamp b{color:var(--cyan);font-weight:400}
.ro{display:flex;gap:clamp(.75rem,2vw,1.7rem);flex-wrap:wrap}
.ro .k{display:block;font-family:var(--mono);font-size:.55rem;letter-spacing:.15em;text-transform:uppercase;color:var(--ink3)}
.ro .v{font-family:var(--mono);font-size:1.18rem;font-variant-numeric:tabular-nums;line-height:1.25}
.gr{display:grid;gap:.8rem;grid-template-columns:1fr}
@media(min-width:1020px){.gr{grid-template-columns:1fr 282px}}
.vp{position:relative;background:var(--bg);border:1px solid var(--edge);border-radius:var(--r);overflow:hidden;aspect-ratio:4/3}
@media(min-width:1020px){.vp{aspect-ratio:16/10}}
canvas{display:block;width:100%;height:100%}
.hud{position:absolute;inset:0;pointer-events:none;z-index:2}
.hud .cor{position:absolute;width:14px;height:14px;border:1px solid var(--ink4)}
.tl{top:8px;left:8px;border-right:0;border-bottom:0}.tr{top:8px;right:8px;border-left:0;border-bottom:0}
.bl{bottom:8px;left:8px;border-right:0;border-top:0}.br{bottom:8px;right:8px;border-left:0;border-top:0}
.rd{position:absolute;font-family:var(--mono);font-size:.57rem;letter-spacing:.1em;color:var(--ink3)}
.rd.a{top:9px;left:30px}.rd.b{top:9px;right:30px}.rd b{color:var(--cyan);font-weight:400}
.lg{position:absolute;left:30px;bottom:9px;display:flex;flex-direction:column;gap:.2rem;
font-family:var(--mono);font-size:.57rem;color:var(--ink3);z-index:2}
.lg i{display:inline-block;width:13px;height:2px;margin-right:.35rem;vertical-align:middle}
.tip{position:absolute;pointer-events:none;opacity:0;transform:translate(-50%,-150%);background:var(--panel);
border:1px solid var(--edge);border-radius:var(--r);padding:.35rem .5rem;font-family:var(--mono);
font-size:.66rem;white-space:nowrap;transition:opacity .12s;box-shadow:0 8px 24px rgba(0,0,0,.45);z-index:3}
.tip b{color:var(--gold)}.tip span{color:var(--ink3)}
.rail{display:flex;flex-direction:column;gap:.8rem;min-width:0}
.card{background:var(--bg2);border:1px solid var(--edge);border-radius:var(--r);padding:.7rem .8rem}
.card h2{margin:0 0 .55rem;font-family:var(--mono);font-size:.56rem;letter-spacing:.16em;
text-transform:uppercase;color:var(--ink3);font-weight:600}
ul{list-style:none;margin:0;padding:0}
.att li{display:grid;grid-template-columns:auto 1fr;gap:.5rem;padding:.28rem 0;border-bottom:1px solid var(--edge2)}
.att li:last-child{border-bottom:0}
.att .n{font-family:var(--mono);font-size:1rem;font-variant-numeric:tabular-nums;line-height:1.15;color:var(--warn)}
.att .crit .n{color:var(--crit)}.att .idle .n{color:var(--ink3)}
.att .t{font-family:var(--mono);font-size:.68rem;color:var(--ink)}
.att .d{font-size:.67rem;color:var(--ink3);line-height:1.35}
.sq button{width:100%;display:grid;grid-template-columns:7px 1fr auto;align-items:center;gap:.45rem;
background:transparent;border:0;padding:.26rem .28rem;cursor:pointer;font-family:var(--mono);
font-size:.71rem;color:var(--ink2);text-align:left;border-radius:2px;transition:background .16s,color .16s}
.sq button:hover,.sq button[aria-pressed=true]{background:var(--panel);color:var(--ink)}
.sq button:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.sq .pip{width:7px;height:7px;border-radius:50%;background:var(--ink4)}
.sq .ct{font-variant-numeric:tabular-nums;color:var(--ink3);font-size:.65rem}
.sq .tk{display:block;height:2px;background:var(--edge2);border-radius:2px;margin-top:.2rem;overflow:hidden}
.sq .tk i{display:block;height:100%;background:var(--gold);opacity:.7}
.det{min-height:104px}
.det .nm{font-family:var(--mono);font-size:.85rem;color:var(--gold);margin:0}
.det .rl{margin:.05rem 0 .45rem;color:var(--ink2);font-size:.71rem}
.det li{font-family:var(--mono);font-size:.66rem;color:var(--ink2);display:flex;gap:.35rem;padding:.08rem 0}
.det li em{color:var(--cyan);font-style:normal}
.det li .pr{color:var(--warn)}
.det .hint{color:var(--ink3);font-size:.71rem;margin:0}
.det .bg{display:inline-block;font-family:var(--mono);font-size:.55rem;letter-spacing:.08em;
padding:.08rem .32rem;border:1px solid;border-radius:2px;margin-bottom:.35rem}
.act li{display:grid;grid-template-columns:54px 1fr;gap:.45rem;font-family:var(--mono);font-size:.63rem;
color:var(--ink3);padding:.16rem 0;border-bottom:1px solid var(--edge2)}
.act li:last-child{border-bottom:0}.act .s{color:var(--gold)}
.foot{margin-top:.9rem;color:var(--ink3);font-size:.71rem;max-width:88ch}
.foot code{font-family:var(--mono);color:var(--ink2);background:var(--panel);padding:.05rem .28rem;border-radius:2px}
@media(prefers-reduced-motion:reduce){*{transition-duration:.01ms!important}}
</style>

<div class="sh">
  <div class="bar">
    <div><h1>QG · centro de operações</h1><div class="stamp" id="stamp"></div></div>
    <div class="ro" id="ro"></div>
  </div>
  <div class="gr">
    <div class="vp" id="vp">
      <canvas id="cv"></canvas>
      <div class="hud">
        <span class="cor tl"></span><span class="cor tr"></span><span class="cor bl"></span><span class="cor br"></span>
        <div class="rd a">ARVEX · MALHA OPERACIONAL</div>
        <div class="rd b">SCAN <b id="scan">000°</b></div>
      </div>
      <div class="lg">
        <span><i style="background:var(--gold)"></i>orquestração · c-level → squad</span>
        <span><i style="background:var(--cyan)"></i>conhecimento · declarado em knowledge_sources</span>
        <span><i style="background:var(--warn)"></i>conhecimento · citado só na prosa do agente</span>
      </div>
      <div class="tip" id="tip"></div>
    </div>
    <div class="rail">
      <div class="card"><h2>Atenção</h2><ul class="att" id="att"></ul></div>
      <div class="card"><h2>Squads</h2><ul class="sq" id="sq"></ul></div>
      <div class="card det" id="det"><p class="hint">Aponte um nó, ou selecione um squad para isolar a cadeia.</p></div>
      <div class="card"><h2>Atividade</h2><ul class="act" id="act"></ul></div>
    </div>
  </div>
  <p class="foot">Gerado por <code>python tools/qg/build.py</code>, que varre <code>squads/</code>,
    <code>.claude/clones/</code> e o <code>git log</code>. Nenhum número foi digitado à mão.
    Estado que não dá para derivar vive em <code>docs/qg/estado.yaml</code>.</p>
</div>

<script>
const D = __DATA__;
(function(){
  const cv=document.getElementById('cv'),ctx=cv.getContext('2d'),vp=document.getElementById('vp'),
        tip=document.getElementById('tip'),det=document.getElementById('det');
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W=0,H=0,t=0,focus=null,hover=null,sweep=0;
  const N=[],L=[];
  const C=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const AG={}; D.squads.forEach(s=>s.agents.forEach(a=>AG[a.id]=Object.assign({sq:s.id},a)));

  document.getElementById('stamp').innerHTML=D.rev+' · varredura <b>'+D.stamp+'</b>';
  document.getElementById('ro').innerHTML=[['Squads',D.totals.sq,'--ink'],['Agentes',D.totals.ag,'--ink'],
    ['Clones',D.totals.cl,'--ink'],['Ligações',D.totals.lk,'--cyan'],
    ['Órfãos',D.totals.orf,D.totals.orf?'--crit':'--ok']]
    .map(([k,v,c])=>`<div><span class="k">${k}</span><span class="v" style="color:var(${c})">${v}</span></div>`).join('');
  document.getElementById('att').innerHTML=D.att.map(([n,t_,d,c])=>
    `<li class="${c}"><span class="n">${n}</span><span><span class="t">${t_}</span><br><span class="d">${d}</span></span></li>`).join('');
  document.getElementById('act').innerHTML=D.activity.map(a=>
    `<li><span class="s">${a.sha}</span><span>${a.subject.slice(0,58)}</span></li>`).join('');

  function build(){
    N.length=0;L.length=0;
    const cx=W/2,cy=H/2,R=Math.min(W,H)*.30,RC=Math.min(W,H)*.445;
    const hub=D.squads.find(s=>s.id==='c-level')||D.squads[0];
    const ops=D.squads.filter(s=>s!==hub);
    const hn={k:'hub',id:hub.id,lb:hub.id,x:cx,y:cy,r:8,sq:hub.id,ct:hub.agents.length,icon:hub.icon};
    N.push(hn);
    hub.agents.forEach((a,i)=>N.push({k:'ag',...a,sq:hub.id,lb:a.p,ox:cx,oy:cy,rad:44,
      ang:i/hub.agents.length*6.283-1.57,ph:i*.7,r:3.9}));
    ops.forEach((s,i)=>{
      const ang=-1.57+i/ops.length*6.283+.34,hx=cx+Math.cos(ang)*R,hy=cy+Math.sin(ang)*R;
      const sn={k:'sq',id:s.id,lb:s.id,x:hx,y:hy,r:5+s.agents.length*.48,sq:s.id,ct:s.agents.length,icon:s.icon};
      N.push(sn);L.push({a:hn,b:sn,t:'o'});
      const rad=20+s.agents.length*2.7;
      s.agents.forEach((a,j)=>N.push({k:'ag',...a,sq:s.id,lb:a.p,ox:hx,oy:hy,rad,
        ang:j/s.agents.length*6.283+i,ph:j*.55,r:3.3}));
    });
    D.clones.forEach((c,i)=>{
      const ang=-1.57+i/D.clones.length*6.283+.16;
      N.push({k:'cl',id:c.id,lb:c.id,feeds:c.feeds,prim:c.prim,docs:c.docs,
        x:cx+Math.cos(ang)*RC,y:cy+Math.sin(ang)*RC,r:4.2,sq:null});
    });
    D.squads.forEach(s=>s.agents.forEach(a=>{
      const an=N.find(n=>n.k==='ag'&&n.id===a.id);if(!an)return;
      (a.cf||[]).forEach(c=>{const cn=N.find(n=>n.k==='cl'&&n.id===c);if(cn)L.push({a:cn,b:an,t:'k'})});
      (a.cp||[]).forEach(c=>{const cn=N.find(n=>n.k==='cl'&&n.id===c);if(cn)L.push({a:cn,b:an,t:'p'})});
    }));
  }
  function resize(){const d=Math.min(devicePixelRatio||1,2);W=vp.clientWidth;H=vp.clientHeight;
    cv.width=W*d;cv.height=H*d;ctx.setTransform(d,0,0,d,0,0);build();}
  const P=n=>n.x!==undefined?n:(()=>{const a=n.ang+(reduce?0:t*55e-6+Math.sin(t*35e-5+n.ph)*.14);
    return{x:n.ox+Math.cos(a)*n.rad,y:n.oy+Math.sin(a)*n.rad}})();
  const dim=n=>!focus?1:(n.k==='cl'?(n.feeds.some(f=>AG[f]&&AG[f].sq===focus)?1:.1):(n.sq===focus?1:.1));
  function lit(p){if(reduce)return 1;let a=Math.atan2(p.y-H/2,p.x-W/2)-sweep;
    a=((a%6.283)+6.283)%6.283;return a<1.1?1-a/1.1:0}
  const stC=s=>s==='ok'?C('--ok'):s==='warn'?C('--warn'):C('--ink4');

  function draw(){
    const g=C('--gold'),cyn=C('--cyan'),wr=C('--warn'),ed=C('--edge'),ink=C('--ink'),i3=C('--ink3');
    ctx.clearRect(0,0,W,H);
    const cx=W/2,cyy=H/2,R=Math.min(W,H)*.30,RC=Math.min(W,H)*.445;
    ctx.strokeStyle=ed;ctx.lineWidth=1;ctx.globalAlpha=.4;
    [R,RC].forEach(r=>{ctx.beginPath();ctx.arc(cx,cyy,r,0,6.283);ctx.stroke()});
    ctx.globalAlpha=.15;
    for(let i=0;i<24;i++){const a=i/24*6.283;ctx.beginPath();
      ctx.moveTo(cx+Math.cos(a)*(R-13),cyy+Math.sin(a)*(R-13));
      ctx.lineTo(cx+Math.cos(a)*(R-6),cyy+Math.sin(a)*(R-6));ctx.stroke()}
    ctx.globalAlpha=1;
    if(!reduce){
      if(ctx.createConicGradient){const gr=ctx.createConicGradient(sweep,cx,cyy);
        gr.addColorStop(0,'rgba(90,214,218,.12)');gr.addColorStop(.14,'rgba(90,214,218,0)');
        gr.addColorStop(1,'rgba(90,214,218,0)');ctx.fillStyle=gr;
        ctx.beginPath();ctx.arc(cx,cyy,RC+20,0,6.283);ctx.fill()}
      ctx.strokeStyle=cyn;ctx.globalAlpha=.28;ctx.beginPath();ctx.moveTo(cx,cyy);
      ctx.lineTo(cx+Math.cos(sweep)*(RC+20),cyy+Math.sin(sweep)*(RC+20));ctx.stroke();ctx.globalAlpha=1;
    }
    L.forEach(l=>{
      const A=P(l.a),B=P(l.b),al=Math.min(dim(l.a),dim(l.b));
      const col=l.t==='o'?g:l.t==='p'?wr:cyn,kn=l.t!=='o';
      ctx.strokeStyle=col;ctx.globalAlpha=(kn?.14:.26)*al;ctx.lineWidth=kn?1:1.25;
      if(l.t==='p')ctx.setLineDash([3,3]);
      ctx.beginPath();const mx=(A.x+B.x)/2,my=(A.y+B.y)/2,b=kn?.13:0;
      ctx.moveTo(A.x,A.y);ctx.quadraticCurveTo(mx+(B.y-A.y)*b,my-(B.x-A.x)*b,B.x,B.y);ctx.stroke();
      ctx.setLineDash([]);
      if(!reduce&&al>.5&&l.t!=='p'){const p=(t*(kn?16e-5:22e-5)+(l.a.x+l.b.y)*.004)%1;
        ctx.globalAlpha=(1-Math.abs(p-.5)*2)*.9*al;ctx.fillStyle=col;
        ctx.beginPath();ctx.arc(A.x+(B.x-A.x)*p,A.y+(B.y-A.y)*p,kn?1.4:1.8,0,6.283);ctx.fill()}
    });
    ctx.globalAlpha=1;ctx.textAlign='center';
    N.forEach(n=>{
      const p=P(n),al=dim(n),hv=hover===n,li=lit(p);ctx.globalAlpha=al;
      if(n.k==='hub'||n.k==='sq'){
        const pl=reduce?0:Math.sin(t*16e-4+n.x)*.5+.5;
        ctx.strokeStyle=g;ctx.globalAlpha=al*(.16+pl*.2);
        ctx.beginPath();ctx.arc(p.x,p.y,n.r+5+pl*3,0,6.283);ctx.stroke();
        ctx.globalAlpha=al;ctx.fillStyle=g;ctx.shadowColor=g;ctx.shadowBlur=hv?14:7;
        ctx.beginPath();ctx.arc(p.x,p.y,n.r,0,6.283);ctx.fill();ctx.shadowBlur=0;
        ctx.fillStyle=ink;ctx.font=`600 ${n.k==='hub'?11:10}px ${C('--mono')}`;
        ctx.fillText(n.lb,p.x,p.y+n.r+13);
        ctx.fillStyle=i3;ctx.font=`8.5px ${C('--mono')}`;
        ctx.fillText(n.ct+' agentes',p.x,p.y+n.r+23);
      }else if(n.k==='cl'){
        ctx.strokeStyle=cyn;ctx.lineWidth=n.prim?1.8:1.1;ctx.setLineDash(n.prim?[]:[2.5,2.5]);
        ctx.beginPath();ctx.arc(p.x,p.y,n.r,0,6.283);ctx.stroke();ctx.setLineDash([]);
        ctx.globalAlpha=al*.2;ctx.fillStyle=cyn;ctx.fill();ctx.globalAlpha=al;
        ctx.fillStyle=hv?cyn:i3;ctx.font=`9.5px ${C('--mono')}`;
        ctx.fillText(n.lb,p.x,p.y-n.r-7);
      }else{
        const col=stC(n.st);ctx.fillStyle=col;ctx.shadowColor=col;ctx.shadowBlur=n.st?9:0;
        ctx.beginPath();ctx.arc(p.x,p.y,hv?n.r+1.6:n.r,0,6.283);ctx.fill();ctx.shadowBlur=0;
        const show=Math.max(li,hv?1:0,focus===n.sq?1:0);
        if(show>.03){ctx.globalAlpha=al*show;ctx.fillStyle=hv?g:C('--ink2');
          ctx.font=`9.5px ${C('--mono')}`;ctx.fillText(n.lb,p.x,p.y-n.r-6)}
      }
      ctx.globalAlpha=1;
    });
  }
  function loop(ts){t=ts;if(!reduce)sweep=(ts*22e-5)%6.283;
    document.getElementById('scan').textContent=String(Math.round(sweep*57.3)).padStart(3,'0')+'°';
    draw();requestAnimationFrame(loop)}

  vp.addEventListener('mousemove',e=>{
    const r=vp.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
    let b=null,bd=15;N.forEach(n=>{const p=P(n),d=Math.hypot(p.x-mx,p.y-my);if(d<bd){bd=d;b=n}});
    hover=b;
    if(b){const p=P(b);tip.style.left=p.x+'px';tip.style.top=p.y+'px';tip.style.opacity=1;
      tip.innerHTML=b.k==='cl'?`<b>${b.lb}</b> <span>${b.prim?'fonte primária · '+b.docs+' docs':'consultivo'} · alimenta ${b.feeds.length}</span>`
        :b.k==='ag'?`<b>${b.lb}</b> <span>${b.id} · ${b.sq}</span>`
        :`<b>${b.lb}</b> <span>${b.ct} agentes</span>`;
      detail(b)}else tip.style.opacity=0});
  vp.addEventListener('mouseleave',()=>{hover=null;tip.style.opacity=0});

  function detail(n){
    if(n.k==='cl'){
      det.innerHTML=`<span class="bg" style="color:var(--cyan);border-color:var(--cyan)">${n.prim?'FONTE PRIMÁRIA · '+n.docs+' DOCS':'CONSULTIVO'}</span>
        <p class="nm">${n.lb}</p><p class="rl">clone · fonte de conhecimento</p>
        <ul>${n.feeds.map(f=>`<li><em>→</em>${f}</li>`).join('')||'<li class="pr">órfão</li>'}</ul>`;
    }else if(n.k==='ag'){
      const cf=(n.cf||[]).map(c=>`<li><em>←</em>${c}</li>`).join('');
      const cp=(n.cp||[]).map(c=>`<li><span class="pr">←</span>${c} <span class="pr">só em prosa</span></li>`).join('');
      const dd=(n.d||[]).map(c=>`<li><em>·</em>${c}</li>`).join('');
      det.innerHTML=`${n.lead?'<span class="bg" style="color:var(--gold);border-color:var(--gold)">LEAD</span>':''}
        <p class="nm">${n.lb}</p><p class="rl">${n.id} · squad ${n.sq}</p>
        ${n.note?`<p class="rl" style="color:var(--warn)">${n.note}</p>`:''}
        ${cf+cp+dd?`<ul>${cf}${cp}${dd}</ul>`:'<p class="hint">Sem fonte ligada — opera só com a própria persona.</p>'}`;
    }else{
      const s=D.squads.find(x=>x.id===n.id);
      det.innerHTML=`<p class="nm">${s.icon} ${s.id}</p><p class="rl">${s.agents.length} agentes</p>
        <ul>${s.agents.map(a=>`<li><em>·</em>${a.p} <span style="color:var(--ink3)">${a.id}</span></li>`).join('')}</ul>`;
    }
  }

  const ul=document.getElementById('sq'),mx=Math.max(...D.squads.map(s=>s.agents.length));
  D.squads.forEach(s=>{const li=document.createElement('li');
    li.innerHTML=`<button aria-pressed="false" data-id="${s.id}">
      <span class="pip" style="background:${s.id==='c-level'?'var(--gold)':'var(--ink4)'}"></span>
      <span>${s.id}<i class="tk"><i style="width:${s.agents.length/mx*100}%"></i></i></span>
      <span class="ct">${s.agents.length}</span></button>`;ul.appendChild(li)});
  ul.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
    focus=focus===b.dataset.id?null:b.dataset.id;
    ul.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.id===focus)));
    if(focus){const n=N.find(x=>(x.k==='sq'||x.k==='hub')&&x.id===focus);n&&detail(n)}
    else det.innerHTML='<p class="hint">Aponte um nó, ou selecione um squad para isolar a cadeia.</p>'});

  addEventListener('resize',resize);resize();requestAnimationFrame(loop);
})();
</script>
"""


if __name__ == "__main__":
    state = build_state()
    data = payload(state)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        TPL.replace("__DATA__", json.dumps(data, ensure_ascii=False)),
        encoding="utf-8")
    (OUT.parent / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    t = state["totals"]
    print(f"QG gerado -> {OUT.relative_to(ROOT)}")
    print(f"  {t['agents']} agentes · {t['links']} ligações · "
          f"{t['prose_only_links']} só em prosa · {len(t['orphan_clones'])} órfãos")
