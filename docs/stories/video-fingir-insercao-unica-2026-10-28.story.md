# Vídeo pessoal — uma inserção no topo e legenda

Status: Done

## Revisão v3 — redução e publicação autorizadas

Status: Published. Usuário em 28/10 pediu diminuir imagens/headline e autorizou publicar diretamente no Instagram.
- [x] Reduzir largura total das imagens de 900 para 800 px (cada uma 400×540); headline de 68 para 60 px.
- [x] Preservar música e restante do conteúdo, validar arquivo final.
- [x] Publicar revisão v3 na conta Instagram conectada da marca pessoal e verificar link/status.
- [x] Desativar o item antigo R90 no fluxo de aprovação para impedir publicação duplicada da versão anterior durante a alteração.
- V3: `videos/2026-10-28-fingir-v2/2026-10-28-fingir-musica-headline-v3.mp4`, 35,572 s, 29.968.638 bytes, música/voz com SHA-256 idêntico à fonte; decodificação integral sem erros; quatro quadros inspecionados.
- Publicação imediata via Zernio, uma única requisição com Idempotency-Key; ID `6ae26538191365efca60876a`. Confirmado por nova consulta GET: published, sem erro, URL https://www.instagram.com/reel/DfDXrQ8EyS5/ .
- Cópia v3 salva em `Vídeos claude/Prontos/2026-10-28-fingir-musica-headline-v3.mp4`; versões anteriores preservadas.

## Revisão v2 — novo take e referência visual do usuário

Status v2: Ready for Review; prévia no WhatsApp, código R90, aguardando aprovação de postagem.
- [x] Identificar a fonte correta: `Prontos/8E65D8F0-627B-4A82-AAA3-D1A616F81A6B.mp4`, 35,566667 s, 41.952.392 bytes, enviado em 28/10 às 16h22. O arquivo de 56 s era o vídeo das viagens e não será usado.
- [x] Preservar música, voz, cortes e legendas já incorporadas à fonte enviada pelo usuário.
- [x] Substituir atleta pelas duas imagens fornecidas, lado a lado.
- [x] Headline literal com aspas: “quanto mais você finge, menos você finge.”, abaixo das imagens e acima/próximo do boné, seguindo referência.
- [x] Conferir MP4 e quadros finais e entregar revisão no mesmo destino Drive já autorizado.
- File list v2: `videos/2026-10-28-fingir-v2/` (fonte, mídia fornecida, transcrição local, cortes, legenda, exportador e revisão final).
- Scripts vigentes v2: `prepare_top.py`, `render_v2.py`, `validate_v2.py`, `send_approval.py`. Exportador anterior copiado não é usado. Pacote de aprovação em `docs/conteudo/maquina/02-Rascunhos/2026-10-28-codex-fingir-v2/`, com final.mp4 e legenda.txt.
- Validação v2: 35,572 s; 29.310.661 bytes; áudio SHA-256 idêntico à fonte com música; decodificação sem erros; quatro frames inspecionados; layout revisado por Rui; HyperFrames lint sem erros/avisos. Distorção de rosto perto de 21 s já presente na fonte foi sinalizada na aprovação.
- Drive v2: ID `1USRa2EwT-9cTxELW99offv85lGmSGdWM`, tamanho e MD5 conferidos. WhatsApp: R90, status previa; somente aprovação explícita aciona o fluxo existente de agendamento. Próximo horário consultado: 28/10 às 21h, Brasília.

## Objetivo
Editar o vídeo novo da pasta Vídeos claude no Drive, conforme pedido de 28/10/2026: somente uma inserção no topo e legendas sincronizadas.

## Critérios de aceitação
- [x] Identificar o vídeo novo: ABAB5FBE-6150-48AE-AF90-DE7003E00CE1.mp4, 43,366667 s, 1080×1920, 30 fps, enviado hoje às 15h14.
- [x] Transcrever localmente, sem enviar mídia a um serviço externo.
- [x] Usar uma única foto de treino no topo, com rosto livre, sem outras inserções.
- [x] Adicionar legenda branca sincronizada no peito.
- [x] Cortar pausas excessivas e auditar repetições/falsos começos, preservando a sequência da fala e reajustando as legendas.
- [x] Conferir quadros e integridade do MP4 final.
- [x] Atualizar handoff e entregar arquivo local.

