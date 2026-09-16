const fs = require('fs');
const CUT0 = 39.30, CUT1 = 44.98, SH = CUT1 - CUT0, END = 50.43 - SH;
const BR = '\\N';
const raw = [
  [0.00, 'A gente não vai na|loja de quadrinhos,', 'pip'], [1.50, 'mas se os quadrinhos|estivessem no jornal,', 'pip'], [3.42, 'a gente leria.', 'pip'],
  [4.26, 'Quem disse isso foi esse|famoso empreendedor lendário'], [6.48, 'lá nos Estados Unidos.'],
  [7.30, 'E, ainda que simples,|essa frase'], [8.70, 'clareou para mim|ainda mais'], [9.72, 'como a próxima geração|de milionários'], [11.86, 'está sendo|construída aqui.'],
  [13.12, 'Porque preste atenção:'], [13.86, 'o Garfield era de graça|em todo jornal.'],
  [15.86, 'Foi assim que milhões|de pessoas'], [17.06, 'começaram a conhecê-lo.'], [17.90, 'Foi assim que você|provavelmente'], [19.30, 'começou a conhecê-lo.'],
  [20.98, 'E teve recorde mundial|de tirinhas mais publicadas'], [23.98, 'de todos os tempos.'],
  [24.72, 'Os bilhões vieram depois,'], [25.90, 'com camiseta, com caneca,', 'prod'], [27.08, 'filme, por aí vai.', 'prod'],
  [27.86, 'Os empreendedores|dessa geração'], [28.96, 'não estão construindo|lojas de quadrinhos,'], [30.88, 'nem deveriam.'],
  [31.68, 'Eles estão aparecendo|no jornal.'], [33.50, 'A maior vantagem|que existe hoje'], [34.76, 'é estar imerso onde|a atenção mora,'], [36.70, 'aqui.'],
  [37.26, 'E construir uma marca|para alavancar isso.'],
  [45.06, 'Porque ninguém desvia|o caminho'], [46.24, 'para ir para a|loja de quadrinhos.'], [47.88, 'Mas ninguém tira o quadrinho|da mão quando ele chega.'],
];
const c = raw.map(([t, x, k]) => [t >= CUT1 ? t - SH : t, x.split('|').join(BR), k]);
const ts = s => { const m = Math.floor(s / 60), se = (s % 60).toFixed(2).padStart(5, '0'); return `0:${String(m).padStart(2, '0')}:${se}`; };
let ev = '';
c.forEach(([t, x, k], i) => {
  let e = i + 1 < c.length ? c[i + 1][0] : END;
  if (t < CUT0 && e > CUT0) e = CUT0 - 0.05;
  const y = k === 'prod' ? 1275 : 1330;
  ev += `Dialogue: 0,${ts(t)},${ts(e)},C,,0,0,0,,{\\pos(540,${y})}${x}\n`;
});
const head = [
  '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1080', 'PlayResY: 1920', 'WrapStyle: 2', '',
  '[V4+ Styles]',
  'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
  'Style: C,Segoe UI,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,0.6,2.5,5,60,60,0,1', '',
  '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text', ''].join('\n');
fs.writeFileSync(__dirname + '/cap.ass', head + ev);
console.log('ok', c.length, END.toFixed(2));
