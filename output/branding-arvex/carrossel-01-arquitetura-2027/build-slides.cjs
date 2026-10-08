const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const OUT = __dirname;
const SLIDES = path.join(OUT, 'slides');
fs.mkdirSync(SLIDES, { recursive: true });

const C = {
  ink: '#090D14',
  ink2: '#101722',
  ink3: '#182131',
  ivory: '#F2F0E9',
  paper: '#E8E4DA',
  muted: '#A7AFBC',
  mutedDark: '#586170',
  indigo: '#5B6CFF',
  indigo2: '#8793FF',
  line: '#2A3445',
  alert: '#C8A96E',
};

const esc = (s) => String(s)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;');

function tspans(lines, x, y, lineHeight, attrs = '') {
  return `<text x="${x}" y="${y}" ${attrs}>${lines.map((line, i) =>
    `<tspan x="${x}" dy="${i ? lineHeight : 0}">${esc(line)}</tspan>`).join('')}</text>`;
}

function wordmark(x = 76, y = 62, inverse = true) {
  const fg = inverse ? C.ivory : C.ink;
  return `
    <g transform="translate(${x} ${y})">
      <path d="M0 0h38v10H10v28H0Z" fill="${fg}"/>
      <path d="M58 58H20V48h28V20h10Z" fill="${fg}"/>
      <rect x="25" y="25" width="10" height="10" rx="1" fill="${C.indigo}" transform="rotate(45 30 30)"/>
      <text x="78" y="43" fill="${fg}" font-size="34" font-weight="900" letter-spacing="2">ARVEX</text>
    </g>`;
}

function chrome(page, inverse = true, label = 'ARQUITETURA OPERACIONAL') {
  const fg = inverse ? C.ivory : C.ink;
  const muted = inverse ? C.muted : C.mutedDark;
  return `
    ${wordmark(76, 54, inverse)}
    <text x="1004" y="82" text-anchor="end" fill="${muted}" font-size="20" font-weight="700" letter-spacing="2.6">${label}</text>
    <line x1="76" y1="130" x2="1004" y2="130" stroke="${inverse ? C.line : '#C8C2B6'}" stroke-width="2"/>
    <line x1="76" y1="1264" x2="1004" y2="1264" stroke="${inverse ? C.line : '#C8C2B6'}" stroke-width="2"/>
    <text x="76" y="1308" fill="${muted}" font-size="20" font-weight="700" letter-spacing="2.2">REGISTRO 01</text>
    <text x="1004" y="1308" text-anchor="end" fill="${fg}" font-size="20" font-weight="800" letter-spacing="2.2">${String(page).padStart(2, '0')}—07</text>`;
}

function defs() {
  return `<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${C.ink}"/><stop offset="1" stop-color="#111B2B"/>
    </linearGradient>
    <linearGradient id="indigoGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${C.indigo2}"/><stop offset="1" stop-color="${C.indigo}"/>
    </linearGradient>
    <filter id="grain" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="2" seed="17"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="table" tableValues="0 0.035"/></feComponentTransfer>
    </filter>
    <pattern id="grid" width="54" height="54" patternUnits="userSpaceOnUse">
      <path d="M54 0H0V54" fill="none" stroke="#8793FF" stroke-opacity="0.08" stroke-width="1"/>
    </pattern>
  </defs>`;
}

