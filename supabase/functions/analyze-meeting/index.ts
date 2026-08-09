// ============================================================================
// [SYNC 2026-07-29] Este arquivo foi RESSINCRONIZADO a partir do que está
// deployado em produção (Management API → projects/{ref}/functions/analyze-meeting/body).
// O repo havia ficado para trás do deploy: a autorização JWT + posse (ADR-18/D2) e
// o limite de transcript de 180k (ADR-18/D1) já rodavam em produção e NÃO existiam
// aqui. A formatação é a do bundle (transpilado) — o comportamento é o de produção.
// Regra: editar aqui e deployar; nunca editar só pelo dashboard.
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
  "rapport",
  "diagnostico",
  "escuta",
  "valor",
  "controle",
  "fechamento",
  "transicao",
  "objecoes"
];
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};
function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json"
    }
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

A estrutura de call de referência (fases, transições, isolamento de objeção, fechamento) está no conhecimento curado abaixo — use-a como régua e NÃO repita aqui o que já está lá.

TOM: honesto, específico, sem bajular. Fale com o closer ("você"). Use as palavras do lead. Profundidade > quantidade.

REGRAS DE ESCRITA (o closer lê isso no celular, entre duas calls):
· NÃO REPITA o mesmo erro em vários campos. Se o erro central já está no resumo_diretor, os outros campos acrescentam coisa nova — não reformulam o mesmo ponto.
· resumo_diretor: no máximo 5 frases, ancorado na PIOR dimensão da rubrica.
· erro_estrategico: no máximo 6 linhas. Uma frase dizendo o erro + o reframe que faltou, com a frase pronta que ele deveria ter dito. Sem recapitular a call.
· Cada item de acertos/erros/faltou: UMA linha, começando por verbo, com evidência entre aspas quando houver.
· "faltou" é OBRIGATÓRIO: liste 2 a 4 PERGUNTAS EXATAS que o closer deveria ter feito, no formato em que ele as faria. Nunca devolva vazio.
· proxima_acao_lead: escreva a MENSAGEM PRONTA para o closer mandar hoje para ESTE lead (WhatsApp, 1º pessoa, tom dele, sem emoji, referenciando algo específico da conversa). Se a venda estiver perdida de forma irreversível, escreva a mensagem de encerramento com porta aberta. Este campo nunca fica vazio — toda call tem um próximo movimento.

EXEMPLO DE NÍVEL ESPERADO (gold-standard, resumido):
resumo_diretor: "Essa venda não foi perdida no fechamento — foi perdida antes. Você conduz bem e gera conexão, mas apresenta a solução ANTES de tornar o problema inevitável. Quando ela disse 'tenho ideias que precisam sair do papel' e 'a operação me puxa', ali estava a venda (dor de execução) — e você passou para a apresentação em vez de ficar mais tempo nesse lugar emocional."
dor_dominante: "Execução — ela tem clareza estratégica mas é atropelada pela operação (cita TDAH, ideias 'emboladas'). Não era tráfego nem conteúdo."
objecao: { tipo: "genuina", explicacao: "Manteve a mesma narrativa do início ao fim: 'eu preciso' + 'abrindo outra loja' + 'vai pesar' + 'não é o momento'. Consistência = objeção real, não cortina." }
erro_estrategico: "Aceitou o enquadramento 'estou investindo numa nova loja' sem reframar para 'justamente por isso é a hora de ter estrutura'. Tentou tarde demais."
missao: "Na próxima call, fique 100% no impacto da dor emocional (custo de continuar assim) ANTES de mostrar qualquer parte do programa."
`.trim();
// Rubrica de notas (0-10) — só DEPOIS do julgamento qualitativo.
// ÂNCORAS EXPLÍCITAS por faixa: sem elas a nota é ruído (a mesma call recebia
// 3.0 ou 4.5 em rodadas diferentes). Cada faixa descreve um FATO verificável na
// transcrição, não uma impressão — é o que torna a nota comparável entre calls
// e entre closers, que é o uso que interessa (evolução no tempo).
const RUBRICA = `
Dê nota 0-10 por dimensão usando ESTAS ÂNCORAS. Escolha a faixa pelo que ACONTECEU na transcrição, não pela impressão geral. Se ficar entre duas faixas, use o limite inferior.

