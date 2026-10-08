# Kiwify — revisão V5

Pedido executado: preservar a abertura com criar um ecossistema; retirar o primeiro
“dentro”, “em algo específico”, a pausa após IA e a hesitação “é” depois de “vai”.
V1–V4 e fonte preservadas. Sem CRM/produtos pessoais, CTA ou avisos ilustrativos adicionados.

## Montagem

- 21,067s, 1080×1920, 30fps, H.264/AAC. Voz acelerada moderadamente, sem mudar altura.
- Cortes finos em nove blocos, tempos originais/remapeados no manifesto.
- IA: motion novo de estrutura sendo formada, substitui completamente código filmado e card antigo.
- Construir marca: 1,65s do vídeo da Manu Cit incorporado à página oficial da Guday.
  É apresentação da marca, não ensaio de modelagem. Vídeo sem seu áudio original.
- Funil: redesenhado, linhas/fluxos animados, ramificação para marca/comunidade/tech.
- Três flashes quentes isolados; contraste e nitidez aumentados moderadamente.
- Música substituída por Fallen (Asper), Eugenio Mininni, Mixkit; redução automática sob a voz.

## Fontes e direitos

Guday: https://guday.com.br/pages/historia — vídeo na seção
“UMA MENSAGEM DA NOSSA FUNDADORA / Olá, eu sou a Manu Cit”. Atribuição por texto da
página, não reconhecimento facial. Fonte pública não equivale a licença de reutilização:
confirmar autorização antes de publicar a peça. Nenhuma publicação realizada.

Música: https://mixkit.co/free-stock-music/mood/serious/
Arquivo: https://assets.mixkit.co/music/565/565.mp3
Catálogo: Fallen (Asper), Eugenio Mininni, Atmospheres/Film Score/Mysterious/Documentary/Mystery.
Licença anunciada: Mixkit Stock Music Free License. Motion criado localmente em canvas.

## Reprodução e verificação

Na raiz do projeto:

```powershell
node output/video-edits/kiwify-2324-2411/v5-assets/build-motions.cjs
node output/video-edits/kiwify-2324-2411/build-v5.cjs --render
node output/video-edits/kiwify-2324-2411/check-v3.cjs --v5
```

Os scripts preservam MP4s existentes. Não sobrescrever para reexecutar: usar nova versão.
`validation-v5.json` registra decodificação, streams, duração e loudness; `qa-v5.jpg`
reúne oito quadros. Pré-visualizações dos motions na pasta v5-assets.

Limite: a sessão não oferece escuta ao modelo. As emendas vêm do feedback do usuário,
ASR local e waveform. Em especial, o ASR omitia a repetição de dentro e juntava a
hesitação com vai; ajustes manuais estão registrados no script. Escuta humana de
emendas, legendas e equilíbrio subjetivo da nova trilha permanece pendente.
