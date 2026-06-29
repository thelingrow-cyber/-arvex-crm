/* ============================================================================
 * ARVEX Meet Transcriber — content.js
 * Roda dentro do meet.google.com. Observa as legendas, acumula a transcrição
 * (dedupe + finaliza turnos estáveis) e guarda em chrome.storage.local.
 * Mostra um widget flutuante (Iniciar/Parar, contador, Copiar, Baixar).
 * ========================================================================== */
(function () {
  "use strict";
  const P = window.ArvexCaptionParser;
  if (!P) return;

  const meetingId = (location.pathname.replace(/\//g, "") || "meet") + "";
  const STORE_KEY = "arvex_transcript_" + meetingId;

  let capturing = false;
  let transcript = [];        // [{speaker, text, at}]
  let active = new Map();      // key(speaker) -> {text, stable}
  let pollTimer = null;
  let observer = null;

  // ---- storage ----
  function save() {
    try { chrome.storage.local.set({ [STORE_KEY]: transcript }); } catch (e) {}
  }
  function load(cb) {
    try {
      chrome.storage.local.get([STORE_KEY], (r) => { transcript = r[STORE_KEY] || []; cb && cb(); });
    } catch (e) { cb && cb(); }
  }

  // ---- finalização de turnos (dedupe) ----
  // Meet reescreve a legenda enquanto a pessoa fala. Só "fechamos" um turno
  // quando o texto para de mudar (estável por 2 leituras) → evita lixo.
  function lastFor(speaker) {
    for (let i = transcript.length - 1; i >= 0; i--) {
      if (transcript[i].speaker === speaker) return transcript[i];
    }
    return null;
  }
  function commit(speaker, text) {
    const prev = lastFor(speaker);
    if (prev && prev.text === text) return;        // dedupe exato
    // se o novo texto só ESTENDE o anterior (mesma fala crescendo), substitui
    if (prev && text.startsWith(prev.text) && (Date.now() - prev.at) < 15000) {
      prev.text = text; prev.at = Date.now(); save(); return;
    }
    transcript.push({ speaker, text, at: Date.now() });
    save();
    updateBadge();
  }

  function tick() {
    if (!capturing) return;
    const region = P.findRegion();
    const rows = P.parseRows(region);
    const seenKeys = new Set();
    for (const row of rows) {
      const key = row.speaker || "_";
      seenKeys.add(key);
      const a = active.get(key);
      if (a && a.text === row.text) {
        a.stable++;
        if (a.stable >= 2) { commit(key === "_" ? "" : key, row.text); active.delete(key); }
      } else {
        active.set(key, { text: row.text, stable: 0 });
      }
    }
    // turnos que sumiram da tela → finaliza
    for (const [key, a] of active) {
      if (!seenKeys.has(key)) { commit(key === "_" ? "" : key, a.text); active.delete(key); }
    }
  }

  function start() {
    if (capturing) return;
    capturing = true;
    active.clear();
    pollTimer = setInterval(tick, 1000);
    const region = P.findRegion();
    if (region) {
      observer = new MutationObserver(() => { /* o tick de 1s consolida */ });
      observer.observe(region, { childList: true, subtree: true, characterData: true });
    }
    render();
  }
  function stop() {
    capturing = false;
    clearInterval(pollTimer); pollTimer = null;
    if (observer) { observer.disconnect(); observer = null; }
    // finaliza o que sobrou ativo
    for (const [key, a] of active) commit(key === "_" ? "" : key, a.text);
    active.clear();
    render();
  }
  function clearAll() {
    transcript = []; active.clear(); save(); updateBadge();
  }

  // ---- export ----
  function asText() {
    return transcript.map(t => (t.speaker ? t.speaker + ": " : "") + t.text).join("\n");
  }

  // ---- widget flutuante ----
  let elBadge;
  function render() {
    let box = document.getElementById("arvex-tx-box");
    if (!box) {
      box = document.createElement("div");
      box.id = "arvex-tx-box";
      box.innerHTML =
        '<div id="arvex-tx-row">' +
          '<button id="arvex-tx-toggle"></button>' +
          '<span id="arvex-tx-badge">0 linhas</span>' +
          '<button id="arvex-tx-copy" title="Copiar">⧉</button>' +
          '<button id="arvex-tx-dl" title="Baixar .txt">⤓</button>' +
        '</div>';
      document.body.appendChild(box);
      box.querySelector("#arvex-tx-toggle").addEventListener("click", () => capturing ? stop() : start());
      box.querySelector("#arvex-tx-copy").addEventListener("click", () => {
        navigator.clipboard.writeText(asText()).then(() => flash("Copiado!"));
      });
      box.querySelector("#arvex-tx-dl").addEventListener("click", download);
      elBadge = box.querySelector("#arvex-tx-badge");
    }
    const tgl = box.querySelector("#arvex-tx-toggle");
    tgl.textContent = capturing ? "● Gravando" : "▶ Transcrever";
    tgl.className = capturing ? "rec" : "";
    updateBadge();
  }
  function updateBadge() { if (elBadge) elBadge.textContent = transcript.length + " linhas"; }
  function flash(msg) {
    const f = document.createElement("div"); f.className = "arvex-tx-flash"; f.textContent = msg;
    document.body.appendChild(f); setTimeout(() => f.remove(), 1500);
  }
  function download() {
    const blob = new Blob([asText()], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "transcricao-meet-" + meetingId + ".txt";
    a.click(); URL.revokeObjectURL(url);
  }

  // ---- mensagens do popup ----
  try {
    chrome.runtime.onMessage.addListener((msg, _s, reply) => {
      if (msg.cmd === "status") reply({ capturing, count: transcript.length, text: asText() });
      if (msg.cmd === "start") { start(); reply({ ok: true }); }
      if (msg.cmd === "stop") { stop(); reply({ ok: true }); }
      if (msg.cmd === "clear") { clearAll(); reply({ ok: true }); }
      return true;
    });
  } catch (e) {}

  load(() => render());
})();
