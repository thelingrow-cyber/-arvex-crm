'use strict';

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = __dirname;
const SLIDES = path.join(OUT, 'slides');
fs.mkdirSync(SLIDES, { recursive: true });

const C = {
  coal: '#091013',
  coal2: '#10181B',
  ivory: '#F0ECE3',
  paper: '#E5DED2',
  gold: '#C5A266',
  lightMuted: '#AAA7A0',
  darkMuted: '#5C6263',
  lineDark: '#293237',
  lineLight: '#C5BCAF',
};

const sources = {
  cover: path.join(OUT, 'assets/podcast-04.png'),
  architecture: path.join(OUT, 'assets/rearquitetura-editorial-generated.png'),
};

const data = Object.fromEntries(Object.entries(sources).map(([key, file]) => {
  const ext = path.extname(file).toLowerCase();
  const mime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : 'image/png';
  return [key, `data:${mime};base64,${fs.readFileSync(file).toString('base64')}`];
}));

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function tspans(lines, x, y, lh, attrs = '') {
  return `<text x="${x}" y="${y}" ${attrs}>${lines.map((line, i) =>
    `<tspan x="${x}" dy="${i ? lh : 0}">${esc(line)}</tspan>`).join('')}</text>`;
}

function defs(extra = '') {
  return `<defs>
    <filter id="documentaryMono" color-interpolation-filters="sRGB">
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncR type="linear" slope="1.12" intercept="-.035"/><feFuncG type="linear" slope="1.12" intercept="-.035"/><feFuncB type="linear" slope="1.12" intercept="-.035"/></feComponentTransfer>
    </filter>
    <filter id="warm" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix" values=".30 .59 .11 0 0  .279 .549 .102 0 0  .234 .460 .086 0 0  0 0 0 1 0"/>
      <feComponentTransfer><feFuncR type="linear" slope="1.12" intercept="-.035"/><feFuncG type="linear" slope="1.12" intercept="-.035"/><feFuncB type="linear" slope="1.12" intercept="-.035"/></feComponentTransfer>
    </filter>
    <filter id="warmSoft" color-interpolation-filters="sRGB">
      <feColorMatrix type="saturate" values=".38"/>
      <feComponentTransfer><feFuncR type="linear" slope="1.05"/><feFuncG type="linear" slope="1.01"/><feFuncB type="linear" slope=".88"/></feComponentTransfer>
    </filter>
    <filter id="grain" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency=".72" numOctaves="3" seed="23"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="table" tableValues="0 .052"/></feComponentTransfer>
    </filter>
    <radialGradient id="mineralWash" cx="82%" cy="8%" r="92%"><stop offset="0" stop-color="#24404A" stop-opacity=".34"/><stop offset=".44" stop-color="#14252B" stop-opacity=".18"/><stop offset="1" stop-color="${C.coal}" stop-opacity="0"/></radialGradient>
    <radialGradient id="paperWash" cx="16%" cy="5%" r="100%"><stop offset="0" stop-color="#FFF9ED" stop-opacity=".62"/><stop offset=".54" stop-color="#EEE7DB" stop-opacity=".24"/><stop offset="1" stop-color="#C9BCA8" stop-opacity=".16"/></radialGradient>
    <linearGradient id="fadeLeft" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${C.coal}"/><stop offset=".62" stop-color="${C.coal}" stop-opacity=".88"/><stop offset="1" stop-color="${C.coal}" stop-opacity="0"/></linearGradient>
    <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.coal}" stop-opacity="0"/><stop offset=".55" stop-color="${C.coal}" stop-opacity=".72"/><stop offset="1" stop-color="${C.coal}"/></linearGradient>
    <linearGradient id="coverFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.coal}" stop-opacity="0"/><stop offset=".2" stop-color="${C.coal}" stop-opacity=".28"/><stop offset=".42" stop-color="${C.coal}" stop-opacity=".68"/><stop offset=".72" stop-color="${C.coal}" stop-opacity=".91"/><stop offset="1" stop-color="${C.coal}" stop-opacity=".98"/></linearGradient>
    ${extra}
  </defs>`;
}

