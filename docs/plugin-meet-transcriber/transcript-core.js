/* ============================================================================
 * ARVEX Meet Transcriber — transcript-core.js
 * Núcleo PURO de merge/dedupe/export da transcrição — sem chrome.* e sem DOM
 * real (só usa o `el` como token de identidade via getAttribute/setAttribute,
 * que qualquer nó real ou fake com essa interface satisfaz). Compartilhado
 * entre content.js (produção) e tests/run.js (regressão): o teste exercita
 * este MESMO código, não uma reimplementação. Ver DEEP-ANALYSIS-FABLE.md ADR-2.
 * ========================================================================== */
(function (global) {
  "use strict";

  // ---- escolhe o melhor texto entre versões do MESMO bloco (legenda que cresce/rola) ----
  function bestText(oldT, newT) {
    if (!oldT) return newT;
    if (!newT || newT === oldT) return oldT;
    if (newT.startsWith(oldT)) return newT; // cresceu
    if (oldT.startsWith(newT)) return oldT; // encurtou (rolou) → mantém o maior
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

  function fmtHHMMSS(ms) {
    const s = Math.max(0, Math.floor(ms / 1000));
    const hh = String(Math.floor(s / 3600)).padStart(2, "0");
    const mm = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
    const ss = String(s % 60).padStart(2, "0");
    return hh + ":" + mm + ":" + ss;
  }

  // ---- store: estado da transcrição + upsert por identidade de bloco ----
  // Espelha 1:1 o que era `transcript`/`nodeToIdx`/`nodeSeq`/`upsertRow` no content.js.
  function createStore() {
    let transcript = [];
    let nodeToIdx = new Map();
    let nodeSeq = 0;

    // permite injetar `at` fixo em teste (determinismo); produção usa Date.now() real
    function upsert(row, opts) {
      const o = opts || {};
      const now = o.now || Date.now;
      const text = (row.text || "").trim();
      if (!text) return null;
      const el = row.el;
      let id = null;
      if (el && el.getAttribute) {
        id = el.getAttribute("data-arvex-id");
        if (!id) { id = "n" + (++nodeSeq); try { el.setAttribute("data-arvex-id", id); } catch (e) {} }
      } else if (row.id) {
        id = row.id; // fixtures de teste sem elemento real podem passar um id direto
      }
      if (id && nodeToIdx.has(id)) {
        const turn = transcript[nodeToIdx.get(id)];
        // Guard 1 (ADR-9, DEEP-ANALYSIS-FABLE.md §6.4): o Meet pode reciclar o MESMO nó
        // de DOM pra um falante diferente. Se o turno já tem um speaker e o novo row tem
        // OUTRO speaker (ambos não-vazios), NÃO faz merge — trata como turno novo e
        // remapeia o id daqui pra frente. Sem isso, a fala de um falante era absorvida
        // dentro do turno do outro (bug real encontrado na 1ª call ao vivo).
        const speakerChanged = !!(turn && turn.speaker && row.speaker && turn.speaker !== row.speaker);
        if (turn && !speakerChanged) {
          const merged = bestText(turn.text, text);
          if (merged !== turn.text) {
            let kind = "replaced";
            if (text.startsWith(turn.text)) kind = "grew";
            else if (turn.text.startsWith(text)) kind = "rolled";
            else if (merged !== text) kind = "merged-overlap";
            turn.text = merged; turn.at = now();
            if (o.onChange) o.onChange(turn, false, kind);
          }
          return turn;
        }
      }
      const row2 = { speaker: row.speaker || "", text, at: now() };
      transcript.push(row2);
      if (id) nodeToIdx.set(id, transcript.length - 1);
      if (o.onChange) o.onChange(row2, true, "new");
      return row2;
    }

    function clear() {
      transcript = []; nodeToIdx = new Map(); nodeSeq = 0;
    }

    function asText(opts) {
      const o = opts || {};
      const resolve = o.resolveSpeaker || ((s) => s);
      const withTimestamps = !!o.withTimestamps;
      const t0 = transcript.length ? transcript[0].at : Date.now();
      return transcript.map((t) => {
        const sp = resolve(t.speaker);
        const prefix = withTimestamps ? "[" + fmtHHMMSS(t.at - t0) + "] " : "";
        return prefix + (sp ? sp + ": " : "") + t.text;
      }).join("\n");
    }

    return {
      get transcript() { return transcript; },
      set transcript(v) { transcript = Array.isArray(v) ? v : []; },
      upsert,
      clear,
      asText,
    };
  }

  const api = { bestText, mergeRolling, fmtHHMMSS, createStore };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.ArvexTranscriptCore = api;
})(typeof window !== "undefined" ? window : globalThis);
