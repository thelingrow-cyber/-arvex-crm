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
  // supabase-js manda authorization + apikey + x-client-info; "*" evita bloqueio no preflight
  "Access-Control-Allow-Headers": "*, authorization, apikey, content-type, x-client-info",
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

    // 3a2) desconectar (logout) — pra trocar de número
    if (action === "disconnect") {
      const r = await fetch(`${EVO_URL}/instance/logout/${EVO_INST}`, { method: "DELETE", headers: H });
      const d = await r.json().catch(() => ({}));
      return json({ ok: r.ok, detail: d });
    }

    // 3b) estado da conexão (+ qual número/dono está conectado — resolve "não atualiza" no front)
    if (action === "status") {
      const r = await fetch(`${EVO_URL}/instance/connectionState/${EVO_INST}`, { headers: H });
      const d = await r.json().catch(() => ({}));
      const state = d?.instance?.state || d?.state || "unknown";
      const connected = state === "open";
      // número só faz sentido conectado; best-effort via fetchInstances (não quebra o status se falhar)
      let number: string | null = null;
      let profileName: string | null = null;
      if (connected) {
        try {
          const fr = await fetch(`${EVO_URL}/instance/fetchInstances?instanceName=${EVO_INST}`, { headers: H });
          const fd = await fr.json().catch(() => null);
          const inst = Array.isArray(fd) ? fd[0] : (fd?.instance || fd);
          const owner = inst?.ownerJid || inst?.owner || inst?.instance?.ownerJid || inst?.instance?.owner || null;
          number = owner ? String(owner).split("@")[0].split(":")[0] : null;
          profileName = inst?.profileName || inst?.instance?.profileName || null;
        } catch { /* best-effort */ }
      }
      return json({ state, connected, number, profileName });
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
      // "por" = quem atendeu, vindo do login validado (não forjável pelo front)
      const atendente = (user.email || "").split("@")[0] || "humano";

      // Fonte de verdade da conversa = agente_sdr_historico (memória da Carol).
      // Grava o turno do operador como mensagem 'ai' marcada com operator: assim
      // aparece no chat do CRM como "Você" E a Carol, ao retomar, não repete nem
      // lê como fala do cliente (session_id = telefone, igual ao n8n).
      await service.from("agente_sdr_historico").insert({
        session_id: tel,
        message: {
          type: "ai",
          content: text,
          tool_calls: [],
          additional_kwargs: { operator: atendente, ts: Date.now() },
          response_metadata: {},
          invalid_tool_calls: [],
        },
      }).then(() => {}, () => {});

      // continuidade do lead (status/nota) — best-effort, não é mais a fonte do chat
      await service.rpc("registrar_evento_lead", {
        p_tel: tel, p_nome: tel, p_texto: text, p_autor: "humano", p_por: atendente,
      }).then(() => {}, () => {});
      // pausa o agente (best-effort; a coluna pode ainda não existir — não quebra o envio)
      await service.from("leads").update({ agente_pausado: true }).eq("tel", tel).then(
        () => {}, () => {},
      );
      return json({ ok: true });
    }

    // 3d) sincroniza mensagens que SAÍRAM do celular (fromMe) → historico
    // As da Carol também são fromMe; dedup por balão já gravado (type:ai) separa
    // "Carol" de "humano digitou no celular". wa_id evita re-inserir a mesma msg.
    if (action === "sync_out") {
      const SYNC_APPLY = false;  // dry-run: só diagnostica, NÃO escreve no historico (fase de verificação)
      const service = createClient(
        Deno.env.get("SUPABASE_URL")!,
        Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
      );
      const r = await fetch(`${EVO_URL}/chat/findMessages/${EVO_INST}`, {
        method: "POST",
        headers: H,
        body: JSON.stringify({ where: {}, page: 1, offset: 100 }),
      });
      const d = await r.json().catch(() => ({}));
      // normaliza vários formatos possíveis de resposta do Evolution v2
      const records = d?.messages?.records || d?.records ||
        (Array.isArray(d?.messages) ? d.messages : (Array.isArray(d) ? d : []));
      const out = (records as any[]).filter((m) => m?.key?.fromMe === true);

      // balões já gravados (type:ai) por sessão → pra pular o que é da Carol
      const { data: hist } = await service.from("agente_sdr_historico").select("session_id, message");
      const baloesPorSessao: Record<string, Set<string>> = {};
      const waIds = new Set<string>();
      for (const row of (hist || []) as any[]) {
        const sid = row.session_id;
        const m = row.message || {};
        const wa = m?.additional_kwargs?.wa_id; if (wa) waIds.add(wa);
        if (m.type === "ai") {
          const set = baloesPorSessao[sid] || (baloesPorSessao[sid] = new Set());
          String(m.content || "").split("||").map((s: string) => s.trim()).filter(Boolean).forEach((b: string) => set.add(b));
        }
      }
      const textoDe = (msg: any) => msg?.conversation || msg?.extendedTextMessage?.text
        || (msg?.imageMessage ? (msg.imageMessage.caption ? "📷 " + msg.imageMessage.caption : "📷 imagem") : "")
        || (msg?.audioMessage ? "🎤 áudio" : "") || (msg?.videoMessage ? "🎬 vídeo" : "")
        || (msg?.documentMessage ? "📎 documento" : "") || "[mídia]";

      const candidatos: any[] = [];
      for (const m of out) {
        const jid = String(m?.key?.remoteJid || "");
        if (jid.endsWith("@g.us")) continue;
        const sid = jid.split("@")[0].split(":")[0]; if (!sid) continue;
        const waId = m?.key?.id; if (waId && waIds.has(waId)) continue;         // já sincronizada
        const texto = textoDe(m?.message || {});
        if ((baloesPorSessao[sid] || new Set()).has(texto)) continue;           // é balão da Carol → pula
        candidatos.push({ sid, waId, texto, ts: m?.messageTimestamp ? Number(m.messageTimestamp) * 1000 : Date.now() });
      }

      let inseridas = 0;
      if (SYNC_APPLY) {
        for (const c of candidatos) {
          await service.from("agente_sdr_historico").insert({
            session_id: c.sid,
            message: { type: "ai", content: c.texto, tool_calls: [], additional_kwargs: { operator: "Equipe (WhatsApp)", wa_id: c.waId, ts: c.ts }, response_metadata: {}, invalid_tool_calls: [] },
          }).then(() => { inseridas++; }, () => {});
        }
      }

      // diagnóstico (leio via DB direto pra validar formato/lógica antes de ligar o insert)
      await service.from("_evo_sync_debug").insert({
        info: { apply: SYNC_APPLY, http: r.status, ok: r.ok, keys: Object.keys(d || {}), total: (records as any[]).length, fromMe: out.length, candidatos: candidatos.length, amostra_record: (records as any[])[0] || null, amostra_candidato: candidatos[0] || null },
      }).then(() => {}, () => {});

      return json({ ok: true, apply: SYNC_APPLY, total: (records as any[]).length, saidas: out.length, candidatos: candidatos.length, inseridas });
    }

    return json({ error: "action_invalida", validas: ["qr", "status", "send", "disconnect", "sync_out"] }, 400);
  } catch (e) {
    return json({ error: String((e as Error).message || e) }, 500);
  }
});
