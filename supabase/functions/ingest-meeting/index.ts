// ============================================================================
// Sales Coach — Edge Function: ingest-meeting
// Recebe uma transcrição (da extensão do Meet), cria a reunião no CRM e
// dispara a análise (analyze-meeting) automaticamente.
// import npm: (jsr dá BOOT_ERROR). verify_jwt=false (chamada da extensão).
// ============================================================================
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(body, status) {
  return new Response(JSON.stringify(body), { status: status || 200, headers: { ...cors, "Content-Type": "application/json" } });
}

// comparação em tempo constante (evita vazar por timing quanto do secret bateu) — ADR-3
function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length || a.length === 0) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

const MAX_TRANSCRIPT_BYTES = 200 * 1024; // ADR-3: fecha o vetor de "queimar créditos Anthropic" com payload gigante

Deno.serve(async function (req) {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const INGEST_KEY = Deno.env.get("ARVEX_INGEST_KEY");
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);

  // shared-secret obrigatório (ADR-3, DEEP-ANALYSIS-FABLE.md CRITICAL-1): a URL desta
  // function está embutida no content-script da extensão (pública por design), então
  // sem isso qualquer um cria reuniões e dispara analyze-meeting em loop, queimando
  // créditos Anthropic. ARVEX_INGEST_KEY é setado via `supabase secrets set`.
  if (!INGEST_KEY || !safeEqual(req.headers.get("x-arvex-key") || "", INGEST_KEY)) {
    return json({ error: "não autorizado" }, 401);
  }

  try {
    const body = await req.json().catch(function () { return {}; });
    const transcript = (body.transcript || "").toString().trim();
    const closer_email = (body.closer_email || "").toString().trim() || null;
    const cliente = (body.cliente || "").toString().trim() || null;
    const produto = (body.produto || "").toString().trim() || null;
    const resultado = ["ganhou", "perdeu", "aberto"].indexOf(body.resultado) >= 0 ? body.resultado : "aberto";
    const client_key = (body.client_key || "").toString().trim() || null;
    const notas = (body.notas || "").toString().trim() || null;
    if (!transcript) return json({ error: "transcript obrigatório" }, 400);
    if (new TextEncoder().encode(transcript).length > MAX_TRANSCRIPT_BYTES) {
      return json({ error: "transcript excede o limite de 200KB" }, 413);
    }

    // resolve closer_id pelo e-mail (profiles.name = email no CRM) — opcional
    let closer_id = null;
    if (closer_email) {
      const p = await admin.from("profiles").select("id").eq("name", closer_email).limit(1).maybeSingle();
      if (p && p.data && p.data.id) closer_id = p.data.id;
    }

    const rec = {
      transcript: transcript,
      cliente_nome: cliente,
      closer_nome: closer_email,
      closer_id: closer_id,
      produto: produto,
      resultado: resultado,
      data_reuniao: new Date().toISOString().slice(0, 10),
      status: "pending",
      client_key: client_key,
      notas: notas,
    };

    // com client_key: upsert (ADR-4 — duplo-clique/retry atualizam a MESMA reunião
    // em vez de duplicar). Sem client_key (chamadas antigas/manuais): insert direto.
    let meeting_id;
    if (client_key) {
      const up = await admin.from("meetings").upsert(rec, { onConflict: "client_key" }).select("id").single();
      if (up.error || !up.data) return json({ error: "Falha ao criar/atualizar reunião: " + (up.error && up.error.message) }, 500);
      meeting_id = up.data.id;
    } else {
      const ins = await admin.from("meetings").insert(rec).select("id").single();
      if (ins.error || !ins.data) return json({ error: "Falha ao criar reunião: " + (ins.error && ins.error.message) }, 500);
      meeting_id = ins.data.id;
    }

    // dispara a análise (não bloqueia a resposta se demorar)
    try {
      await fetch(SUPABASE_URL + "/functions/v1/analyze-meeting", {
        method: "POST",
        headers: { "apikey": SERVICE_KEY, "Authorization": "Bearer " + SERVICE_KEY, "Content-Type": "application/json" },
        body: JSON.stringify({ meeting_id: meeting_id }),
      });
    } catch (_) { /* a análise pode ser re-disparada depois; reunião já existe */ }

    return json({ ok: true, meeting_id: meeting_id });
  } catch (e) {
    const msg = (e && e.message) ? e.message : String(e);
    return json({ ok: false, error: msg }, 500);
  }
});
