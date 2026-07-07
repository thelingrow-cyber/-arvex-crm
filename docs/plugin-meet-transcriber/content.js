/* ============================================================================
 * ARVEX Meet Transcriber — content.js
 * Roda dentro do meet.google.com. Observa as legendas ao vivo, reconstrói a
 * transcrição (lida com legenda ROLANTE do Meet: texto que cresce e "rola")
 * e mostra um PAINEL LATERAL com a transcrição em tempo real (estilo Tactiq).
 * Guarda em chrome.storage.local. Envia pro CRM em 1 clique.
 * A lógica de merge/dedupe/export vive em transcript-core.js (compartilhada
 * com a regressão em tests/) — aqui só orquestra DOM, storage e rede.
 * ========================================================================== */
(function () {
  "use strict";
  const P = window.ArvexCaptionParser;
  const Core = window.ArvexTranscriptCore;
  if (!P || !Core) return;

  // ---- identidade da reunião: inclui a DATA pra sala recorrente não herdar
  // a transcrição da call anterior (ADR-5, MEDIUM-1 do DEEP-ANALYSIS-FABLE.md) ----
  function todayStr() {
    const d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  const meetingId = (location.pathname.replace(/\//g, "") || "meet") + "_" + todayStr();
  const STORE_KEY = "arvex_transcript_" + meetingId;
  const SENT_KEY = "arvex_sent_" + meetingId;
  const NOTES_KEY = "arvex_notes_" + meetingId;
  const INGEST_URL = "https://sgeoikzyahhdrncesbpn.supabase.co/functions/v1/ingest-meeting";
  const PUB_KEY = "sb_publishable_awL7tcTl7HMzkvHqYihHKA_JZwO_CKI";
  const CLEANUP_DAYS = 7;
  const CC_LABEL_RE = /ligar legendas|turn on captions|ativar legendas|activar subt[íi]tulos|activer les sous-titres|untertitel aktivieren/i;

  const store = Core.createStore();
  let capturing = false;
  let pollTimer = null;
  let canaryTimer = null;
  let observer = null;
  let selfName = "";
  let sentAt = null;       // timestamp do último envio bem-sucedido (ou null)
  let sendInFlight = false;
  let activeTab = "transcript"; // "transcript" | "notes"
  let renderedNodes = [];  // paralelo a store.transcript: {groupEl, txEl} já no DOM (render incremental — MEDIUM-3)

  // canário de captura (ADR-1.1): detecta falha SILENCIOSA (região some / zero linhas)
  let regionMissingSince = 0;
  let emptyRowsSince = 0;
  let statusState = "idle"; // idle | ok | cc-trying | cc-off | parser-stale

  // Guard 2 (ADR-9, DEEP-ANALYSIS-FABLE.md §6.4): se o caminho principal (dsyhDe) achou
  // nós há <2s e agora sumiu momentaneamente (o Meet reconstrói o DOM da legenda), pula
  // o tick em vez de cair no fallback (menos confiável, pode criar turno espúrio).
  let lastMainPathNodesSeenAt = 0;
  const TRANSIENT_GRACE_MS = 2000;

  // Flight recorder (ADR-8): ring buffer dos últimos ticks — pra diagnosticar de fato
  // (não adivinhar) o que aconteceu numa call real. Sai junto no copyDebug().
  const RECORDER_MAX = 120;
  let recorder = [];
  function recordTick(path, rowCount, rowsInfo, mergeEvents) {
    recorder.push({ t: Date.now(), path, rowCount, rows: rowsInfo || [], merges: mergeEvents || [] });
    if (recorder.length > RECORDER_MAX) recorder.shift();
  }

  // ---- storage: transcrição + metadado de quando foi salva (pra limpeza por idade) ----
  function save() {
    try { chrome.storage.local.set({ [STORE_KEY]: { transcript: store.transcript, updatedAt: Date.now() } }); } catch (e) {}
  }
  function load(cb) {
    try {
      chrome.storage.local.get([STORE_KEY, SENT_KEY, NOTES_KEY], (r) => {
        const rec = r && r[STORE_KEY];
        store.transcript = (rec && rec.transcript) || [];
        sentAt = (r && r[SENT_KEY]) || null;
        cb && cb((r && r[NOTES_KEY]) || "");
      });
    } catch (e) { cb && cb(""); }
  }
  // limpeza: transcrições de reuniões >7 dias somem sozinhas (MEDIUM-1)
  function cleanupOldTranscripts() {
    try {
      chrome.storage.local.get(null, (all) => {
        const now = Date.now();
        const toRemove = [];
        for (const k in all) {
          if (!k.indexOf || k.indexOf("arvex_transcript_") !== 0) continue;
          const rec = all[k];
          const ts = (rec && rec.updatedAt) || 0;
          if (ts && now - ts > CLEANUP_DAYS * 24 * 3600 * 1000) toRemove.push(k);
        }
        if (toRemove.length) chrome.storage.local.remove(toRemove);
      });
    } catch (e) {}
  }

  // ---- nome do usuário: troca "Você" pelo nome real (config ou auto-detect) ----
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

  // ---- tick: lê o parser, upserta no core, renderiza, roda o canário ----
  function tick() {
    if (!capturing) return;

    // Guard 2: checagem barata de candidatos do caminho principal ANTES de chamar
    // o parser de verdade — se sumiram agora mas existiam há <2s, pula este tick.
    let mainPathNodeCount = 0;
    try { mainPathNodeCount = document.querySelectorAll('[jsname="dsyhDe"]').length; } catch (e) {}
    const now = Date.now();
    if (mainPathNodeCount > 0) {
      lastMainPathNodesSeenAt = now;
    } else if (lastMainPathNodesSeenAt && now - lastMainPathNodesSeenAt < TRANSIENT_GRACE_MS) {
      recordTick("skipped-transient", 0, []);
      return;
    }

    let region = null, rows = [];
    try { region = P.findRegion(); rows = P.parseRows(region); } catch (e) {}
    const mergeEvents = [];
    for (const row of rows) {
      store.upsert(row, { onChange: (turn, isNew, kind) => mergeEvents.push({ speaker: turn.speaker || "", kind: kind || (isNew ? "new" : "?") }) });
    }
    recordTick(P.getLastPath ? P.getLastPath() : "unknown", rows.length,
      rows.map((r) => ({ speaker: r.speaker || "", text: (r.text || "").slice(0, 40) })), mergeEvents);
    save();
    renderTranscript();
    updateBadge();
    runCanary(!!region, rows.length);
  }

  // ---- canário (ADR-1.1): região sumiu 15s OU região existe mas 0 linhas por 30s ----
  function runCanary(regionFound, rowCount) {
    const now = Date.now();
    if (!regionFound) {
      if (!regionMissingSince) regionMissingSince = now;
      emptyRowsSince = 0;
      if (now - regionMissingSince > 15000) setStatus("cc-off");
      return;
    }
    regionMissingSince = 0;
    if (rowCount === 0) {
      if (!emptyRowsSince) emptyRowsSince = now;
      if (now - emptyRowsSince > 30000) setStatus("parser-stale");
    } else {
      emptyRowsSince = 0;
      setStatus("ok");
    }
  }

  function start() {
    if (capturing) return;
    capturing = true;
    regionMissingSince = 0; emptyRowsSince = 0;
    if (!P.findRegion()) {
      setStatus("cc-trying");
      tryEnableCC((ok) => { attachObserver(); setStatus(ok ? "ok" : "cc-off"); });
    } else {
      attachObserver();
      setStatus("ok");
    }
    pollTimer = setInterval(tick, 700);
    renderControls();
  }
  function attachObserver() {
    const region = P.findRegion();
    if (region && !observer) {
      observer = new MutationObserver(() => tick());
      observer.observe(region, { childList: true, subtree: true, characterData: true });
    }
  }
  // auto-CC (ADR-6): tenta ligar a legenda sozinho ao iniciar, se ela não estiver visível
  function tryEnableCC(cb) {
    const btn = [...document.querySelectorAll("button[aria-label], [role=button][aria-label]")]
      .find((b) => CC_LABEL_RE.test(b.getAttribute("aria-label") || ""));
    if (!btn) { cb(false); return; }
    try { btn.click(); } catch (e) {}
    let tries = 0;
    const iv = setInterval(() => {
      tries++;
      if (P.findRegion()) { clearInterval(iv); cb(true); }
      else if (tries >= 15) { clearInterval(iv); cb(false); } // ~3s (15 * 200ms)
    }, 200);
  }
  function stop() {
    capturing = false;
    clearInterval(pollTimer); pollTimer = null;
    if (observer) { observer.disconnect(); observer = null; }
    regionMissingSince = 0; emptyRowsSince = 0;
    tick();
    setStatus("idle");
    renderControls();
  }
  function clearAll() {
    store.clear();
    renderedNodes = [];
    save(); renderTranscript(); updateBadge();
  }

  // ---- export: agora com timestamp [hh:mm:ss] relativo ao início (ADR-5 / HIGH-3) ----
  function asText() {
    return store.asText({ resolveSpeaker, withTimestamps: true });
  }

  // ============================ PAINEL LATERAL (ADR-7) ============================
  function buildPanel() {
    if (document.getElementById("arvex-panel")) return;
    const p = document.createElement("div");
    p.id = "arvex-panel";
    p.innerHTML =
      '<div id="arvex-head">' +
        '<span id="arvex-logo">ARVEX</span>' +
        '<span id="arvex-title">Meet Transcriber</span>' +
        '<button id="arvex-rec" class="arvex-icon" title="Iniciar/parar">●</button>' +
        '<button id="arvex-crm-icon" class="arvex-icon" title="Estado do envio ao CRM">☁</button>' +
        '<button id="arvex-gear" class="arvex-icon" title="Configurar">⚙</button>' +
        '<button id="arvex-min" class="arvex-icon" title="Recolher">–</button>' +
      '</div>' +
      '<div id="arvex-config" class="arvex-hidden">' +
        '<label>Seu nome</label><input id="cfg-name" placeholder="Ex: Vitor Simões" />' +
        '<label>E-mail (CRM)</label><input id="cfg-email" type="email" placeholder="voce@email.com" />' +
        '<label>Chave de envio (CRM)</label><input id="cfg-key" type="password" placeholder="x-arvex-key" />' +
        '<button id="cfg-close">Fechar</button>' +
      '</div>' +
      '<div id="arvex-status" class="arvex-hidden"></div>' +
      '<div id="arvex-tabs">' +
        '<button id="tab-transcript" class="active">Transcrição</button>' +
        '<button id="tab-notes">Notas</button>' +
      '</div>' +
      '<div id="arvex-list"></div>' +
      '<textarea id="arvex-notes-text" class="arvex-hidden" placeholder="Anote aqui — vai junto pro CRM"></textarea>' +
      '<div id="arvex-foot">' +
        '<div class="arvex-foot-row">' +
          '<button id="arvex-toggle"></button>' +
          '<span id="arvex-badge">0 linhas</span>' +
          '<button id="arvex-copy" title="Copiar">⧉</button>' +
          '<button id="arvex-menu-btn" title="Mais ações">⋯</button>' +
        '</div>' +
        '<div id="arvex-menu" class="arvex-hidden">' +
          '<button id="arvex-dl">⤓ Baixar .txt</button>' +
          '<button id="arvex-dbg">🐞 Diagnóstico</button>' +
          '<button id="arvex-clear">🗑 Limpar</button>' +
        '</div>' +
        '<div class="arvex-foot-row">' +
          '<input id="arvex-cliente" placeholder="Nome do cliente" />' +
          '<button id="arvex-crm" title="Criar reunião + análise no CRM">⬆ Enviar ao CRM</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(p);

    const tab = document.createElement("button");
    tab.id = "arvex-tab"; tab.textContent = "ARVEX ›"; tab.title = "Abrir transcrição";
    tab.style.display = "none";
    document.body.appendChild(tab);

    p.querySelector("#arvex-toggle").addEventListener("click", () => (capturing ? stop() : start()));
    p.querySelector("#arvex-rec").addEventListener("click", () => (capturing ? stop() : start()));
    p.querySelector("#arvex-copy").addEventListener("click", () =>
      navigator.clipboard.writeText(asText()).then(() => flash("Copiado!")));
    p.querySelector("#arvex-dl").addEventListener("click", download);
    p.querySelector("#arvex-clear").addEventListener("click", () => { if (confirmClear()) clearAll(); });
    p.querySelector("#arvex-crm").addEventListener("click", sendToCRM);
    p.querySelector("#arvex-dbg").addEventListener("click", copyDebug);
    p.querySelector("#arvex-menu-btn").addEventListener("click", () =>
      p.querySelector("#arvex-menu").classList.toggle("arvex-hidden"));
    p.querySelector("#arvex-min").addEventListener("click", () => {
      p.classList.add("hidden"); tab.style.display = "block";
    });
    tab.addEventListener("click", () => { p.classList.remove("hidden"); tab.style.display = "none"; });

    p.querySelector("#tab-transcript").addEventListener("click", () => switchTab("transcript"));
    p.querySelector("#tab-notes").addEventListener("click", () => switchTab("notes"));

    p.querySelector("#arvex-gear").addEventListener("click", () => openConfig());
    p.querySelector("#cfg-close").addEventListener("click", () => closeConfig());

    const notesEl = p.querySelector("#arvex-notes-text");
    let notesSaveTimer = null;
    notesEl.addEventListener("input", () => {
      clearTimeout(notesSaveTimer);
      notesSaveTimer = setTimeout(() => {
        try { chrome.storage.local.set({ [NOTES_KEY]: notesEl.value }); } catch (e) {}
      }, 400);
    });

    renderControls();
    renderTranscript();
    renderSentBadge();
  }

  function switchTab(name) {
    activeTab = name;
    const list = document.getElementById("arvex-list");
    const notes = document.getElementById("arvex-notes-text");
    const tt = document.getElementById("tab-transcript");
    const tn = document.getElementById("tab-notes");
    if (name === "transcript") {
      list.classList.remove("arvex-hidden"); notes.classList.add("arvex-hidden");
      tt.classList.add("active"); tn.classList.remove("active");
    } else {
      list.classList.add("arvex-hidden"); notes.classList.remove("arvex-hidden");
      tn.classList.add("active"); tt.classList.remove("active");
    }
  }

  function openConfig() {
    try {
      chrome.storage.local.get(["arvex_self_name", "arvex_closer_email", "arvex_ingest_key"], (r) => {
        document.getElementById("cfg-name").value = (r && r.arvex_self_name) || "";
        document.getElementById("cfg-email").value = (r && r.arvex_closer_email) || "";
        document.getElementById("cfg-key").value = (r && r.arvex_ingest_key) || "";
      });
    } catch (e) {}
    document.getElementById("arvex-config").classList.remove("arvex-hidden");
  }
  function closeConfig() {
    const name = document.getElementById("cfg-name").value.trim();
    const email = document.getElementById("cfg-email").value.trim();
    const key = document.getElementById("cfg-key").value.trim();
    try {
      chrome.storage.local.set({ arvex_self_name: name, arvex_closer_email: email, arvex_ingest_key: key });
    } catch (e) {}
    document.getElementById("arvex-config").classList.add("arvex-hidden");
  }

  // status badge (canário + auto-CC) — oculto quando tudo ok e sem nada a comunicar
  function setStatus(state) {
    statusState = state;
    const el = document.getElementById("arvex-status");
    if (!el) return;
    const MAP = {
      idle: null,
      ok: null,
      "cc-trying": "⏳ Ligando a legenda (CC)…",
      "cc-off": "⚠ Legenda (CC) não detectada — ligue manualmente",
      "parser-stale": "⚠ Sem captura há 30s — toque para copiar diagnóstico",
    };
    const msg = MAP[state];
    if (!msg) { el.classList.add("arvex-hidden"); el.textContent = ""; return; }
    el.textContent = msg;
    el.classList.remove("arvex-hidden");
    el.onclick = state === "parser-stale" ? copyDebug : null;
  }

  let clearArmed = false;
  function confirmClear() {
    if (clearArmed) { clearArmed = false; return true; }
    clearArmed = true; flash("Clique de novo pra limpar");
    setTimeout(() => (clearArmed = false), 2500);
    return false;
  }

  function renderControls() {
    const t = document.getElementById("arvex-toggle");
    const rec = document.getElementById("arvex-rec");
    if (!t) return;
    t.textContent = capturing ? "⏸ Parar" : "⏺ Transcrever";
    t.className = capturing ? "rec" : "";
    if (rec) rec.className = "arvex-icon" + (capturing ? " rec" : "");
    updateBadge();
  }
  function updateBadge() {
    const b = document.getElementById("arvex-badge");
    if (b) b.textContent = store.transcript.length + (store.transcript.length === 1 ? " linha" : " linhas");
  }
  function renderSentBadge() {
    const btn = document.getElementById("arvex-crm");
    if (!btn) return;
    if (sendInFlight) { btn.textContent = "Enviando…"; btn.disabled = true; return; }
    btn.disabled = false;
    if (sentAt) {
      const d = new Date(sentAt);
      const hhmm = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
      btn.textContent = "✓ Enviada às " + hhmm + " · Reenviar";
    } else {
      btn.textContent = "⬆ Enviar ao CRM";
    }
  }
  // Render INCREMENTAL (MEDIUM-3): antes reconstruía innerHTML da lista inteira a cada
  // tick (700ms) — em calls longas isso cresce O(n) por tick E destrói qualquer seleção
  // de texto que o usuário estivesse fazendo. Agora só cria/atualiza os nós que mudaram.
  function renderTranscript() {
    const list = document.getElementById("arvex-list");
    if (!list) return;
    if (!store.transcript.length) {
      renderedNodes = [];
      list.innerHTML =
        '<div id="arvex-empty">' +
          '<div class="arvex-empty-step">1. Ligue a legenda (CC) do Meet — ou deixe a ARVEX tentar sozinha</div>' +
          '<div class="arvex-empty-step">2. Clique em <b>⏺ Transcrever</b></div>' +
          '<div class="arvex-empty-step">3. Fale — o texto aparece aqui em tempo real</div>' +
        '</div>';
      return;
    }
    if (list.querySelector("#arvex-empty")) { list.innerHTML = ""; renderedNodes = []; }
    const near = list.scrollTop + list.clientHeight >= list.scrollHeight - 40;
    for (let i = 0; i < store.transcript.length; i++) {
      const turn = store.transcript[i];
      const sp = resolveSpeaker(turn.speaker);
      const existing = renderedNodes[i];
      if (existing) {
        if (existing.txEl.textContent !== turn.text) existing.txEl.textContent = turn.text;
        continue;
      }
      const prevSp = i > 0 ? resolveSpeaker(store.transcript[i - 1].speaker) : null;
      let groupEl = (i > 0 && sp === prevSp && renderedNodes[i - 1]) ? renderedNodes[i - 1].groupEl : null;
      if (!groupEl) {
        groupEl = document.createElement("div");
        groupEl.className = "arvex-group";
        if (sp) {
          const d = new Date(turn.at);
          const hhmm = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
          const spEl = document.createElement("div");
          spEl.className = "arvex-sp";
          spEl.textContent = sp + " ";
          const timeEl = document.createElement("span");
          timeEl.className = "arvex-time";
          timeEl.textContent = hhmm;
          spEl.appendChild(timeEl);
          groupEl.appendChild(spEl);
        }
        list.appendChild(groupEl);
      }
      const txEl = document.createElement("div");
      txEl.className = "arvex-tx";
      txEl.textContent = turn.text;
      groupEl.appendChild(txEl);
      renderedNodes[i] = { groupEl, txEl };
    }
    if (near) list.scrollTop = list.scrollHeight;
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

  // ADR-8: copia HTML da legenda + flight recorder juntos (diagnóstico real, não
  // adivinhado) — usar no MEIO e no FIM da call de teste (protocolo ADR-10).
  function copyDebug() {
    const t = document.querySelector('[jsname="dsyhDe"]');
    let region = t
      ? (t.closest(".a4cQT") || t.parentElement)
      : [...document.querySelectorAll('[role="region"][aria-label]')]
          .find((el) => /caption|legenda|subtitle/i.test(el.getAttribute("aria-label") || ""));
    const payload = JSON.stringify({
      html: region ? region.outerHTML.slice(0, 8000) : "(legenda não visível no momento)",
      recorder: recorder,
    }, null, 2);
    navigator.clipboard.writeText(payload)
      .then(() => flash("Diagnóstico copiado! Cole no chat"))
      .catch(() => flash("Erro ao copiar diagnóstico"));
  }

  // ---- enviar pro CRM: idempotency key (client_key) + retry c/ backoff + estado persistente ----
  // ⚠️ Dedup de verdade (upsert por client_key) depende da Edge Function ingest-meeting
  // aceitar/usar esse campo (ADR-4) — fora do alcance deste ambiente (repo arvex-crm não
  // acessível aqui). O que dá pra garantir client-side: não reenviar em duplo-clique
  // (botão desabilitado durante o envio) e reenviar automaticamente com backoff em falha.
  function sendToCRM() {
    if (!store.transcript.length) { flash("Nada pra enviar ainda"); return; }
    if (sendInFlight) return;
    chrome.storage.local.get(["arvex_closer_email", "arvex_ingest_key"], (r) => {
      const email = (r && r.arvex_closer_email) || "";
      const ingestKey = (r && r.arvex_ingest_key) || "";
      const clienteEl = document.getElementById("arvex-cliente");
      const cliente = clienteEl ? clienteEl.value.trim() : "";
      const notesEl = document.getElementById("arvex-notes-text");
      const notas = notesEl ? notesEl.value.trim() : "";
      const payload = JSON.stringify({
        transcript: asText(),
        closer_email: email,
        cliente: cliente,
        client_key: meetingId,
        notas: notas,
      });
      sendInFlight = true;
      renderSentBadge();
      flash("Enviando…");
      attemptSend(payload, ingestKey, 0);
    });
  }
  function attemptSend(payload, ingestKey, attempt) {
    const delays = [0, 2000, 6000];
    const headers = { "apikey": PUB_KEY, "Content-Type": "application/json" };
    if (ingestKey) headers["x-arvex-key"] = ingestKey;
    const ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timeoutId = ctrl ? setTimeout(() => ctrl.abort(), 15000) : null;
    fetch(INGEST_URL, { method: "POST", headers, body: payload, signal: ctrl ? ctrl.signal : undefined })
      .then((res) => { if (timeoutId) clearTimeout(timeoutId); return res.json(); })
      .then((d) => {
        sendInFlight = false;
        if (d && d.ok) {
          sentAt = Date.now();
          try { chrome.storage.local.set({ [SENT_KEY]: sentAt }); } catch (e) {}
          flash("Enviado! Análise rodando no CRM");
        } else {
          flash("Erro: " + ((d && d.error) || "falha"));
        }
        renderSentBadge();
      })
      .catch(() => {
        if (timeoutId) clearTimeout(timeoutId);
        if (attempt < delays.length - 1) {
          setTimeout(() => attemptSend(payload, ingestKey, attempt + 1), delays[attempt + 1]);
        } else {
          sendInFlight = false;
          flash("Erro de rede ao enviar (tentei " + delays.length + "x)");
          renderSentBadge();
        }
      });
  }

  // ---- mensagens do popup ----
  try {
    chrome.runtime.onMessage.addListener((msg, _s, reply) => {
      if (msg.cmd === "status") reply({ capturing, count: store.transcript.length, text: asText() });
      if (msg.cmd === "start") { start(); reply({ ok: true }); }
      if (msg.cmd === "stop") { stop(); reply({ ok: true }); }
      if (msg.cmd === "clear") { clearAll(); reply({ ok: true }); }
      return true;
    });
  } catch (e) {}

  load((notes) => {
    buildPanel();
    loadSelfName();
    const notesEl = document.getElementById("arvex-notes-text");
    if (notesEl) notesEl.value = notes || "";
    cleanupOldTranscripts();
  });

  // Hook de teste (regressão em tests/) — nunca ativo em produção real do Meet.
  if (typeof window !== "undefined" && window.__ARVEX_TEST__) {
    window.__arvexDebug = { store, renderTranscript, updateBadge, sendToCRM, tick, getRecorder: () => recorder, setCapturing: (v) => { capturing = v; } };
  }
})();
