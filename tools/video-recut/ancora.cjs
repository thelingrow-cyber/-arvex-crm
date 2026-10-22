// Acha o tempo de uma frase na transcricao.json (início da 1ª palavra). at("operação black recorde") · at("black", 2) = 2ª ocorrência
const fs = require("fs"), path = require("path");
const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9 ]/g, " ").trim();
module.exports = (work) => {
  const W = JSON.parse(fs.readFileSync(path.join(work, "transcricao.json"), "utf8")).words.map((w) => ({ ...w, n: norm(w.word) }));
  const achar = (frase, k = 1) => {
    const alvo = norm(frase).split(/\s+/);
    for (let i = 0, c = 0; i <= W.length - alvo.length; i++)
      if (alvo.every((a, j) => W[i + j].n === a) && ++c === k) return i;
    throw new Error(`frase não encontrada: "${frase}" (${k})`);
  };
  const at = (frase, k) => +W[achar(frase, k)].start.toFixed(2);
  const fim = (frase, k) => { const i = achar(frase, k) + norm(frase).split(/\s+/).length - 1; return +W[i].end.toFixed(2); };
  return { at, fim, W };
};