function logo(x = 72, y = 52, inverse = true, scale = .255) {
  const fg = inverse ? C.ivory : C.coal2;
  return `<g transform="translate(${x} ${y}) scale(${scale})">
    <g fill="none" stroke="${fg}" stroke-width="27" stroke-linecap="square" stroke-linejoin="miter">
      <path d="M14 128 58 12"/><path d="M80 12 126 128"/><path d="M38 92h64"/>
    </g>
    <g fill="${fg}" fill-rule="evenodd">
      <path d="M160 140V0h58c38 0 61 20 61 51 0 23-13 40-35 47l39 42h-43l-34-38h-12v38Zm34-68h21c19 0 29-7 29-21 0-14-10-21-29-21h-21Z"/>
      <path d="M310 0h38l34 103L416 0h38l-55 140h-34Z"/>
      <path d="M480 0h114v30h-80v24h68v30h-68v26h80v30H480Z"/>
      <path d="M620 0h40l32 48 32-48h40l-50 70 50 70h-40l-32-48-32 48h-40l50-70Z"/>
    </g>
    <rect x="680" y="58" width="24" height="24" rx="2" fill="${C.gold}" transform="rotate(45 692 70)"/>
  </g>`;
}

function image(key, x, y, w, h, align = 'xMidYMid', filter = 'warm') {
  const filterAttr = filter ? ` filter="url(#${filter})"` : '';
  return `<image href="${data[key]}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="${align} slice"${filterAttr}/>`;
}

function diamond(x, y, size = 14) {
  return `<rect x="${x - size / 2}" y="${y - size / 2}" width="${size}" height="${size}" rx="1" fill="${C.gold}" transform="rotate(45 ${x} ${y})"/>`;
}

function chrome(page, inverse = true, logoInverse = inverse) {
  const fg = inverse ? C.ivory : C.coal2;
  const muted = inverse ? C.lightMuted : C.darkMuted;
  const line = inverse ? 'rgba(242,240,234,.22)' : 'rgba(16,18,22,.18)';
  return `${logo(72, 50, logoInverse)}
    <line x1="72" y1="1268" x2="1008" y2="1268" stroke="${line}" stroke-width="2"/>
    <text x="1008" y="1311" text-anchor="end" fill="${fg}" font-size="20" font-weight="850" letter-spacing="2">${String(page).padStart(2, '0')} / 07</text>`;
}

function shell(bg, body, page, inverse = true, logoInverse = inverse) {
  const atmosphere = inverse
    ? `<rect width="1080" height="1350" fill="url(#mineralWash)"/>`
    : `<rect width="1080" height="1350" fill="url(#paperWash)"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" style="font-family:Inter,Arial,Helvetica,sans-serif">
    ${defs()}<rect width="1080" height="1350" fill="${bg}"/>${atmosphere}${body}${chrome(page, inverse, logoInverse)}
    <rect width="1080" height="1350" filter="url(#grain)" opacity=".62" pointer-events="none"/>
  </svg>`;
}

function slide1() {
  const body = `
    <g filter="url(#documentaryMono)">
      ${image('cover', 0, 0, 1080, 1350, 'xMidYMid', null)}
      <rect width="1080" height="1350" fill="${C.coal}" opacity=".14"/>
      <rect x="0" y="410" width="1080" height="940" fill="url(#coverFade)"/>
    </g>
    ${tspans(['A ARQUITETURA DAS', 'EMPRESAS QUE VÃO', 'DOMINAR SEUS MERCADOS', 'EM 2027'], 72, 730, 72,
      `fill="${C.ivory}" font-size="62" font-weight="900" letter-spacing="-2.3"`)}
    <line x1="72" y1="1040" x2="620" y2="1040" stroke="${C.ivory}" stroke-opacity=".58" stroke-width="2"/>
    ${tspans(['E como construir a sua antes', 'dos seus concorrentes.'], 72, 1100, 39,
      `fill="${C.ivory}" font-size="30" font-weight="700"`)}
    <text x="540" y="1210" text-anchor="middle" fill="${C.gold}" font-size="18" font-weight="850" letter-spacing="2.3">ARRASTE PARA O LADO  →</text>`;
  return shell(C.coal, body, 1, true);
}

