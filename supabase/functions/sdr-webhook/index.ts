// sdr-webhook — entrada única das mensagens do WhatsApp no CRM.
//
// Hoje a conversa só entra no CRM quando alguém abre o board e o front chama
// `evolution-proxy action=sync_out`. Isso torna qualquer resposta automática
// impossível: a mensagem do lead pode ficar horas parada. Esta function é o
// gatilho que faltava — o Evolution chama aqui a cada mensagem (messages.upsert).
//
// Responsabilidades, nesta ordem:
//   1. registrar a mensagem no histórico (fonte de verdade da conversa)
//   2. HANDOFF: se um humano respondeu pelo celular, pausar o agente no lead
//   3. responder como Carol — só se as quatro travas deixarem
//
// NASCE DESLIGADA: enquanto `agente_sdr.ativo = false`, ela registra e faz o
// handoff, mas nunca responde. Mesmo padrão do lembrete de call.
//
// Deploy: supabase functions deploy sdr-webhook --project-ref sgeoikzyahhdrncesbpn --no-verify-jwt
//   (--no-verify-jwt é obrigatório: o Evolution não manda JWT do Supabase. Quem
//    protege a rota é o SDR_WEBHOOK_TOKEN na URL, conferido abaixo.)
// Secrets: SDR_WEBHOOK_TOKEN (novo) · ANTHROPIC_API_KEY · EVOLUTION_API_URL/_KEY/_INSTANCE
// Webhook no Evolution: POST https://<ref>.supabase.co/functions/v1/sdr-webhook?t=<TOKEN>
//   evento messages.upsert apenas.
import { createClient } from "npm:@supabase/supabase-js@2";

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";

function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" }
  });
}

// O Evolution embrulha o texto em um lugar diferente por tipo de mensagem.
// Áudio, imagem sem legenda e figurinha caem fora de propósito: a Carol não
// interpreta mídia, e responder texto genérico a um áudio é pior que silêncio.
function extrairTexto(msg: Record<string, any> | null): string {
  if (!msg) return "";
  return String(
    msg.conversation ||
    msg.extendedTextMessage?.text ||
    msg.imageMessage?.caption ||
    msg.videoMessage?.caption ||
    msg.buttonsResponseMessage?.selectedDisplayText ||
    msg.listResponseMessage?.title ||
    ""
  ).trim();
}

function horaBR(d: Date): number {
  return Number(new Intl.DateTimeFormat("pt-BR", {
    timeZone: "America/Sao_Paulo", hour: "2-digit", hour12: false
  }).format(d));
}

const espera = (ms: number) => new Promise((r) => setTimeout(r, ms));

