// evolution-proxy — ponte segura CRM ↔ Evolution API (WhatsApp)
// A chave do Evolution vive como SECRET aqui (nunca no front). Só usuário logado do CRM chama.
// Ações: qr (QR de conexão), status (estado da conexão), send (enviar mensagem — takeover/responder).
//
// Deploy:  supabase functions deploy evolution-proxy --project-ref <ref>
// Secrets: supabase secrets set EVOLUTION_API_URL=... EVOLUTION_API_KEY=... EVOLUTION_INSTANCE=arvex-agente-sdr
// import npm: (jsr pode dar BOOT_ERROR — padrão das outras functions do projeto)
import { createClient } from "npm:@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });

  try {
    // 1) autenticação — só usuário logado do CRM (JWT do Supabase) passa
    const jwt = (req.headers.get("Authorization") || "").replace("Bearer ", "").trim();
    if (!jwt) return json({ error: "sem_auth" }, 401);
    const sb = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_ANON_KEY")!,
    );
    const { data: { user }, error: authErr } = await sb.auth.getUser(jwt);
    if (authErr || !user) return json({ error: "nao_autorizado" }, 401);

    // 2) config do Evolution (secrets — nunca expostos ao front)
    const EVO_URL = (Deno.env.get("EVOLUTION_API_URL") || "").replace(/\/$/, "");
    const EVO_KEY = Deno.env.get("EVOLUTION_API_KEY") || "";
    const EVO_INST = Deno.env.get("EVOLUTION_INSTANCE") || "arvex-agente-sdr";
    if (!EVO_URL || !EVO_KEY) return json({ error: "evolution_nao_configurado" }, 500);
    const H = { "apikey": EVO_KEY, "Content-Type": "application/json" };

    const { action, number, text } = await req.json().catch(() => ({}));

    // 3a) QR de conexão — devolve o base64 pra desenhar no CRM
    if (action === "qr") {
      const r = await fetch(`${EVO_URL}/instance/connect/${EVO_INST}`, { headers: H });
      const d = await r.json().catch(() => ({}));
      // Evolution devolve {base64, code, pairingCode} se desconectado; {instance:{state}} se já ligado
      return json({
        base64: d.base64 || null,
        pairingCode: d.pairingCode || null,
        connected: !d.base64 && (d?.instance?.state === "open" || d?.state === "open"),
      });
    }

    // 3b) estado da conexão
    if (action === "status") {
      const r = await fetch(`${EVO_URL}/instance/connectionState/${EVO_INST}`, { headers: H });
      const d = await r.json().catch(() => ({}));
      const state = d?.instance?.state || d?.state || "unknown";
      return json({ state, connected: state === "open" });
    }

    // 3c) enviar mensagem (humano assume a conversa — takeover / responder pelo chat)
    if (action === "send") {
      if (!number || !text) return json({ error: "number_e_text_obrigatorios" }, 400);
      const r = await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
        method: "POST",
        headers: H,
        body: JSON.stringify({ number: String(number).replace(/\D/g, ""), text }),
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) return json({ ok: false, error: "evolution_falhou", detail: d }, 502);

      // registra no CRM como mensagem de 'humano' + pausa o agente pra esse lead (takeover)
      const service = createClient(
        Deno.env.get("SUPABASE_URL")!,
        Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
      );
      const tel = String(number).replace(/\D/g, "");
      await service.rpc("registrar_evento_lead", {
        p_tel: tel, p_nome: tel, p_texto: text, p_autor: "humano",
      });
      // pausa o agente (best-effort; a coluna pode ainda não existir — não quebra o envio)
      await service.from("leads").update({ agente_pausado: true }).eq("tel", tel).then(
        () => {}, () => {},
      );
      return json({ ok: true });
    }

    return json({ error: "action_invalida", validas: ["qr", "status", "send"] }, 400);
  } catch (e) {
    return json({ error: String((e as Error).message || e) }, 500);
  }
});
