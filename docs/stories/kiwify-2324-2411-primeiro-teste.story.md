# Story — Primeiro teste vertical do podcast Kiwify, 23:24–24:11

> Status: **Ready for Review — revisão V7 com dois casos de autoridade exportada**
> Data: 2026-09-13
> Responsável pela preparação: @sm (River)
> Origem: pedido do usuário nesta sessão, incluindo o intervalo 23:24–24:11.
> Escopo: execução local de mídia e script reproduzível; nenhuma alteração na aplicação.

## Objetivo

Como Vitor, quero um primeiro corte vertical do trecho escolhido do podcast Kiwify,
com meu rosto como foco, legendas limpas, inserts pertinentes e CTA para acompanhar
meu conteúdo, para avaliar a linguagem de edição do posicionamento Negócios AI Native.

## Contexto e fontes

- Intervalo autorizado: **00:23:24 a 00:24:11**, equivalente a **1404–1451s**, com duração
  bruta de **47s**.
- Fonte local: `Downloads/YTDown.com_YouTube_FATURAMOS-MILHOES-EM-MICRO-NICHOS-IGNORA_Media_oWH2m8law6c_001_1080p.mp4`.
- Referência fornecida: `Downloads/snapinsta-1789281850388.mp4`; aproveitar close e legendas
  curtas, claras, com destaque pontual.
