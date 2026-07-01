/* ============================================================================
 * ARVEX Meet Transcriber — content.js
 * Roda dentro do meet.google.com. Observa as legendas ao vivo, reconstrói a
 * transcrição (lida com legenda ROLANTE do Meet: texto que cresce e "rola")
 * e mostra um PAINEL LATERAL com a transcrição em tempo real (estilo Tactiq).
 * Guarda em chrome.storage.local. Envia pro CRM em 1 clique.
 * ========================================================================== */
(function () {
  "use strict";
  const P = window.ArvexCaptionParser;
  if (!P) return;

  const meetingId = (location.pathname.replace(/\//g, "") || "meet") + "";
  const STORE_KEY = "arvex_transcript_" + meetingId;
  const INGEST_URL = "https://sgeoikzyahhdrncesbpn.supabase.co/functions/v1/ingest-meeting";
  const PUB_KEY = "sb_publishable_awL7tcTl7HMzkvHqYihHKA_JZwO_CKI";

  let capturing = false;
  let transcript = [];        // [{speaker, text, at}]
  let pollTimer = null;
  let observer = null;
  let nodeSeq = 0;
  let nodeToIdx = new Map();   // id do bloco de legenda -> índice no transcript (anti-duplicação)
  let selfName = "";           // nome real do usuário (troca "Você")

  // ---- storage ----
  function save() {
    try { chrome.storage.local.set({ [STORE_KEY]: transcript }); } catch (e) {}
  }
  function load(cb) {
    try {
      chrome.storage.local.get([STORE_KEY], (r) => { transcript = r[STORE_KEY] || []; cb && cb(); });
    } catch (e) { cb && cb(); }
  }

  // ---- nome do usuário: troca "Você" pelo nome real (config no popup ou auto-detect) ----
  function loadSelfName() {
    try {
      chrome.storage.local.get(["arvex_self_name"], (r) => {
        selfName = (r && r.arvex_self_name) || detectSelfName() || "";
        renderTranscript();
      });
      if (chrome.storage.onChanged) {
        chrome.storage.onChanged.addListener((ch, area) => {
          if (area === "local" && ch.arvex_self_name) {
            selfName = ch.arvex_self_name.newValue || detectSelfName() || "";
            renderTranscript();
          }
        });
      }
    } catch (e) {}
  }
  // best-effort: descobre o próprio nome pelo marcador "(Você)"/"(You)" do Meet
  function detectSelfName() {
    const hit = [...document.querySelectorAll("[aria-label]")]
      .map((el) => el.getAttribute("aria-label") || "")
      .find((l) => /\((você|voc[eê]|you)\)\s*$/i.test(l));
    return hit ? hit.replace(/\s*\((você|voc[eê]|you)\)\s*$/i, "").trim() : "";
  }
  function resolveSpeaker(sp) {
    if (!sp) return "";
    if (P.SELF_NAMES && P.SELF_NAMES.test(sp)) return selfName || sp;
    return sp;
  }

  // ---- escolhe o melhor texto entre versões do MESMO bloco (legenda que cresce/rola) ----
  function bestText(oldT, newT) {
    if (!oldT) return newT;
    if (!newT || newT === oldT) return oldT;
    if (newT.startsWith(oldT)) return newT;   // cresceu
    if (oldT.startsWith(newT)) return oldT;    // encurtou (rolou) → mantém o maior
    if (oldT.includes(newT)) return oldT;
    if (newT.includes(oldT)) return newT;
    const merged = mergeRolling(oldT, newT);
    return merged || (newT.length >= oldT.length ? newT : oldT);
  }
  // concatena por sobreposição de palavras (fim de a == começo de b)
  function mergeRolling(a, b) {
    const aw = a.split(/\s+/), bw = b.split(/\s+/);
    const max = Math.min(aw.length, bw.length);
    for (let k = max; k > 0; k--) {
      if (aw.slice(aw.length - k).join(" ").toLowerCase() ===
          bw.slice(0, k).join(" ").toLowerCase()) {
        return a + " " + bw.slice(k).join(" ");
      }
    }
    return null;
  }

  // ---- upsert por BLOCO: cada caixa de legenda visível = 1 turno FIXO (anti-duplicação) ----
  // O Meet mostra vários blocos ao mesmo tempo; marcamos cada nó com um id estável
  // e mapeamos pro seu turno, então o mesmo bloco nunca vira 2 linhas.
  function upsertRow(row) {
    const text = (row.text || "").trim();
    if (!text) return;
    const el = row.el;
    let id = null;
    if (el && el.getAttribute) {
      id = el.getAttribute("data-arvex-id");
      if (!id) { id = "n" + (++nodeSeq); try { el.setAttribute("data-arvex-id", id); } catch (e) {} }
    }
    if (id && nodeToIdx.has(id)) {
      const turn = transcript[nodeToIdx.get(id)];
      if (turn) {
        const merged = bestText(turn.text, text);
        if (merged !== turn.text) { turn.text = merged; turn.at = Date.now(); save(); }
        return;
      }
    }
    transcript.push({ speaker: row.speaker || "", text, at: Date.now() });
    if (id) nodeToIdx.set(id, transcript.length - 1);
    save();
  }

  function tick() {
    if (!capturing) return;
    let rows = [];
    try { rows = P.parseRows(P.findRegion()); } catch (e) {}
    for (const row of rows) upsertRow(row);
    renderTranscript();
    updateBadge();
  }

  function start() {
    if (capturing) return;
    capturing = true;
    pollTimer = setInterval(tick, 700);
    const region = P.findRegion();
    if (region) {
      observer = new MutationObserver(() => tick());
      observer.observe(region, { childList: true, subtree: true, characterData: true });
    }
    renderControls();
  }
  function stop() {
    capturing = false;
    clearInterval(pollTimer); pollTimer = null;
    if (observer) { observer.disconnect(); observer = null; }
    tick();
    renderControls();
  }
  function clearAll() {
    transcript = []; nodeToIdx = new Map(); nodeSeq = 0;
    save(); renderTranscript(); updateBadge();
  }

  // ---- export ----
  function asText() {
    return transcript.map((t) => {
      const sp = resolveSpeaker(t.speaker);
      return (sp ? sp + ": " : "") + t.text;
    }).join("\n");
  }

  // ============================ PAINEL LATERAL ============================
  function buildPanel() {
    if (document.getElementById("arvex-panel")) return;
    const p = document.createElement("div");
    p.id = "arvex-panel";
    p.innerHTML =
      '<div id="arvex-head">' +
        '<span id="arvex-logo">ARVEX</span>' +
        '<span id="arvex-title">Transcrição ao vivo</span>' +
        '<button id="arvex-min" title="Recolher">–</button>' +
      '</div>' +
      '<div id="arvex-list"></div>' +
      '<div id="arvex-foot">' +
        '<div class="arvex-foot-row">' +
          '<button id="arvex-toggle"></button>' +
          '<span id="arvex-badge">0 linhas</span>' +
          '<button id="arvex-copy" title="Copiar">⧉</button>' +
          '<button id="arvex-dl" title="Baixar .txt">⤓</button>' +
          '<button id="arvex-clear" title="Limpar">🗑</button>' +
          '<button id="arvex-dbg" title="Copiar HTML da legenda (debug)">🐞</button>' +
        '</div>' +
        '<div class="arvex-foot-row">' +
          '<input id="arvex-cliente" placeholder="Nome do cliente" />' +
          '<button id="arvex-crm" title="Criar reunião + análise no CRM">⬆ CRM</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(p);

    // aba pra reabrir quando recolhido
    const tab = document.createElement("button");
    tab.id = "arvex-tab"; tab.textContent = "ARVEX ›"; tab.title = "Abrir transcrição";
    tab.style.display = "none";
    document.body.appendChild(tab);

    p.querySelector("#arvex-toggle").addEventListener("click", () => capturing ? stop() : start());
    p.querySelector("#arvex-copy").addEventListener("click", () =>
      navigator.clipboard.writeText(asText()).then(() => flash("Copiado!")));
    p.querySelector("#arvex-dl").addEventListener("click", download);
    p.querySelector("#arvex-clear").addEventListener("click", () => {
      if (confirmClear()) clearAll();
    });
    p.querySelector("#arvex-crm").addEventListener("click", sendToCRM);
    p.querySelector("#arvex-dbg").addEventListener("click", copyDebug);
    p.querySelector("#arvex-min").addEventListener("click", () => {
      p.classList.add("hidden"); tab.style.display = "block";
    });
    tab.addEventListener("click", () => { p.classList.remove("hidden"); tab.style.display = "none"; });

    renderControls();
    renderTranscript();
  }

  // simples: sem window.confirm (evita bloquear a extensão). Duplo-clique confirma.
  let clearArmed = false;
  function confirmClear() {
    if (clearArmed) { clearArmed = false; return true; }
    clearArmed = true; flash("Clique de novo pra limpar");
    setTimeout(() => (clearArmed = false), 2500);
    return false;
  }

  function renderControls() {
    const t = document.getElementById("arvex-toggle");
    if (!t) return;
    t.textContent = capturing ? "● Gravando" : "▶ Transcrever";
    t.className = capturing ? "rec" : "";
    updateBadge();
  }
  function updateBadge() {
    const b = document.getElementById("arvex-badge");
    if (b) b.textContent = transcript.length + (transcript.length === 1 ? " linha" : " linhas");
  }
  function renderTranscript() {
    const list = document.getElementById("arvex-list");
    if (!list) return;
    if (!transcript.length) {
      list.innerHTML = '<div id="arvex-empty">Ligue a legenda (CC) do Meet e clique em ' +
        '<b>▶ Transcrever</b>.<br>O texto aparece aqui conforme você fala.</div>';
      return;
    }
    const near = list.scrollTop + list.clientHeight >= list.scrollHeight - 40; // auto-scroll só se já tá no fim
    list.innerHTML = transcript.map((t) => {
      const sp = resolveSpeaker(t.speaker);
      return '<div class="arvex-turn">' +
        (sp ? '<span class="arvex-sp">' + esc(sp) + ':</span> ' : '') +
        '<span class="arvex-tx">' + esc(t.text) + '</span>' +
      '</div>';
    }).join("");
    if (near) list.scrollTop = list.scrollHeight;
  }
  function esc(s) {
    return (s || "").replace(/[&<>"]/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function flash(msg) {
    const f = document.createElement("div"); f.className = "arvex-flash"; f.textContent = msg;
    document.body.appendChild(f); setTimeout(() => f.remove(), 1600);
  }
  function download() {
    const blob = new Blob([asText()], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "transcricao-meet-" + meetingId + ".txt";
    a.click(); URL.revokeObjectURL(url);
  }

  // ---- DEBUG: copia o HTML bruto da região de legenda (pra calibrar o parser) ----
  function copyDebug() {
    const t = document.querySelector('[jsname="dsyhDe"]'); // texto de fala = sinal confiável
    let region = t
      ? (t.closest(".a4cQT") || t.parentElement)
      : [...document.querySelectorAll('[role="region"][aria-label]')]
          .find((el) => /caption|legenda|subtitle/i.test(el.getAttribute("aria-label") || ""));
    if (!region) { flash("Fale primeiro (legenda não visível)"); return; }
    navigator.clipboard.writeText(region.outerHTML.slice(0, 8000))
      .then(() => flash("HTML copiado! Cole no chat"))
      .catch(() => flash("Erro ao copiar HTML"));
  }

  // ---- enviar pro CRM (cria reunião + dispara análise) ----
  function sendToCRM() {
    if (!transcript.length) { flash("Nada pra enviar ainda"); return; }
    chrome.storage.local.get(["arvex_closer_email"], (r) => {
      const email = (r && r.arvex_closer_email) || "";
      const clienteEl = document.getElementById("arvex-cliente");
      const cliente = clienteEl ? clienteEl.value.trim() : "";
      flash("Enviando…");
      fetch(INGEST_URL, {
        method: "POST",
        headers: { "apikey": PUB_KEY, "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: asText(), closer_email: email, cliente: cliente }),
      })
        .then((res) => res.json())
        .then((d) => flash(d && d.ok ? "Enviado! Análise rodando no CRM" : ("Erro: " + ((d && d.error) || "falha"))))
        .catch(() => flash("Erro de rede ao enviar (CSP do Meet?)"));
    });
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

  load(() => { buildPanel(); loadSelfName(); });
})();
