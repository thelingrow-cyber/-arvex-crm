// ============================================================================
// Sales Coach — Edge Function: distill-knowledge
//
// Recebe material BRUTO (trecho de livro, script de vídeo/aula, SOP, transcrição)
// e devolve um bloco DESTILADO pronto para virar linha em `sales_knowledge`.
//
// Por que destilar em vez de guardar o material cru: o cérebro entra no system
// prompt de toda análise. Material cru (a) estoura o custo por call, (b) faz o
// modelo citar jargão do livro em vez de julgar a call que está na frente dele.
// O que serve é princípio operável com fonte — 1.000 a 2.000 chars por bloco.
//
// Body: { texto, tipo?, titulo?, fonte?, salvar? }
//   tipo: icp | metodo | oferta | objecao | caso | produto  (default: metodo)
//   salvar: se true, grava direto em sales_knowledge e devolve o id
//
// Auth: mesmo padrão ADR-18 das outras functions — Bearer do usuário (só admin
// pode destilar/gravar) ou a service_role key para uso service-to-service.
// ============================================================================
import { createClient } from "npm:@supabase/supabase-js@2";

const CLAUDE_MODEL = "claude-sonnet-4-6";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MAX_ENTRADA = 200000; // ~50k tokens: cabe um capítulo ou uma aula inteira

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });
}

const TIPOS = ["icp", "metodo", "oferta", "objecao", "caso", "produto"];

const SYSTEM = `
Você destila material de vendas em CONHECIMENTO OPERÁVEL para um agente que analisa calls de vendas
consultivas no nicho de óticas (operação Cindy Batista / ARVEX).

O bloco que você produzir vai entrar no system prompt do analisador de calls. Logo:
- Escreva REGRAS E CRITÉRIOS aplicáveis a uma call, não resumo de conteúdo.
  Ruim: "o autor defende que rapport é importante".
  Bom:  "Se o closer apresenta preço antes de o lead verbalizar a consequência da dor, o erro é de
         ordem, não de preço — aponte como erro_estrategico."
- Seja específico e verificável numa transcrição. Cada linha deve permitir que alguém olhe a call e
  diga "isso aconteceu" ou "isso não aconteceu".
- Preserve números, nomes de etapas, frases-gatilho e vocabulário do nicho quando existirem no material.
- NÃO invente nada que não esteja no material. Se o material for raso, produza um bloco curto — é melhor
  que um bloco inflado.
- NÃO copie parágrafos inteiros do original. Destile.
- Português do Brasil, direto, sem jargão de consultoria e sem elogio ao autor.
- Tamanho-alvo: 800 a 2.000 caracteres. Nunca passe de 2.500.
`.trim();

const TOOL = {
  name: "registrar_bloco",
  description: "Registra o bloco destilado de conhecimento.",
  input_schema: {
    type: "object",
    properties: {
      titulo: { type: "string", description: "Título curto e descritivo do bloco (máx 80 chars)." },
      conteudo: { type: "string", description: "O bloco destilado: regras e critérios operáveis." },
      tipo: { type: "string", enum: TIPOS, description: "Classificação do bloco." },
      tags: { type: "array", items: { type: "string" }, description: "3 a 6 tags curtas." },
      peso: { type: "number", description: "1-5: quão central é este bloco para julgar uma call." },
    },
    required: ["titulo", "conteudo", "tipo", "tags", "peso"],
  },
};

async function authenticate(req: Request, admin: any, SERVICE_KEY: string) {
  const h = req.headers.get("authorization") || req.headers.get("Authorization") || "";
  const token = h.replace(/^Bearer\s+/i, "").trim();
  if (!token) return { ok: false, status: 401, msg: "não autorizado (sem token)" };
  if (token === SERVICE_KEY) return { ok: true, isAdmin: true };
  const { data, error } = await admin.auth.getUser(token);
  if (error || !data?.user) return { ok: false, status: 401, msg: "token inválido" };
  const { data: profile } = await admin.from("profiles").select("role").eq("id", data.user.id).single();
  if (profile?.role !== "admin") return { ok: false, status: 403, msg: "só admin pode alimentar o cérebro" };
  return { ok: true, isAdmin: true };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });

  const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
  const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");
  const admin = createClient(SUPABASE_URL, SERVICE_KEY);

  try {
    const auth = await authenticate(req, admin, SERVICE_KEY);
    if (!auth.ok) return json({ error: auth.msg }, auth.status);
    if (!ANTHROPIC_API_KEY) return json({ error: "ANTHROPIC_API_KEY não configurada" }, 500);

    const body = await req.json().catch(() => ({}));
    const texto = (body.texto || "").toString().trim();
    if (texto.length < 200) return json({ error: "material curto demais para destilar (mín. 200 chars)" }, 400);

    const tipoSugerido = TIPOS.includes(body.tipo) ? body.tipo : "metodo";
    const fonte = (body.fonte || "").toString().trim() || null;
    const dica = body.titulo ? `\nO usuário sugeriu este título/assunto: "${body.titulo}".` : "";

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
        system: SYSTEM,
        tools: [TOOL],
        tool_choice: { type: "tool", name: "registrar_bloco" },
        messages: [{
          role: "user",
          content: `Destile o material abaixo em um bloco de conhecimento do tipo "${tipoSugerido}".${dica}

MATERIAL:
"""
${texto.slice(0, MAX_ENTRADA)}
"""`,
        }],
      }),
    });

    if (!resp.ok) return json({ error: `Claude API ${resp.status}: ${(await resp.text()).slice(0, 300)}` }, 502);

    const data = await resp.json();
    const bloco = (data.content || []).find((c: any) => c.type === "tool_use")?.input;
    if (!bloco?.conteudo) return json({ error: "resposta da IA sem bloco" }, 502);

    const peso = Math.max(1, Math.min(5, Math.round(Number(bloco.peso) || 3)));
    const tipo = TIPOS.includes(bloco.tipo) ? bloco.tipo : tipoSugerido;

    if (!body.salvar) return json({ ok: true, bloco: { ...bloco, tipo, peso, fonte } });

    const { data: ins, error: insErr } = await admin.from("sales_knowledge").insert({
      tipo, titulo: bloco.titulo, conteudo: bloco.conteudo, fonte,
      tags: Array.isArray(bloco.tags) ? bloco.tags.slice(0, 8) : [], peso, ativo: true,
    }).select("id").single();

    if (insErr) return json({ error: "falha ao salvar: " + insErr.message }, 500);
    return json({ ok: true, id: ins.id, bloco: { ...bloco, tipo, peso, fonte } });
  } catch (e) {
    return json({ error: String((e as Error)?.message || e) }, 500);
  }
});