RAPPORT — conexão genuína
0-3 foi direto ao assunto, lead monossilábico · 4-6 cordial mas protocolar · 7-8 o lead revelou coisas que não foram perguntadas (contexto pessoal, medo, números) · 9-10 além disso o lead pediu opinião ou se abriu sobre algo sensível.

DIAGNOSTICO — profundidade até a dor real
0-3 só perguntas de situação (quanto fatura, quantos anos), ou menos de 5 min · 4-6 chegou a perguntas de problema ("qual o gargalo?") mas parou aí · 7-8 fez ao menos 2 perguntas de IMPLICAÇÃO (o que isso te custa / o que acontece se continuar) · 9-10 o lead MEDIU o próprio problema em voz alta, com número ou consequência concreta.

ESCUTA — deixou falar e usou o que ouviu
0-3 interrompeu ou emendou pergunta sem reagir à resposta · 4-6 ouviu mas não devolveu · 7-8 parafraseou ("então o que eu entendi é...") ao menos 2 vezes · 9-10 usou as PALAVRAS EXATAS do lead depois, na apresentação.

VALOR — construiu antes do preço
0-3 apresentou catálogo de entregáveis · 4-6 ligou alguns entregáveis a dores genéricas · 7-8 cada pilar amarrado a uma dor que o lead verbalizou · 9-10 além disso fez conta/prova com número na frente do lead (ex.: conta da base).

CONTROLE — conduziu a call
0-3 o lead conduziu ou a call dispersou · 4-6 seguiu roteiro mas perdeu momentos · 7-8 contrato de call no início e transições claras · 9-10 recuperou desvios e manteve o tempo (diagnóstico ≥ apresentação).

FECHAMENTO — pediu e amarrou
0-3 não pediu a venda, ou terminou com "me manda no WhatsApp" · 4-6 pediu de forma vaga ou aceitou "vou pensar" sem tratar · 7-8 pediu com clareza e tratou a objeção real · 9-10 saiu com PEDIDO ou AVANÇO: valor, data e próximo passo com dia/hora marcados.

TRANSICAO — apresentou na hora certa
0-3 apresentou antes de qualquer dor verbalizada · 4-6 apresentou logo após o primeiro problema aparecer · 7-8 apresentou depois da dor construída · 9-10 fez pergunta de verificação ABERTA antes de avançar ("do que eu falei, o que mais fez sentido?").

OBJECOES — isolou e resolveu
0-3 respondeu a primeira objeção que apareceu, ou ignorou · 4-6 respondeu bem mas sem isolar · 7-8 isolou ("além disso, tem mais alguma coisa?") antes de resolver · 9-10 isolou, resolveu e RE-PERGUNTOU ("isso resolve? podemos seguir?").