- Pessoa em foco: convidado de camiseta preta, à direita no plano dos convidados.
- Contexto existente: [CURRENT.md, seção 10](../sessions/CURRENT.md#10-execução-de-conteúdo--primeiro-corte-do-podcast-kiwify-1309).
  O conteúdo credencia a atuação do Vitor; o CTA convida a acompanhar seu trabalho.
- A fonte foi registrada como 1920×1080/H.264/AAC no handoff. O agente executor deve
  conferir os dados do recorte antes da exportação.
- Observação preliminar da execução: aproximadamente os últimos nove segundos podem
  mostrar a apresentadora. Confirmar o ponto de troca de câmera na análise do trecho.

## Acceptance Criteria

- [x] **AC1 — Fonte preservada:** não sobrescrever nem modificar o MP4 original; todos os
  derivados ficam em `output/video-edits/kiwify-2324-2411/`.
- [x] **AC2 — Corte bruto:** disponibilizar o trecho exato 23:24–24:11 em arquivo separado,
  com áudio e duração de 47s, admitindo apenas a tolerância de um frame na duração do vídeo.
- [x] **AC3 — Edição vertical:** exportar teste em 9:16, com duração final declarada. Cortes
  de pausas ou reorganização da fala devem preservar o sentido; registrar mudanças relevantes.
- [x] **AC4 — Foco no rosto:** enquadrar e acompanhar o rosto do convidado de preto nos
  momentos em que ele está disponível na fonte, com ajustes de recorte e aproximação legíveis.
  Nos planos da apresentadora, usar uma solução editorial identificável; não simular a boca
  do Vitor nem apresentar outra fala como se fosse dele.
- [ ] **AC5 — Legendas:** transcrever a fala real e sincronizar as legendas com o áudio da
  edição, conferindo nomes, termos, números, começo e fim das frases. Manter leitura confortável
  e evitar sobrepor textos ao rosto.
- [x] **AC6 — Inserts e CTA:** inserts precisam ajudar a compreensão do argumento. Por
  correção explícita do usuário, não mostrar seu CRM nem seus produtos; diagramas ou ilustrações
  conceituais não devem inventar provas, resultados ou dados. Correção explícita V5:
  remover todos os avisos adicionados de cena ilustrativa/ilustração conceitual.
  Correção V2: remover CTA e congelamento final, encerrando na fala real.
- [ ] **AC7 — Áudio e integridade:** voz inteligível, sem clipping introduzido pela edição,
  streams de áudio/vídeo presentes, reprodução e decodificação conferidas, sem quadros pretos
  acidentais ou dessincronização perceptível.
- [x] **AC8 — Revisão e reprodução:** inspecionar visualmente quadros do começo, inserts,
  transições e final; registrar a verificação de legendas/áudio, os comandos ou script de
  reprodução da edição, parâmetros e limitações observadas.

## Tasks / Subtasks

- [x] Inspecionar fonte, referência, mudanças de câmera e duração; extrair o corte bruto (AC1–2).
- [ ] Transcrever e revisar a fala do intervalo, identificando frases completas e pausas (AC3, AC5).
- [x] Definir a montagem sobre a fala real, recorte vertical e acompanhamento do rosto (AC3–4).
- [x] Preparar legendas, inserts pertinentes e CTA escrito (AC5–6).
- [x] Implementar execução local reproduzível e exportar a primeira versão (AC1, AC3, AC7–8).
- [ ] Verificar integridade técnica e revisar imagens, áudio e sincronismo (AC5, AC7–8).
- [x] Executar os gates do projeto uma vez, registrar resultados e eventuais indisponibilidades.
- [x] Atualizar checklist, file list efetiva e registro de execução; o agente principal atualiza
  `docs/sessions/CURRENT.md` ao encerrar a entrega.

## Dev Notes

Esta é uma tarefa local de produção de conteúdo, derivada do pedido explícito do usuário,
e segue o precedente das stories descritivas em `docs/stories/`. Não depende de mudanças
no produto, API, banco de dados ou configuração de deployment. Não foi identificada
orientação específica de arquitetura para edição de vídeo; não introduzir bibliotecas
ou serviços de aplicação por causa deste teste.

O handoff informa ferramentas portáteis em `output/video-tools/`; usar somente as
capacidades verificadas pelo executor. Registrar os nomes definitivos dos artefatos ao
concluir. O corte bruto serve de referência auditável caso a edição final tenha outra duração.
O usuário avalia o acabamento do primeiro teste; validação técnica não implica aprovação
estética nem publicação.

## File List efetiva

- [x] `docs/stories/kiwify-2324-2411-primeiro-teste.story.md`
- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-original.mp4`
- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v1.mp4`
- [x] `output/video-edits/kiwify-2324-2411/captions.ass` e `captions.srt`
- [x] `output/video-edits/kiwify-2324-2411/transcript.json`, `transcript.txt`, `transcribe_local.py`, `source.wav`
- [x] `output/video-edits/kiwify-2324-2411/build-edit.cjs`, `filter.ffmpeg`, `render-args.json`, `assets/`
- [x] `output/video-edits/kiwify-2324-2411/README.md`, `edit-manifest.json`, `validation.json`, `qa/`
- [x] `docs/sessions/CURRENT.md`

## Validação planejada

- Conferir duração, resolução, proporção e streams do bruto e do teste vertical.
- Decodificar o arquivo entregue e revisar enquadramento, inserts, legenda, CTA e áudio.
- Registrar a duração antes/depois e limitações da câmera original.
- Rodar `npm run lint`, `npm run typecheck`, `npm test` e `npm run build`; registrar falhas ou
  scripts inexistentes sem alterar configurações alheias à edição.
- Conferir `git diff --check` e preservar mudanças preexistentes no working tree.

## CodeRabbit Integration

`coderabbit_integration` não consta na configuração local `.aiox-core/core-config.yaml`.
Nenhuma revisão CodeRabbit foi executada ou presumida. Revisão manual de mídia e script
integra os critérios desta entrega; não há PR, push ou publicação no escopo atual.

## Registro de execução

Primeiro teste exportado e inspecionado: 32,034s, 1080×1920, 30fps, 961 frames, H.264/AAC.
Cópia horizontal exata de 47s disponível. Decodificação integral sem erro; diferença A/V
menor que 1ms. Medição de áudio -16,01 LUFS/-2,86 dBTP. Oito quadros de começo, inserts,
rosto, legenda e CTA revisados visualmente. Sem CRM ou produtos pessoais nos inserts.

AC5 e parte auditiva de AC7 ficam pendentes de conferência humana: transcrição ASR local
e timestamps foram usados, mas a sessão não disponibilizou entrada de áudio ao modelo.
A frase “Você pode ser explorado...” merece confirmação. Não foi inventada revisão auditiva.
A maior parte da fala de reconhecimento incerto no fim foi retirada deste primeiro teste.
Roteiro de cortes e limites registrados no manifesto/README. Aprovação estética pendente.

`node --check` e diff dos documentos passam. `npm run lint`, `typecheck` e `build` não
existem; `npm test` aponta incompatibilidade pré-existente entre títulos de CURRENT.md e
seu verificador. Não foram feitas alterações alheias no package.json ou no contrato.
Sem commit, push ou publicação.

## Revisão V2 — feedback executado em 13/09/2026

- [x] Pesquisar exemplos concretos antes de operar; distinguir observação de inferência.
- [x] Acelerar moderadamente a fala, sincronizando vídeo/legendas e preservando altura.
- [x] Animar ecossistema e funil; criar vídeo motion de criação por IA sem produtos/CRM pessoais.
- [x] Preservar o card aprovado, aplicar flashes pontuais e música baixa licenciada.
- [x] Remover CTA e congelamento; preservar fonte e V1.
- [x] Exportar e conferir decodificação, metadados, loudness e oito amostras visuais.
- [ ] Aprovação auditiva humana das legendas, emendas e equilíbrio música/voz.

Resultado: 27,067s, 1080×1920/30fps, 812 frames, H.264/AAC, 9.028.590 bytes.
Decodificação integral sem erro; diferença A/V <1ms; -16,00 LUFS/-2,67 dBTP.
Velocidades aproximadas 1,10/1,06/1,12/1,12/1,04×. Motions ocupam6,8s; restante
mantém rosto em foco. V1 inalterada. Gates repetidos: mesmos scripts ausentes e
falha preexistente de CURRENT.md. `node --check` passa. Sem commit/publicação.

### File List adicional V2

- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v2.mp4`
- [x] `output/video-edits/kiwify-2324-2411/build-v2.cjs`, `check-v2.cjs`
- [x] `output/video-edits/kiwify-2324-2411/v2-motion/` (script, três MP4s e previews)
- [x] `output/video-edits/kiwify-2324-2411/captions-v2.ass`, `captions-v2.srt`
- [x] `output/video-edits/kiwify-2324-2411/filter-v2.ffmpeg`, `render-args-v2.json`, `edit-manifest-v2.json`
- [x] `output/video-edits/kiwify-2324-2411/music-close-up-1167.mp3`
- [x] `output/video-edits/kiwify-2324-2411/README-v2.md`, `validation-v2.json`, `qa-v2.jpg`, `analysis-v2/`
- [x] `docs/sessions/CURRENT.md`

## Revisão V3 — cenas e corte de redundâncias

V2 rejeitada por flashes imperceptíveis, falta de inserts de cenas e fala repetitiva.

- [x] Remover introdução sobre infoprodutos/marca e duas retomadas de “pode ser explorado”.
- [x] Começar diretamente na tese sobre o expert; preservar sentido com seis blocos de fala.
- [x] Incluir duas cenas filmadas licenciadas: desenvolvimento no computador e colaboração.
- [x] Manter card aprovado, música e foco no rosto; sem CTA, CRM ou produtos pessoais.
- [x] Aplicar três flashes perceptíveis e conferir pico/decaimento na exportação.
- [x] Decodificar integralmente e conferir metadados, loudness e oito amostras visuais.
- [ ] Conferir de ouvido as emendas, derivadas dos timestamps do ASR.

V3:17,134s,1080×1920/30fps,514frames,H.264/AAC,7.195.737bytes. Diferença A/V<1ms;
decodificação passa; -15,85LUFS/-2,51dBTP. Frames confirmam ambos os B-rolls e flashes
claros em~3,03s e~10,47s. Terceiro flash previsto em5,22s no manifesto. Gates repetidos
com mesmas falhas preexistentes/scripts ausentes. V1/V2 preservadas; sem publicação.

### File List adicional V3

- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v3.mp4`
- [x] `output/video-edits/kiwify-2324-2411/build-v3.cjs`, `check-v3.cjs`
- [x] `output/video-edits/kiwify-2324-2411/v3-assets/` (duas cenas Full HD, previews e overlays)
- [x] `output/video-edits/kiwify-2324-2411/captions-v3.ass`, `captions-v3.srt`
- [x] `output/video-edits/kiwify-2324-2411/filter-v3.ffmpeg`, `render-args-v3.json`, `edit-manifest-v3.json`
- [x] `output/video-edits/kiwify-2324-2411/README-v3.md`, `validation-v3.json`, `qa-v3.jpg`
- [x] `docs/sessions/CURRENT.md`

## Revisão V5 — cortes finos, novos motions e trilha

V4 restaurou a abertura solicitada (criar um ecossistema), mas foi substituída pelo
novo pedido antes da entrega. V5 preserva essa abertura em nove blocos de fala.

- [x] Cortar o primeiro dentro, em algo específico, pausa após IA e é/pausa após vai.
- [x] Trocar completamente o visual de IA e redesenhar o funil com fluxos animados.
- [x] Inserir cena da Manu Cit/Guday atribuída pela página oficial; é apresentação da marca,
  não ensaio de modelagem. Legendas próprias da fonte permanecem no vídeo.
- [x] Remover avisos ilustrativos adicionados, manter ausência de CTA/CRM/produtos pessoais.
- [x] Reforçar moderadamente contraste/nitidez e substituir trilha por Fallen (Asper), Mixkit.
- [x] Renderizar, decodificar e conferir metadados, loudness e oito quadros finais.
- [ ] Escuta humana das emendas, legendas e equilíbrio subjetivo da trilha.
- [ ] Confirmar direitos de reutilização do trecho Guday antes de publicar.

Resultado:21,067s,1080×1920/30fps,632frames,8.450.288bytes,H.264/AAC.
Decode passa; diferença A/V<1ms; -16,02LUFS/-3,28dBTP. Flashes isolados em
6,167/10,233/14,617s; pico inspecionado. ASR omitia dentro repetido e juntava vai/é;
limites corrigidos pelo feedback e waveform. Não foi alegada audição pelo modelo.
Sintaxe dos scripts e git diff --check passam. Lint/typecheck ausentes; npm test
mantém falha preexistente no contrato de títulos de CURRENT.md. Nenhuma alteração
no produto, commit ou publicação realizada por esta edição.

### File List adicional V4/V5

- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v4.mp4` (rascunho preservado)
- [x] `output/video-edits/kiwify-2324-2411/v4-assets/`, `README-v4.md`, captions/filter/manifest/args V4
- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v5.mp4`
- [x] `output/video-edits/kiwify-2324-2411/build-v5.cjs`, `check-v3.cjs --v5`, `check-speech-v5.py`
- [x] `output/video-edits/kiwify-2324-2411/v5-assets/` (fontes públicas, trilha, motions, previews, diagnóstico)
- [x] `output/video-edits/kiwify-2324-2411/captions-v5.ass`, `captions-v5.srt`
- [x] `output/video-edits/kiwify-2324-2411/filter-v5.ffmpeg`, `render-args-v5.json`, `edit-manifest-v5.json`
- [x] `output/video-edits/kiwify-2324-2411/README-v5.md`, `validation-v5.json`, `qa-v5.jpg`
- [x] `docs/sessions/CURRENT.md`

## Revisão V6 — tratamento de imagem

Por pedido do usuário, não houve mudança de montagem. V6 mantém os mesmos 21,067s,
cortes, inserts, legendas, flashes, música e mixagem da V5.

- [x] Reduzir moderadamente ruído/artefatos antes do upscale.
- [x] Usar spline36 e nitidez adaptativa leve, sem reconstrução facial generativa.
- [x] Corrigir discretamente o excesso de verde e preservar tons de pele.
- [x] Renderizar novamente desde as fontes em H.264 High/CRF14/preset slow.
- [x] Decodificar e inspecionar oito quadros mais um frame de rosto em resolução integral.

V6:21,067s,1080×1920/30fps,632frames,25.347.069bytes. Vídeo~9,41Mbps,
contra~2,99Mbps da V5. A/V<1ms; -16,02LUFS/-3,28dBTP. O aumento de taxa evita
perda adicional, mas não recupera detalhe ausente no recorte da fonte 1080p.

### File List adicional V6

- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v6.mp4`
- [x] `output/video-edits/kiwify-2324-2411/build-v5.cjs --v6`, `check-v3.cjs --v6`
- [x] `output/video-edits/kiwify-2324-2411/captions-v6.ass`, `captions-v6.srt`
- [x] `output/video-edits/kiwify-2324-2411/filter-v6.ffmpeg`, `render-args-v6.json`, `edit-manifest-v6.json`
- [x] `output/video-edits/kiwify-2324-2411/README-v6.md`, `validation-v6.json`, `qa-v6.jpg`

## Revisão V7 — autoridade emprestada contextualizada

Por pedido do usuário, o exemplo da Guday foi mantido e ganhou um segundo caso,
MrBeast/Feastables. Montagem continua com21,067s; fala, tratamento V6, áudio e fim intactos.

- [x] Identificar Manu Cit × Guday e MrBeast × Feastables no próprio insert.
- [x] Ampliar exemplos de1,65s para2,67s, sem alongar o Reel.
- [x] Usar trecho do comercial oficial em que MrBeast, marca e produto aparecem.
- [x] Retirar do enquadramento a legenda inglesa grande da fonte.
- [x] Conferir ambos os casos, transição, produto, funil e encerramento.
- [ ] Confirmar autorização das duas fontes antes de publicação comercial.

V7:21,067s,1080×1920/30fps,632frames,24.935.416bytes,H.264/AAC.
Vídeo~9,25Mbps; decode passa; A/V<1ms; -16,02LUFS/-3,28dBTP. Fontes e limites
registrados em README/manifesto. Nenhuma publicação ou alegação de parceria.

### File List adicional V7

- [x] `output/video-edits/kiwify-2324-2411/kiwify-2324-2411-edit-v7.mp4`
- [x] `output/video-edits/kiwify-2324-2411/v7-assets/` (fontes, casos preparados, labels e QA)
- [x] `output/video-edits/kiwify-2324-2411/captions-v7.ass`, `captions-v7.srt`
- [x] `output/video-edits/kiwify-2324-2411/filter-v7.ffmpeg`, `render-args-v7.json`, `edit-manifest-v7.json`
- [x] `output/video-edits/kiwify-2324-2411/README-v7.md`, `validation-v7.json`, `qa-v7.jpg`
- [x] `output/video-tools/yt-dlp.exe` (binário oficial usado para o recorte da fonte)

## Revisão do rascunho (@sm)

Requisitos, fontes, limites, arquivos de saída e critérios verificáveis presentes. Escopo local
suficiente para execução; nenhuma integração ClickUp solicitada, e MCP está desabilitado na
configuração do projeto. Não foram criados requisitos de produto ou novos epics.
