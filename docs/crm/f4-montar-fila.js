// F4: monta a fila do poll, aplica os GATES (ADR-F4-2) e marca deve_tocar por lead.
const agentes = $('Buscar Agente').all().map(i => i.json).filter(a => a && a.instrucoes);
if (!agentes.length) return []; // sem agente ATIVO -> nao processa nada (gate global)
const agente = agentes[0];
const cadencia = agente.cadencia || { toques_horas: [4, 24, 48, 168], encerra_horas: 192 };
const promptFollowup = agente.prompt_followup ||
  'A conversa com este lead parou faz um tempo. Gere UM follow-up curto e natural pra reengajar, retomando o ultimo assunto que voces tocaram. Nao pareca cobranca, nao repita o que ja disse, sem travessao. Portugues do Brasil, tom leve e humano.';

const devidos = $('Buscar Devidos').all().map(i => i.json).filter(f => f && f.lead_id);

const out = [];
for (const f of devidos) {
  const acts = (f.activities || []).map(a => ({
    autor: a.autor || null,
    text: a.text != null ? a.text : (a.texto || ''),
  }));
  // GATES (ADR-F4-2, ordem importa)
  let deve = true, motivo = '';
  if (f.agente_pausado === true) { deve = false; motivo = 'humano assumiu'; }
  else if (f.lead_status !== 'contato') { deve = false; motivo = 'lead avancou de etapa'; }
  else {
    let ultAgente = -1, ultLead = -1;
    for (let i = 0; i < acts.length; i++) {
      if (acts[i].autor === 'agente' || acts[i].autor === 'humano') ultAgente = i;
      if (acts[i].autor === 'lead') ultLead = i;
    }
    if (ultLead > ultAgente) { deve = false; motivo = 'lead respondeu'; }
  }
  out.push({ json: {
    followup_id: f.id, lead_id: f.lead_id, tel: f.tel, nome: f.nome,
    tentativa: f.tentativa, toques: cadencia.toques_horas, prompt_followup: promptFollowup,
    deve_tocar: deve, motivo,
  }});
}
return out;
