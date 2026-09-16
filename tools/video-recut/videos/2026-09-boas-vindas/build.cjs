// Boas-vindas grupo VIP — Desafio Ótica +100K (Cindy) — 66.9s
// Áudio: WhatsApp 2026-09-15 19.21 (frase repetida removida em 55.9–58.6) + trilha ambiente com ducking.
// Vídeo: 11 cortes de 6 takes (4928 loja cheia · 4929 entrada · 4930 gaveta · 4931 mãos/óculos · 4934 atendimento · 4937 computador).
const path = require("path");
const V = require("../../lib.cjs").criar({ dur: 66.9 });

// cortes em: 0 · 6.4 · 12 · 19.4 · 24.6 · 30.6 · 37 · 41.8 · 48.4 · 55.2 · 60.9
V.camera([
  [0, 6.4, 1.06, 1.14], [6.4, 12.0, 1.0, 1.09], [12.0, 19.4, 1.13, 1.02], [19.4, 24.6, 1.0, 1.1],
  [24.6, 30.6, 1.11, 1.02], [30.6, 37.0, 1.0, 1.08], [37.0, 41.8, 1.13, 1.04], [41.8, 48.4, 1.0, 1.09],
  [48.4, 55.2, 1.11, 1.02], [55.2, 60.9, 1.0, 1.09], [60.9, 66.9, 1.14, 1.04],
]);

V.flash([12.0, 30.6, 48.4, 60.9]);

V.cardTitulo("c1", 5.6, 9.0, { kicker: "VOCÊ ESTÁ DENTRO DO", titulo: "GRUPO VIP", gold: "+100K", tituloAt: 6.06, goldAt: 7.8 });
V.cardTitulo("c2", 9.4, 11.9, { kicker: "ANTES DE QUALQUER COISA", titulo: "SEJA MUITO", gold: "BEM-VINDO", tituloAt: 9.9, goldAt: 10.95 });
V.cardTitulo("c3", 22.7, 26.9, { kicker: "A PARTIR DE AMANHÃ", titulo: "VAMOS EXPLICAR", gold: "TUDO", tituloAt: 23.7, goldAt: 24.7 });

V.cardLista("c4", 27.7, 33.5, {
  kicker: "O QUE VEM POR AÍ",
  itens: [["O QUE VAMOS CONSTRUIR", 28.28], ["QUAIS SÃO AS ETAPAS", 29.5], ["O QUE VOCÊ VAI FAZER", 30.95]],
  extra: ["COMO VAMOS TRABALHAR", 32.9],
});

// número "100 mil/mês" NÃO vira card (regra do lançamento); "+100K" é o nome do evento
V.insertCrescimento({ start: 34.0, end: 38.4, kicker: "RUMO AO CRESCIMENTO", selo: "+100K", seloAt: 36.5 });

V.cardTitulo("c5", 43.3, 48.1, { kicker: "NÃO VAI SER", titulo: "CURSO PARA", gold: "ASSISTIR", tituloAt: 43.9, goldAt: 45.4 });
V.cardTitulo("c6", 48.7, 53.7, { kicker: "A IDEIA AQUI É COLOCAR A", titulo: "MÃO NA", gold: "MASSA", tituloAt: 49.9, goldAt: 50.4 });
V.cardTitulo("c7", 57.9, 61.3, { kicker: "COMEÇA AMANHÃ", titulo: "FIQUE ATENTO", gold: "NO GRUPO", tituloAt: 58.5, goldAt: 59.6 });
V.cardCTA("c8", 61.8, { kicker: "NÃO DEIXE PARA DEPOIS", texto: "A GENTE SE VÊ AMANHÃ", popAt: 62.5 });

V.legendaDinamica(require("../../work/2026-09-boas-vindas/legenda.json"), {
  destaques: ["bem-vindo", "VIP", "100K", "grupo", "desafio", "amanhã", "etapas", "construir", "massa", "atento", "depois", "loja", "sozinho"],
});

V.salvar(process.argv[2] || path.join(__dirname, "../../work/2026-09-boas-vindas/public/index.html"));
