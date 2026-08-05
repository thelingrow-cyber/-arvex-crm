// ============================================================================
// [SYNC 2026-07-29] Este arquivo foi RESSINCRONIZADO a partir do que está
// deployado em produção (Management API → projects/{ref}/functions/coach-chat/body).
// O repo havia ficado para trás do deploy: a autorização JWT + posse (ADR-18/D2) e
// o limite de transcript de 180k (ADR-18/D1) já rodavam em produção e NÃO existiam
// aqui. A formatação é a do bundle (transpilado) — o comportamento é o de produção.
// Regra: editar aqui e deployar; nunca editar só pelo dashboard.
// Sales Coach — Edge Function: coach-chat
// Conversa sobre UMA reunião. Recebe {meeting_id, pergunta}, responde como
// diretor comercial grounded na transcrição + análise daquela call, e
// persiste o histórico em meetings.chat.
// IMPORTANTE: import npm: (jsr dá BOOT_ERROR). verify_jwt=false (gateway) — a
// validação real do JWT é feita em código (ADR-18, docs/crm/SALES-COACH-V2-FABLE.md):
// extrai o Bearer, resolve o usuário via admin.auth.getUser(jwt) e confere
// meeting.closer_id === user.id OU role admin em `profiles`.
// ============================================================================
import { createClient } from "npm:@supabase/supabase-js@2";
async function authenticate(req, admin) {
  const authHeader = req.headers.get("authorization") || req.headers.get("Authorization") || "";
  const token = authHeader.replace(/^Bearer\s+/i, "").trim();
  if (!token) return {
    ok: false,
    status: 401,
    msg: "não autorizado (sem token)"
  };
  const { data, error } = await admin.auth.getUser(token);
  if (error || !data?.user) return {
    ok: false,
    status: 401,
    msg: "token inválido"
  };
  const userId = data.user.id;
  const { data: profile } = await admin.from("profiles").select("role").eq("id", userId).single();
  const isAdmin = profile?.role === "admin";
  return {
    ok: true,
    userId,
    isAdmin
  };
}
const CLAUDE_MODEL = "claude-sonnet-4-6";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};
function json(body, status) {
  return new Response(JSON.stringify(body), {
    status: status || 200,
    headers: {
      ...cors,
      "Content-Type": "application/json"
    }
  });
}
// ── CÉREBRO (sales_knowledge) ───────────────────────────────────────────────
// Mesmo conhecimento curado que o analyze-meeting usa: quem é o comprador, o que
// a casa vende, objeções reais do nicho. É o que separa "responder sobre a call"
// de "responder como quem conhece o negócio". Falha na leitura degrada em silêncio.
const KB_MAX_CHARS = 18000; // 12k→18k (2026-08-05): ICP v2 + blocos do Hormozi somam ~15,5k
async function carregarCerebro(admin) {
  try {
    const { data, error } = await admin.from("sales_knowledge").select("tipo, titulo, conteudo").eq("ativo", true).order("peso", {
      ascending: false
    }).limit(30);
    if (error || !data || !data.length) return "";
    const blocos = [];
    let total = 0;
    for (const k of data){
      const b = `--- [${k.tipo}] ${k.titulo} ---\n${k.conteudo}`;
      if (total + b.length > KB_MAX_CHARS) break;
      blocos.push(b);
      total += b.length;
    }
    return blocos.length ? `\n\n=== O QUE VOCÊ SABE SOBRE ESTE NEGÓCIO (conhecimento curado da casa) ===\n${blocos.join("\n\n")}` : "";
  } catch (_e) {
    return "";
  }
}
function buildSystem(m, cerebro) {
  const sc = m.scores || {};
  const ins = m.insights || {};
  const notas = Object.keys(sc).map((k)=>k + " " + sc[k]).join(", ");
  const resumo = ins.resumo_diretor ? "\nResumo do diretor: " + ins.resumo_diretor : "";
  const dor = ins.dor_dominante ? "\nDor dominante: " + ins.dor_dominante : "";
  // ADR-18/D1: 14.000 → 180.000 chars (a call real de 55KB cabe inteira; o corte
  // vira proteção de borda, não mutilação sistemática do fechamento da call).
  const transcript = (m.transcript || "").toString().slice(0, 180000);
  return [
    "Você é um DIRETOR COMERCIAL sênior e mentor. Está conversando com o closer sobre ESTA reunião específica.",
    "Responda à pergunta dele baseado APENAS na transcrição e na análise abaixo. Cite trechos reais. Seja direto, prático e honesto (sem bajular), tom de mentor. Respostas curtas e úteis.",
    "Não invente dados que não estão na call.",
    "\n=== ANÁLISE DESTA CALL ===",
    "Resultado: " + (m.resultado || "—") + " | Nota geral: " + (m.nota_geral != null ? m.nota_geral : "—"),
    "Notas: " + notas + resumo + dor,
    ins.erro_estrategico ? "Erro estratégico: " + ins.erro_estrategico : "",
    cerebro || "",
    "\n=== TRANSCRIÇÃO ===\n" + transcript
  ].join("\n");
}
Deno.serve(async function(req) {
  if (req.method === "OPTIONS") return new Response("ok", {
    headers: cors
  });
  const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);
  try {
    const auth = await authenticate(req, admin);
    if (!auth.ok) return json({
      error: auth.msg
    }, auth.status);
    const body = await req.json().catch(function() {
      return {};
    });
    const meeting_id = body.meeting_id;
    const pergunta = (body.pergunta || "").toString().trim();
    if (!meeting_id || !pergunta) return json({
      error: "meeting_id e pergunta obrigatórios"
    }, 400);
    if (!ANTHROPIC_API_KEY) return json({
      error: "ANTHROPIC_API_KEY não configurada"
    }, 500);
    const r = await admin.from("meetings").select("id, closer_id, transcript, scores, insights, resultado, nota_geral, chat").eq("id", meeting_id).single();
    if (r.error || !r.data) return json({
      error: "Reunião não encontrada"
    }, 404);
    const m = r.data;
    if (!auth.isAdmin && m.closer_id !== auth.userId) {
      return json({
        error: "não autorizado (não é dono desta reunião)"
      }, 403);
    }
    const chat = Array.isArray(m.chat) ? m.chat : [];
    const history = chat.map(function(c) {
      return {
        role: c.role === "assistant" ? "assistant" : "user",
        content: String(c.content || "")
      };
    });
    const messages = history.concat([
      {
        role: "user",
        content: pergunta
      }
    ]);
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        model: CLAUDE_MODEL,
        max_tokens: 1200,
        temperature: 0.3,
        system: buildSystem(m, await carregarCerebro(admin)),
        messages: messages
      })
    });
    if (!resp.ok) return json({
      error: "Claude API " + resp.status + ": " + await resp.text()
    }, 500);
    const data = await resp.json();
    const parts = (data.content || []).filter(function(c) {
      return c.type === "text";
    });
    const resposta = parts.map(function(c) {
      return c.text;
    }).join("\n").trim() || "(sem resposta)";
    const now = new Date().toISOString();
    const novoChat = chat.concat([
      {
        role: "user",
        content: pergunta,
        at: now
      },
      {
        role: "assistant",
        content: resposta,
        at: now
      }
    ]);
    await admin.from("meetings").update({
      chat: novoChat
    }).eq("id", meeting_id);
    return json({
      ok: true,
      resposta: resposta
    });
  } catch (e) {
    const msg = e && e.message ? e.message : String(e);
    return json({
      ok: false,
      error: msg
    }, 500);
  }
});
