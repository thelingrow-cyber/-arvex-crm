// MODELO — copie para videos/<nome>/build.cjs. Tempos em segundos JÁ NO CORTE (ver legenda.json / saída do prep).
const path = require("path");
const fs = require("fs");
const NOME = path.basename(__dirname);
const work = path.join(__dirname, "../../work", NOME);
const meta = JSON.parse(fs.readFileSync(path.join(work, "meta.json"), "utf8").replace(/^﻿/, ""));
const V = require("../../lib.cjs").criar({ dur: meta.duracao });

// 1) Câmera: [início, fim, escalaInicial, escalaFinal]. Troque a escala nas palavras de ênfase (corte com zoom).
V.camera([
  [0, 3, 1.0, 1.05],
  // [3, 6, 1.15, 1.2],
]);

// 2) Cards no topo (rosto fica livre). Um de cada tipo:
// V.cardTitulo("c1", 2.9, 5.0, { kicker: "CONVITE ESPECIAL", titulo: "NOME DO", gold: "EVENTO", goldAt: 4.0 });
// V.cardLista("c2", 10, 18, { kicker: "O QUE VOCÊ VAI VER", itens: [["ITEM 1", 11], ["ITEM 2", 13]], extra: ["E MUITO MAIS", 16] });
// V.cardCTA("c9", 30, { kicker: "CLIQUE NO LINK ABAIXO", texto: "ENTRE NO GRUPO VIP", popAt: 31 });

// 3) Inserts em tela cheia (no máx. 2–3 por vídeo; rosto some durante o insert):
// V.insertCirculo({ start: 5, end: 9.5, kicker: "3 DIAS COMIGO", blocos: [["22", 6], ["23", 6.7], ["24", 7.4]], rodape: "DE SETEMBRO", rodapeAt: 8.1, selo: "AO VIVO", seloAt: 9 });
// V.insertCrescimento({ start: 12, end: 14.8, kicker: "ESTRUTURA PARA CRESCER", selo: "+100K", seloAt: 12.8 });

// 4) Legenda (gerada pelo prep; corrigir erros de transcrição direto no JSON)
V.legenda(JSON.parse(fs.readFileSync(path.join(work, "legenda.json"), "utf8")));
V.salvar(process.argv[2] || path.join(work, "public/index.html"));
