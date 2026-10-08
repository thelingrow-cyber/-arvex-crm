# Diagnóstico visual — referência local e primeira edição

Data: 2026-09-13. Inspeção de frames e manifesto; nenhuma revisão auditiva realizada.
Referência: `C:/Users/Vitor Simões/Downloads/snapinsta-1789281850388.mp4`.
V1: `C:/Users/Vitor Simões/Desktop/ARVEX/output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v1.mp4`.

## Evidência observada

- Referência: 720×1280, 30fps, 47,414s. Rosto permanece dominante nas amostras do vídeo; não foi observada uma sequência de B-roll nas folhas de contato.
- O efeito de película está concentrado em **um evento composto**, de aproximadamente **10,633 a 10,967s**. Pico amarelo/laranja de 10,633 a 10,700s (3 quadros); decaimento vermelho até aproximadamente 10,833s; breve repique de 10,933 a 10,967s (2 quadros). Janela inteira de cerca de 0,367s, incluindo intervalo entre pulsos.
- Aos **20,300s** há mudança brusca de pose/jump cut **sem flash**. A leitura anterior de um segundo light leak nesse ponto não se confirma nos frames.
- A detecção de cena FFmpeg, em 180×320, identifica mudança forte em 10,633s, com luminância média Y de aproximadamente 138 e pico 168 no quadro seguinte. Fora do efeito, Y fica aproximadamente 65–68. Essa diferença mede brilho do quadro, não opacidade da camada original.
- No trecho antes do efeito a legenda enfatiza “mais gravam” em amarelo, maior e quebrada em duas linhas. Depois volta a unidades menores de legenda. Existe variação de hierarquia, não apenas mudança de cor.
- Na V1 o manifesto reserva 3,5s para ecossistema e 2,5s para funil em tela inteira: **6s de diagramas estáticos**. O card IA ocupa 2,7s sobre o rosto. Há ainda 2,4s de congelamento final. Isso permite localizar a sensação de espera apontada pelo usuário sem atribuí-la exclusivamente à sua comunicação.

## Recomendações editoriais para teste, não fatos sobre viralidade

1. Retirar CTA inteiro e congelamento: encerrar na conclusão da fala, preservando sua última sílaba e um pequeno respiro natural.
2. Experimentar voz **1,12–1,16× nos trechos cobertos por inserts**; eventual aceleração no rosto deve ser mais discreta, **1,03–1,05×**. Manter pitch e remapear vídeo, palavras e legendas com a mesma função temporal. A combinação 1,05× no rosto e 1,15× nos 8,7s de inserts da V1 resultaria em aproximadamente **27,50s** de fala, antes de eventuais mudanças de montagem.
3. Ecossistema: card principal entra em 6 quadros; conectores se desenham; quatro nós entram escalonados a cada 3–4 quadros; repouso de leitura. Evitar apenas aplicar zoom ao PNG pronto, porque o movimento não acompanha a ideia de construção.
4. “Por IA”: mostrar ação de criação por 2–2,6s — solicitação curta sendo digitada, blocos aparecendo, artefato se formando. Interface genérica identificável como ilustração, sem CRM/produtos pessoais nem prova fabricada. Preservar a linguagem do card “Novas possibilidades / IA + tecnologia” que o usuário aprovou, agora como título ou etapa do motion.
5. Funil: construção/desenho de 8–12 quadros, seguida de expansão lateral para novas possibilidades, duração total editorial aproximada de 1,8–2,2s. Isso expressa o argumento “além de um único funil”.
6. Começar com **dois flashes breves nos pontos de mudança de assunto**, não em cada legenda. Pulso quente de aproximadamente **4–6 quadros (0,13–0,20s)**, pico de 1–2 quadros e decaimento rápido; sem esconder o rosto por uma longa área branca. Demais mudanças podem ser corte seco com alternância dos dois crops já existentes. A referência usa flash como pontuação rara, não como regra de todo corte.
7. Rosto deve continuar sendo a maior parte do vídeo. Para ~28s, cerca de 6–7s de inserts em tela inteira manteriam ~75–79% de exposição direta do rosto. O motion pode ocupar parte do quadro para aumentar ainda mais essa presença.
8. Legendas: manter unidades curtas, mas permitir 1–2 momentos de hierarquia maior nas palavras-chave. Não fazer todos os textos competirem com os títulos dos inserts.

## Arquivos de diagnóstico

- `reference-10p3-11p9.jpg`: 48 quadros consecutivos, começando em 10,300s; leitura esquerda→direita, cima→baixo, 1/30s por célula. Última célula em 11,867s.
- `reference-19p9-20p966.jpg`: 32 quadros consecutivos, começando em 19,900s; mesma leitura, última célula em 20,933s.

Nenhum vídeo final, script da V1, story ou CURRENT foi alterado por esta subanálise.
