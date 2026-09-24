// Gera embed-elementor.html a partir de index.html: versão para colar no widget HTML do Elementor.
// O Elementor descarta <html>/<head>/<body> — então o CSS vai escopado em #r100k (fundo, cor, fonte
// do body passam para o wrapper), o wrapper ocupa 100vw e o script roda mesmo se "load" já passou.
// uso: node gerar-embed.cjs
const fs = require("fs");
const path = require("path");
const SCOPE = "#r100k";
const src = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

const css = src.slice(src.indexOf("<style>") + 7, src.indexOf("</style>")).replace(/\/\*[\s\S]*?\*\//g, ""); // sem comentários (senão "/* x */ @media" vira seletor)
const body = src.slice(src.indexOf("<body>") + 6, src.indexOf("<script>"));
const js = src.slice(src.indexOf("<script>") + 8, src.lastIndexOf("</script>"));
const fonts = (src.match(/<link href="https:\/\/fonts\.googleapis\.com[^>]+>/) || [""])[0];

// ── escopo de CSS (parser simples de blocos; @media/@supports recursivo, @keyframes/@font-face intactos) ──
function splitSel(p) {
  const out = []; let d = 0, cur = "";
  for (const ch of p) { if (ch === "(") d++; if (ch === ")") d--; if (ch === "," && !d) { out.push(cur); cur = ""; } else cur += ch; }
  return [...out, cur].map((s) => s.trim()).filter(Boolean);
}
function scopeSel(s) {
  if (/^(html|body|:root)$/.test(s)) return SCOPE;
  if (/^(html|body)\b/.test(s)) return s.replace(/^(html|body)/, SCOPE);
  return `${SCOPE} ${s}`;
}
function scope(text) {
  let out = "", i = 0;
  while (i < text.length) {
    const open = text.indexOf("{", i);
    if (open < 0) { out += text.slice(i); break; }
    const prelude = text.slice(i, open);
    let d = 1, j = open + 1;
    while (d && j < text.length) { if (text[j] === "{") d++; else if (text[j] === "}") d--; j++; }
    const inner = text.slice(open + 1, j - 1);
    const p = prelude.trim();
    if (/^@(media|supports)/.test(p)) out += `${prelude}{${scope(inner)}}`;
    else if (p.startsWith("@")) out += `${prelude}{${inner}}`;
    else {
      const lead = prelude.match(/^\s*/)[0];
      out += `${lead}${splitSel(p).map(scopeSel).join(", ")} {${inner}}`;
    }
    i = j;
  }
  return out;
}

// ── blindagem contra o tema/Elementor (vem ANTES das regras da página, que têm a mesma ou maior especificidade) ──
const base = `
    ${SCOPE} { position: relative; width: 100vw; max-width: 100vw; left: 50%; margin-left: -50vw; text-align: left; line-height: normal; }
    ${SCOPE} h1, ${SCOPE} h2, ${SCOPE} h3, ${SCOPE} h4, ${SCOPE} h5, ${SCOPE} h6, ${SCOPE} p, ${SCOPE} li, ${SCOPE} span, ${SCOPE} strong, ${SCOPE} em {
      font-family: inherit; color: inherit; text-transform: none; letter-spacing: normal; line-height: inherit; }
    ${SCOPE} a { color: inherit; text-decoration: none; box-shadow: none; }
    ${SCOPE} button { font: inherit; color: inherit; background: none; border: 0; box-shadow: none; text-transform: none; letter-spacing: normal; cursor: pointer; }
    ${SCOPE} img { border: 0; box-shadow: none; border-radius: 0; }
    ${SCOPE} ul, ${SCOPE} ol { list-style: none; }
    html { scroll-behavior: smooth; }
    body { overflow-x: hidden; }
    .elementor-widget-html:has(${SCOPE}), .elementor-widget-html:has(${SCOPE}) .elementor-widget-container { overflow: visible; }`;

// imagens abaixo da dobra carregam sob demanda (a 1ª — hero — continua imediata)
let n = 0;
const bodyOut = body.replace(/<img /g, () => (n++ === 0 ? '<img fetchpriority="high" ' : '<img loading="lazy" decoding="async" '));

// script isolado; "load" pode já ter passado quando o Elementor injeta o widget
const jsOut = js.replace(/window\.addEventListener\('load',\s*/g, "onLoad(");

const out = `<!-- Desafio Ótica +100K — página de venda (gerado de index.html por gerar-embed.cjs; não editar à mão) -->
${fonts}
<style>${base}
${scope(css)}
</style>
<div id="r100k">
${bodyOut.trim()}
</div>
<script>
(function () {
  const onLoad = (f) => (document.readyState === 'complete' ? f() : window.addEventListener('load', f));
${jsOut}
})();
</script>
`;
fs.writeFileSync(path.join(__dirname, "embed-elementor.html"), out);
console.log(`embed-elementor.html: ${(out.length / 1024).toFixed(0)} KB · ${n} imagens · onLoad trocados: ${(js.match(/window\.addEventListener\('load'/g) || []).length}`);