function slide2() {
  const body = `
    <text x="72" y="212" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2.8">O JOGO VAI VIRAR</text>
    ${tspans(['EM 2027, TER IA', 'NÃO SERÁ VANTAGEM.'], 72, 300, 82,
      `fill="${C.ivory}" font-size="78" font-weight="900" letter-spacing="-3"`)}
    <line x1="540" y1="500" x2="540" y2="990" stroke="${C.gold}" stroke-width="3"/>
    ${diamond(540, 745, 15)}
    <text x="72" y="590" fill="${C.lightMuted}" font-size="22" font-weight="850" letter-spacing="2">ADICIONAR IA</text>
    ${tspans(['modelos', 'agentes', 'ferramentas'], 72, 665, 54,
      `fill="${C.lightMuted}" font-size="40" font-weight="650"`)}
    <text x="595" y="590" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2">A VANTAGEM</text>
    ${tspans(['REDESENHAR', 'A EMPRESA'], 595, 682, 66,
      `fill="${C.ivory}" font-size="56" font-weight="900" letter-spacing="-2.1"`)}
    ${tspans(['contexto', 'fluxo', 'execução'], 595, 875, 45,
      `fill="${C.lightMuted}" font-size="31" font-weight="650"`)}
    <line x1="72" y1="1065" x2="1008" y2="1065" stroke="${C.lineDark}" stroke-width="2"/>
    <text x="72" y="1130" fill="${C.ivory}" font-size="31" font-weight="700">O modelo será acessível.</text>
    <text x="72" y="1185" fill="${C.gold}" font-size="42" font-weight="900">A ARQUITETURA SERÁ A VANTAGEM.</text>`;
  return shell(C.coal, body, 2, true);
}

function note(x, y, n, lines, anchorX, anchorY) {
  return `<g>
    <path d="M${x + 26} ${y + 34}L${anchorX} ${anchorY}" fill="none" stroke="${C.gold}" stroke-width="2"/>
    ${diamond(anchorX, anchorY, 10)}
    <circle cx="${x}" cy="${y}" r="25" fill="${C.coal}"/><text x="${x}" y="${y + 9}" text-anchor="middle" fill="${C.gold}" font-size="25" font-weight="900">${n}</text>
    ${tspans(lines, x + 40, y - 3, 32, `fill="${C.coal}" font-size="25" font-weight="750"`)}
  </g>`;
}

function slide3() {
  const body = `
    <text x="872" y="420" fill="${C.coal}" opacity=".045" font-size="390" font-weight="900">01</text>
    <text x="72" y="205" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2.8">1º MOVIMENTO</text>
    ${tspans(['TORNAR A', 'OPERAÇÃO LEGÍVEL.'], 72, 292, 84,
      `fill="${C.coal}" font-size="80" font-weight="900" letter-spacing="-3"`)}
    <text x="72" y="490" fill="${C.darkMuted}" font-size="31" font-weight="650">Antes de automatizar, descubra:</text>
    <line x1="72" y1="550" x2="1008" y2="550" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="625" fill="${C.gold}" font-size="38" font-weight="900">01</text><text x="155" y="625" fill="${C.coal}" font-size="34" font-weight="800">Onde o lead deixa de avançar?</text>
    <line x1="72" y1="680" x2="1008" y2="680" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="755" fill="${C.gold}" font-size="38" font-weight="900">02</text><text x="155" y="755" fill="${C.coal}" font-size="34" font-weight="800">O que se repete todos os dias?</text>
    <line x1="72" y1="810" x2="1008" y2="810" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="885" fill="${C.gold}" font-size="38" font-weight="900">03</text><text x="155" y="885" fill="${C.coal}" font-size="34" font-weight="800">O que ainda depende do dono?</text>
    <line x1="72" y1="940" x2="1008" y2="940" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="1015" fill="${C.gold}" font-size="38" font-weight="900">04</text><text x="155" y="1015" fill="${C.coal}" font-size="34" font-weight="800">Onde o contexto se perde?</text>
    <line x1="72" y1="1070" x2="1008" y2="1070" stroke="${C.lineLight}" stroke-width="2"/>
    ${tspans(['O GARGALO REVELA', 'A PRIMEIRA PEÇA.'], 72, 1132, 51,
      `fill="${C.coal}" font-size="47" font-weight="900" letter-spacing="-1.4"`)}
    <text x="1008" y="1215" text-anchor="end" fill="${C.darkMuted}" font-size="19" font-weight="650">Sem diagnóstico, a IA executa o mesmo erro mais rápido.</text>`;
  return shell(C.ivory, body, 3, false);
}

