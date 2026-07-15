// F4: depois de enviar o toque, calcula o proximo estado (ADR-F4-3): avanca ou encerra.
const it = $('Loop Followup').item.json;
const toques = it.toques || [4, 24, 48, 168];
const proximo = it.tentativa + 1;
if (proximo < toques.length) {
  const horas = toques[proximo];
  const agendado = new Date(Date.now() + horas * 3600 * 1000).toISOString();
  return [{ json: { encerra: false, followup_id: it.followup_id, lead_id: it.lead_id, tentativa: proximo, agendado_para: agendado } }];
}
return [{ json: { encerra: true, followup_id: it.followup_id, lead_id: it.lead_id } }];
