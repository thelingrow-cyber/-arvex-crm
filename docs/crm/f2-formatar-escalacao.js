// F2 Formatar + extração de marcador de sinalização (ADR-ESC-1). Remove antes de enviar.
let raw = ($json.output || '').trim();
let sinal = null, motivo = '';
const m = raw.match(/\n*\[(QUALIFICADO|ESCALAR)\]\s*([^\n]*)\s*$/i);
if (m) {
  sinal = m[1].toLowerCase();       // 'qualificado' | 'escalar'
  motivo = (m[2] || '').trim();
  raw = raw.slice(0, m.index).trim(); // tira o marcador — o lead não vê
}
const parts = raw.split('||').map(s => s.trim()).filter(Boolean);
let balao1, balao2;
if (parts.length >= 2) { balao1 = parts[0]; balao2 = parts.slice(1).join('\n\n'); }
else { balao1 = raw.replace(/\|\|/g, '\n\n'); balao2 = ''; }
const texto_resposta = parts.length ? parts.join('\n\n') : balao1;
return [{ json: { balao1, balao2, texto_resposta, sinal, motivo } }];
