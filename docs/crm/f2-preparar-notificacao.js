// F2 escalação: monta a notificação pra Thalita. no-op se sem número (ADR-ESC-4, não inventa).
const cfg = ($('Buscar Config Agente').all().map(i => i.json)[0]) || {};
const fmt = $('Formatar Resposta').item.json;
const lead = $('Extrair Dados Evolution').item.json;
if (cfg.notificar_ativo !== true || !cfg.notificar_contato) return []; // desligado ou sem numero -> nao envia
const nome = lead.nome || lead.tel;
let texto;
if (fmt.sinal === 'qualificado') {
  texto = '🔔 [Carol] ' + nome + ' (' + lead.tel + ') foi QUALIFICADO. Bora marcar a call. Abrir no CRM.';
} else if (fmt.sinal === 'escalar') {
  texto = '🔔 [Carol] ' + nome + ' (' + lead.tel + ') ESCALADO: ' + (fmt.motivo || 'precisa de humano') + '. Abrir no CRM.';
} else {
  return [];
}
return [{ json: { number: String(cfg.notificar_contato).replace(/\D/g, ''), text: texto } }];