function shell(bg, body, page, inverse = true, label) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" style="font-family: Inter, Arial, Helvetica, sans-serif">
    ${defs()}
    <rect width="1080" height="1350" fill="${bg}"/>
    ${body}
    ${chrome(page, inverse, label)}
    <rect width="1080" height="1350" filter="url(#grain)" opacity=".7"/>
  </svg>`;
}

function slide1() {
  const body = `
    <rect width="1080" height="1350" fill="url(#bg)"/>
    <rect width="1080" height="1350" fill="url(#grid)"/>
    <text x="516" y="1130" fill="none" stroke="#8B96AA" stroke-opacity=".16" stroke-width="3"
      font-size="420" font-weight="900" letter-spacing="-24">2027</text>
    <path d="M820 202h184v184" fill="none" stroke="${C.ivory}" stroke-width="18"/>
    <path d="M1004 512H820V328" fill="none" stroke="${C.ivory}" stroke-width="18"/>
    <rect x="888" y="345" width="50" height="50" rx="4" fill="url(#indigoGlow)" transform="rotate(45 913 370)"/>
    <text x="76" y="228" fill="${C.indigo2}" font-size="25" font-weight="800" letter-spacing="3.2">UMA PREVISÃO PARA QUEM QUER CHEGAR ANTES</text>
    ${tspans(['A ARQUITETURA QUE', 'AS EMPRESAS VÃO', 'USAR PARA'], 76, 318, 72,
      `fill="${C.ivory}" font-size="65" font-weight="900" letter-spacing="-2.6"`)}
    ${tspans(['DOMINAR', 'SEUS MERCADOS'], 76, 572, 104,
      `fill="${C.ivory}" font-size="102" font-weight="900" letter-spacing="-5"`)}
    <rect x="76" y="790" width="388" height="86" rx="4" fill="${C.indigo}"/>
    <text x="105" y="849" fill="${C.ivory}" font-size="48" font-weight="900" letter-spacing="-1">EM 2027</text>
    <line x1="76" y1="944" x2="714" y2="944" stroke="${C.line}" stroke-width="3"/>
    ${tspans(['E como você pode se antecipar', 'aos seus concorrentes.'], 76, 1008, 48,
      `fill="${C.ivory}" font-size="37" font-weight="600" letter-spacing="-.5"`)}
    <path d="M898 1070h106v106" fill="none" stroke="${C.indigo}" stroke-width="5"/>
    <circle cx="1004" cy="1176" r="7" fill="${C.indigo}"/>`;
  return shell(C.ink, body, 1, true, 'VISÃO / 2027');
}

function slide2() {
  const body = `
    <rect x="0" y="0" width="1080" height="1350" fill="url(#bg)"/>
    <text x="76" y="228" fill="${C.indigo2}" font-size="24" font-weight="800" letter-spacing="3">A PREVISÃO</text>
    ${tspans(['EM 2027, TER IA', 'NÃO SERÁ VANTAGEM.'], 76, 305, 82,
      `fill="${C.ivory}" font-size="75" font-weight="900" letter-spacing="-3"`)}
    ${tspans(['Os mesmos modelos, agentes e ferramentas estarão', 'disponíveis para todos os seus concorrentes.'], 76, 515, 42,
      `fill="${C.muted}" font-size="30" font-weight="500"`)}
    <rect x="76" y="626" width="414" height="294" rx="8" fill="#141B26" stroke="${C.line}" stroke-width="2"/>
    <text x="108" y="682" fill="${C.muted}" font-size="19" font-weight="800" letter-spacing="2.5">ADICIONAR IA</text>
    <g fill="none" stroke="#717A89" stroke-width="3" opacity=".65">
      <rect x="113" y="737" width="88" height="88" rx="8"/><rect x="259" y="716" width="68" height="68" rx="7"/>
      <rect x="368" y="772" width="88" height="88" rx="8"/><rect x="243" y="822" width="54" height="54" rx="6"/>
    </g>
    <line x1="221" y1="776" x2="250" y2="757" stroke="#717A89" stroke-dasharray="7 8"/>
    <line x1="330" y1="755" x2="370" y2="801" stroke="#717A89" stroke-dasharray="7 8"/>
    <text x="108" y="893" fill="${C.muted}" font-size="22">peças soltas</text>
    <rect x="514" y="626" width="490" height="294" rx="8" fill="#111B2B" stroke="${C.indigo}" stroke-width="3"/>
    <text x="546" y="682" fill="${C.indigo2}" font-size="19" font-weight="800" letter-spacing="2.5">REDESENHAR A EMPRESA</text>
    <g fill="none" stroke="${C.indigo2}" stroke-width="3">
      <path d="M570 754h100v100H570Z"/><path d="M848 754h100v100H848Z"/>
      <path d="M694 714h100v100H694Z"/><path d="M694 836h100v54H694Z"/>
      <line x1="670" y1="804" x2="694" y2="764"/><line x1="794" y1="764" x2="848" y2="804"/><line x1="744" y1="814" x2="744" y2="836"/>
    </g>
    <rect x="724" y="774" width="40" height="40" rx="3" fill="${C.indigo}" transform="rotate(45 744 794)"/>
    <text x="546" y="893" fill="${C.ivory}" font-size="22">um sistema em execução</text>
    ${tspans(['A diferença estará entre empresas que apenas adicionam IA', 'ao que já existe e empresas redesenhadas para transformar', 'inteligência em execução.'], 76, 994, 39,
      `fill="${C.ivory}" font-size="29" font-weight="500"`)}
    <text x="76" y="1106" fill="${C.muted}" font-size="23" font-weight="800">E essa arquitetura começa por três movimentos. →</text>
    <rect x="76" y="1124" width="928" height="102" rx="5" fill="${C.ivory}"/>
    <text x="108" y="1156" fill="${C.ink}" font-size="29" font-weight="900">O modelo será acessível.</text>
    <text x="108" y="1192" fill="${C.indigo}" font-size="29" font-weight="900">A arquitetura será a vantagem.</text>`;
  return shell(C.ink, body, 2, true, 'PREVISÃO');
}

function questionCard(x, y, n, lines) {
  return `<g>
    <rect x="${x}" y="${y}" width="438" height="202" rx="7" fill="${C.ivory}" stroke="#C7C1B4" stroke-width="2"/>
    <rect x="${x}" y="${y}" width="74" height="202" rx="7" fill="${C.ink}"/>
    <text x="${x + 37}" y="${y + 64}" text-anchor="middle" fill="${C.indigo2}" font-size="33" font-weight="900">${n}</text>
    ${tspans(lines, x + 100, y + 70, 42, `fill="${C.ink}" font-size="31" font-weight="750"`)}
  </g>`;
}

function slide3() {
  const body = `
    <text x="854" y="412" fill="none" stroke="#0A0E16" stroke-opacity=".08" stroke-width="4" font-size="430" font-weight="900">01</text>
    <text x="76" y="222" fill="${C.indigo}" font-size="24" font-weight="900" letter-spacing="3">1º MOVIMENTO</text>
    ${tspans(['TORNAR A OPERAÇÃO', 'LEGÍVEL.'], 76, 302, 78,
      `fill="${C.ink}" font-size="72" font-weight="900" letter-spacing="-3"`)}
    <text x="76" y="466" fill="${C.mutedDark}" font-size="31" font-weight="600">Antes de automatizar, a empresa precisa saber:</text>
    ${questionCard(76, 520, '1', ['Em que etapa o lead', 'deixa de avançar?'])}
    ${questionCard(566, 520, '2', ['Qual tarefa se repete', 'todos os dias?'])}
    ${questionCard(76, 744, '3', ['Qual decisão ainda', 'depende do dono?'])}
    ${questionCard(566, 744, '4', ['Onde dados e contexto', 'se perdem?'])}
    <rect x="76" y="990" width="928" height="214" rx="8" fill="${C.ink}"/>
    ${tspans(['O gargalo certo revela a primeira peça', 'que precisa ser reconstruída.'], 112, 1052, 47,
      `fill="${C.ivory}" font-size="38" font-weight="900" letter-spacing="-.8"`)}
    <line x1="112" y1="1168" x2="198" y2="1168" stroke="${C.indigo}" stroke-width="6"/>
    <text x="222" y="1178" fill="${C.muted}" font-size="26" font-weight="600">Sem diagnóstico, a IA executa o mesmo erro mais rápido. →</text>`;
  return shell(C.paper, body, 3, false, 'DIAGNÓSTICO');
}

function moduleBox(x, y, w, h, label, sub, accent = false) {
  const subText = Array.isArray(sub)
    ? tspans(sub, x + 26, y + 82, 27, `fill="${accent ? C.ivory : C.muted}" font-size="19" font-weight="600"`)
    : `<text x="${x + 26}" y="${y + 84}" fill="${accent ? C.ivory : C.muted}" font-size="22" font-weight="600">${sub}</text>`;
  return `<g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="${accent ? C.indigo : C.ink3}" stroke="${accent ? C.indigo2 : C.line}" stroke-width="2"/>
    <text x="${x + 26}" y="${y + 47}" fill="${accent ? C.ivory : C.indigo2}" font-size="25" font-weight="900" letter-spacing="1.8">${label}</text>
    ${subText}
  </g>`;
}

function slide4() {
  const body = `
    <rect width="1080" height="1350" fill="url(#bg)"/>
    <rect width="1080" height="1350" fill="url(#grid)"/>
    <text x="76" y="218" fill="${C.indigo2}" font-size="24" font-weight="900" letter-spacing="3">2º MOVIMENTO</text>
    <text x="76" y="302" fill="${C.ivory}" font-size="70" font-weight="900" letter-spacing="-3">REARQUITETAR</text>
    <text x="76" y="374" fill="${C.ivory}" font-size="58" font-weight="900" letter-spacing="-2">COMO O TRABALHO ACONTECE.</text>
    <text x="76" y="455" fill="${C.muted}" font-size="29" font-weight="600">A pergunta não é “qual ferramenta de IA vamos comprar?”.</text>
    <rect x="76" y="492" width="928" height="150" rx="8" fill="${C.ivory}"/>
    ${tspans(['COMO ESTA EMPRESA DEVERIA OPERAR', 'SE FOSSE DESENHADA HOJE?'], 110, 552, 48,
      `fill="${C.ink}" font-size="40" font-weight="900" letter-spacing="-.8"`)}
    <line x1="540" y1="688" x2="540" y2="955" stroke="${C.indigo}" stroke-width="4"/>
    <line x1="246" y1="756" x2="540" y2="756" stroke="${C.indigo}" stroke-width="4"/>
    <line x1="540" y1="862" x2="834" y2="862" stroke="${C.indigo}" stroke-width="4"/>
    <circle cx="540" cy="756" r="9" fill="${C.indigo}"/><circle cx="540" cy="862" r="9" fill="${C.indigo}"/>
    ${moduleBox(76, 690, 360, 130, 'PESSOAS', 'julgamento • relação • exceção')}
    ${moduleBox(644, 796, 360, 130, 'SISTEMAS', 'regras • contexto • dados')}
    ${moduleBox(360, 944, 360, 130, 'IA', ['execução • monitoramento', 'encaminhamento'], true)}
    <rect x="76" y="1100" width="928" height="126" rx="7" fill="#141B26" stroke="${C.line}" stroke-width="2"/>
    <text x="108" y="1144" fill="${C.indigo2}" font-size="24" font-weight="900">NEGÓCIO AI NATIVE</text>
    ${tspans(['Empresa desenhada para operar com IA no núcleo.', 'Não é instalar IA na empresa antiga. É redesenhar a parte que trava. →'], 108, 1180, 30,
      `fill="${C.ivory}" font-size="22" font-weight="600"`)} `;
  return shell(C.ink, body, 4, true, 'REARQUITETURA');
}

function compareRow(y, leftTop, leftLines, rightTop, rightLines) {
  return `<g>
    <rect x="76" y="${y}" width="451" height="150" fill="#DAD6CD" stroke="#C6C0B4" stroke-width="2"/>
    <rect x="527" y="${y}" width="477" height="150" fill="#121B2A" stroke="${C.line}" stroke-width="2"/>
    <circle cx="112" cy="${y + 42}" r="7" fill="#777E89"/>
    <circle cx="563" cy="${y + 42}" r="7" fill="${C.indigo}"/>
    <text x="138" y="${y + 50}" fill="${C.mutedDark}" font-size="23" font-weight="900">${esc(leftTop)}</text>
    ${tspans(leftLines, 108, y + 92, 31, `fill="${C.ink}" font-size="25" font-weight="700"`)}
    <text x="589" y="${y + 50}" fill="${C.indigo2}" font-size="23" font-weight="900">${esc(rightTop)}</text>
    ${tspans(rightLines, 559, y + 92, 31, `fill="${C.ivory}" font-size="25" font-weight="750"`)}
  </g>`;
}

function slide5() {
  const body = `
    <text x="76" y="218" fill="${C.indigo}" font-size="24" font-weight="900" letter-spacing="3">APLICAÇÃO PRÁTICA</text>
    ${tspans(['A OPERAÇÃO DEIXA DE', 'DEPENDER DA MEMÓRIA.'], 76, 298, 68,
      `fill="${C.ink}" font-size="64" font-weight="900" letter-spacing="-2.5"`)}
    <text x="76" y="460" fill="${C.mutedDark}" font-size="21" font-weight="900" letter-spacing="2">OPERAÇÃO TRADICIONAL</text>
    <text x="527" y="460" fill="${C.indigo}" font-size="21" font-weight="900" letter-spacing="2">NEGÓCIO AI NATIVE</text>
    ${compareRow(490, 'ESPERA', ['O lead espera alguém', 'responder'], 'RESPOSTA', ['Todo lead recebe', 'resposta'])}
    ${compareRow(640, 'DEPENDE', ['O follow-up depende', 'do time'], 'ACONTECE', ['O acompanhamento acontece', 'continuamente'])}
    ${compareRow(790, 'PRESO', ['O contexto fica preso', 'no WhatsApp'], 'ALIMENTA', ['Cada conversa alimenta', 'a operação'])}
    ${compareRow(940, 'ACOMPANHA', ['O dono acompanha', 'cada detalhe'], 'RECEBE EXCEÇÕES', ['As exceções chegam a quem', 'precisa decidir'])}
    <rect x="76" y="1112" width="928" height="114" rx="7" fill="${C.ink}"/>
    ${tspans(['Autonomia não é eliminar pessoas.', 'É reservar pessoas para julgamento, relacionamento e exceção. →'], 110, 1157, 38,
      `fill="${C.ivory}" font-size="28" font-weight="800"`)} `;
  return shell(C.paper, body, 5, false, 'ANTES / DEPOIS');
}

function step(x, y, n, title, final = false) {
  return `<g>
    <path d="M${x} ${y}h134v22H${x + 22}v112H${x}Z" fill="${final ? C.indigo : C.ivory}"/>
    <path d="M${x + 184} ${y + 184}H${x + 50}v-22h112V${y + 50}h22Z" fill="${final ? C.indigo : C.ivory}"/>
    <rect x="${x + 77}" y="${y + 77}" width="30" height="30" rx="2" fill="${final ? C.ivory : C.indigo}" transform="rotate(45 ${x + 92} ${y + 92})"/>
    <text x="${x + 92}" y="${y + 230}" text-anchor="middle" fill="${C.muted}" font-size="20" font-weight="900" letter-spacing="2">0${n}</text>
    <text x="${x + 92}" y="${y + 268}" text-anchor="middle" fill="${C.ivory}" font-size="24" font-weight="900">${title}</text>
  </g>`;
}

function slide6() {
  const body = `
    <rect width="1080" height="1350" fill="url(#bg)"/>
    <rect width="1080" height="1350" fill="url(#grid)"/>
    <text x="76" y="218" fill="${C.indigo2}" font-size="24" font-weight="900" letter-spacing="3">3º MOVIMENTO</text>
    ${tspans(['IMPLEMENTAR UMA', 'PEÇA POR VEZ.'], 76, 300, 78,
      `fill="${C.ivory}" font-size="75" font-weight="900" letter-spacing="-3"`)}
    ${tspans(['Não se reconstrói uma empresa inteira', 'em um projeto interminável.'], 76, 496, 43,
      `fill="${C.muted}" font-size="32" font-weight="600"`)}
    <line x1="76" y1="594" x2="1004" y2="594" stroke="${C.line}" stroke-width="2"/>
    <path d="M166 756L354 694L540 756L726 694L914 756" fill="none" stroke="${C.indigo}" stroke-width="5" stroke-dasharray="4 12"/>
    ${step(74, 654, 1, 'Diagnosticar')}
    ${step(260, 592, 2, 'Redesenhar')}
    ${step(446, 654, 3, 'Instalar')}
    ${step(632, 592, 4, 'Conectar')}
    ${step(818, 654, 5, 'Medir', true)}
    <text x="76" y="1015" fill="${C.muted}" font-size="29" font-weight="600">Só então avance para a próxima peça.</text>
    <rect x="76" y="1061" width="928" height="165" rx="8" fill="${C.ivory}"/>
    ${tspans(['CADA PEÇA PRECISA', 'FUNCIONAR SOZINHA.'], 112, 1123, 55,
      `fill="${C.ink}" font-size="48" font-weight="900" letter-spacing="-1.5"`)}
    <path d="M904 1120h70v70" fill="none" stroke="${C.indigo}" stroke-width="6"/>`;
  return shell(C.ink, body, 6, true, 'IMPLEMENTAÇÃO');
}

function slide7() {
  const body = `
    <rect width="1080" height="1350" fill="url(#bg)"/>
    <rect width="1080" height="1350" fill="url(#grid)"/>
    <text x="24" y="730" fill="none" stroke="#A8B0BF" stroke-opacity=".10" stroke-width="4" font-size="330" font-weight="900" letter-spacing="-18">FAZER</text>
    <text x="76" y="220" fill="${C.indigo2}" font-size="24" font-weight="900" letter-spacing="3">CONCLUSÃO</text>
    ${tspans(['A VANTAGEM NÃO ESTÁ', 'EM TER IA. ESTÁ EM', 'FAZÊ-LA FUNCIONAR.'], 76, 302, 77,
      `fill="${C.ivory}" font-size="71" font-weight="900" letter-spacing="-3"`)}
    <g transform="translate(76 610)">
      <rect width="286" height="202" rx="8" fill="#151D2A" stroke="${C.line}" stroke-width="2"/>
      <text x="28" y="55" fill="${C.indigo2}" font-size="23" font-weight="900">01</text>
      <text x="28" y="110" fill="${C.ivory}" font-size="31" font-weight="900">Diagnosticar</text>
      ${tspans(['o gargalo que limita', 'a empresa.'], 28, 151, 29, `fill="${C.muted}" font-size="21" font-weight="600"`)}
    </g>
    <g transform="translate(397 610)">
      <rect width="286" height="202" rx="8" fill="#151D2A" stroke="${C.line}" stroke-width="2"/>
      <text x="28" y="55" fill="${C.indigo2}" font-size="23" font-weight="900">02</text>
      <text x="28" y="110" fill="${C.ivory}" font-size="31" font-weight="900">Rearquitetar</text>
      ${tspans(['pessoas, sistemas,', 'dados e IA.'], 28, 151, 29, `fill="${C.muted}" font-size="21" font-weight="600"`)}
    </g>
    <g transform="translate(718 610)">
      <rect width="286" height="202" rx="8" fill="${C.indigo}" stroke="${C.indigo2}" stroke-width="2"/>
      <text x="28" y="55" fill="${C.ivory}" font-size="23" font-weight="900">03</text>
      <text x="28" y="110" fill="${C.ivory}" font-size="31" font-weight="900">Implementar</text>
      ${tspans(['uma capacidade real', 'em produção.'], 28, 151, 29, `fill="${C.ivory}" font-size="21" font-weight="600"`)}
    </g>
    <text x="76" y="885" fill="${C.ivory}" font-size="30" font-weight="800">Ser AI Native é o destino.</text>
    <text x="76" y="927" fill="${C.muted}" font-size="30" font-weight="600">A gente começa pela parte que está travando.</text>
    <rect x="76" y="964" width="928" height="164" rx="8" fill="${C.ivory}"/>
    ${tspans(['QUAL PARTE DA SUA EMPRESA', 'AINDA DEPENDE COMPLETAMENTE', 'DE VOCÊ?'], 110, 1016, 42,
      `fill="${C.ink}" font-size="36" font-weight="900" letter-spacing="-.8"`)}
    <g transform="translate(76 1158)">
      <path d="M0 0h40v10H10v30H0Z" fill="${C.ivory}"/><path d="M60 60H20V50h30V20h10Z" fill="${C.ivory}"/>
      <rect x="25" y="25" width="10" height="10" fill="${C.indigo}" transform="rotate(45 30 30)"/>
      <text x="82" y="42" fill="${C.ivory}" font-size="26" font-weight="900" letter-spacing=".5">CONHEÇA AS SOLUÇÕES DA ARVEX →</text>
    </g>`;
  return shell(C.ink, body, 7, true, 'CONCLUSÃO');
}

const slides = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6(), slide7()];

async function build() {
  const pngs = [];
  for (let i = 0; i < slides.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    const svgPath = path.join(SLIDES, `${n}.svg`);
    const pngPath = path.join(SLIDES, `${n}.png`);
    fs.writeFileSync(svgPath, slides[i]);
    await sharp(Buffer.from(slides[i])).png().toFile(pngPath);
    pngs.push(pngPath);
  }

  const thumbW = 324;
  const thumbH = 405;
  const gap = 28;
  const margin = 44;
  const canvasW = margin * 2 + thumbW * 4 + gap * 3;
  const canvasH = margin * 2 + thumbH * 2 + gap;
  const base = sharp({ create: { width: canvasW, height: canvasH, channels: 4, background: '#D8D5CE' } });
  const composites = [];
  for (let i = 0; i < pngs.length; i++) {
    const col = i % 4;
    const row = Math.floor(i / 4);
    composites.push({
      input: await sharp(pngs[i]).resize(thumbW, thumbH).png().toBuffer(),
      left: margin + col * (thumbW + gap),
      top: margin + row * (thumbH + gap),
    });
  }
  await base.composite(composites).png().toFile(path.join(OUT, 'contact-sheet.png'));

  const cards = slides.map((_, i) => {
    const n = String(i + 1).padStart(2, '0');
    return `<figure><img src="slides/${n}.png" alt="Slide ${i + 1}"><figcaption>Slide ${i + 1}</figcaption></figure>`;
  }).join('\n');
  const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARVEX — Carrossel 01</title><style>
    :root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#090d14;color:#f2f0e9;font-family:Arial,sans-serif}header{padding:44px max(4vw,28px);border-bottom:1px solid #283243}h1{margin:0 0 8px;font-size:clamp(28px,4vw,54px)}p{margin:0;color:#a7afbc;font-size:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px;padding:36px max(4vw,28px)}figure{margin:0}img{display:block;width:100%;height:auto;border:1px solid #283243}figcaption{padding:12px 0;color:#a7afbc;font-weight:700}
  </style></head><body><header><h1>ARVEX — A arquitetura das empresas de 2027</h1><p>Carrossel institucional · 1080 × 1350 · 7 slides</p></header><main class="grid">${cards}</main></body></html>`;
  fs.writeFileSync(path.join(OUT, 'index.html'), html);
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
