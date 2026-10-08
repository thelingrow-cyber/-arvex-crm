# Primeiro teste — Kiwify 23:24–24:11

Fonte autorizada: podcast local de 1920×1080, 30 fps. Original preservado em Downloads.

## Entregas

- `kiwify-2324-2411-original.mp4`: extração horizontal exata de 47 segundos.
- `kiwify-2324-2411-edit-v1.mp4`: teste vertical 1080×1920, 30 fps, 32,033 segundos.
- `captions.srt` / `captions.ass`: legendas da edição com timestamps remapeados.
- `edit-manifest.json`: intervalos, crops, inserts, duração e decisões.
- `build-edit.cjs`: gera assets e renderiza localmente com FFmpeg; parâmetros em `render-args.json`.

## Decisões de edição

A seleção começa na frase “vou fazer conteúdo, vou vender o infoproduto” e encerra em
“expansão, seu crescimento”. Foram retirados o primeiro fragmento repetido, a retomada
“que ele é o expert”, parte de uma hesitação e a continuação final da conversa.
Todos os pontos de origem/saída estão registrados no manifesto. O arquivo bruto permite
comparar a edição com todo o intervalo solicitado.

O convidado de preto ocupa o quadro. Há duas escalas de crop e deslocamento horizontal
discreto; não foi realizada reconstrução facial. A resolução da fonte limita o detalhe
do recorte ampliado. A exportação em 1080×1920 não recupera detalhe perdido.

Por instrução do usuário, nenhum CRM, tela ou produto pessoal aparece nos inserts.
Foram desenhados três inserts conceituais: ecossistema da marca, IA/tecnologia e funil.
Não são provas de resultados nem telas de produtos. O CTA aparece escrito por 2,4 segundos
sobre um frame final congelado, sem voz sintetizada ou simulação de fala.

Áudio: filtro de graves abaixo de 75 Hz, compressão leve e normalização para alvo
-16 LUFS/-1,5 dBTP. Sem trilha musical adicionada. Sem alteração de velocidade da fala.

## Reprodução

Do diretório do projeto: `node output/video-edits/kiwify-2324-2411/build-edit.cjs --render`.
O render usa `-n` e não sobrescreve um vídeo existente. Dependências já disponíveis:
`@napi-rs/canvas`, fontes Segoe UI locais, FFmpeg portátil em `output/video-tools/`.

## Verificação e limites

ASR executado localmente com faster-whisper-small; nenhuma gravação enviada a terceiros.
Grafia de “infoproduto” normalizada. A maior parte final de reconhecimento incerto não
integra esta primeira montagem. A fala “Você pode ser explorado...” ainda requer conferência
auditiva humana na aprovação, pois a ferramenta de entrada de áudio não está disponível
nesta sessão. Não alegar que a revisão auditiva foi feita.

Dados técnicos do export e revisão visual serão registrados em `validation.json`.
Uma primeira versão tecnicamente verificada continua sujeita à aprovação estética do usuário.

Gates do repositório: `node --check` do script passa; lint, typecheck e build não existem
no package.json atual; `npm test` falha pelo formato pré-existente dos títulos de CURRENT.md.
Não foram alterados package.json, scripts do produto ou o contrato de handoff por este teste.
Sem publicação ou commit.