Depois de dar as notas, identifique a PIOR dimensão — ela deve ser o eixo do resumo_diretor e da missão.
`.trim();
// ── CÉREBRO (sales_knowledge) ───────────────────────────────────────────────
// O coach não pode julgar uma call sem saber quem é o comprador, o que a casa
// vende e quais objeções são reais nesse nicho. Sem isto ele vira um consultor
// genérico de vendas. Conteúdo curado vive na tabela `sales_knowledge` (ativo=true),
// ordenado por peso. Falha na leitura NUNCA derruba a análise — degrada para o
// comportamento antigo (prompt sem cérebro).
const KB_MAX_CHARS = 28000; // teto final: ~7k tokens de contexto fixo por analise. Acima disso a atencao do modelo dilui — a partir daqui, bloco novo EXPULSA bloco antigo.
async function carregarCerebro(admin) {
  try {
    const { data, error } = await admin.from("sales_knowledge").select("tipo, titulo, conteudo, peso").eq("ativo", true).order("peso", {
      ascending: false
    }).limit(30);
    if (error || !data || !data.length) return "";
    const blocos = [];
    let total = 0;
    for (const k of data){
      const bloco = `--- [${k.tipo}] ${k.titulo} ---\n${k.conteudo}`;
      if (total + bloco.length > KB_MAX_CHARS) break;
      blocos.push(bloco);
      total += bloco.length;
    }
    if (!blocos.length) return "";
    return `\n\n=== O QUE VOCÊ SABE SOBRE ESTE NEGÓCIO (conhecimento curado, extraído de calls e material da casa) ===\nUse isto para julgar a call com o critério de quem conhece o comprador e a oferta. Se a call contradiz este conhecimento, aponte. NÃO invente nada que não esteja aqui nem na transcrição.\n\n${blocos.join("\n\n")}`;
  } catch (_e) {
    return "";
  }
}
// ── HISTÓRICO DO CLOSER ─────────────────────────────────────────────────────
// O coach deixa de analisar calls soltas e passa a acompanhar UMA PESSOA ao
// longo do tempo. Puxa as análises anteriores DESTE closer (nunca a call atual)
// para poder dizer "esse erro é a 3ª vez" ou "isto você melhorou".
// Degrada em silêncio: sem histórico, a análise segue normal.
const HIST_MAX = 12;
async function carregarHistoricoCloser(admin, closerId, meetingIdAtual) {
  if (!closerId) return "";
  try {
    const { data, error } = await admin.from("meetings")
      .select("id, data_reuniao, cliente_nome, resultado, nota_geral, insights")
      .eq("closer_id", closerId).eq("status", "done").neq("id", meetingIdAtual)
      .order("data_reuniao", { ascending: false }).limit(HIST_MAX);
    if (error || !data || !data.length) return "";
    const linhas = data.map((m)=>{
      const i = m.insights || {};
      const partes = [
        `• ${m.data_reuniao || "?"} — ${m.cliente_nome || "sem nome"} [${m.resultado || "aberto"}${m.nota_geral != null ? ", nota " + m.nota_geral : ""}]`,
      ];
      if (i.dor_dominante) partes.push(`  dor: ${String(i.dor_dominante).slice(0, 180)}`);
      if (i.erro_estrategico) partes.push(`  erro: ${String(i.erro_estrategico).slice(0, 220)}`);
      if (i.missao) partes.push(`  missão dada: ${String(i.missao).slice(0, 180)}`);
      return partes.join("\n");
    });
    return `\n\n=== HISTÓRICO DESTE CLOSER (${data.length} call${data.length > 1 ? "s" : ""} anterior${data.length > 1 ? "es" : ""}, da mais recente para a mais antiga) ===
Você acompanha esta pessoa, não analisa calls avulsas. USE ISTO:
· Se um erro se repete, DIGA que se repete e há quantas calls ("é a 3ª vez que...").
· Se a missão dada na call anterior foi cumprida, RECONHEÇA explicitamente. Se foi ignorada, aponte.
· A missão desta call deve ter CONTINUIDADE com a anterior — não recomece do zero a cada análise.
· Não invente evolução que os dados não mostram.