## Decisões
- Fonte já existia no cache local do Drive, com tamanho igual à listagem remota: 51.007.201 bytes.
- Vídeo sobre “quanto mais você finge, menos você finge”; não é gravação do roteiro das viagens discutido anteriormente.
- Sem música, título, zoom, inserções laterais ou tela cheia. Uma foto constante no topo e legenda de uma palavra.
- Atualização do usuário: usar agentes de edição para depurar fala, repetições e pausas. Rui acionado para auditoria independente. Primeira exportação integral preservada; nova versão terá os cortes aprovados na análise editorial. Não foram detectadas frases refeitas; repetição do gancho é intencional.
- O keep automático de limpar.cjs foi descartado por perder palavras devido à diferença entre VAD e timestamps. Cortes finais baseados no interior dos silêncios (-38 dB), com margens de 120 ms, quantização a 30 fps e remapeamento de todas as palavras. Preservados início e pausa na pergunta dos atletas. Cauda mantém 400 ms após fala.
- Transcrição Groq bloqueada pela revisão automática por falta de consentimento explícito para envio a esse serviço. Alternativa local concluída com Whisper base e small; nenhuma mídia enviada ao Groq.
- HyperFrames skills update falhou (manifesto GitHub inacessível). Edição/exportação pelo fluxo leve FFmpeg/ASS existente, devido também à RAM livre observada de 0,64 GB. Arquivo de composição HyperFrames preservado como fonte editável; não afirmar render HyperFrames.
- Foto: Muhammad Ali e Rahaman Ali treinando, Tom Easterling, The Courier-Journal, 31/01/1960. Commons identifica PD-US-not-renewed; origem em CREDITOS.md.

## File list
- `docs/stories/video-fingir-insercao-unica-2026-10-28.story.md`
- `videos/2026-10-28-drive-insercao-unica/` (brief, transcrições, fonte da composição, exportador, foto, legenda, MP4 e validação)
- `videos/2026-10-28-drive-insercao-unica/plan_cuts.py`, `cuts.json`, `timing-corrections.json`, `build.py`, `validate.py`
- `videos/2026-10-28-drive-insercao-unica/revisao-rui.md`, `captions.ass`, `captions.json`, `validation.json`, `contact-sheet.jpg`, `preview-final.jpg`
- `videos/2026-10-28-drive-insercao-unica/fingir-insercao-legendas-cortado.mp4` (entrega final)
- `docs/sessions/CURRENT.md`

## Validação
- MP4 final: 38,066 s, 1080×1920, 30 fps, H.264/AAC, 47.632.860 bytes (45,4 MiB).
- Retirados 5,3 segundos em 12 intervalos de pausa/cauda. Nenhuma frase refeita identificada; gancho intencional preservado.
- 108 eventos de legenda; comparação textual confirma preservação das 112 palavras da transcrição small.
- Correção de alinhamento de “escolher” após pausa longa, conforme auditoria Rui; demais palavras remapeadas para o corte.
- MP4 decodificado integralmente sem erros; duração de vídeo e áudio compatíveis.
- Oito quadros finais inspecionados; foto acima da cabeça e legenda no peito, fora do rosto e área inferior de interface.
- Composição HyperFrames passa lint com zero erros/avisos. Exportação efetiva em FFmpeg; nenhuma afirmação de render HyperFrames.
- Scripts npm lint e typecheck ausentes na raiz. npm test de integridade do handoff executado no fechamento.
- Sem publicação ou envio por WhatsApp. Fonte original e primeira montagem integral preservadas.
- Upload solicitado e destino confirmado pelo usuário: `Vídeos claude/Prontos/2026-10-28-fingir-editado.mp4`, concluído em 28/10 às 16h09. ID `1ISl2QU5OH-ZKCc4HNfEaozY79HW36gvL`; tamanho e MD5 remoto conferidos com o local. Compartilhamento não alterado.