function slide4() {
  const body = `
    <text x="72" y="205" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2.8">2º MOVIMENTO</text>
    ${tspans(['REARQUITETAR COMO', 'O TRABALHO ACONTECE.'], 72, 292, 76,
      `fill="${C.ivory}" font-size="72" font-weight="900" letter-spacing="-2.8"`)}
    ${image('architecture', 360, 420, 720, 780, 'xMidYMid', null)}
    <rect x="330" y="390" width="750" height="840" fill="url(#fadeLeft)" opacity=".82"/>
    <rect x="0" y="930" width="1080" height="310" fill="url(#fadeBottom)" opacity=".72"/>
    ${tspans(['Não é “qual ferramenta comprar?”.', 'É: como operaríamos se começássemos hoje?'], 72, 485, 40,
      `fill="${C.lightMuted}" font-size="28" font-weight="650"`)}
    <text x="72" y="660" fill="${C.gold}" font-size="21" font-weight="900" letter-spacing="2">PESSOAS</text>
    <text x="72" y="700" fill="${C.ivory}" font-size="28" font-weight="750">julgam e se relacionam</text>
    <text x="72" y="785" fill="${C.gold}" font-size="21" font-weight="900" letter-spacing="2">SISTEMAS</text>
    <text x="72" y="825" fill="${C.ivory}" font-size="28" font-weight="750">guardam regras e contexto</text>
    <text x="72" y="910" fill="${C.gold}" font-size="21" font-weight="900" letter-spacing="2">IA</text>
    <text x="72" y="950" fill="${C.ivory}" font-size="28" font-weight="750">executa e acompanha</text>
    <line x1="72" y1="1080" x2="1008" y2="1080" stroke="${C.gold}" stroke-opacity=".7" stroke-width="2"/>
    <text x="72" y="1140" fill="${C.ivory}" font-size="31" font-weight="800">AI Native é IA no núcleo da operação.</text>
    <text x="72" y="1185" fill="${C.gold}" font-size="31" font-weight="900">Não instalada por cima.</text>`;
  return shell(C.coal, body, 4, true);
}

function pair(y, left, right) {
  return `<g>
    <text x="88" y="${y}" fill="${C.lightMuted}" font-size="24" font-weight="800">${esc(left)}</text>
    <line x1="410" y1="${y - 9}" x2="514" y2="${y - 9}" stroke="${C.gold}" stroke-width="2"/><path d="M514 ${y - 9}l-14-9v18Z" fill="${C.gold}"/>
    <text x="554" y="${y}" fill="${C.ivory}" font-size="25" font-weight="900">${esc(right)}</text>
  </g>`;
}

function slide5() {
  const body = `
    <text x="72" y="205" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2.8">APLICAÇÃO PRÁTICA</text>
    ${tspans(['QUANDO A OPERAÇÃO', 'DEIXA DE DEPENDER', 'DA MEMÓRIA.'], 72, 292, 72,
      `fill="${C.coal}" font-size="68" font-weight="900" letter-spacing="-2.6"`)}
    <text x="72" y="555" fill="${C.darkMuted}" font-size="19" font-weight="900" letter-spacing="2">ANTES</text>
    <text x="610" y="555" fill="${C.gold}" font-size="19" font-weight="900" letter-spacing="2">DEPOIS</text>
    <line x1="72" y1="600" x2="1008" y2="600" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="665" fill="${C.darkMuted}" font-size="31" font-weight="700">ESPERA</text><text x="505" y="665" fill="${C.gold}" font-size="30" font-weight="900">→</text><text x="610" y="665" fill="${C.coal}" font-size="32" font-weight="900">RESPOSTA</text>
    <line x1="72" y1="720" x2="1008" y2="720" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="785" fill="${C.darkMuted}" font-size="31" font-weight="700">DEPENDÊNCIA</text><text x="505" y="785" fill="${C.gold}" font-size="30" font-weight="900">→</text><text x="610" y="785" fill="${C.coal}" font-size="32" font-weight="900">CONTINUIDADE</text>
    <line x1="72" y1="840" x2="1008" y2="840" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="905" fill="${C.darkMuted}" font-size="31" font-weight="700">CONTROLE TOTAL</text><text x="505" y="905" fill="${C.gold}" font-size="30" font-weight="900">→</text><text x="610" y="905" fill="${C.coal}" font-size="32" font-weight="900">EXCEÇÕES</text>
    <line x1="72" y1="960" x2="1008" y2="960" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="1030" fill="${C.gold}" font-size="22" font-weight="900" letter-spacing="2">AUTONOMIA</text>
    ${tspans(['NÃO ELIMINA PESSOAS.', 'LIBERA PESSOAS PARA JULGAMENTO,', 'RELACIONAMENTO E EXCEÇÃO.'], 72, 1090, 45,
      `fill="${C.coal}" font-size="38" font-weight="900" letter-spacing="-1"`)} `;
  return shell(C.ivory, body, 5, false);
}

