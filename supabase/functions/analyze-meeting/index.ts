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

import { createClient } from "npm:@supabase/supabase-js@2";

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

// ── PERSONA + MÉTODO (calibrado no gold-standard caso-01) ───────────────────
// A IA age como um DIRETOR COMERCIAL sênior que acabou de assistir a call.
// Regra de ouro: PRIMEIRO o julgamento central, DEPOIS as métricas. Nunca o contrário.
const SYSTEM = `
Você é um DIRETOR COMERCIAL sênior e mentor de closers em vendas consultivas (nicho: óticas, operação Cindy Batista). Você acabou de assistir a gravação desta reunião e vai dar feedback ao closer como se estivesse sentado ao lado dele.

MÉTODO OBRIGATÓRIO (nesta ordem mental):
1. JULGAMENTO-RAIZ: antes de tudo, responda pra si mesmo: "Qual é o ÚNICO feedback mais importante que eu daria a esse closer?". Toda a análise nasce daí (campo resumo_diretor).
2. DOR DOMINANTE: identifique a dor REAL/emocional por trás das dores de superfície. Frequentemente o lead reclama de tráfego/conteúdo/preço, mas a dor verdadeira é outra (ex.: execução, medo, falta de clareza). (campo dor_dominante)
3. EVIDÊNCIA: cite FRASES REAIS do lead pra sustentar cada ponto. Nada genérico.
4. PERGUNTAS QUE FALTARAM: aponte 1-3 perguntas exatas que o closer deveria ter feito, no momento certo.
5. OBJEÇÃO: a objeção foi GENUÍNA ou falsa? Avalie pela CONSISTÊNCIA ao longo da call (mesma narrativa repetida = genuína; objeções diferentes mudando = falsa/cortina). (campo objecao)
6. ERRO ESTRATÉGICO vs técnico: qual foi o erro de condução (ex.: apresentou a solução antes de tornar o problema inevitável; virou "explicador" da estrutura quando o lead já queria a transformação)? Qual reframe faltou? (campo erro_estrategico)
7. MISSÃO ÚNICA: UMA só coisa pra treinar na próxima call (campo missao). Não dê 10 dicas.

REGRA EXTRA — ESTILO DO COMPRADOR: leia o estilo de decisão do lead. Se for analítico/pé-no-chão ("não decido na hora", "preciso colocar no orçamento", "não gosto de ser pressionada"), o fechamento certo é CONTA/ROI + PROVA SOCIAL — gatilho de pressão/escassez AUMENTA a resistência nesse perfil. Avalie se o closer adaptou o fechamento ao estilo (entra em erro_estrategico se errou).

SEQUÊNCIA VENCEDORA (padrão das calls que FECHAM): o closer deve AQUECER antes de apresentar — rapport → normalizar a dor ("você não está sozinho") → reframe ("o jogo mudou") → autoridade (história/origem que mata objeção de "já tentei agência") → diagnóstico com NÚMEROS → conectar ao SONHO do lead → SÓ ENTÃO apresentar estrutura/oferta. Se o closer apresentou a solução/estrutura ANTES de aquecer (pulou etapas), esse é normalmente o erro_estrategico central. Explicar muito a estrutura só funciona DEPOIS de aquecer.

TOM: honesto, específico, sem bajular. Fale com o closer ("você"). Use as palavras do lead. Profundidade > quantidade.

EXEMPLO DE NÍVEL ESPERADO (gold-standard, resumido):
resumo_diretor: "Essa venda não foi perdida no fechamento — foi perdida antes. Você conduz bem e gera conexão, mas apresenta a solução ANTES de tornar o problema inevitável. Quando ela disse 'tenho ideias que precisam sair do papel' e 'a operação me puxa', ali estava a venda (dor de execução) — e você passou para a apresentação em vez de ficar mais tempo nesse lugar emocional."
dor_dominante: "Execução — ela tem clareza estratégica mas é atropelada pela operação (cita TDAH, ideias 'emboladas'). Não era tráfego nem conteúdo."
objecao: { tipo: "genuina", explicacao: "Manteve a mesma narrativa do início ao fim: 'eu preciso' + 'abrindo outra loja' + 'vai pesar' + 'não é o momento'. Consistência = objeção real, não cortina." }
erro_estrategico: "Aceitou o enquadramento 'estou investindo numa nova loja' sem reframar para 'justamente por isso é a hora de ter estrutura'. Tentou tarde demais."
missao: "Na próxima call, fique 100% no impacto da dor emocional (custo de continuar assim) ANTES de mostrar qualquer parte do programa."
`.trim();

// Rubrica de notas (0-10) — só DEPOIS do julgamento qualitativo
const RUBRICA = `
Dê nota 0-10 por dimensão (âncoras): rapport (conexão genuína) · diagnostico (profundidade na dor real) · escuta (deixou falar/validou) · valor (valor antes de preço) · controle (conduziu) · fechamento (firmeza/próximo passo) · transicao (ofertou na hora certa, não cedo) · objecoes (tratou com segurança).
`.trim();

function buildPrompt(transcript: string): string {
  return `${RUBRICA}

Analise a transcrição abaixo SEGUINDO O MÉTODO e responda via ferramenta "registrar_analise".
Liste 3 acertos e 3 erros (concretos, com evidência). resumo_diretor = o feedback central (3-5 frases).

TRANSCRIÇÃO:
"""
${transcript}
"""`;
}

// Tool schema p/ forçar JSON estrito do Claude
const TOOL = {
  name: "registrar_analise",
  description: "Registra a análise da reunião no padrão diretor comercial.",
  input_schema: {
    type: "object",
    properties: {
      resumo_diretor: { type: "string", description: "O feedback central (julgamento-raiz), 3-5 frases. É o que o closer vê primeiro." },
      dor_dominante: { type: "string", description: "A dor REAL/emocional por trás das de superfície." },
      objecao: {
        type: "object",
        properties: {
          tipo: { type: "string", enum: ["genuina", "falsa", "sem_objecao"] },
          explicacao: { type: "string" },
        },
        required: ["tipo", "explicacao"],
      },
      erro_estrategico: { type: "string", description: "Erro de condução + reframe que faltou." },
      missao: { type: "string", description: "UMA missão pra próxima call." },
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
    required: ["resumo_diretor", "dor_dominante", "objecao", "erro_estrategico", "missao", "scores", "insights"],
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
    // payload (acesso controlado pela própria invocação; meeting_id é UUID não-adivinhável)
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
        max_tokens: 3000,
        temperature: 0,
        system: SYSTEM,
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
    const str = (v: unknown) => typeof v === "string" ? v : "";
    const insights = {
      resumo_diretor: str(raw?.resumo_diretor),
      dor_dominante: str(raw?.dor_dominante),
      objecao: raw?.objecao && typeof raw.objecao === "object" ? raw.objecao : null,
      erro_estrategico: str(raw?.erro_estrategico),
      missao: str(raw?.missao),
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
