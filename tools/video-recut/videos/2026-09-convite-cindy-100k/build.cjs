// Convite Desafio Ótica +100K (Cindy) — 43.1s, corte 16.1→59.2 do IMG_3043.MOV. Versão aprovada: v2 (2026-09-15).
const path = require("path");
const V = require("../../lib.cjs").criar({ dur: 43.1 });
const { M, maskIn, shimmer } = V;

V.camera([
  [0, 3.08, 1.0, 1.05], [3.08, 4.78, 1.16, 1.2], [4.78, 9.75, 1.0, 1.04], [9.75, 10.56, 1.0, 1.03],
  [10.56, 12.0, 1.13, 1.16], [12.0, 14.88, 1.0, 1.0], [14.88, 22.88, 1.0, 1.08], [22.88, 26.44, 1.14, 1.18],
  [26.44, 28.3, 1.0, 1.04], [28.3, 32.1, 1.12, 1.16], [32.1, 40.38, 1.0, 1.07], [40.38, 43.1, 1.14, 1.2],
]);

V.cardTitulo("c1", 2.95, 4.74, { kicker: "CONVITE ESPECIAL", titulo: "DESAFIO ÓTICA", gold: "+100K", goldAt: 4.12 });

V.insertCirculo({
  start: 4.78, end: 9.75, kicker: "3 DIAS COMIGO",
  blocos: [["22", 6.12], ["23", 6.74], ["24", 7.42]],
  rodape: "DE SETEMBRO", rodapeAt: 8.15, selo: "AO VIVO", seloAt: 9.12,
});

// número "100 mil/mês" NÃO vira card (regra do lançamento); "+100K" é o nome do evento
V.insertCrescimento({ start: 12.0, end: 14.85, kicker: "ESTRUTURA PARA CRESCER", selo: "+100K", seloAt: 12.84 });

V.cardLista("c3", 14.95, 22.8, {
  kicker: "O QUE VOCÊ VAI VER",
  itens: [["ESTRATÉGIA", 16.24], ["POSICIONAMENTO", 16.9], ["FUNIS DE VENDA", 17.76], ["RECUPERAÇÃO DE CLIENTES", 18.96], ["INSTAGRAM COMERCIAL", 20.44]],
  extra: ["E MUITO MAIS", 21.72],
});

V.cardTitulo("c4", 23.0, 26.4, { kicker: "NO DESAFIO", titulo: "TIRE DÚVIDAS", gold: "AO VIVO", tituloAt: 24.3, goldAt: 25.4 });
V.cardTitulo("c5", 27.7, 31.95, { kicker: "CONDIÇÃO ESPECIAL", titulo: "SÓ NO", gold: "GRUPO VIP", tituloAt: 29.4, goldAt: 30.9 });
V.cardCTA("c6", 32.1, { kicker: "CLIQUE NO LINK ABAIXO", texto: "ENTRE NO GRUPO VIP", popAt: 33.45 });

V.legenda(require("./legenda.json"));
V.salvar(process.argv[2] || path.join(__dirname, "../../work/2026-09-convite-cindy-100k/public/index.html"));
