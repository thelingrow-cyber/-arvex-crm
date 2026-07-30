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

    // Diagnóstico da ponte: grava em _evo_sync_debug o que o Evolution respondeu.
    // Sem isto, quando o QR "não vai" não sobra evidência nenhuma — o front só
    // mostra "Falha ao gerar QR" e o motivo real (estado da instância, HTTP,
    // mensagem de erro do Evolution) se perde. base64 é grande: guarda só o
    // tamanho, nunca o conteúdo.
    const logEvo = async (acao, r, d, extra = null)=>{
      try {
        const service = createClient(Deno.env.get("SUPABASE_URL"), Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"));
        const resumo = {};
        for (const k of Object.keys(d || {})){
          const v = d[k];
          resumo[k] = (k === "base64" || k === "qrcode") ? `<${String(v || "").length} chars>` : (typeof v === "object" ? v : String(v).slice(0, 300));
        }
        await service.from("_evo_sync_debug").insert({
          info: { acao, http: r?.status ?? null, ok: r?.ok ?? null, instancia: EVO_INST, resposta: resumo, ...(extra || {}) }
        });
      } catch  {}
    };

    // 3a) QR de conexão — devolve o base64 pra desenhar no CRM
    if (action === "qr") {
      const r = await fetch(`${EVO_URL}/instance/connect/${EVO_INST}`, {
        headers: H
      });
      const d = await r.json().catch(()=>({}));
      await logEvo("qr", r, d, { tem_base64: !!d.base64 });
      // Evolution devolve {base64, code, pairingCode} se desconectado; {instance:{state}} se já ligado
      return json({
        base64: d.base64 || null,
        pairingCode: d.pairingCode || null,
        connected: !d.base64 && (d?.instance?.state === "open" || d?.state === "open"),
        // repassa o erro do Evolution pro front em vez de virar só "QR não retornado"
        evo_error: (!d.base64 && !r.ok) ? (d?.message || d?.error || `HTTP ${r.status}`) : null
      });
    }
    // 3a2) desconectar (logout) — pra trocar de número
    if (action === "disconnect") {
      const r = await fetch(`${EVO_URL}/instance/logout/${EVO_INST}`, {
        method: "DELETE",
        headers: H
      });
      const d = await r.json().catch(()=>({}));
      await logEvo("disconnect", r, d);
      return json({
        ok: r.ok,
        detail: d
      });
    }
    // 3a4) mídia de uma mensagem (áudio/imagem/vídeo/documento) em base64.
    // Buscada ON-DEMAND pelo wa_id: guardar o arquivo no histórico inflaria a
    // tabela sem necessidade, já que o Evolution mantém a mídia.
    if (action === "media") {
      const waId = (text || number || "").toString().trim();   // reaproveita o payload existente
      if (!waId) return json({ error: "wa_id obrigatorio" }, 400);

      // 1) o Evolution precisa do OBJETO da mensagem, não só do id: ele lê
      // message.ephemeralMessage/audioMessage pra saber como baixar e
      // descriptografar. Mandar {key:{id}} dava 400 "Cannot read properties of
      // null (reading 'ephemeralMessage')". Então primeiro recupera a mensagem.
      const achar = async (where, offset)=>{
        const rf = await fetch(`${EVO_URL}/chat/findMessages/${EVO_INST}`, {
          method: "POST",
          headers: H,
          body: JSON.stringify({ where, page: 1, offset })
        });
        const df = await rf.json().catch(()=>({}));
        const recs = df?.messages?.records || df?.records || (Array.isArray(df?.messages) ? df.messages : Array.isArray(df) ? df : []);
        return Array.isArray(recs) ? recs : [];
      };
      // tenta filtrado; se o Evolution ignorar o where, varre uma página e acha pelo id
      let recs = await achar({ key: { id: waId } }, 5);
      let msg = recs.find((m)=>m?.key?.id === waId);
      if (!msg) {
        recs = await achar({}, 300);
        msg = recs.find((m)=>m?.key?.id === waId);
      }
      if (!msg) {
        await logEvo("media", { status: 404, ok: false }, {}, { wa_id: waId, motivo: "mensagem_nao_encontrada" });
        return json({ error: "mensagem não encontrada no Evolution" }, 404);
      }

      // 2) agora sim: pede o base64 passando a mensagem completa
      const r = await fetch(`${EVO_URL}/chat/getBase64FromMediaMessage/${EVO_INST}`, {
        method: "POST",
        headers: H,
        body: JSON.stringify({ message: msg, convertToMp4: false })
      });
      const d = await r.json().catch(()=>({}));
      if (!r.ok) {
        await logEvo("media", r, d, { wa_id: waId });
        return json({ error: d?.response?.message?.[0] || d?.message || d?.error || `HTTP ${r.status}` }, 502);
      }
      return json({
        ok: true,
        base64: d?.base64 || d?.media || null,
        mimetype: d?.mimetype || d?.mimeType || null
      });
    }
    // 3a3) diagnóstico completo da instância (pra descobrir por que o QR não vai)
    if (action === "diag") {
      const out = {};
      for (const [nome, url, met] of [
        ["connectionState", `${EVO_URL}/instance/connectionState/${EVO_INST}`, "GET"],
        ["fetchInstances", `${EVO_URL}/instance/fetchInstances?instanceName=${EVO_INST}`, "GET"]
      ]){
        try {
          const rr = await fetch(url, { method: met, headers: H });
          const dd = await rr.json().catch(()=>({}));
          out[nome] = { http: rr.status, ok: rr.ok, body: dd };
        } catch (err) {
          out[nome] = { erro: String(err?.message || err) };
        }
      }
      await logEvo("diag", { status: 200, ok: true }, {}, { diag: out });
      return json({ ok: true, instancia: EVO_INST, diag: out });
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
      // grava o wa_id devolvido pelo Evolution: é o que faz o sync reconhecer
      // esta mensagem quando ela voltar como fromMe, em vez de duplicar
      const waIdEnviada = d?.key?.id || null;
      await service.from("agente_sdr_historico").insert({
        session_id: tel,
        wa_id: waIdEnviada,
        message: {
          type: "ai",
          content: text,
          tool_calls: [],
          additional_kwargs: {
            operator: atendente,
            wa_id: waIdEnviada,
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
    // ESCOPO (a regra que faltava e causou o incidente das 76.145 linhas):
    // findMessages traz TODAS as conversas do número, inclusive as pessoais.
    // Entra no CRM apenas a conversa que:
    //   (a) for com um telefone que JÁ é lead no banco — inclusive o histórico
    //       antigo dela; OU
    //   (b) começar depois do marco evo_sync_state.desde — conversa nova, tanto
    //       iniciada pela equipe no celular quanto pela Carol.
    // Conversa antiga com quem não é lead fica de fora. Números em
    // evo_sync_state.ignorados nunca entram.
    //
    // ANTI-DUPLICAÇÃO: agora é o BANCO que garante (índice único em wa_id) —
    // não mais um Set em memória alimentado por um .select() que o PostgREST
    // truncava em 1000 linhas, que foi exatamente o que estourou a tabela.
    if (action === "sync_out") {
      // LIGADO 2026-07-29 depois do dry-run confirmar o escopo: 14 conversas
      // dentro (todas de leads), 4 fora, 105 candidatos — e não mais a caixa
      // inteira. A duplicação agora é barrada pelo índice único em wa_id.
      const SYNC_APPLY = true;
      const service = createClient(Deno.env.get("SUPABASE_URL"), Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"));

      // marco temporal + lista de ignorados
      const stR = await service.from("evo_sync_state").select("desde, ignorados").eq("id", 1).maybeSingle();
      const desdeMs = stR?.data?.desde ? new Date(stR.data.desde).getTime() : Date.now();
      const ignorados = new Set((stR?.data?.ignorados || []).map((t)=>String(t).replace(/\D/g, "")));

      // telefones que já são lead. O CRM guarda em formatos variados, então
      // normaliza e indexa com e sem o DDI 55 pra casar dos dois jeitos.
      const semDdi = (s)=>String(s || "").replace(/\D/g, "").replace(/^55/, "");
      const ldR = await service.from("leads").select("tel").limit(5000);
      const leadTels = new Set();
      for (const l of ldR.data || []){
        const d = semDdi(l.tel);
        if (d) leadTels.add(d);
      }
      const ehLead = (sid)=>leadTels.has(semDdi(sid));
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
      // Guard secundário só para o que NÃO tem wa_id (mensagens gravadas pelo n8n
      // ou pelo CRM antes deste deploy). O limite é explícito: sem ele o PostgREST
      // corta em 1000 silenciosamente — a causa raiz do incidente.
      const { data: hist } = await service.from("agente_sdr_historico").select("session_id, message").is("wa_id", null).limit(5000);
      const baloesAi = {};      // sessão → Set de balões já gravados como "ai"
      const textosHuman = {};   // sessão → Set de textos já gravados como "human"
      for (const row of hist || []){
        const sid = row.session_id;
        const m = row.message || {};
        if (m.type === "ai") {
          const set = baloesAi[sid] || (baloesAi[sid] = new Set());
          String(m.content || "").split("||").map((s)=>s.trim()).filter(Boolean).forEach((b)=>set.add(b));
        } else if (m.type === "human") {
          const set = textosHuman[sid] || (textosHuman[sid] = new Set());
          String(m.content || "").trim() && set.add(String(m.content).trim());
        }
      }
      const textoDe = (msg)=>msg?.conversation || msg?.extendedTextMessage?.text || (msg?.imageMessage ? msg.imageMessage.caption ? "📷 " + msg.imageMessage.caption : "📷 imagem" : "") || (msg?.audioMessage ? "🎤 áudio" : "") || (msg?.videoMessage ? "🎬 vídeo" : "") || (msg?.documentMessage ? "📎 documento" : "") || "";
      // tipo de mídia guardado à parte: é o que permite ao CRM oferecer o player
      // (o texto "🎤 áudio" era um beco sem saída — dizia que existia e não dava
      // como ouvir). O arquivo em si é buscado on-demand pela action "media".
      const midiaDe = (msg)=>msg?.audioMessage ? "audio" : msg?.imageMessage ? "image" : msg?.videoMessage ? "video" : msg?.documentMessage ? "document" : null;
      const candidatos = [];
      let entradas = 0, saidas = 0, foraEscopo = 0, ignoradas = 0;
      const forasAmostra = new Set();   // quem ficou de fora, pra conferir a regra
      const dentroPorLead = new Set(), dentroPorNova = new Set();
      for (const m of records){
        const keyO = m?.key || {};
        const jid = String(keyO.remoteJid || "");
        if (jid.endsWith("@g.us")) continue;            // grupo
        if (jid.startsWith("status@")) continue;        // status/stories
        // WhatsApp @lid: o telefone real vem em remoteJidAlt (…@s.whatsapp.net)
        const jidPhone = String(keyO.remoteJidAlt || keyO.remoteJid || "");
        const sid = jidPhone.split("@")[0].split(":")[0].replace(/\D/g, "");
        if (!sid) continue;
        if (ignorados.has(semDdi(sid))) { ignoradas++; continue; }
        const texto = textoDe(m?.message || {});
        if (!texto) continue;                           // sem conteúdo legível: ignora
        const midia = midiaDe(m?.message || {});
        const ts = m?.messageTimestamp ? Number(m.messageTimestamp) * 1000 : Date.now();

        // ── a REGRA de escopo ──
        const lead = ehLead(sid);
        const nova = ts >= desdeMs;
        if (!lead && !nova) { foraEscopo++; if (forasAmostra.size < 20) forasAmostra.add(sid); continue; }
        if (lead) dentroPorLead.add(sid); else dentroPorNova.add(sid);

        const waId = keyO.id || null;
        const saida = keyO.fromMe === true;
        // guard textual só vale pro histórico sem wa_id; o resto o índice único barra
        if (saida) {
          if ((baloesAi[sid] || new Set()).has(texto)) continue;
          saidas++;
        } else {
          if ((textosHuman[sid] || new Set()).has(texto)) continue;
          entradas++;
        }
        candidatos.push({ sid, waId, texto, saida, ts, lead, midia });
      }
      // ordem cronológica: o CRM ordena a conversa pelo id serial da tabela, então
      // inserir fora de ordem embaralharia os balões na tela
      candidatos.sort((a, b)=>a.ts - b.ts);
      // janela de tempo lida do Evolution — se as mensagens recentes não vierem
      // nesta fatia de 300, é aqui que se enxerga
      const tsRecords = records.map((m)=>Number(m?.messageTimestamp || 0) * 1000).filter(Boolean);
      const janela = tsRecords.length ? {
        de: new Date(Math.min(...tsRecords)).toISOString(),
        ate: new Date(Math.max(...tsRecords)).toISOString()
      } : null;
      // Disjuntor: no incidente das 76.145 linhas o polling reinseria tudo a cada
      // 25s. Um ciclo normal traz dezenas de mensagens; centenas significa que
      // algo voltou a escapar — melhor não gravar e deixar registrado.
      const TETO = 500;
      const estourou = candidatos.length > TETO;
      let inseridas = 0, falhas = 0;
      if (SYNC_APPLY && !estourou) {
        for (const c of candidatos){
          const message = c.saida ? {
            type: "ai",
            content: c.texto,
            tool_calls: [],
            additional_kwargs: {
              operator: "Equipe (WhatsApp)",
              wa_id: c.waId,
              media: c.midia,
              ts: c.ts
            },
            response_metadata: {},
            invalid_tool_calls: []
          } : {
            type: "human",
            content: c.texto,
            additional_kwargs: {
              wa_id: c.waId,
              media: c.midia,
              ts: c.ts
            },
            response_metadata: {}
          };
          // wa_id na COLUNA: o índice único torna a duplicata impossível.
          // Conflito (23505) = já sincronizada → não é erro, é o guard funcionando.
          const ins = await service.from("agente_sdr_historico").insert({
            session_id: c.sid,
            wa_id: c.waId,
            message
          });
          if (!ins.error) inseridas++;
          else if (ins.error.code !== "23505") falhas++;
        }
      }
      await service.from("_evo_sync_debug").insert({
        info: {
          apply: SYNC_APPLY,
          estourou_teto: estourou,
          janela,
          http: r.status,
          ok: r.ok,
          total: records.length,
          desde: new Date(desdeMs).toISOString(),
          leads_no_banco: leadTels.size,
          entradas,
          saidas,
          fora_do_escopo: foraEscopo,
          ignoradas,
          conversas_por_lead: [...dentroPorLead],
          conversas_novas: [...dentroPorNova],
          conversas_fora: [...forasAmostra],
          candidatos: candidatos.length,
          inseridas,
          falhas,
          amostra_candidatos: candidatos.slice(0, 8)
        }
      }).then(()=>{}, ()=>{});
      return json({
        ok: true,
        apply: SYNC_APPLY,
        total: records.length,
        entradas,
        saidas,
        fora_do_escopo: foraEscopo,
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
        "sync_out",
        "diag",
        "media"
      ]
    }, 400);
  } catch (e) {
    return json({
      error: String(e.message || e)
    }, 500);
  }
});
