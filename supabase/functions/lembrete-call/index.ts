// lembrete-call — lembrete automático de call para o LEAD via WhatsApp (Evolution API)
//
// Pedido da Thalita (closer) · 2026-09-10
//
// Dois disparos por call: 9h do dia (todas as calls do dia) e 1h antes de cada uma.
// Texto FIXO com variáveis, vindo de `lembretes_config` — não passa pela Carol.
//
// Quem chama: pg_cron via pg_net (ver docs/crm/setup-lembrete-call-v1-cron.sql).
// Autenticação: Bearer com a chave `service_role` do projeto — o gateway valida a
// assinatura e aqui só se confere o papel declarado (ver papelDoToken). Nenhum
// secret novo a criar.
//
// Deploy:  supabase functions deploy lembrete-call --project-ref sgeoikzyahhdrncesbpn
// Secrets: reusa os do evolution-proxy (EVOLUTION_API_URL / _KEY / _INSTANCE).
//
// Chamada:
//   POST /lembrete-call  { "tipo": "manha" | "1h", "dry_run": true|false }
//   dry_run=true simula tudo (grava como 'simulado', não manda WhatsApp).
import { createClient } from "npm:@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "*, authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};

function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...CORS, "Content-Type": "application/json; charset=utf-8" }
  });
}

// Nomes de lead no CRM são bagunçados de verdade: "🩵", "Financeiro óptica veja bem",
// "Waleria da Ótica 👓". Chamar alguém de "Oi Financeiro" é pior do que não usar nome.
// Só aceita como nome uma primeira palavra alfabética de 2+ letras que não seja
// rótulo de setor.
const NAO_E_NOME = new Set([
  "financeiro", "otica", "ótica", "loja", "empresa", "contato", "cliente",
  "comercial", "atendimento", "recepcao", "recepção", "adm", "administracao"
]);

function primeiroNome(nome: string | null): string {
  const bruto = String(nome || "").trim();
  if (!bruto) return "";
  const p = bruto.split(/\s+/)[0].replace(/[^\p{L}]/gu, "");
  if (p.length < 2) return "";
  if (NAO_E_NOME.has(p.toLowerCase())) return "";
  return p.charAt(0).toUpperCase() + p.slice(1);
}

// Formata em horário de Brasília — a function roda em UTC.
function partesBR(d: Date) {
  const fmt = (opts: Intl.DateTimeFormatOptions) =>
    new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", ...opts }).format(d);
  return {
    hora: fmt({ hour: "2-digit", minute: "2-digit" }),
    data: fmt({ day: "2-digit", month: "2-digit" }),
    horaNum: Number(fmt({ hour: "2-digit", hour12: false })),
    diaISO: new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }).format(d)
  };
}

function montarTexto(modelo: string, lead: Record<string, unknown>, callEm: Date): string {
  const { hora, data } = partesBR(callEm);
  const nome = primeiroNome(lead.nome as string);
  const texto = modelo
    .replaceAll("{nome}", nome)
    .replaceAll("{hora}", hora)
    .replaceAll("{data}", data)
    .replaceAll("{resp}", String(lead.resp || "").split(/\s+/)[0] || "")
    // sem nome, "Oi {nome}, bom dia" viraria "Oi , bom dia"
    .replace(/ +([,!?.])/g, "$1")
    .replace(/^([^\S\n]*)([,!?.])\s*/gm, "$1")
    .replace(/[^\S\n]{2,}/g, " ")
    .trim();

  // Se o modelo abre com {nome} e o lead não tem nome usável, a frase começaria
  // em minúscula ("nossa conversa é daqui a pouco..."). Vale para qualquer texto
  // que alguém escrever depois na config, não só para os dois padrões de hoje.
  return texto.charAt(0).toLocaleUpperCase("pt-BR") + texto.slice(1);
}

