# Arquivos chatos — PUBLICADO 30/10/2026 04h08

- **Reel:** https://www.instagram.com/reel/DfHAuX0giis/ (Zernio post `6ae441d17b3c70c1e51b165d`).
- **Arquivo publicado:** `final-oficial.mp4`, a v6 com a música do Vitor (80,7 s). Ele subiu em Drive `Prontos/D1832DCD…mp4`.
- **Legenda:** `legenda.txt` ("siga: @vitorsimoesb" + hashtags).

## O que ele ensinou nesta edição (v1 → v6)

1. **Pixel art pura no estilo do Fabiano não serve.** Fica o híbrido: vídeo real recortado + interfaces + pouca pixel art. Tela dividida estilo Elias (sombra de 280 px fundindo, sem linha) e legenda da casa (Segoe UI Semibold 68).
2. **Abertura no molde da casa:** 3 fotos lado a lado no topo, que precisam ter a ver com a fala (laboratório/empresa, não pintura aleatória). Embaixo, título fino em Arial caixa-alta, grande (66) e um pouco abaixo das fotos.
3. **Vídeo citado na fala:** começa dividido e abre em tela cheia no momento-chave ("ninguém abre").
4. **Decupagem:**
   - Não engolir fim de palavra (só termina quando o som cai) e respiro de ~0,18 s entre frases.
   - Repetição escondida em "palavra longa" do Whisper: transcrever o trecho isolado. Na Handshake, a 2ª tentativa era a boa.
   - A gravação começava no meio do "Tem": foi emprestado o "tem" de outra frase (95,12–95,22 s), conferido pela transcrição.
5. **Menos repetição do número:** saíram "É sério, quatro milhões" e o "Quatro milhões" solto.
6. **Headline (Halbert):** "VENDERIA SEUS ARQUIVOS POR 4 MILHÕES?" fecha o ciclo com o "você vendia? comenta aqui" do fim.

Montador final: `tools/video-recut/work/2026-10-29-arquivos-chatos/build5.py` (decupagem em `corte/cortar5.py` + `juntar.py` + `respiros.py`, feitos para pouca RAM).
