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

Deno.serve(async function (req) {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);

  try {
    const body = await req.json().catch(function () { return {}; });
    const transcript = (body.transcript || "").toString().trim();
    const closer_email = (body.closer_email || "").toString().trim() || null;
    const cliente = (body.cliente || "").toString().trim() || null;
    const produto = (body.produto || "").toString().trim() || null;
    const resultado = ["ganhou", "perdeu", "aberto"].indexOf(body.resultado) >= 0 ? body.resultado : "aberto";
    if (!transcript) return json({ error: "transcript obrigatório" }, 400);

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
    };
    const ins = await admin.from("meetings").insert(rec).select("id").single();
    if (ins.error || !ins.data) return json({ error: "Falha ao criar reunião: " + (ins.error && ins.error.message) }, 500);
    const meeting_id = ins.data.id;

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