function frame(key, x, y, w, h, n, label, align = 'xMidYMid', filter = 'warm') {
  return `<g>
    <rect x="${x - 8}" y="${y - 8}" width="${w + 16}" height="${h + 16}" fill="${C.coal}"/>
    ${image(key, x, y, w, h, align, filter)}
    <rect x="${x}" y="${y + h - 62}" width="${w}" height="62" fill="${C.coal}" fill-opacity=".86"/>
    <text x="${x + 18}" y="${y + h - 22}" fill="${C.gold}" font-size="23" font-weight="900">0${n}</text>
    <text x="${x + 62}" y="${y + h - 22}" fill="${C.ivory}" font-size="22" font-weight="850">${label}</text>
  </g>`;
}

function slide6() {
  const body = `
    <text x="72" y="205" fill="${C.gold}" font-size="22" font-weight="850" letter-spacing="2.8">3º MOVIMENTO</text>
    ${tspans(['IMPLEMENTAR', 'UMA PEÇA POR VEZ.'], 72, 292, 82,
      `fill="${C.ivory}" font-size="78" font-weight="900" letter-spacing="-3"`)}
    ${tspans(['Não se reconstrói', 'uma empresa inteira', 'de uma vez.'], 700, 450, 34,
      `fill="${C.lightMuted}" font-size="25" font-weight="650"`)}
    <path d="M100 555L270 690L440 825L610 960L805 1090" fill="none" stroke="${C.gold}" stroke-width="3"/>
    ${diamond(100, 555, 14)}${diamond(270, 690, 14)}${diamond(440, 825, 14)}${diamond(610, 960, 14)}${diamond(805, 1090, 18)}
    <text x="72" y="530" fill="${C.gold}" font-size="22" font-weight="900">01</text><text x="112" y="530" fill="${C.ivory}" font-size="35" font-weight="850">DIAGNOSTICAR</text>
    <text x="242" y="665" fill="${C.gold}" font-size="22" font-weight="900">02</text><text x="282" y="665" fill="${C.ivory}" font-size="35" font-weight="850">REDESENHAR</text>
    <text x="412" y="800" fill="${C.gold}" font-size="22" font-weight="900">03</text><text x="452" y="800" fill="${C.ivory}" font-size="35" font-weight="850">INSTALAR</text>
    <text x="582" y="935" fill="${C.gold}" font-size="22" font-weight="900">04</text><text x="622" y="935" fill="${C.ivory}" font-size="35" font-weight="850">CONECTAR</text>
    <text x="777" y="1065" fill="${C.gold}" font-size="22" font-weight="900">05</text><text x="817" y="1065" fill="${C.ivory}" font-size="35" font-weight="850">MEDIR</text>
    ${tspans(['CADA PEÇA FUNCIONA', 'ANTES DA PRÓXIMA.'], 72, 1135, 52,
      `fill="${C.ivory}" font-size="48" font-weight="900" letter-spacing="-1.5"`)} `;
  return shell(C.coal, body, 6, true);
}

