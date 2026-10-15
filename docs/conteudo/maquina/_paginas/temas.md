# Listar temas não cobertos

## Quando esta página é usada
Na etapa 2: depois de cada coleta dos concorrentes (a cada 2 dias), pelo comando `python tools/maquina/maquina.py temas`.

## O que chega
- O caminho da coleta mais recente: `docs/conteudo/maquina/05-Concorrentes/coletas/<dia>/`, com um JSON por perfil (views, legenda, abertura e transcrição de cada reel).
- O caminho da lista atual, `01-Ideias/TEMAS-NAO-COBERTOS.md`, e o último número usado.

Exemplo de reel da coleta: `{"perfil": "jettfranzen", "views": 325243, "abertura": "When I was a kid, I thought this is what adulthood would look like. Imagine my disappointment."}`

## O que sai
Só as linhas novas da tabela, de 10 a 15, continuando a numeração:
```
| 4 | Você se sente atrasado em relação a um adulto que só existia na cabeça de uma criança de oito anos. | Identidade | pergunta com alvo | @jettfranzen https://www.instagram.com/reel/DedDyegxjJc/ | 325.243 |
```
Colunas: N · tema (a tese, numa frase do Vitor) · molde (Regra, Identidade, Tendência, Negócio ou Bastidor) · estilo de gancho · veio de (@perfil + link) · views.

## Como fazer
1. Leia `squads/conteudo/voz.md` e `docs/conteudo/maquina/_regras/proibido.md`.
2. Abra cada JSON da coleta e ordene os reels por views.
3. Para cada reel com muitas views, escreva a **tensão** dele como tese, nas palavras do Vitor.
4. Liste o que o Vitor já cobriu: as pastas de `03-Publicados/` e `02-Rascunhos/`, os títulos de `docs/conteudo/banco-pautas/` e as seções "Adaptação" das fichas de `docs/conteudo/banco-roteiros/referencias/`.
5. Corte toda tese que repete algo já coberto, mesmo com outras palavras.
6. Corte toda tese que cai no `proibido.md`.
7. Escreva as linhas no formato acima.

## Regras que não se quebram
- IA não é o assunto. *Motivo: o Vitor vetou duas vezes em 14/10.*
- Sem historinha, sem preço, sem negócio aberto. *Motivo: quatro roteiros reprovados em 14/10.*
- A tese parece errada à primeira vista. *Motivo: conselho que todo mundo já ouviu não vira vídeo (portão 7).*
- A frase do concorrente não entra, nem traduzida. *Motivo: modelar não é transpor (08/10).*

## Critério de pronto
- [ ] Toda linha começa com `| N |` e tem as 6 colunas.
- [ ] Toda linha tem link do reel de origem.
- [ ] Nenhuma tese aparece já coberta nas pastas e listas do passo 4.
- [ ] Nenhuma tese cai no `proibido.md`.
- [ ] Nada antes ou depois das linhas.

## Erros conhecidos
| Sintoma | Causa | Correção |
|---|---|---|
| (vazio: anotar aqui quando aparecer) | | |
