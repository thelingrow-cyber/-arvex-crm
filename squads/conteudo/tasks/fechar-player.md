# task: fechar-player

**Agente:** analista-referencias · **Saída:** `docs/conteudo/banco-roteiros/players/<nome>/README.md` + estudo atualizado

## Passos

1. Colher de 3 a 5 peças do mesmo perfil, misturando as que foram bem e as que foram mal:
   `python tools\roteiros\colher.py <url> [--lang pt|en]`
2. Abrir o perfil no navegador e medir a **grade de Reels** (visualizações por vídeo).
3. Comparar **dentro** do perfil. O que aparece também nas fracas é estilo, não causa.
4. Checar a época dos posts — número baixo em post antigo pode ser tamanho de conta.
5. Fechar o README do player: posicionamento, grade, mecânicas, o que copiar, o que não copiar, contraste com o Vitor.
6. Atualizar `ESTUDO-GANCHOS.md` com as aberturas novas. Se um caso contradisser uma regra, **corrigir a regra** e registrar o caso.

## Falhas conhecidas

- Concluir com um vídeo só: sem os fracos, tudo parece funcionar.
- Tratar transcrição automática como citação literal (o Whisper já grafou "ChadGBT" e "atletista").