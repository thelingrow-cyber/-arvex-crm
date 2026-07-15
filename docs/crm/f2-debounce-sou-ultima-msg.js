// Debounce: só a ÚLTIMA mensagem de um burst responde, e ela agrupa todas as mensagens
// que o lead mandou desde a última resposta do agente/humano.
const atual = $('Extrair Dados Evolution').item.json; // {tel, texto, nome, ...}
const conv = ($('Buscar Conversa').all().map(i => i.json)[0]) || {};
const acts = (conv.activities || []).map(a => ({
  text: a.text != null ? a.text : (a.texto || ''),
  autor: a.autor || null,
  date: a.date != null ? a.date : (a.data ? Date.parse(a.data) : 0),
})).filter(a => a.text);

// última mensagem do lead registrada
const doLead = acts.filter(a => a.autor === 'lead');
const ultimaLead = doLead[doLead.length - 1];

// se a última msg do lead não é a que disparou esta execução, chegou outra depois -> aborta
// (a execução da mensagem mais nova é que vai responder o burst inteiro)
if (!ultimaLead || ultimaLead.text.trim() !== String(atual.texto || '').trim()) {
  return [];
}

// sou a última: agrupa tudo que o lead mandou desde a última resposta do agente/humano
let ultimoAgente = -1;
for (let i = acts.length - 1; i >= 0; i--) {
  if (acts[i].autor === 'agente' || acts[i].autor === 'humano') { ultimoAgente = i; break; }
}
const novas = acts.slice(ultimoAgente + 1).filter(a => a.autor === 'lead').map(a => a.text.trim());
const texto_agrupado = (novas.join('\n') || String(atual.texto || '')).trim();

return [{ json: Object.assign({}, atual, { texto_agrupado }) }];
