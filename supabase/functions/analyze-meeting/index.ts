// ============================================================================
// Sales Coach — Edge Function: analyze-meeting
// arvex-crm · Story S2 · Autor: @dev (build autônomo) · 2026-06-27
// Refs: docs/crm/sales-coach-architecture.md §2/§3 · setup-sales-coach-v1.sql
//
// Recebe { meeting_id }, valida o usuário (JWT), lê a transcrição (service_role),
// chama a API do Claude com rubrica fixa + playbook curto, força JSON estrito,
// clampa as notas 0-10, calcula nota_geral e grava em meetings.
// Em erro: status='error' + erro_msg (nunca derruba a função).
//
// Secrets necessários (Supabase → Edge Functions → Secrets):
//   ANTHROPIC_API_KEY            (obrigatório)
//   SUPABASE_URL                 (injetado automaticamente)
//   SUPABASE_SERVICE_ROLE_KEY    (injetado automaticamente)
//   SUPABASE_ANON_KEY            (injetado automaticamente)
// ============================================================================

import { createClient } from "jsr:@supabase/supabase-js@2";

const CLAUDE_MODEL = "claude-sonnet-4-6"; // qualidade p/ análise; trocar p/ claude-haiku-4-5 se quiser mais barato
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";

const DIMENSOES = [
  "rapport", "diagnostico", "escuta", "valor",
  "controle", "fechamento", "transicao", "objecoes",
] as const;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

// ── Rubrica fixa (garante notas consistentes) ──────────────────────────────
const RUBRICA = `
Avalie CADA dimensão de 0 a 10 com estas âncoras:
- rapport: conexão genuína com o lead (0-3 nenhuma · 4-6 superficial · 7-8 boa · 9-10 forte)
- diagnostico: profundidade na investigação da dor real (0-3 não investigou · 7-8 boa · 9-10 cirúrgica)
- escuta: deixou o lead falar, não interrompeu, validou (0-3 atropelou · 9-10 escuta ativa exemplar)
- valor: construção de valor antes de preço (0-3 jogou preço · 9-10 valor irresistível)
- controle: conduziu a reunião com direção (0-3 lead conduziu · 9-10 controle natural)
- fechamento: clareza e firmeza no fechamento/próximo passo (0-3 não fechou · 9-10 fechou com naturalidade)
- transicao: passagem de diagnóstico para oferta no momento certo (0-3 cedo/abrupto · 9-10 perfeita)
- objecoes: tratamento de objeções com segurança (0-3 cedeu fácil · 9-10 reverteu com valor)
`.trim();

// ── Playbook curto hardcoded (Sales Brain/pgvector é Fase 2) ───────────────
const PLAYBOOK = `
Contexto: vendas consultivas de mentoria/consultoria para donos de ótica (operação Cindy Batista).
Boas práticas esperadas: criar rapport real, diagnosticar a dor antes de ofertar, construir valor
antes de falar preço, não apresentar a solução cedo demais, explorar impacto financeiro da dor,
usar silêncio após o preço, não conceder desconto cedo.
`.trim();

function buildPrompt(transcript: string): string {
  return `${PLAYBOOK}

${RUBRICA}

Analise a transcrição da reunião de vendas abaixo e responda usando a ferramenta "registrar_analise".
Seja específico e construtivo. Para acertos/erros liste exatamente 3 itens cada.

TRANSCRIÇÃO:
"""
${transcript}
"""`;
}

// Tool schema p/ forçar JSON estrito do Claude
const TOOL = {
  name: "registrar_analise",
  description: "Registra a análise estruturada da reunião de vendas.",
  input_schema: {
    type: "object",
    properties: {
      scores: {
        type: "object",
        properties: Object.fromEntries(
          DIMENSOES.map((d) => [d, { type: "number", minimum: 0, maximum: 10 }]),
        ),
        required: [...DIMENSOES],
      },
      insights: {
        type: "object",
        properties: {
          acertos: { type: "array", items: { type: "string" } },
          erros: { type: "array", items: { type: "string" } },
          faltou: { type: "array", items: { type: "string" } },
          sugestoes: { type: "array", items: { type: "string" } },
        },
        required: ["acertos", "erros", "faltou", "sugestoes"],
      },
    },
    required: ["scores", "insights"],
  },
};

