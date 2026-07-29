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
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};
function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      ...CORS,
      "Content-Type": "application/json"
    }
  });
}
Deno.serve(async (req)=>{
  if (req.method === "OPTIONS") return new Response("ok", {
    headers: CORS
  });
  try {
    // 1) autenticação — só usuário logado do CRM (JWT do Supabase) passa
    const jwt = (req.headers.get("Authorization") || "").replace("Bearer ", "").trim();
    if (!jwt) return json({
      error: "sem_auth"
    }, 401);
    const sb = createClient(Deno.env.get("SUPABASE_URL"), Deno.env.get("SUPABASE_ANON_KEY"));
    const { data: { user }, error: authErr } = await sb.auth.getUser(jwt);
    if (authErr || !user) return json({
      error: "nao_autorizado"
    }, 401);
    // 2) config do Evolution (secrets — nunca expostos ao front)
    const EVO_URL = (Deno.env.get("EVOLUTION_API_URL") || "").replace(/\/$/, "");
    const EVO_KEY = Deno.env.get("EVOLUTION_API_KEY") || "";
    const EVO_INST = Deno.env.get("EVOLUTION_INSTANCE") || "arvex-agente-sdr";
    if (!EVO_URL || !EVO_KEY) return json({
      error: "evolution_nao_configurado"
    }, 500);
    const H = {
      "apikey": EVO_KEY,
      "Content-Type": "application/json"
    };
    const { action, number, text } = await req.json().catch(()=>({}));
    // 3a) QR de conexão — devolve o base64 pra desenhar no CRM
    if (action === "qr") {
      const r = await fetch(`${EVO_URL}/instance/connect/${EVO_INST}`, {
        headers: H
      });
      const d = await r.json().catch(()=>({}));
      // Evolution devolve {base64, code, pairingCode} se desconectado; {instance:{state}} se já ligado
      return json({
        base64: d.base64 || null,
        pairingCode: d.pairingCode || null,
        connected: !d.base64 && (d?.instance?.state === "open" || d?.state === "open")
      });
    }
    // 3a2) desconectar (logout) — pra trocar de número
    if (action === "disconnect") {
      const r = await fetch(`${EVO_URL}/instance/logout/${EVO_INST}`, {
        method: "DELETE",
        headers: H
      });
      const d = await r.json().catch(()=>({}));
      return json({
        ok: r.ok,
        detail: d
      });
    }
    // 3b) estado da conexão (+ qual número/dono está conectado — resolve "não atualiza" no front)
    if (action === "status") {
      const r = await fetch(`${EVO_URL}/instance/connectionState/${EVO_INST}`, {
        headers: H
      });
      const d = await r.json().catch(()=>({}));
      const state = d?.instance?.state || d?.state || "unknown";
      const connected = state === "open";
      // número só faz sentido conectado; best-effort via fetchInstances (não quebra o status se falhar)
      let number = null;
      let profileName = null;
      if (connected) {
        try {
          const fr = await fetch(`${EVO_URL}/instance/fetchInstances?instanceName=${EVO_INST}`, {
            headers: H
          });
          const fd = await fr.json().catch(()=>null);
          const inst = Array.isArray(fd) ? fd[0] : fd?.instance || fd;
          const owner = inst?.ownerJid || inst?.owner || inst?.instance?.ownerJid || inst?.instance?.owner || null;
          number = owner ? String(owner).split("@")[0].split(":")[0] : null;
          profileName = inst?.profileName || inst?.instance?.profileName || null;
        } catch  {}
      }
      return json({
        state,
        connected,
        number,
        profileName
      });
    }
    // 3c) enviar mensagem (humano assume a conversa — takeover / responder pelo chat)
    if (action === "send") {
      if (!number || !text) return json({
        error: "number_e_text_obrigatorios"
      }, 400);
      const r = await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
        method: "POST",
        headers: H,
        body: JSON.stringify({
          number: String(number).replace(/\D/g, ""),
          text
        })
      });
      const d = await r.json().catch(()=>({}));
      if (!r.ok) return json({
        ok: false,
        error: "evolution_falhou",
        detail: d
      }, 502);
      // registra no CRM como mensagem de 'humano' + pausa o agente pra esse lead (takeover)
      const service = createClient(Deno.env.get("SUPABASE_URL"), Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"));
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
          additional_kwargs: {
            operator: atendente,
            ts: Date.now()
          },
          response_metadata: {},
          invalid_tool_calls: []
        }
      }).then(()=>{}, ()=>{});
      // continuidade do lead (status/nota) — best-effort, não é mais a fonte do chat
      await service.rpc("registrar_evento_lead", {
        p_tel: tel,
        p_nome: tel,
        p_texto: text,
        p_autor: "humano",
        p_por: atendente
      }).then(()=>{}, ()=>{});
      // pausa o agente (best-effort; a coluna pode ainda não existir — não quebra o envio)
      await service.from("leads").update({
        agente_pausado: true
      }).eq("tel", tel).then(()=>{}, ()=>{});
      return json({
        ok: true
      });
    }
    // 3d) sincroniza a conversa REAL do WhatsApp → agente_sdr_historico
    //
    // Antes só trazia as saídas (fromMe) e ainda por cima em dry-run, então o
    // inbox do CRM ficava vazio: a SDR mandava mensagem pelo celular e não
    // aparecia lugar nenhum, e o que o cliente respondia dependia do n8n (que
    // não está gravando). Agora puxa OS DOIS SENTIDOS e grava de verdade:
    //   fromMe=true  → type "ai"    (nós: Carol ou pessoa digitando no celular)
    //   fromMe=false → type "human" (o cliente)
    // Isto torna o Evolution a fonte de verdade da conversa, sem depender do n8n.
    //
    // Dedupe em 3 camadas, pra não duplicar no polling de 25s:
    //   1. wa_id  — id da mensagem no WhatsApp: a prova mais forte, cobre tudo
    //               que já entrou por esta rota.
    //   2. balões type "ai" já gravados — o que a Carol/o operador mandou pelo
    //               CRM chega de volta como fromMe; compara o texto pra não
    //               gravar a mesma fala duas vezes.
    //   3. textos type "human" já gravados — mesma ideia para a entrada, cobrindo
    //               o que o n8n porventura tenha gravado (ele não grava wa_id).
    if (action === "sync_out") {
      // DESLIGADO 2026-07-29: ligar isto despejou a caixa INTEIRA do WhatsApp no
      // inbox (conversas pessoais do número, contatos que nada têm a ver com a
      // operação). findMessages com where:{} traz tudo — falta um critério de
      // quais conversas pertencem ao atendimento antes de gravar qualquer coisa.
      const SYNC_APPLY = false;
      const service = createClient(Deno.env.get("SUPABASE_URL"), Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"));
      const r = await fetch(`${EVO_URL}/chat/findMessages/${EVO_INST}`, {
        method: "POST",
        headers: H,
        body: JSON.stringify({
          where: {},
          page: 1,
          offset: 300
        })
      });
      const d = await r.json().catch(()=>({}));
      // normaliza vários formatos possíveis de resposta do Evolution v2
      const records = d?.messages?.records || d?.records || (Array.isArray(d?.messages) ? d.messages : Array.isArray(d) ? d : []);
      const { data: hist } = await service.from("agente_sdr_historico").select("session_id, message");
      const baloesAi = {};      // sessão → Set de balões já gravados como "ai"
      const textosHuman = {};   // sessão → Set de textos já gravados como "human"
      const waIds = new Set();
      for (const row of hist || []){
        const sid = row.session_id;
        const m = row.message || {};
        const wa = m?.additional_kwargs?.wa_id;
        if (wa) waIds.add(wa);
        if (m.type === "ai") {
          const set = baloesAi[sid] || (baloesAi[sid] = new Set());
          String(m.content || "").split("||").map((s)=>s.trim()).filter(Boolean).forEach((b)=>set.add(b));
        } else if (m.type === "human") {
          const set = textosHuman[sid] || (textosHuman[sid] = new Set());
          String(m.content || "").trim() && set.add(String(m.content).trim());
        }
      }
      const textoDe = (msg)=>msg?.conversation || msg?.extendedTextMessage?.text || (msg?.imageMessage ? msg.imageMessage.caption ? "📷 " + msg.imageMessage.caption : "📷 imagem" : "") || (msg?.audioMessage ? "🎤 áudio" : "") || (msg?.videoMessage ? "🎬 vídeo" : "") || (msg?.documentMessage ? "📎 documento" : "") || "";
      const candidatos = [];
      let entradas = 0, saidas = 0;
      for (const m of records){
        const keyO = m?.key || {};
        const jid = String(keyO.remoteJid || "");
        if (jid.endsWith("@g.us")) continue;            // grupo
        if (jid.startsWith("status@")) continue;        // status/stories
        // WhatsApp @lid: o telefone real vem em remoteJidAlt (…@s.whatsapp.net)
        const jidPhone = String(keyO.remoteJidAlt || keyO.remoteJid || "");
        const sid = jidPhone.split("@")[0].split(":")[0].replace(/\D/g, "");
        if (!sid) continue;
        const waId = keyO.id;
        if (waId && waIds.has(waId)) continue;          // já sincronizada
        const texto = textoDe(m?.message || {});
        if (!texto) continue;                           // sem conteúdo legível: ignora
        const saida = keyO.fromMe === true;
        if (saida) {
          if ((baloesAi[sid] || new Set()).has(texto)) continue;      // já é balão nosso
          saidas++;
        } else {
          if ((textosHuman[sid] || new Set()).has(texto)) continue;   // entrada já gravada
          entradas++;
        }
        candidatos.push({
          sid,
          waId,
          texto,
          saida,
          ts: m?.messageTimestamp ? Number(m.messageTimestamp) * 1000 : Date.now()
        });
      }
      // ordem cronológica: o CRM ordena a conversa pelo id serial da tabela, então
      // inserir fora de ordem embaralharia os balões na tela
      candidatos.sort((a, b)=>a.ts - b.ts);
      let inseridas = 0;
      if (SYNC_APPLY) {
        for (const c of candidatos){
          const message = c.saida ? {
            type: "ai",
            content: c.texto,
            tool_calls: [],
            additional_kwargs: {
              operator: "Equipe (WhatsApp)",
              wa_id: c.waId,
              ts: c.ts
            },
            response_metadata: {},
            invalid_tool_calls: []
          } : {
            type: "human",
            content: c.texto,
            additional_kwargs: {
              wa_id: c.waId,
              ts: c.ts
            },
            response_metadata: {}
          };
          const ins = await service.from("agente_sdr_historico").insert({
            session_id: c.sid,
            message
          });
          if (!ins.error) inseridas++;
        }
      }
      await service.from("_evo_sync_debug").insert({
        info: {
          apply: SYNC_APPLY,
          http: r.status,
          ok: r.ok,
          total: records.length,
          entradas,
          saidas,
          candidatos: candidatos.length,
          inseridas,
          amostra_candidatos: candidatos.slice(0, 8)
        }
      }).then(()=>{}, ()=>{});
      return json({
        ok: true,
        apply: SYNC_APPLY,
        total: records.length,
        entradas,
        saidas,
        candidatos: candidatos.length,
        inseridas
      });
    }
    return json({
      error: "action_invalida",
      validas: [
        "qr",
        "status",
        "send",
        "disconnect",
        "sync_out"
      ]
    }, 400);
  } catch (e) {
    return json({
      error: String(e.message || e)
    }, 500);
  }
});