// Papel declarado no JWT. Ler o payload SEM verificar assinatura é seguro aqui:
// o gateway do Supabase (verify_jwt, ligado) já rejeitou qualquer token inválido
// antes da requisição chegar nesta function — confirmado em teste: chave fora do
// projeto morre no gateway com corpo vazio, sem tocar neste código.
//
// Comparar direto com SUPABASE_SERVICE_ROLE_KEY não serve: a env injetada pelo
// Supabase neste projeto não é a mesma string da chave `service_role` legada que
// o cron usa (o projeto tem as novas API keys convivendo com as antigas).
function papelDoToken(jwt: string): string {
  try {
    const payload = jwt.split(".")[1];
    if (!payload) return "";
    const b64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const dados = JSON.parse(atob(b64.padEnd(b64.length + ((4 - b64.length % 4) % 4), "=")));
    return String(dados.role || "");
  } catch {
    return "";
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });

  try {
    // 1) autenticação — só o cron entra. Não há usuário do CRM chamando isto.
    const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
    const bearer = (req.headers.get("Authorization") || "").replace("Bearer ", "").trim();
    const autorizado = (SERVICE_KEY && bearer === SERVICE_KEY) ||
      papelDoToken(bearer) === "service_role";
    if (!autorizado) return json({ error: "nao_autorizado" }, 401);

    const body = await req.json().catch(() => ({})) as { tipo?: string; dry_run?: boolean };
    const tipo = body.tipo === "1h" ? "1h" : body.tipo === "manha" ? "manha" : null;
    if (!tipo) return json({ error: "tipo_invalido", esperado: "manha | 1h" }, 400);
    const dryRun = body.dry_run === true;

    const sb = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    // 2) config
    const { data: cfg, error: cfgErr } = await sb
      .from("lembretes_config").select("*").eq("id", 1).maybeSingle();
    if (cfgErr || !cfg) return json({ error: "config_ausente", detalhe: cfgErr?.message }, 500);
    if (!cfg.ativo && !dryRun) return json({ ok: true, pulado: "lembretes_desligados" });

    const agora = new Date();
    const { horaNum, diaISO } = partesBR(agora);

    // Janela de silêncio — vale inclusive para o disparo da manhã, caso alguém
    // mude hora_manha para um horário indelicado.
    if (!dryRun && (horaNum < cfg.nao_enviar_antes || horaNum >= cfg.nao_enviar_depois)) {
      return json({ ok: true, pulado: "fora_da_janela_de_horario", hora: horaNum });
    }

    // 3) calls elegíveis
    const { data: calls, error: callsErr } = await sb
      .from("calls_agendadas").select("*").order("call_em");
    if (callsErr) return json({ error: "falha_ao_ler_calls", detalhe: callsErr.message }, 500);

    const alvos = (calls || []).filter((c) => {
      const callEm = new Date(c.call_em as string);
      const faltamMin = (callEm.getTime() - agora.getTime()) / 60000;
      if (faltamMin <= 0) return false; // call já passou

      if (tipo === "manha") {
        // só as calls de HOJE, e só as que ainda estão suficientemente longe —
        // avisar de manhã uma call que começa em 20 min é ruído, o de 1h cobre.
        return partesBR(callEm).diaISO === diaISO && faltamMin >= cfg.gap_minimo_min;
      }
      // "1h antes": janela em torno de antecedencia_min. O cron roda a cada 10 min;
      // se dois ciclos pegarem a mesma call, o índice único barra o segundo envio.
      return (
        faltamMin <= cfg.antecedencia_min + cfg.janela_min &&
        faltamMin >= cfg.antecedencia_min - cfg.janela_min
      );
    });

    // 3b) dedupe por telefone. O CRM tem cadastros duplicados da mesma pessoa
    //     (dois "Orleany Santos", "Eduarda" e "Eduarda Rodrigues" com o mesmo
    //     número escrito de formas diferentes). O índice único é por lead_id,
    //     então sem isto a pessoa receberia a mesma mensagem duas vezes.
    //     Compara pelos últimos 8 dígitos — imune a DDI e ao 9 extra do celular.
    const vistos = new Set<string>();
    const alvosUnicos = alvos.filter((c) => {
      const chave = String(c.tel || "").replace(/\D/g, "").slice(-8);
      if (!chave || vistos.has(chave)) return false;
      vistos.add(chave);
      return true;
    });

    // 4) descarta o que já foi enviado (o índice único é a garantia final, mas
    //    filtrar antes evita chamar o Evolution à toa)
    const modelo = tipo === "manha" ? cfg.texto_manha : cfg.texto_1h;
    const EVO_URL = (Deno.env.get("EVOLUTION_API_URL") || "").replace(/\/$/, "");
    const EVO_KEY = Deno.env.get("EVOLUTION_API_KEY") || "";
    const EVO_INST = Deno.env.get("EVOLUTION_INSTANCE") || "arvex-agente-sdr";
    if (!dryRun && (!EVO_URL || !EVO_KEY)) return json({ error: "evolution_nao_configurado" }, 500);

    const resultado: Array<Record<string, unknown>> = [];

    for (const c of alvosUnicos) {
      const callEm = new Date(c.call_em as string);
      const tel = String(c.tel || "").replace(/\D/g, "");
      const texto = montarTexto(modelo as string, c, callEm);

      const { data: jaFoi } = await sb
        .from("lembretes_call")
        .select("id")
        .eq("lead_id", c.lead_id)
        .eq("tipo", tipo)
        .eq("call_em", callEm.toISOString())
        .maybeSingle();
      if (jaFoi) {
        resultado.push({ lead: c.nome, tel, status: "ja_enviado" });
        continue;
      }

      if (dryRun) {
        resultado.push({ lead: c.nome, tel, status: "simulado", texto });
        continue;
      }

      // 5) envia
      let status = "enviado";
      let detalhe: string | null = null;
      let waId: string | null = null;
      try {
        const r = await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
          method: "POST",
          headers: { apikey: EVO_KEY, "Content-Type": "application/json" },
          body: JSON.stringify({ number: tel, text: texto })
        });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) {
          status = "falha";
          detalhe = JSON.stringify(d).slice(0, 500);
        } else {
          waId = d?.key?.id || null;
        }
      } catch (e) {
        status = "falha";
        detalhe = String(e).slice(0, 500);
      }

      // 6) grava o log ANTES de qualquer outra coisa — é ele que impede o reenvio.
      //    Conflito no índice único significa que outro ciclo já mandou: não é erro.
      const { error: logErr } = await sb.from("lembretes_call").insert({
        lead_id: c.lead_id,
        tipo,
        call_em: callEm.toISOString(),
        tel,
        texto,
        status,
        detalhe
      });
      if (logErr && logErr.code === "23505") {
        resultado.push({ lead: c.nome, tel, status: "corrida_evitada" });
        continue;
      }

      // 7) espelha no chat do CRM, no mesmo padrão do evolution-proxy: grava com
      //    o wa_id devolvido pelo Evolution para o sync não duplicar a mensagem
      //    quando ela voltar como fromMe.
      if (status === "enviado") {
        await sb.from("agente_sdr_historico").insert({
          session_id: tel,
          wa_id: waId,
          message: {
            type: "ai",
            content: texto,
            tool_calls: [],
            additional_kwargs: { operator: "lembrete-call", wa_id: waId, ts: Date.now() },
            response_metadata: {},
            invalid_tool_calls: []
          }
        }).then(() => {}, () => {});

        await sb.rpc("registrar_evento_lead", {
          p_tel: tel,
          p_nome: String(c.nome || tel),
          p_texto: texto,
          p_autor: "humano",
          p_por: "lembrete-call"
        }).then(() => {}, () => {});
      }

      resultado.push({ lead: c.nome, tel, status, detalhe });
    }

    return json({
      ok: true,
      tipo,
      dry_run: dryRun,
      calls_elegiveis: alvosUnicos.length,
      descartados_duplicados: alvos.length - alvosUnicos.length,
      enviados: resultado.filter((r) => r.status === "enviado").length,
      falhas: resultado.filter((r) => r.status === "falha").length,
      resultado
    });
  } catch (e) {
    return json({ error: "erro_inesperado", detalhe: String(e) }, 500);
  }
});
