import { createClient } from "jsr:@supabase/supabase-js@2";

Deno.serve(async (req: Request) => {
  try {
    const body = await req.json();
    console.log("BODY:", JSON.stringify(body));

    const answers = body?.respondent?.raw_answers || [];

    const get = (id: string) => answers.find((a: any) => a.question.question_id === id);
    const arr = (v: any) => [].concat(v || []).join(", ");

    const nomeObj   = get("015f6a58f57a");
    const telObj    = get("x2sckxc03maq");
    const lojaObj   = get("xbun8ezavigg");
    const colabObj  = get("xeljido7mzb");
    const perfilObj = get("xbx99fbcapm");
    const fatObj    = get("xqk9eo3025bh");
    const desafObj  = get("x22e7kijok7w");
    const tempoObj  = get("xh05c2mb06aw");
    const travaObj  = get("xzkxhk6sw1i");
    const compObj   = get("x1v402tyug49");

    const nome    = nomeObj?.answer || "";
    const telData = telObj?.answer || {};
    const tel     = typeof telData === "object"
      ? (telData.country || "55") + telData.phone
      : String(telData);
    const loja = lojaObj?.answer || "";

    const obs = [
      loja              ? "@ da loja: " + loja                     : "",
      colabObj?.answer  ? "Colaboradores: " + arr(colabObj.answer)  : "",
      perfilObj?.answer ? "Perfil: "        + arr(perfilObj.answer) : "",
      fatObj?.answer    ? "Faturamento: "   + arr(fatObj.answer)    : "",
      desafObj?.answer  ? "Desafio: "       + arr(desafObj.answer)  : "",
      tempoObj?.answer  ? "Tempo: "         + arr(tempoObj.answer)  : "",
      travaObj?.answer  ? "Trava: "         + travaObj.answer       : "",
      compObj?.answer   ? "Comprometimento: " + compObj.answer + "/5" : "",
    ].filter(Boolean).join(" | ");

    console.log("nome:", nome, "tel:", tel, "loja:", loja);

    if (!nome) return new Response("sem nome", { status: 400 });

    const sb = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    const { error } = await sb.from("leads").insert({
      nome,
      tel,
      expert: "Cindy Batista",
      origem: "Respondi",
      status: "novo",
      obs,
    });
    console.log("insert error:", error);

    // ── Abordagem automática: manda a mensagem de abertura na hora ────────────
    // SÓ dispara se houver agente ATIVO (o toggle da Carol controla ligar/desligar).
    try {
      if (tel) {
        const { data: ag } = await sb
          .from("agente_sdr")
          .select("mensagem_abertura, ativo")
          .eq("ativo", true)
          .limit(1)
          .maybeSingle();
        if (ag && ag.ativo && ag.mensagem_abertura) {
          const EVO_URL = (Deno.env.get("EVOLUTION_API_URL") || "").replace(/\/$/, "");
          const EVO_KEY = Deno.env.get("EVOLUTION_API_KEY") || "";
          const EVO_INST = Deno.env.get("EVOLUTION_INSTANCE") || "arvex-agente-sdr";
          if (EVO_URL && EVO_KEY) {
            const primeiro = (nome || "").trim().split(" ")[0] || nome;
            const abertura = String(ag.mensagem_abertura).replace(/\{nome\}/g, primeiro);
            const baloes = abertura.split("||").map((b: string) => b.trim()).filter(Boolean);
            const H = { "apikey": EVO_KEY, "Content-Type": "application/json" };
            const num = tel.replace(/\D/g, "");
            // delays crescentes: cada balão chega espaçado (o Evolution mostra "digitando")
            for (let i = 0; i < baloes.length; i++) {
              await fetch(`${EVO_URL}/message/sendText/${EVO_INST}`, {
                method: "POST",
                headers: H,
                body: JSON.stringify({ number: num, text: baloes[i], delay: 500 + i * 2000 }),
              });
            }
            // registra a abertura no CRM (o lead vira 'contato')
            await sb.rpc("registrar_evento_lead", {
              p_tel: num, p_nome: nome, p_texto: abertura.replace(/\|\|/g, "\n\n"), p_autor: "agente",
            });
            console.log("abertura enviada:", num, baloes.length, "baloes");
          }
        } else {
          console.log("agente inativo — lead criado sem abordagem automatica");
        }
      }
    } catch (e) {
      console.log("abordagem automatica falhou (nao critico):", (e as Error).message);
    }

    return new Response("ok", { status: 200 });
  } catch (e) {
    console.log("ERRO:", e.message);
    return new Response("erro: " + e.message, { status: 500 });
  }
});
