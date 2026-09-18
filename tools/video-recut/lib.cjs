// video-recut — motor de composição HyperFrames para Reels 9:16 (talking-head + cards + inserts)
// Validado no convite Desafio Ótica +100K (2026-09-15). Ver README.md.
const fs = require("fs");
const path = require("path");

function criar({ dur, fps = 30 }) {
  const DUR = dur;
  const q = (t) => (Math.round(t * fps) / fps).toFixed(4);
  let js = "";
  let layers = "";
  const add = (s) => (js += "  " + s + "\n");

  // ── helpers de motion ──
  const M = (txt, cls = "") => `<span class="m"><span class="mi ${cls}">${txt}</span></span>`;
  const hide = (sel, vars, t) => add(`tl.set('${sel}', ${vars}, ${q(t)});`);
  const maskIn = (sel, t, stagger = 0, setAt = null) => {
    if (setAt !== null) add(`tl.set('${sel}', { yPercent: 115 }, ${q(setAt)});`);
    add(`tl.fromTo('${sel}', { yPercent: 115 }, { yPercent: 0, duration: 0.6, ease: 'expo.out', stagger: ${stagger}, immediateRender: false }, ${q(t)});`);
  };
  const shimmer = (sel, t) =>
    add(`tl.fromTo('${sel}', { backgroundPosition: '220% 0%' }, { backgroundPosition: '-60% 0%', duration: 1.2, ease: 'power2.inOut', immediateRender: false }, ${q(t)});`);
  const sheen = (sel, t) =>
    add(`tl.fromTo('${sel}', { xPercent: -160 }, { xPercent: 360, duration: 0.9, ease: 'power2.inOut', immediateRender: false }, ${q(t)});`);

  // ── câmera: [início, fim, escalaInicial, escalaFinal] — escala diferente no início = corte com zoom ──
  function camera(segs) {
    segs.forEach(([a, b, s0, s1]) => {
      add(`tl.set('#video-zoom', { scale: ${s0} }, ${q(a)});`);
      if (s1 !== s0) add(`tl.to('#video-zoom', { scale: ${s1}, duration: ${(b - a - 0.034).toFixed(3)}, ease: 'none' }, ${q(a)});`);
    });
  }

  // ── card no topo (y 130px). inner = HTML; extra(start) = animações internas ──
  function card(id, start, end, inner, extra = () => {}) {
    layers += `    <div class="card-host clip" id="host-${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="2">
      <div class="scrim" id="${id}-scrim"></div><div class="panel" id="${id}-panel"><i class="kline" id="${id}-kline"></i>${inner}</div>
    </div>\n`;
    const panel = `#${id}-panel`;
    add(`// ${id}`);
    // tipografia sobre degradê (sem caixa): entra com desfoque, fio dourado desenha, deriva leve na tela
    add(`tl.fromTo('#${id}-scrim', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' }, ${q(start)});`);
    add(`tl.fromTo('${panel}', { opacity: 0, y: 26, filter: 'blur(14px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.6, ease: 'power3.out' }, ${q(start)});`);
    add(`tl.fromTo('#${id}-kline', { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: 'expo.out' }, ${q(start + 0.05)});`);
    const vive = end - start - 1.2;
    if (vive > 1.2) add(`tl.to('${panel}', { y: -6, duration: ${vive.toFixed(2)}, ease: 'sine.inOut' }, ${q(start + 0.7)});`);
    maskIn(`${panel} .kicker .mi`, start + 0.12, 0, start);
    extra(start);
    if (end < DUR) {
      add(`tl.to('${panel}', { opacity: 0, y: -24, filter: 'blur(12px)', duration: 0.35, ease: 'power2.in' }, ${q(end - 0.35)});`);
      add(`tl.to('#${id}-scrim', { opacity: 0, duration: 0.35, ease: 'power2.in' }, ${q(end - 0.35)});`);
    }
  }

  // card padrão kicker + título (goldText opcional com brilho em goldAt)
  function cardTitulo(id, start, end, { kicker, titulo, gold = "", tituloAt, goldAt }) {
    card(id, start, end,
      `<div class="kicker">${M(kicker)}</div><div class="title">${M(titulo)}${gold ? " " + M(gold, "gold") : ""}</div>`,
      (s) => { maskIn(`#${id}-panel .title .mi`, tituloAt ?? s + 0.2, 0.1, s); if (gold) shimmer(`#${id}-panel .gold`, goldAt ?? (tituloAt ?? s + 0.2) + 0.8); });
  }

  // card lista: itens trocam no tempo em que são falados, com barra de progresso
  function cardLista(id, start, end, { kicker, itens, extra }) {
    const n = itens.length;
    const all = extra ? [...itens, extra] : itens;
    card(id, start, end,
      `<div class="row-top"><div class="kicker">${M(kicker)}</div><div class="count" id="${id}-count">01/${String(n).padStart(2, "0")}</div></div>
      <div class="slot">${all.map(([t], i) => `<div class="item${i === n ? " gold" : ""}" id="${id}-i${i}">${t}</div>`).join("")}</div>
      <div class="bar">${itens.map((_, i) => `<i><b id="${id}-b${i}"></b></i>`).join("")}</div>`,
      () => {
        hide(`#${id}-panel .item`, "{ yPercent: 120 }", start);
        all.forEach(([, ti], i) => {
          if (i > 0) add(`tl.to('#${id}-i${i - 1}', { yPercent: -120, duration: 0.26, ease: 'power3.in' }, ${q(ti - 0.12)});`);
          add(`tl.fromTo('#${id}-i${i}', { yPercent: 120 }, { yPercent: 0, duration: 0.5, ease: 'expo.out', immediateRender: false }, ${q(ti)});`);
          if (i < n) {
            add(`tl.fromTo('#${id}-b${i}', { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: 'expo.out', immediateRender: false }, ${q(ti)});`);
            add(`tl.set('#${id}-count', { textContent: '${String(i + 1).padStart(2, "0")}/${String(n).padStart(2, "0")}' }, ${q(ti)});`);
          } else shimmer(`#${id}-i${i}`, ti + 0.2);
        });
      });
  }

  // card CTA verde pulsando até o fim
  function cardCTA(id, start, { kicker, texto, popAt }) {
    card(id, start, DUR,
      `<div class="kicker center">${M(kicker)}</div>
      <div class="cta-wrap"><div class="cta" id="${id}-cta"><span class="cta-sheen" id="${id}-cta-sheen"></span>${texto} <span class="arrow" id="${id}-arrow"></span></div></div>`,
      () => {
        const p = popAt ?? start + 0.5;
        const rest = DUR - p - 1;
        hide(`#${id}-cta`, "{ scale: 0.4, opacity: 0 }", start);
        add(`tl.fromTo('#${id}-cta', { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(2.2)', immediateRender: false }, ${q(p)});`);
        add(`tl.to('#${id}-cta', { scale: 1.045, duration: 0.5, ease: 'sine.inOut', yoyo: true, repeat: ${Math.max(1, Math.floor(rest / 0.5) - 1)} }, ${q(p + 0.85)});`);
        add(`tl.fromTo('#${id}-arrow', { y: -4 }, { y: 6, duration: 0.35, ease: 'sine.inOut', yoyo: true, repeat: ${Math.max(1, Math.floor(rest / 0.35) - 1)}, immediateRender: false }, ${q(p + 0.55)});`);
        add(`tl.fromTo('#${id}-cta-sheen', { xPercent: -200 }, { xPercent: 500, duration: 0.8, ease: 'power2.inOut', repeat: ${Math.max(0, Math.floor(rest / 1.65) - 1)}, repeatDelay: 0.85, immediateRender: false }, ${q(p + 1.1)});`);
      });
  }

  // ── INSERT: pessoa num círculo + 3 blocos (datas, números curtos) ──
  // faceX/faceY = centro do rosto no quadro 1080×1920
  function insertCirculo({ start, end, kicker, blocos, rodape, rodapeAt, selo, seloAt, faceX = 540, faceY = 595 }) {
    const id = "ins-circ";
    const ring = (sz) => `left:${faceX - sz / 2}px;top:${faceY - sz / 2}px;width:${sz}px;height:${sz}px`;
    layers += `    <div class="insert clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="4">
      <div class="ins-bg" id="${id}-bg"><div class="grid" id="${id}-grid"></div><div class="glow"></div></div>
      <div class="ring" id="${id}-ring" style="${ring(536)}"></div><div class="ring dashed" id="${id}-ring2" style="${ring(592)}"></div>
      <div class="ins-kicker">${M(kicker)}</div>
      ${selo ? `<div class="live big" id="${id}-live" style="top:${faceY + 263}px"><span class="dot" id="${id}-dot"></span>${selo}</div>` : ""}
      <div class="dates">${blocos.map(([d], i) => `<span class="d" id="${id}-d${i}">${d}</span>`).join("")}</div>
      ${rodape ? `<div class="ins-mes">${M(rodape)}</div>` : ""}
    </div>\n`;
    const clipAt = `at ${faceX}px ${faceY}px`;
    add(`// insert círculo`);
    circuloAbre(id, start, end, { faceX, faceY });
    maskIn(`#${id} .ins-kicker .mi`, start + 0.35, 0, start);
    hide(`#${id} .d`, "{ rotationX: -95, opacity: 0 }", start);
    hide(`#${id}-ring, #${id}-ring2`, "{ scale: 0.7, opacity: 0 }", start);
    add(`tl.fromTo(['#${id}-ring', '#${id}-ring2'], { scale: 0.7, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: 'expo.out', stagger: 0.08, immediateRender: false }, ${q(start + 0.45)});`);
    add(`tl.fromTo('#${id}-ring2', { rotation: 0 }, { rotation: 120, duration: ${(end - start - 0.5).toFixed(2)}, ease: 'none', immediateRender: false }, ${q(start + 0.5)});`);
    blocos.forEach(([, t], i) =>
      add(`tl.fromTo('#${id}-d${i}', { rotationX: -95, opacity: 0, y: 40 }, { rotationX: 0, opacity: 1, y: 0, duration: 0.7, ease: 'expo.out', transformPerspective: 900, immediateRender: false }, ${q(t - 0.05)});`));
    if (rodape) maskIn(`#${id} .ins-mes .mi`, rodapeAt, 0, start);
    if (selo) {
      hide(`#${id}-live`, "{ scale: 0, opacity: 0 }", start);
      add(`tl.fromTo('#${id}-live', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(2.6)', immediateRender: false }, ${q(seloAt)});`);
      add(`tl.fromTo('#${id}-dot', { opacity: 1 }, { opacity: 0.2, duration: 0.25, ease: 'sine.inOut', yoyo: true, repeat: 1, immediateRender: false }, ${q(seloAt + 0.2)});`);
    }
  }

  // ── INSERT: gráfico de crescimento com selo ──
  function insertCrescimento({ start, end, kicker, selo, seloAt }) {
    const id = "ins-grow";
    const bars = [150, 250, 370, 520, 700];
    const bx = (i) => 150 + i * 170;
    const base = 1110;
    const pts = bars.map((h, i) => [bx(i) + 55, base - h - 40]);
    let len = 0;
    for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    layers += `    <div class="insert clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="5">
      <div class="ins-bg" id="${id}-bg"><div class="grid" id="${id}-grid"></div><div class="glow"></div>
        <div class="ins-kicker">${M(kicker)}</div>
        ${bars.map((h, i) => `<div class="gbar" style="left:${bx(i)}px;height:${h}px;top:${base - h}px"></div>`).join("")}
        <div class="baseline" id="${id}-base"></div>
        <svg class="gline" width="1080" height="1920" viewBox="0 0 1080 1920"><polyline id="${id}-line" points="${pts.map((p) => p.join(",")).join(" ")}" fill="none" stroke="#F1D594" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="${len.toFixed(1)}" stroke-dashoffset="${len.toFixed(1)}"/></svg>
        ${pts.map((p) => `<div class="gdot" style="left:${p[0] - 14}px;top:${p[1] - 14}px"></div>`).join("")}
        ${selo ? `<div class="badge" id="${id}-badge"><span class="gold-fill" id="${id}-badge-t">${selo}</span></div>` : ""}
      </div>
    </div>\n`;
    add(`// insert crescimento`);
    maskIn(`#${id} .ins-kicker .mi`, start + 0.3, 0, start);
    hide(`#${id} .gbar`, "{ scaleY: 0 }", start); hide(`#${id}-base`, "{ scaleX: 0 }", start); hide(`#${id} .gdot`, "{ scale: 0 }", start);
    add(`tl.fromTo('#${id}-bg', { clipPath: 'circle(0% at 50% 31%)' }, { clipPath: 'circle(150% at 50% 31%)', duration: 0.65, ease: 'power4.inOut' }, ${q(start)});`);
    add(`tl.fromTo('#${id}-grid', { backgroundPosition: '0px 0px' }, { backgroundPosition: '0px -90px', duration: ${(end - start).toFixed(2)}, ease: 'none' }, ${q(start)});`);
    add(`tl.fromTo('#${id}-base', { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: 'expo.out', immediateRender: false }, ${q(start + 0.3)});`);
    add(`tl.fromTo('#${id} .gbar', { scaleY: 0 }, { scaleY: 1, duration: 0.7, ease: 'expo.out', stagger: 0.09, immediateRender: false }, ${q(start + 0.4)});`);
    add(`tl.to('#${id}-line', { strokeDashoffset: 0, duration: 0.8, ease: 'power2.inOut' }, ${q(start + 0.75)});`);
    add(`tl.fromTo('#${id} .gdot', { scale: 0 }, { scale: 1, duration: 0.35, ease: 'back.out(3)', stagger: 0.16, immediateRender: false }, ${q(start + 0.8)});`);
    if (selo) {
      hide(`#${id}-badge`, "{ scale: 0.2, opacity: 0 }", start);
      add(`tl.fromTo('#${id}-badge', { scale: 0.2, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -4, duration: 0.6, ease: 'back.out(2.2)', immediateRender: false }, ${q(seloAt)});`);
      shimmer(`#${id}-badge-t`, seloAt + 0.45);
    }
    add(`tl.to('#${id} .gbar', { scaleY: 1.06, duration: 1.2, ease: 'sine.inOut', stagger: 0.05 }, ${q(start + 1.3)});`);
    add(`tl.to('#${id}-bg', { clipPath: 'inset(0% 0% 100% 0%)', duration: 0.55, ease: 'power4.inOut' }, ${q(end - 0.55)});`);
  }

  // ── Legenda palavra a palavra: groups = [[["palavra", início], ...], ...] ──
  function legenda(groups) {
    groups.forEach((g, gi) => {
      const start = Math.max(0, g[0][1] - 0.06);
      const nextStart = gi + 1 < groups.length ? groups[gi + 1][0][1] - 0.06 : DUR;
      const lastWord = g[g.length - 1][1];
      let end = Math.min(nextStart, Math.max(lastWord + 0.7, start + 0.6));
      if (gi === groups.length - 1) end = DUR;
      const id = `cap-${String(gi).padStart(2, "0")}`;
      layers += `    <div class="cap clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="3"><div class="cap-line">${g
        .map((w, wi) => `<span class="w" id="${id}-w${wi}">${w[0]}</span>`).join(" ")}</div></div>\n`;
      add(`tl.fromTo('#${id} .cap-line', { scale: 0.8, opacity: 0, y: 14 }, { scale: 1, opacity: 1, y: 0, duration: 0.22, ease: 'back.out(2.4)', immediateRender: false }, ${q(start)});`);
      g.forEach((w, wi) => {
        const off = wi + 1 < g.length ? g[wi + 1][1] : end;
        add(`tl.set('#${id}-w${wi}', { color: '#F1D594' }, ${q(w[1])}); tl.fromTo('#${id}-w${wi}', { scale: 1.12 }, { scale: 1, duration: 0.25, ease: 'power2.out', immediateRender: false }, ${q(w[1])}); tl.set('#${id}-w${wi}', { color: '#FFFFFF' }, ${q(off)});`);
      });
    });
  }

  // ── Legenda dinâmica: cada palavra entra no tempo falado, com variação de entrada por grupo ──
  // groups = [[["palavra", início], ...], ...] · destaques = palavras que ganham dourado fixo + sublinhado
  function legendaDinamica(groups, { destaques = [] } = {}) {
    const norm = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9-]/g, "").toUpperCase();
    const chave = new Set(destaques.map(norm));
    // 4 entradas diferentes, alternadas por grupo — cada palavra aparece quando é falada
    const entradas = [
      { de: "{ scale: 0.45, opacity: 0, y: 30 }", para: "{ scale: 1, opacity: 1, y: 0, duration: 0.3, ease: 'back.out(3.2)' }" },
      { de: "{ opacity: 0, y: 64, rotationX: -80, transformPerspective: 800 }", para: "{ opacity: 1, y: 0, rotationX: 0, duration: 0.34, ease: 'expo.out' }" },
      { de: "{ opacity: 0, x: -52, skewX: 16 }", para: "{ opacity: 1, x: 0, skewX: 0, duration: 0.3, ease: 'power3.out' }" },
      { de: "{ scale: 1.75, opacity: 0 }", para: "{ scale: 1, opacity: 1, duration: 0.26, ease: 'power3.out' }" },
    ];
    groups.forEach((g, gi) => {
      const start = Math.max(0, g[0][1] - 0.18);
      const nextStart = gi + 1 < groups.length ? groups[gi + 1][0][1] - 0.18 : DUR;
      const lastWord = g[g.length - 1][1];
      let end = Math.min(nextStart, Math.max(lastWord + 0.85, start + 0.7));
      if (gi === groups.length - 1) end = DUR;
      const id = `cap-${String(gi).padStart(2, "0")}`;
      const e = entradas[gi % entradas.length];
      const tilt = gi % 3 === 1 ? -1.4 : gi % 3 === 2 ? 1.4 : 0;
      layers += `    <div class="cap clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="3"><div class="cap-line" id="${id}-line">${g
        .map((w, wi) => {
          const key = chave.has(norm(w[0]));
          return `<span class="w${key ? " key" : ""}" id="${id}-w${wi}">${w[0]}${key ? `<i class="ul" id="${id}-u${wi}"></i>` : ""}</span>`;
        })
        .join(" ")}</div></div>\n`;
      add(`// ${id}`);
      add(`tl.set('#${id}-line', { rotation: ${tilt} }, ${q(start)});`);
      hide(`#${id} .w`, "{ opacity: 0 }", start);
      hide(`#${id} .ul`, "{ scaleX: 0 }", start);
      g.forEach((w, wi) => {
        const t = w[1];
        const off = wi + 1 < g.length ? g[wi + 1][1] : end;
        const key = chave.has(norm(w[0]));
        add(`tl.fromTo('#${id}-w${wi}', ${e.de}, { ...${e.para}, immediateRender: false }, ${q(t)});`);
        if (key) {
          // palavra-chave: pulo maior, tremida curta e sublinhado dourado que desenha
          add(`tl.fromTo('#${id}-w${wi}', { scale: 1.34 }, { scale: 1, duration: 0.42, ease: 'elastic.out(1, 0.55)', immediateRender: false }, ${q(t + 0.02)});`);
          add(`tl.fromTo('#${id}-w${wi}', { rotation: -3.5 }, { rotation: 0, duration: 0.34, ease: 'power2.out', immediateRender: false }, ${q(t + 0.02)});`);
          add(`tl.fromTo('#${id}-u${wi}', { scaleX: 0 }, { scaleX: 1, duration: 0.34, ease: 'expo.out', immediateRender: false }, ${q(t + 0.1)});`);
        } else {
          // palavra comum: fica dourada enquanto é falada e volta ao branco
          add(`tl.set('#${id}-w${wi}', { color: '#F1D594' }, ${q(t)});`);
          add(`tl.fromTo('#${id}-w${wi}', { scale: 1.16 }, { scale: 1, duration: 0.26, ease: 'power2.out', immediateRender: false }, ${q(t)});`);
          add(`tl.set('#${id}-w${wi}', { color: '#FFFFFF' }, ${q(off)});`);
        }
      });
      if (gi < groups.length - 1) {
        add(`tl.to('#${id}-line', { opacity: 0, y: -22, scale: 0.94, duration: 0.16, ease: 'power2.in' }, ${q(end - 0.16)});`);
      }
    });
  }

  // ── Flash curto no corte (impacto sem SFX) ──
  function flash(times, { cor = "rgba(255,243,209,0.5)", dur = 0.22 } = {}) {
    times.forEach((t, i) => {
      const id = `fl-${i}`;
      layers += `    <div class="flash clip" id="${id}" data-start="${q(Math.max(0, t - 0.06))}" data-duration="${q(dur + 0.5)}" data-track-index="6"></div>\n`;
      add(`tl.fromTo('#${id}', { opacity: 0, xPercent: -18 }, { opacity: 0.9, xPercent: 0, duration: 0.14, ease: 'power2.out', immediateRender: false }, ${q(t - 0.06)});`);
      add(`tl.to('#${id}', { opacity: 0, xPercent: 16, duration: ${(dur + 0.2).toFixed(2)}, ease: 'power2.in' }, ${q(t + 0.08)});`);
    });
  }

  // ── Tremida de câmera (impacto). alvo padrão = vídeo; em insert passar o seletor do insert ──
  function shake(times, { forca = 16, alvo = "#video-zoom" } = {}) {
    times.forEach((t) => {
      const f = forca;
      const kf = [[-f, f * 0.6, -0.9], [f * 0.8, -f * 0.5, 0.7], [-f * 0.5, f * 0.35, -0.4], [f * 0.25, -f * 0.15, 0.2], [0, 0, 0]]
        .map(([x, y, r]) => `{ x: ${x.toFixed(1)}, y: ${y.toFixed(1)}, rotation: ${r}, duration: 0.06 }`).join(", ");
      add(`tl.to('${alvo}', { keyframes: [${kf}], ease: 'none' }, ${q(t)});`);
    });
  }

  // ── Fundo desfocado (o próprio vídeo, pré-renderizado) entra atrás dos inserts ──
  let usaDesfoque = false;
  function desfoque(ini, fim) {
    if (!usaDesfoque) { usaDesfoque = true; add(`tl.set('#blur-wrap', { opacity: 0 }, 0);`); }
    add(`tl.to('#blur-wrap', { opacity: 1, duration: 0.6, ease: 'power2.out' }, ${q(ini)});`);
    add(`tl.to('#blur-wrap', { opacity: 0, duration: 0.6, ease: 'power2.in' }, ${q(fim - 0.6)});`);
  }

  // ── Corte com desfoque de movimento: o quadro chega borrado e claro e assenta em 0,22 s ──
  function corteSuave(times) {
    add(`tl.set('#video-wrap', { filter: 'blur(0px) brightness(1)' }, 0);`);
    times.forEach((t) => add(`tl.fromTo('#video-wrap', { filter: 'blur(9px) brightness(1.12)' }, { filter: 'blur(0px) brightness(1)', duration: 0.22, ease: 'power2.out', immediateRender: false }, ${q(t)});`));
  }

  // ── Filtro no vídeo por um trecho (ex.: dessaturar no "cansativo") ──
  function filtro(ini, fim, { de = "grayscale(0) brightness(1) contrast(1)", para = "grayscale(0.9) brightness(0.72) contrast(1.12)" } = {}) {
    add(`tl.set('#video-zoom', { filter: '${de}' }, 0);`);
    add(`tl.to('#video-zoom', { filter: '${para}', duration: 0.3, ease: 'power2.out' }, ${q(ini)});`);
    add(`tl.to('#video-zoom', { filter: '${de}', duration: 0.25, ease: 'power2.in' }, ${q(fim - 0.25)});`);
  }

  // abre a tela navy e encolhe a pessoa num círculo no rosto (base dos inserts de círculo)
  function circuloAbre(id, start, end, { faceX, faceY, raio = 320, escala = 0.78 }) {
    const clipAt = `at ${faceX}px ${faceY}px`;
    add(`tl.set('#video-wrap', { zIndex: 3, transformOrigin: '${faceX}px ${faceY}px' }, ${q(start)});`);
    desfoque(start, end);
    add(`tl.fromTo('#${id}-bg', { opacity: 0 }, { opacity: 1, duration: 0.6, ease: 'power2.out' }, ${q(start)});`);
    add(`tl.fromTo('#video-wrap', { clipPath: 'circle(1400px ${clipAt})', scale: 1 }, { clipPath: 'circle(${raio}px ${clipAt})', scale: ${escala}, duration: 0.9, ease: 'power3.inOut' }, ${q(start)});`);
    add(`tl.to('#video-wrap', { clipPath: 'circle(1400px ${clipAt})', scale: 1, duration: 0.7, ease: 'power3.inOut' }, ${q(end - 0.7)});`);
    add(`tl.to('#${id} > *:not(.ins-bg)', { opacity: 0, y: -16, filter: 'blur(8px)', duration: 0.35, ease: 'power2.in' }, ${q(end - 0.7)});`);
    add(`tl.to('#${id}-bg', { opacity: 0, duration: 0.5, ease: 'power2.in' }, ${q(end - 0.55)});`);
    add(`tl.set('#video-wrap', { zIndex: 1 }, ${q(end)});`);
  }

  // ── INSERT: ciclo do mês — anel enche com contador DIA 1→N e volta a zero (vermelho + alarme) ──
  function insertCiclo({ start, end, kicker, ate = 30, zeroAt, rodape, faceX = 540, faceY = 560 }) {
    const id = "ins-ciclo";
    const R = 292, C = 2 * Math.PI * R;
    const ticks = Array.from({ length: ate }, (_, i) => {
      const a = (i / ate) * 2 * Math.PI - Math.PI / 2;
      const p = (r) => `${(faceX + r * Math.cos(a)).toFixed(1)},${(faceY + r * Math.sin(a)).toFixed(1)}`;
      return `<polyline points="${p(R + 22)} ${p(R + 38)}" stroke="rgba(241,213,148,0.45)" stroke-width="4" stroke-linecap="round"/>`;
    }).join("");
    layers += `    <div class="insert clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="4">
      <div class="ins-bg" id="${id}-bg"><div class="grid" id="${id}-grid"></div><div class="glow"></div><div class="alarm" id="${id}-alarm"></div></div>
      <svg class="ciclo-svg" id="${id}-svg" width="1080" height="1920" viewBox="0 0 1080 1920">${ticks}
        <circle cx="${faceX}" cy="${faceY}" r="${R}" fill="none" stroke="rgba(245,245,240,0.12)" stroke-width="10"/>
        <circle id="${id}-arc" cx="${faceX}" cy="${faceY}" r="${R}" fill="none" stroke="#DDB870" stroke-width="10" stroke-linecap="round" stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${C.toFixed(1)}" transform="rotate(-90 ${faceX} ${faceY})"/></svg>
      <div class="ins-kicker">${M(kicker)}</div>
      <div class="ciclo-num" id="${id}-num" style="top:${faceY + R + 52}px"><span class="lab" id="${id}-lab">DIA</span><span class="n" id="${id}-n">1</span></div>
      ${rodape ? `<div class="ins-mes red" style="top:${faceY + R + 225}px">${M(rodape)}</div>` : ""}
    </div>\n`;
    add(`// insert ciclo`);
    circuloAbre(id, start, end, { faceX, faceY });
    maskIn(`#${id} .ins-kicker .mi`, start + 0.35, 0, start);
    hide(`#${id}-num`, "{ opacity: 0, y: 40 }", start);
    hide(`#${id}-alarm`, "{ opacity: 0 }", start);
    add(`tl.fromTo('#${id}-num', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: 'expo.out', immediateRender: false }, ${q(start + 0.45)});`);
    const a0 = start + 0.6, a1 = zeroAt - 0.12;
    add(`tl.fromTo('#${id}-arc', { strokeDashoffset: ${C.toFixed(1)} }, { strokeDashoffset: ${(C * 0.015).toFixed(1)}, duration: ${(a1 - a0).toFixed(2)}, ease: 'power1.in', immediateRender: false }, ${q(a0)});`);
    for (let k = 1; k <= ate; k++) {
      const t = a0 + ((k - 1) / (ate - 1)) ** 0.8 * (a1 - a0);
      add(`tl.set('#${id}-n', { textContent: '${k}' }, ${q(t)});`);
    }
    // volta a zero
    add(`tl.set('#${id}-arc', { stroke: '#DDB870' }, ${q(start)}); tl.set('#${id}-arc', { stroke: '#FF3B3B' }, ${q(zeroAt - 0.06)});`);
    add(`tl.to('#${id}-arc', { strokeDashoffset: ${C.toFixed(1)}, duration: 0.32, ease: 'expo.out' }, ${q(zeroAt - 0.06)});`);
    add(`tl.set('#${id}-n', { color: '#FFFFFF' }, ${q(start)}); tl.set('#${id}-n', { textContent: '0', color: '#FF4B4B' }, ${q(zeroAt)});`);
    add(`tl.set('#${id}-lab', { textContent: 'DIA' }, ${q(start)}); tl.set('#${id}-lab', { textContent: 'DE VOLTA AO' }, ${q(zeroAt)});`);
    add(`tl.fromTo('#${id}-num', { scale: 1.9 }, { scale: 1, duration: 0.6, ease: 'elastic.out(1, 0.45)', immediateRender: false }, ${q(zeroAt)});`);
    add(`tl.fromTo('#${id}-alarm', { opacity: 0 }, { opacity: 0.6, duration: 0.1, ease: 'none', immediateRender: false }, ${q(zeroAt)}); tl.to('#${id}-alarm', { opacity: 0.22, duration: 0.5, ease: 'power2.out' }, ${q(zeroAt + 0.08)});`);
    shake([zeroAt], { forca: 12, alvo: `#${id}-svg` });
    if (rodape) maskIn(`#${id} .ins-mes .mi`, zeroAt + 0.08, 0, start);
  }

  // ── INSERT: etapas em fila (ex.: ATRAIR → DESEJO → VENDAS); pessoa em círculo menor no topo ──
  function insertEtapas({ start, end, kicker, etapas, faceX = 540, faceY = 560 }) {
    const id = "ins-etapas";
    layers += `    <div class="insert clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="4">
      <div class="ins-bg" id="${id}-bg"><div class="grid" id="${id}-grid"></div><div class="glow"></div></div>
      <div class="ring" id="${id}-ring" style="left:${faceX - 222}px;top:${faceY - 222}px;width:444px;height:444px"></div>
      <div class="ins-kicker">${M(kicker)}</div>
      <div class="etapas">${etapas.map(([t], i) => `${i ? `<div class="con"><b id="${id}-c${i}"></b></div>` : ""}<div class="et" id="${id}-e${i}"><i class="lit" id="${id}-l${i}"></i><span class="num">0${i + 1}</span><span class="tx" id="${id}-t${i}">${t}</span><i class="et-sheen" id="${id}-s${i}"></i></div>`).join("")}</div>
    </div>\n`;
    add(`// insert etapas`);
    circuloAbre(id, start, end, { faceX, faceY, raio: 300, escala: 0.66 });
    maskIn(`#${id} .ins-kicker .mi`, start + 0.35, 0, start);
    hide(`#${id}-ring`, "{ scale: 0.6, opacity: 0 }", start);
    hide(`#${id} .et`, "{ opacity: 0, y: 70, rotationY: -60 }", start);
    hide(`#${id} .lit`, "{ opacity: 0 }", start);
    hide(`#${id} .con b`, "{ scaleX: 0 }", start);
    hide(`#${id} .tx`, "{ color: 'rgba(245,245,240,0.5)' }", start);
    add(`tl.fromTo('#${id}-ring', { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: 'expo.out', immediateRender: false }, ${q(start + 0.45)});`);
    add(`tl.fromTo('#${id} .et', { opacity: 0, y: 70, rotationY: -60 }, { opacity: 1, y: 0, rotationY: 0, transformPerspective: 900, duration: 0.6, ease: 'expo.out', stagger: 0.1, immediateRender: false }, ${q(start + 0.55)});`);
    etapas.forEach(([, t], i) => {
      if (i) add(`tl.fromTo('#${id}-c${i}', { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: 'power2.inOut', immediateRender: false }, ${q(t - 0.3)});`);
      add(`tl.fromTo('#${id}-l${i}', { opacity: 0 }, { opacity: 1, duration: 0.18, ease: 'none', immediateRender: false }, ${q(t)});`);
      add(`tl.set('#${id}-t${i}', { color: '#FFF3D1' }, ${q(t)});`);
      add(`tl.fromTo('#${id}-e${i}', { scale: 1.08 }, { scale: 1, duration: 0.6, ease: 'power3.out', immediateRender: false }, ${q(t)});`);
      add(`tl.fromTo('#${id}-s${i}', { xPercent: -200 }, { xPercent: 700, duration: 0.7, ease: 'power2.inOut', immediateRender: false }, ${q(t + 0.1)});`);
    });
    add(`tl.to('#${id} .et', { y: -10, duration: 0.25, ease: 'power2.out', yoyo: true, repeat: 1, stagger: 0.07 }, ${q(etapas[etapas.length - 1][1] + 0.45)});`);
  }

  // ── INSERT: título em tela cheia (nome do evento) — linhas batem uma a uma, última dourada com estouro ──
  function insertTitulo({ start, end, kicker, linhas }) {
    const id = "ins-titulo";
    const n = linhas.length;
    const dots = Array.from({ length: 16 }, (_, i) => `<i class="bd" id="${id}-p${i}"></i>`).join("");
    layers += `    <div class="insert clip" id="${id}" data-start="${q(start)}" data-duration="${q(end - start)}" data-track-index="5">
      <div class="ins-bg" id="${id}-bg"><div class="rays" id="${id}-rays"></div><div class="glow tt"></div>
        <div class="tt-wrap" id="${id}-wrap">
          ${kicker ? `<div class="tt-k">${M(kicker)}</div>` : ""}
          ${linhas.map(([t], i) => `<div class="tt-l${i === n - 1 ? " last" : ""}" id="${id}-l${i}"><span class="${i === n - 1 ? "gold-fill" : ""}" id="${id}-x${i}">${t}</span></div>`).join("")}
          <div class="burst" id="${id}-burst">${dots}</div>
        </div>
      </div>
    </div>\n`;
    add(`// insert título`);
    desfoque(start, end);
    add(`tl.fromTo('#${id}-bg', { opacity: 0 }, { opacity: 1, duration: 0.45, ease: 'power2.out' }, ${q(start)});`);
    add(`tl.fromTo('#${id}-rays', { rotation: 0 }, { rotation: 50, duration: ${(end - start).toFixed(2)}, ease: 'none' }, ${q(start)});`);
    add(`tl.fromTo('#${id}-wrap', { scale: 1 }, { scale: 1.07, duration: ${(end - start - 0.35).toFixed(2)}, ease: 'none' }, ${q(start)});`);
    if (kicker) maskIn(`#${id} .tt-k .mi`, start + 0.2, 0, start);
    hide(`#${id} .tt-l`, "{ opacity: 0 }", start);
    hide(`#${id} .bd`, "{ opacity: 0 }", start);
    linhas.forEach(([, t], i) => {
      const last = i === n - 1;
      add(`tl.fromTo('#${id}-l${i}', { opacity: 0, scale: ${last ? 1.5 : 1.25}, filter: 'blur(22px)' }, { opacity: 1, scale: 1, filter: 'blur(0px)', duration: ${last ? 0.7 : 0.5}, ease: 'expo.out', immediateRender: false }, ${q(t - 0.04)});`);
      if (last) {
        shimmer(`#${id}-x${i}`, t + 0.3);
        shake([t + 0.08], { forca: 8, alvo: `#${id}-x${i}` });
        for (let k = 0; k < 16; k++) {
          const a = (k / 16) * 2 * Math.PI, d = 330 + (k % 3) * 80;
          add(`tl.fromTo('#${id}-p${k}', { x: 0, y: 0, opacity: 1, scale: 1 }, { x: ${(Math.cos(a) * d).toFixed(0)}, y: ${(Math.sin(a) * d * 0.7).toFixed(0)}, opacity: 0, scale: 0.3, duration: 0.8, ease: 'expo.out', immediateRender: false }, ${q(t + 0.02)});`);
        }
      }
    });
    add(`tl.to('#${id}-wrap', { scale: 1.8, opacity: 0, filter: 'blur(16px)', duration: 0.4, ease: 'power3.in' }, ${q(end - 0.4)});`);
    add(`tl.to('#${id}-bg', { opacity: 0, duration: 0.3, ease: 'power2.in' }, ${q(end - 0.3)});`);
  }

  // ── card de contraste: "NÃO É SOBRE X" (risca) → vira em 3D → "É SOBRE Y" dourado ──
  function cardContraste(id, start, end, { k1, t1, t1At, riscoAt, virarAt, k2, t2, t2At }) {
    card(id, start, end,
      `<div class="flip"><div class="face" id="${id}-a"><div class="kicker">${M(k1)}</div><div class="title"><span class="riscavel" id="${id}-t1">${M(t1)}<i class="risco" id="${id}-risco"></i></span></div></div>
      <div class="face" id="${id}-b"><div class="kicker">${k2}</div><div class="title"><span class="gold-fill" id="${id}-t2">${t2}</span></div></div></div>`,
      (s) => {
        maskIn(`#${id}-t1 .mi`, t1At ?? s + 0.2, 0, s);
        hide(`#${id}-risco`, "{ scaleX: 0, rotation: -3 }", s);
        hide(`#${id}-b`, "{ rotationX: 90, opacity: 0 }", s);
        hide(`#${id}-a`, "{ rotationX: 0, opacity: 1 }", s);
        add(`tl.fromTo('#${id}-risco', { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: 'expo.out', immediateRender: false }, ${q(riscoAt)});`);
        add(`tl.to('#${id}-t1', { opacity: 0.55, duration: 0.2 }, ${q(riscoAt)});`);
        add(`tl.to('#${id}-a', { rotationX: -90, opacity: 0, transformPerspective: 700, transformOrigin: '50% 0%', duration: 0.28, ease: 'power2.in' }, ${q(virarAt)});`);
        add(`tl.fromTo('#${id}-b', { rotationX: 90, opacity: 0 }, { rotationX: 0, opacity: 1, transformPerspective: 700, transformOrigin: '50% 100%', duration: 0.5, ease: 'back.out(1.6)', immediateRender: false }, ${q(virarAt + 0.2)});`);
        shimmer(`#${id}-t2`, t2At);
        add(`tl.fromTo('#${id}-t2', { scale: 1.3 }, { scale: 1, duration: 0.45, ease: 'elastic.out(1, 0.5)', immediateRender: false }, ${q(t2At)});`);
      });
  }

  function salvar(outFile) {
    const css = fs.readFileSync(path.join(__dirname, "estilo.css"), "utf8");
    const html = `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<style>
${css}
</style>
</head>
<body>
  <div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="${DUR}" data-fps="${fps}" data-width="1080" data-height="1920">
    <div id="video-wrap"><div id="video-zoom">
      <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="${DUR}" data-track-index="1"></video>
    </div></div>
${usaDesfoque ? `    <div id="blur-wrap"><video id="blur-video" src="input-blur.mp4" muted playsinline data-start="0" data-duration="${DUR}" data-track-index="11"></video></div>\n` : ""}    <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="${DUR}" data-track-index="10" data-volume="1"></audio>
${layers}
    <script src="vendor/gsap.min.js"></script>
    <script>
(function () {
  const tl = window.gsap.timeline({ paused: true });
${js}
  window.__timelines = window.__timelines || {};
  window.__timelines["talking-head-recut"] = tl;
})();
    </script>
  </div>
</body>
</html>
`;
    fs.mkdirSync(path.dirname(outFile), { recursive: true });
    const blur = path.join(path.dirname(outFile), "input-blur.mp4");
    if (usaDesfoque && !fs.existsSync(blur))
      require("child_process").execFileSync("ffmpeg", ["-v", "error", "-y", "-i", path.join(path.dirname(outFile), "input-video.mp4"), "-an", "-vf",
        "scale=270:480,gblur=sigma=9,eq=brightness=-0.06:saturation=1.15,scale=1080:1920:flags=bicubic,setsar=1", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "24", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", blur], { stdio: "inherit" });
    fs.writeFileSync(outFile, html, "utf8");
    console.log("composição gerada:", outFile);
  }

  return { q, add, M, hide, maskIn, shimmer, sheen, camera, card, cardTitulo, cardLista, cardCTA, insertCirculo, insertCrescimento, insertCiclo, insertEtapas, insertTitulo, cardContraste, shake, filtro, corteSuave, legenda, legendaDinamica, flash, salvar };
}

module.exports = { criar };
