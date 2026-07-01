/* ============================================================================
 * ARVEX Meet Transcriber — caption-parser.js
 * Localiza a região de legendas do Google Meet e extrai {falante, texto}.
 *
 * ⚠️ MANUTENÇÃO: o DOM do Meet NÃO é API pública. Estrutura real (jun/2026):
 *   .a4cQT            → um TURNO de legenda (um bloco falante+fala)
 *     .NmXUuc         → nome/avatar do falante
 *     [jsname=dsyhDe] → o TEXTO da fala (o que a pessoa disse)
 * A estratégia principal itera os nós de TEXTO (jsname="dsyhDe") e deriva o
 * falante do turno .a4cQT. Se o Google mudar isso, ajuste findRegion()/parseRows()
 * aqui (e só aqui). Há fallback genérico por avatar+texto. Ver BUILD-REPORT.md.
 * ========================================================================== */
(function () {
  "use strict";

  // aria-label das legendas varia por idioma: "Captions" (EN), "Legendas" (PT-BR), etc.
  const CAPTION_LABEL_RE = /caption|legenda|subtitle|sottotitoli|untertitel|sous-titres/i;
  const SELF_NAMES = /^(você|voce|you|tu)$/i; // Meet legenda o próprio usuário como "Você"

  function clean(s) {
    return (s || "").replace(/\s+/g, " ").trim();
  }

  // ---- 1) Acha o container das legendas ----
  // ⚠️ CUIDADO: o Meet reusa a classe .a4cQT no SELETOR DE IDIOMA e no botão de
  // config. O sinal confiável de FALA é o nó de texto jsname="dsyhDe". Então
  // priorizamos ele, não a classe .a4cQT (ambígua).
  function findRegion() {
    // a) semântico: role=region com aria-label de legendas (exclui <button>)
    for (const r of document.querySelectorAll('[role="region"][aria-label]')) {
      if (r.tagName !== "BUTTON" && CAPTION_LABEL_RE.test(r.getAttribute("aria-label") || "")) return r;
    }
    // b) container dos textos de legenda (dsyhDe só existe na fala real)
    const t = document.querySelector('[jsname="dsyhDe"]');
    if (t) {
      const turn = t.closest(".a4cQT");
      return (turn && turn.parentElement) || t.parentElement;
    }
    // c) último recurso: um .a4cQT que CONTENHA texto de legenda (ignora o de idioma)
    for (const a of document.querySelectorAll(".a4cQT")) {
      if (a.querySelector('[jsname="dsyhDe"]')) return a.parentElement || a;
    }
    return null;
  }

  // ---- 2) Extrai os turnos visíveis: [{ speaker, text }] ----
  function parseRows(region) {
    const root = region || document;
    const rows = [];

    // ESTRATÉGIA PRINCIPAL: cada fala tem um nó de texto jsname="dsyhDe".
    let textNodes = root.querySelectorAll('[jsname="dsyhDe"]');
    if (!textNodes.length) textNodes = document.querySelectorAll('[jsname="dsyhDe"]');
    if (textNodes.length) {
      for (const tn of textNodes) {
        const text = clean(tn.innerText || tn.textContent);
        if (!text) continue;
        // el = identidade estável do bloco (pra não duplicar entre ticks)
        rows.push({ speaker: speakerFor(tn, text), text, el: tn });
      }
      if (rows.length) return rows;
    }

    // FALLBACK genérico (estrutura antiga): turnos com avatar + texto no mesmo bloco.
    let list = root.querySelectorAll(".a4cQT, .nMcdL");
    if (!list.length) list = root.querySelectorAll("div:has(> img)");
    if (!list.length && root.children) list = root.children;
    for (const b of list) {
      const full = clean(b.innerText);
      if (!full) continue;
      let speaker = "";
      const img = b.querySelector("img[alt]");
      if (img && img.getAttribute("alt") && img.getAttribute("alt").length < 60) {
        speaker = clean(img.getAttribute("alt"));
      }
      let text = full;
      if (speaker && full.startsWith(speaker)) {
        text = clean(full.slice(speaker.length).replace(/^[\s:.\-–—]+/, ""));
      }
      if (text) rows.push({ speaker, text, el: b });
    }
    return rows;
  }

  // ---- descobre o falante associado a um nó de texto ----
  function speakerFor(textNode, text) {
    const turn = textNode.closest(".a4cQT") ||
      (textNode.parentElement && textNode.parentElement.parentElement) ||
      textNode.parentElement;
    if (!turn) return "";
    // a) bloco de nome .NmXUuc
    const nameEl = turn.querySelector(".NmXUuc");
    if (nameEl) {
      const n = clean(nameEl.innerText);
      if (n && n.length < 60 && n !== text) return n;
    }
    // b) avatar com alt
    const img = turn.querySelector("img[alt]");
    if (img) {
      const alt = clean(img.getAttribute("alt"));
      if (alt && alt.length < 60) return alt;
    }
    // c) diferença: texto do turno menos a fala
    const full = clean(turn.innerText);
    const idx = full.lastIndexOf(text);
    if (idx > 0) {
      const n = clean(full.slice(0, idx)).replace(/[:.\-–—\s]+$/, "");
      if (n && n.length < 60) return n;
    }
    return "";
  }

  window.ArvexCaptionParser = { findRegion, parseRows, SELF_NAMES };
})();
