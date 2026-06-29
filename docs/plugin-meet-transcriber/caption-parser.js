/* ============================================================================
 * ARVEX Meet Transcriber — caption-parser.js
 * Localiza a região de legendas do Google Meet e extrai {falante, texto}.
 *
 * ⚠️ MANUTENÇÃO: o DOM do Meet NÃO é API pública. Os seletores semânticos
 * (role=region + aria-label) são os mais estáveis. As classes ofuscadas
 * (.nMcdL, .bh44bd, .ygicle...) mudam sem aviso — por isso há FALLBACK
 * heurístico. Se um dia parar de capturar, ajuste findRegion()/parseRows()
 * aqui (e só aqui). Ver BUILD-REPORT.md.
 * ========================================================================== */
(function () {
  "use strict";

  // aria-label das legendas varia por idioma: "Captions" (EN), "Legendas" (PT-BR), etc.
  const CAPTION_LABEL_RE = /caption|legenda|subtitle|sottotitoli|untertitel|sous-titres/i;

  // 1) Acha a região de legendas — semântico primeiro, fallback depois.
  function findRegion() {
    // a) semântico: role=region com aria-label de legendas
    const regions = document.querySelectorAll('[role="region"][aria-label]');
    for (const r of regions) {
      if (CAPTION_LABEL_RE.test(r.getAttribute("aria-label") || "")) return r;
    }
    // b) fallback: qualquer região cujo aria-label bata
    const labelled = document.querySelectorAll('[aria-label]');
    for (const el of labelled) {
      if (CAPTION_LABEL_RE.test(el.getAttribute("aria-label") || "") &&
          el.querySelectorAll("*").length > 1) return el;
    }
    // c) fallback heurístico: container com avatares googleusercontent (linhas de legenda)
    const avatar = document.querySelector('img[src*="googleusercontent.com"]');
    if (avatar) {
      let p = avatar;
      for (let i = 0; i < 6 && p; i++) { p = p.parentElement; }
      if (p) return p;
    }
    return null;
  }

  // 2) Extrai as linhas visíveis: [{ speaker, text }]
  //    Cada "turno" no Meet costuma ter: [avatar/nome] + [texto]. Estrutura varia,
  //    então tentamos várias estratégias e caímos no texto cru se preciso.
  function parseRows(region) {
    if (!region) return [];
    const rows = [];
    // candidatos a "linha de legenda": filhos diretos relevantes da região
    const blocks = region.querySelectorAll(":scope > div, :scope > div > div");
    const list = blocks.length ? blocks : region.children;

    for (const b of list) {
      const full = (b.innerText || "").trim();
      if (!full) continue;

      let speaker = "";
      let text = full;

      // estratégia A: nome perto de um avatar (img)
      const img = b.querySelector('img[src*="googleusercontent.com"], img[alt]');
      if (img) {
        const alt = (img.getAttribute("alt") || "").trim();
        if (alt && alt.length < 60) speaker = alt;
      }
      // estratégia B: primeiro elemento "curto" (nome) + resto (texto)
      if (!speaker) {
        const spans = b.querySelectorAll("span, div");
        for (const s of spans) {
          const t = (s.innerText || "").trim();
          if (t && t.length <= 40 && full.startsWith(t) && t !== full) {
            speaker = t; break;
          }
        }
      }
      // se achou falante no começo do texto, separa
      if (speaker && text.startsWith(speaker)) {
        text = text.slice(speaker.length).replace(/^[\s:.\-–—]+/, "").trim();
      }
      if (!text) continue;
      rows.push({ speaker: speaker || "", text });
    }
    return rows;
  }

  window.ArvexCaptionParser = { findRegion, parseRows };
})();