Deno.serve(async (req) => {
  try {
    // ── 1) porta de entrada ───────────────────────────────────────────────────
    // A rota é pública (o Evolution não tem como mandar JWT do Supabase), então
    // o token é a única credencial. Sem ele configurado, a function recusa tudo
    // em vez de ficar aberta — fail closed, não fail open.
    const TOKEN = Deno.env.get("SDR_WEBHOOK_TOKEN") || "";
    if (!TOKEN) return json({ error: "webhook_sem_token_configurado" }, 500);
    const url = new URL(req.url);
    const enviado = url.searchParams.get("t") || req.headers.get("x-webhook-token") || "";
    if (enviado !== TOKEN) return json({ error: "nao_autorizado" }, 401);

    const body = await req.json().catch(() => ({})) as Record<string, any>;
    const evento = String(body?.event || "").toLowerCase();
    if (evento && evento !== "messages.upsert") return json({ ok: true, ignorado: evento });

    // `data` vem como objeto num envio e como array em lote, dependendo da versão.
    const itens: Record<string, any>[] = Array.isArray(body?.data) ? body.data : [body?.data].filter(Boolean);
    if (!itens.length) return json({ ok: true, ignorado: "sem_data" });

    const sb = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    const { data: agente } = await sb.from("agente_sdr").select("*").limit(1).maybeSingle();
    const resultado: Record<string, unknown>[] = [];

    for (const item of itens) {
      const jid = String(item?.key?.remoteJid || "");
      // Grupo, status e newsletter não são conversa de lead.
      if (!jid || jid.endsWith("@g.us") || jid.startsWith("status@") || jid.includes("@newsletter")) {
        resultado.push({ jid, status: "ignorado_nao_e_lead" });
        continue;
      }
      const tel = jid.split("@")[0].replace(/\D/g, "");
      const waId = String(item?.key?.id || "") || null;
      const fromMe = item?.key?.fromMe === true;
      const texto = extrairTexto(item?.message);
      const nome = String(item?.pushName || "").trim() || tel;

      // ── 2) dedupe pelo wa_id ────────────────────────────────────────────────
      // Vale para os dois lados: o Evolution reenvia eventos, e toda mensagem que
      // NÓS mandamos (CRM, lembrete ou a própria Carol) volta como fromMe. Se o
      // wa_id já está gravado, isto é eco do que já sabemos — e, principalmente,
      // NÃO é um humano assumindo a conversa.
      if (waId) {
        const { data: jaTem } = await sb
          .from("agente_sdr_historico").select("id").eq("wa_id", waId).maybeSingle();
        if (jaTem) {
          resultado.push({ tel, status: "eco_ja_registrado" });
          continue;
        }
      }

      // ── 3) HANDOFF — humano respondeu pelo celular ──────────────────────────
      // Chegou aqui com fromMe e wa_id desconhecido: alguém do time escreveu
      // fora do CRM. É o furo que impedia ligar o agente com segurança — a Carol
      // escreveria por cima da Thalita. A partir de agora ela sai desse lead.
      if (fromMe) {
        await sb.from("agente_sdr_historico").insert({
          session_id: tel,
          wa_id: waId,
          message: {
            type: "ai",
            content: texto,
            tool_calls: [],
            additional_kwargs: { operator: "Equipe (WhatsApp)", wa_id: waId, ts: Date.now() },
            response_metadata: {},
            invalid_tool_calls: []
          }
        }).then(() => {}, () => {});
        await sb.from("leads").update({ agente_pausado: true }).eq("tel", tel).then(() => {}, () => {});
        resultado.push({ tel, status: "handoff_humano_assumiu" });
        continue;
      }

      // ── 4) mensagem do lead: registra sempre, mesmo sem responder ───────────
      if (!texto) {
        // Mídia sem texto: fica registrada como marcador para o humano ver que
        // chegou algo, e o agente não tenta adivinhar o conteúdo.
        await sb.from("agente_sdr_historico").insert({
          session_id: tel, wa_id: waId,
          message: {
            type: "human", content: "[mídia recebida]", tool_calls: [],
            additional_kwargs: { wa_id: waId, ts: Date.now(), midia: true },
            response_metadata: {}, invalid_tool_calls: []
          }
        }).then(() => {}, () => {});
        resultado.push({ tel, status: "midia_sem_texto_nao_responde" });
        continue;
      }

      const ins = await sb.from("agente_sdr_historico").insert({
        session_id: tel, wa_id: waId,
        message: {
          type: "human", content: texto, tool_calls: [],
          additional_kwargs: { wa_id: waId, ts: Date.now() },
          response_metadata: {}, invalid_tool_calls: []
        }
      }).select("id").maybeSingle();
      const meuId = ins.data?.id ?? null;

      await sb.rpc("registrar_evento_lead", {
        p_tel: tel, p_nome: nome, p_texto: texto, p_autor: "lead"
      }).then(() => {}, () => {});

      // ── 5) as quatro travas ─────────────────────────────────────────────────
      if (!agente || agente.ativo !== true) {
        resultado.push({ tel, status: "registrado_agente_desligado" });
        continue;
      }
      const { data: lead } = await sb
        .from("leads").select("id, nome, agente_pausado, atendente, status").eq("tel", tel).maybeSingle();
      if (lead?.agente_pausado === true) {
        resultado.push({ tel, status: "registrado_agente_pausado" });
        continue;
      }
      if (lead?.atendente) {
        resultado.push({ tel, status: "registrado_tem_atendente", atendente: lead.atendente });
        continue;
      }
      const h = horaBR(new Date());
      const antes = agente.nao_responder_antes ?? 8;
      const depois = agente.nao_responder_depois ?? 21;
      if (h < antes || h >= depois) {
        resultado.push({ tel, status: "registrado_fora_de_horario", hora: h });
        continue;
      }

      // ── 6) debounce: quem responde é a última mensagem do burst ─────────────
      // O lead manda três mensagens picadas em dez segundos. Sem isto, saem três
      // respostas. Mesma regra do f2-debounce-sou-ultima-msg.js, feita aqui com
      // uma releitura do histórico em vez de estado no n8n.
      const debounce = Math.max(0, Number(agente.debounce_seg ?? 12));
      if (debounce > 0) await espera(debounce * 1000);
      const { data: depoisDeMim } = await sb
        .from("agente_sdr_historico")
        .select("id, message")
        .eq("session_id", tel)
        .gt("id", meuId ?? 0)
        .limit(5);
      if ((depoisDeMim || []).some((m: any) => m?.message?.type === "human")) {
        resultado.push({ tel, status: "debounce_outra_msg_chegou" });
        continue;
      }
      // Se um humano respondeu durante a espera, a vez não é mais da Carol.
      if ((depoisDeMim || []).some((m: any) => m?.message?.type === "ai")) {
        resultado.push({ tel, status: "humano_respondeu_durante_espera" });
        continue;
      }

      // ── 7) o que a Carol responde ───────────────────────────────────────────
      const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY") || "";
      if (!ANTHROPIC_API_KEY) {
        resultado.push({ tel, status: "sem_anthropic_key" });
        continue;
      }
      const { data: hist } = await sb
        .from("agente_sdr_historico")
        .select("id, message")
        .eq("session_id", tel)
        .order("id", { ascending: false })
        .limit(40);
      const conversa = (hist || []).slice().reverse()
        .filter((m: any) => String(m?.message?.content || "").trim())
        .map((m: any) => ({
          role: m.message.type === "human" ? "user" : "assistant",
          content: String(m.message.content)
        }));
      // A API exige alternância começando em user; turnos seguidos do mesmo lado
      // são agrupados (o lead escreve picado o tempo todo).
      const msgs: { role: string; content: string }[] = [];
      for (const m of conversa) {
        const ult = msgs[msgs.length - 1];
        if (ult && ult.role === m.role) ult.content += "\n" + m.content;
        else msgs.push({ ...m });
      }
      while (msgs.length && msgs[0].role !== "user") msgs.shift();
      if (!msgs.length) {
        resultado.push({ tel, status: "sem_conversa_para_responder" });
        continue;
      }

      // A escalada já estava escrita na config (`escalar_instrucoes`, com
      // `escalar_ativo = true`), mas o prompt manda "pare de responder" sem dar
      // à Carol nenhum jeito de fazer isso. O marcador abaixo é esse jeito: ela
      // o escreve, a function o remove do texto e pausa o agente de verdade.
      const escalarLigado = agente.escalar_ativo === true && !!agente.escalar_instrucoes;
      const system = [
        agente.instrucoes || "",
        agente.conhecimento ? "\n\n# CONHECIMENTO\n\n" + agente.conhecimento : "",
        agente.qualificacao ? "\n\n# QUALIFICAÇÃO\n\n" + agente.qualificacao : "",
        escalarLigado ? "\n\n# QUANDO PASSAR PARA UM HUMANO\n\n" + agente.escalar_instrucoes : "",
        escalarLigado
          ? "\n\nAo escalar, escreva sua última fala normalmente e termine a mensagem com o marcador [ESCALAR] numa linha só dele. O marcador é interno: ele é removido antes de a mensagem chegar ao lead, avisa o time e faz você sair da conversa. Nunca use o marcador fora de uma escalada de verdade."
          : "",
        lead?.nome ? `\n\n# ESTE LEAD\n\nNome no CRM: ${lead.nome}. Status atual: ${lead.status || "novo"}.` : ""
      ].join("");

      let resposta = "";
      try {
        const r = await fetch(ANTHROPIC_URL, {
          method: "POST",
          headers: {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: agente.modelo || "claude-sonnet-5",
            max_tokens: 700,
            system,
            messages: msgs
          })
        });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) {
          resultado.push({ tel, status: "falha_anthropic", detalhe: JSON.stringify(d).slice(0, 300) });
          continue;
        }
        resposta = (d?.content || []).filter((b: any) => b.type === "text")
          .map((b: any) => b.text).join("\n").trim();
      } catch (e) {
        resultado.push({ tel, status: "falha_anthropic", detalhe: String(e).slice(0, 300) });
        continue;
      }
      if (!resposta) {
        resultado.push({ tel, status: "resposta_vazia" });
        continue;
      }

      // Escalada: tira o marcador do texto que vai para o lead e guarda a
      // decisão para depois do envio — a última fala dela sai normalmente, e só
      // então o agente se retira.
      const escalou = escalarLigado && /\[ESCALAR\]/i.test(resposta);
      if (escalou) resposta = resposta.replace(/\[ESCALAR\]/gi, "").trim();
      if (!resposta) {
        resultado.push({ tel, status: "escalada_sem_texto" });
        // Sem texto sobrando, ainda assim o humano precisa assumir.
        await sb.from("leads").update({ agente_pausado: true }).eq("tel", tel).then(() => {}, () => {});
        continue;
      }

      // ── 8) envio em balões ──────────────────────────────────────────────────
      // `||` separa balões — mesma convenção da mensagem de abertura no
      // respondi-webhook. Sem o separador, vai tudo num balão só.
      const EVO_URL = (Deno.env.get("EVOLUTION_API_URL") || "").replace(/\/$/, "");
      const EVO_KEY = Deno.env.get("EVOLUTION_API_KEY") || "";
      const EVO_INST = Deno.env.get("EVOLUTION_INSTANCE") || "arvex-agente-sdr";
      if (!EVO_URL || !EVO_KEY) {
        resultado.push({ tel, status: "evolution_nao_configurado" });
        continue;
      }
      const baloes = resposta.split("||").map((b) => b.trim()).filter(Boolean);
      let enviados = 0;
      for (let i = 0; i < baloes.length; i++) {
        try {
          const r = await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
            method: "POST",
            headers: { apikey: EVO_KEY, "Content-Type": "application/json" },
            body: JSON.stringify({ number: tel, text: baloes[i], delay: 800 + i * 2200 })
          });
          const d = await r.json().catch(() => ({}));
          if (!r.ok) break;
          enviados++;
          // grava com o wa_id devolvido: é o que faz o eco desta mesma mensagem
          // cair no dedupe do passo 2 em vez de virar "humano assumiu".
          await sb.from("agente_sdr_historico").insert({
            session_id: tel,
            wa_id: d?.key?.id || null,
            message: {
              type: "ai", content: baloes[i], tool_calls: [],
              additional_kwargs: { operator: agente.nome || "Carol", wa_id: d?.key?.id || null, ts: Date.now() },
              response_metadata: {}, invalid_tool_calls: []
            }
          }).then(() => {}, () => {});
        } catch {
          break;
        }
      }
      await sb.rpc("registrar_evento_lead", {
        p_tel: tel, p_nome: nome, p_texto: baloes.join("\n\n"),
        p_autor: "agente", p_por: agente.nome || "Carol"
      }).then(() => {}, () => {});

      // ── 9) escalada: o agente sai e o time é avisado ────────────────────────
      if (escalou) {
        await sb.from("leads").update({ agente_pausado: true }).eq("tel", tel).then(() => {}, () => {});
        const aviso = String(agente.notificar_contato || "").replace(/\D/g, "");
        if (agente.notificar_ativo === true && aviso) {
          const resumo = [
            `🔔 ${agente.nome || "Carol"} passou um lead para vocês`,
            `Lead: ${lead?.nome || nome} (${tel})`,
            `Status no CRM: ${lead?.status || "sem status"}`,
            `Última mensagem do lead: ${msgs[msgs.length - 1]?.content?.slice(0, 200) || ""}`
          ].join("\n");
          await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
            method: "POST",
            headers: { apikey: EVO_KEY, "Content-Type": "application/json" },
            body: JSON.stringify({ number: aviso, text: resumo })
          }).then(() => {}, () => {});
        }
        await sb.rpc("registrar_evento_lead", {
          p_tel: tel, p_nome: nome,
          p_texto: "Agente escalou para humano e saiu da conversa.",
          p_autor: "sistema", p_por: agente.nome || "Carol"
        }).then(() => {}, () => {});
        resultado.push({ tel, status: "escalado_para_humano", baloes: enviados, avisado: !!aviso });
        continue;
      }

      resultado.push({ tel, status: "respondido", baloes: enviados });
    }

    return json({ ok: true, resultado });
  } catch (e) {
    return json({ error: "erro_inesperado", detalhe: String(e) }, 500);
  }
});