function clamp10(n: unknown): number {
  const v = typeof n === "number" ? n : Number(n);
  if (!isFinite(v)) return 0;
  return Math.max(0, Math.min(10, Math.round(v * 10) / 10));
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;
  const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");

  // service client (bypassa RLS — só no servidor)
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);

  let meeting_id: string | undefined;
  try {
    // 1. valida usuário autenticado (JWT vindo do invoke do front)
    const authHeader = req.headers.get("Authorization") ?? "";
    if (!authHeader.startsWith("Bearer ")) return json({ error: "Não autenticado" }, 401);
    const userClient = createClient(SUPABASE_URL, ANON_KEY, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: userData, error: userErr } = await userClient.auth.getUser();
    if (userErr || !userData?.user) return json({ error: "Não autenticado" }, 401);

    // 2. payload
    const body = await req.json().catch(() => ({}));
    meeting_id = body?.meeting_id;
    if (!meeting_id) return json({ error: "meeting_id obrigatório" }, 400);

    if (!ANTHROPIC_API_KEY) throw new Error("ANTHROPIC_API_KEY não configurada");

    // 3. marca processing + lê transcript
    await admin.from("meetings").update({ status: "processing", erro_msg: null }).eq("id", meeting_id);
    const { data: meeting, error: mErr } = await admin
      .from("meetings").select("id, transcript").eq("id", meeting_id).single();
    if (mErr || !meeting) throw new Error("Reunião não encontrada");
    const transcript = (meeting.transcript ?? "").toString().trim();
    if (!transcript) throw new Error("Transcrição vazia");

    // 4. chama Claude (temp 0, tool use força JSON)
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: CLAUDE_MODEL,
        max_tokens: 2000,
        temperature: 0,
        tools: [TOOL],
        tool_choice: { type: "tool", name: "registrar_analise" },
        messages: [{ role: "user", content: buildPrompt(transcript) }],
      }),
    });
    if (!resp.ok) throw new Error(`Claude API ${resp.status}: ${await resp.text()}`);
    const data = await resp.json();
    const toolUse = (data.content ?? []).find((c: any) => c.type === "tool_use");
    if (!toolUse?.input) throw new Error("Resposta da IA sem JSON estruturado");

    // 5. valida + clampa
    const raw = toolUse.input;
    const scores: Record<string, number> = {};
    for (const d of DIMENSOES) scores[d] = clamp10(raw?.scores?.[d]);
    const nota_geral = clamp10(
      DIMENSOES.reduce((s, d) => s + scores[d], 0) / DIMENSOES.length,
    );
    const insights = {
      acertos: Array.isArray(raw?.insights?.acertos) ? raw.insights.acertos.slice(0, 5) : [],
      erros: Array.isArray(raw?.insights?.erros) ? raw.insights.erros.slice(0, 5) : [],
      faltou: Array.isArray(raw?.insights?.faltou) ? raw.insights.faltou.slice(0, 8) : [],
      sugestoes: Array.isArray(raw?.insights?.sugestoes) ? raw.insights.sugestoes.slice(0, 8) : [],
    };

    // 6. grava resultado
    const { error: upErr } = await admin.from("meetings").update({
      scores, insights, nota_geral,
      status: "done", erro_msg: null, analyzed_at: new Date().toISOString(),
    }).eq("id", meeting_id);
    if (upErr) throw new Error(`Falha ao gravar: ${upErr.message}`);

    return json({ ok: true, meeting_id, nota_geral, scores, insights });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    // tenta marcar a reunião como erro (não derruba a função)
    if (meeting_id) {
      await admin.from("meetings").update({ status: "error", erro_msg: msg }).eq("id", meeting_id).catch(() => {});
    }
    return json({ ok: false, error: msg }, 500);
  }
});