function slide7() {
  const body = `
    <rect x="0" y="0" width="1080" height="930" fill="${C.ivory}"/>
    <text x="72" y="215" fill="${C.coal}" font-size="68" font-weight="900" letter-spacing="-2.5">A VANTAGEM NÃO ESTÁ</text>
    <text x="72" y="288" fill="${C.coal}" font-size="68" font-weight="900" letter-spacing="-2.5">EM TER IA.</text>
    <text x="72" y="445" fill="${C.coal}" font-size="93" font-weight="900" letter-spacing="-4">ESTÁ EM</text>
    <text x="72" y="545" fill="${C.coal}" font-size="104" font-weight="900" letter-spacing="-4.5">FAZÊ-LA</text>
    <text x="72" y="650" fill="${C.gold}" font-size="104" font-weight="900" letter-spacing="-4.5">FUNCIONAR.</text>
    <line x1="72" y1="730" x2="1008" y2="730" stroke="${C.lineLight}" stroke-width="2"/>
    <text x="72" y="790" fill="${C.gold}" font-size="22" font-weight="900">01</text><text x="112" y="790" fill="${C.coal}" font-size="22" font-weight="850">DIAGNOSTICAR</text>
    <text x="382" y="790" fill="${C.gold}" font-size="22" font-weight="900">02</text><text x="422" y="790" fill="${C.coal}" font-size="22" font-weight="850">REARQUITETAR</text>
    <text x="728" y="790" fill="${C.gold}" font-size="22" font-weight="900">03</text><text x="768" y="790" fill="${C.coal}" font-size="22" font-weight="850">IMPLEMENTAR</text>
    <text x="72" y="995" fill="${C.ivory}" font-size="27" font-weight="700">Ser AI Native é o destino. A gente começa pela parte que está travando.</text>
    ${tspans(['QUAL PARTE DA SUA EMPRESA', 'AINDA DEPENDE DE VOCÊ?'], 72, 1085, 52,
      `fill="${C.ivory}" font-size="47" font-weight="900" letter-spacing="-1.4"`)}
    <text x="72" y="1215" fill="${C.gold}" font-size="25" font-weight="900">CONHEÇA AS SOLUÇÕES DA ARVEX →</text>`;
  return shell(C.coal, body, 7, true, false);
}

const slides = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6(), slide7()];

async function build() {
  const pngs = [];
  for (let i = 0; i < slides.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    const svgFile = path.join(SLIDES, `${n}.svg`);
    const pngFile = path.join(SLIDES, `${n}.png`);
    fs.writeFileSync(svgFile, slides[i]);
    await sharp(Buffer.from(slides[i])).png().toFile(pngFile);
    pngs.push(pngFile);
  }

  const thumbW = 324, thumbH = 405, gap = 28, margin = 44;
  const canvasW = margin * 2 + thumbW * 4 + gap * 3;
  const canvasH = margin * 2 + thumbH * 2 + gap;
  const comps = [];
  for (let i = 0; i < pngs.length; i++) {
    comps.push({
      input: await sharp(pngs[i]).resize(thumbW, thumbH).png().toBuffer(),
      left: margin + (i % 4) * (thumbW + gap),
      top: margin + Math.floor(i / 4) * (thumbH + gap),
    });
  }
  await sharp({ create: { width: canvasW, height: canvasH, channels: 4, background: C.paper } })
    .composite(comps).png().toFile(path.join(OUT, 'contact-sheet.png'));

  const figures = pngs.map((_, i) => {
    const n = String(i + 1).padStart(2, '0');
    return `<figure><img src="slides/${n}.png" alt="Slide ${i + 1}"><figcaption>Slide ${i + 1}</figcaption></figure>`;
  }).join('');
  fs.writeFileSync(path.join(OUT, 'index.html'), `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARVEX — Carrossel 01 v2</title><style>*{box-sizing:border-box}body{margin:0;background:#091013;color:#f0ece3;font-family:Inter,Arial,sans-serif}header{padding:40px 4vw;border-bottom:1px solid #293237}h1{margin:0 0 10px;font-size:42px}p{margin:0;color:#aaa7a0}.grid{padding:34px 4vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}figure{margin:0}img{display:block;width:100%;border:1px solid #293237}figcaption{padding:10px 0;color:#aaa7a0;font-weight:700}</style></head><body><header><h1>ARVEX — A arquitetura das empresas de 2027</h1><p>Documental Tecnológico Mineral · v2 · 1080 × 1350</p></header><main class="grid">${figures}</main></body></html>`);
}

build().catch((err) => { console.error(err); process.exitCode = 1; });