${linhas.join("\n")}`;
  } catch (_e) {
    return "";
  }
}
function buildPrompt(transcript) {
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
      resumo_diretor: {
        type: "string",
        description: "O feedback central (julgamento-raiz), 3-5 frases. É o que o closer vê primeiro."
      },
      dor_dominante: {
        type: "string",
        description: "A dor REAL/emocional por trás das de superfície."
      },
      objecao: {
        type: "object",
        properties: {
          tipo: {
            type: "string",
            enum: [
              "genuina",
              "falsa",
              "sem_objecao"
            ]
          },
          explicacao: {
            type: "string"
          }
        },
        required: [
          "tipo",
          "explicacao"
        ]
      },
      erro_estrategico: {
        type: "string",
        description: "Erro de condução + reframe que faltou."
      },
      missao: {
        type: "string",
        description: "UMA missão pra próxima call, ancorada na pior dimensão da rubrica."
      },
      pior_dimensao: {
        type: "string",
        enum: [...DIMENSOES],
        description: "A dimensão de menor nota — é o eixo do resumo e da missão."
      },
      proxima_acao_lead: {
        type: "string",
        description: "MENSAGEM PRONTA para o closer mandar HOJE para ESTE lead (WhatsApp, 1ª pessoa, tom natural, sem emoji, citando algo específico da conversa). Toda call tem próximo movimento — se a venda morreu, escreva o encerramento com porta aberta."
      },
      scores: {
        type: "object",
        properties: Object.fromEntries(DIMENSOES.map((d)=>[
            d,
            {
              type: "number",
              minimum: 0,
              maximum: 10
            }
          ])),
        required: [
          ...DIMENSOES
        ]
      },
      insights: {
        type: "object",
        properties: {
          acertos: {
            type: "array",
            items: {
              type: "string"
            }
          },
          erros: {
            type: "array",
            items: {
              type: "string"
            }
          },
          faltou: {
            type: "array",
            items: {
              type: "string"
            }
          },
          sugestoes: {
            type: "array",
            items: {
              type: "string"
            }
          }
        },
        required: [
          "acertos",
          "erros",
          "faltou",
          "sugestoes"
        ]
      }
    },
    required: [
      "resumo_diretor",
      "dor_dominante",
      "objecao",
      "erro_estrategico",
      "missao",
      "pior_dimensao",
      "proxima_acao_lead",
      "scores",
      "insights"
    ]
  }
};
function clamp10(n) {
  const v = typeof n === "number" ? n : Number(n);
  if (!isFinite(v)) return 0;
  return Math.max(0, Math.min(10, Math.round(v * 10) / 10));
}
// ── ADR-18: auth real ────────────────────────────────────────────────────────
// Extrai o Bearer do header Authorization. Dois caminhos válidos:
//  1. service-to-service (ingest-meeting → analyze-meeting): o token É a própria
//     SERVICE_ROLE_KEY (é como ingest-meeting já invoca hoje) → autorizado como admin.
//  2. usuário logado no CRM: token é o JWT de sessão do Supabase Auth → resolve o
//     usuário via admin.auth.getUser(jwt) e confere role em `profiles` (mesma fonte
//     que a RLS usa e que o front já consulta em profile?.role).
async function authenticate(req, admin, SERVICE_KEY) {
  const authHeader = req.headers.get("authorization") || req.headers.get("Authorization") || "";
  const token = authHeader.replace(/^Bearer\s+/i, "").trim();
  if (!token) return {
    ok: false,
    status: 401,
    msg: "não autorizado (sem token)"
  };
  if (token === SERVICE_KEY) return {
    ok: true,
    userId: null,
    isAdmin: true,
    isService: true
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
    isAdmin,
    isService: false
  };
}
Deno.serve(async (req)=>{
  if (req.method === "OPTIONS") return new Response("ok", {
    headers: corsHeaders
  });
  if (req.method !== "POST") return json({
    error: "Method not allowed"
  }, 405);
  const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY");
  const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");
  // service client (bypassa RLS — só no servidor)
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);
  let meeting_id;
  try {
    const auth = await authenticate(req, admin, SERVICE_KEY);
    if (!auth.ok) return json({
      error: auth.msg
    }, auth.status);
    // payload (meeting_id é UUID; a posse é validada abaixo, não mais "não-adivinhável" como barreira)
    const body = await req.json().catch(()=>({}));
    meeting_id = body?.meeting_id;
    if (!meeting_id) return json({
      error: "meeting_id obrigatório"
    }, 400);
    if (!ANTHROPIC_API_KEY) throw new Error("ANTHROPIC_API_KEY não configurada");
    // lê a reunião ANTES de mexer em qualquer status — precisa do closer_id p/ checar posse
    const { data: meetingRow, error: mErr0 } = await admin.from("meetings").select("id, closer_id, transcript").eq("id", meeting_id).single();
    if (mErr0 || !meetingRow) return json({
      error: "Reunião não encontrada"
    }, 404);
    if (!auth.isService && !auth.isAdmin && meetingRow.closer_id !== auth.userId) {
      return json({
        error: "não autorizado (não é dono desta reunião)"
      }, 403);
    }
    // 3. marca processing + lê transcript
    await admin.from("meetings").update({
      status: "processing",
      erro_msg: null
    }).eq("id", meeting_id);
    const meeting = meetingRow;
    const transcript = (meeting.transcript ?? "").toString().trim();
    if (!transcript) throw new Error("Transcrição vazia");
    const cerebro = await carregarCerebro(admin);
    const historico = await carregarHistoricoCloser(admin, meetingRow.closer_id, meeting_id);
    // 4. chama Claude (temp 0, tool use força JSON)
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        model: CLAUDE_MODEL,
        max_tokens: 3000,
        temperature: 0,
        system: SYSTEM + cerebro + historico,
        tools: [
          TOOL
        ],
        tool_choice: {
          type: "tool",
          name: "registrar_analise"
        },
        messages: [
          {
            role: "user",
            content: buildPrompt(transcript)
          }
        ]
      })
    });
    if (!resp.ok) throw new Error(`Claude API ${resp.status}: ${await resp.text()}`);
    const data = await resp.json();
    const toolUse = (data.content ?? []).find((c)=>c.type === "tool_use");
    if (!toolUse?.input) throw new Error("Resposta da IA sem JSON estruturado");
    // 5. valida + clampa
    const raw = toolUse.input;
    const scores = {};
    for (const d of DIMENSOES)scores[d] = clamp10(raw?.scores?.[d]);
    const nota_geral = clamp10(DIMENSOES.reduce((s, d)=>s + scores[d], 0) / DIMENSOES.length);
    const str = (v)=>typeof v === "string" ? v : "";
    const insights = {
      resumo_diretor: str(raw?.resumo_diretor),
      dor_dominante: str(raw?.dor_dominante),
      objecao: raw?.objecao && typeof raw.objecao === "object" ? raw.objecao : null,
      erro_estrategico: str(raw?.erro_estrategico),
      missao: str(raw?.missao),
      pior_dimensao: str(raw?.pior_dimensao),
      proxima_acao_lead: str(raw?.proxima_acao_lead),
      acertos: Array.isArray(raw?.insights?.acertos) ? raw.insights.acertos.slice(0, 5) : [],
      erros: Array.isArray(raw?.insights?.erros) ? raw.insights.erros.slice(0, 5) : [],
      faltou: Array.isArray(raw?.insights?.faltou) ? raw.insights.faltou.slice(0, 8) : [],
      sugestoes: Array.isArray(raw?.insights?.sugestoes) ? raw.insights.sugestoes.slice(0, 8) : []
    };
    // 6. grava resultado
    const { error: upErr } = await admin.from("meetings").update({
      scores,
      insights,
      nota_geral,
      status: "done",
      erro_msg: null,
      analyzed_at: new Date().toISOString()
    }).eq("id", meeting_id);
    if (upErr) throw new Error(`Falha ao gravar: ${upErr.message}`);
    return json({
      ok: true,
      meeting_id,
      nota_geral,
      scores,
      insights
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    // tenta marcar a reunião como erro (não derruba a função)
    if (meeting_id) {
      await admin.from("meetings").update({
        status: "error",
        erro_msg: msg
      }).eq("id", meeting_id).catch(()=>{});
    }
    return json({
      ok: false,
      error: msg
    }, 500);
  }
});
