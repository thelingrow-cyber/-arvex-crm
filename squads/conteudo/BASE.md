# 📚 BASE — o que o squad lê, e o que está superado

> Atualizado em 2026-09-23. **Este é o ponto único de entrada.** Antes de escrever qualquer coisa, o agente lê daqui.
> Regra: documento que não está nesta lista não é fonte. Documento marcado como SUPERADO nunca é fonte.

## Vigente — pesquisa de conteúdo (construída em 21-23/09/2026)

| Fonte | O que resolve |
|---|---|
| `docs/conteudo/ESTUDO-GANCHOS.md` | as 9 famílias de gancho que funcionam e as 5 que afundam, com desempenho medido em 50 aberturas |
| `docs/conteudo/DOSSIE-ROTEIROS.md` | cruzamento viral × normal por player, com ressalvas metodológicas |
| `docs/conteudo/banco-roteiros/referencias/` | ~65 fichas: transcrição com tempo, arquitetura por segundo, mecânicas nomeadas |
| `docs/conteudo/banco-roteiros/players/` | player fechado: hormozi · daniel-dalen · matheus-gomes · gringos-ia · troncoso · seb-stritt |
| `docs/conteudo/pautas/` | histórico de pautas colhidas (evita repetir assunto) |
| `docs/conteudo/roteiros-prontos/` | roteiros escritos e ainda não gravados |
| `docs/conteudo/DESEMPENHO.md` | o que foi publicado e como performou no 7º dia — **a base que manda quando existir dado próprio** |

## Vigente — marca e grade

| Fonte | O que resolve |
|---|---|
| `docs/ecossistema/linha-editorial-e-calendario.md` | grade fixa da semana e a função de cada dia |
| `docs/ecossistema/sistema-de-roteiro.md` | famílias G1-G10, esqueleto por formato e os 5 filtros antes de gravar |
| `docs/ecossistema/sistema-de-conteudo.md` | rede de pesquisa e a operação da semana |
| `docs/ecossistema/brand-book-marca-pessoal.md` | arquétipo e tom — **conferir se a categoria citada é a do Brand Book v2** |

## ⚠️ Em conflito — o Vitor precisa dizer qual manda

- **Posicionamento:** `posicionamento-v1-negocio-nativo.md` · `DOSSIE-POSICIONAMENTO-2026-09.md` · `posicionamento-marca-pessoal-ORIGINAL.md`
- **Oferta:** `oferta-v1-catalogo-instalacao.md` · `ofertas/oferta-leticia-wendy.md`

## Faltando (nenhum agente resolve sozinho)

| Arquivo | Como se alimenta |
|---|---|
| `squads/conteudo/voz.md` | trechos que o Vitor aprovou e reprovou, palavras que ele usa e recusa |
| `squads/conteudo/cliente.md` | 10 a 20 mensagens REAIS de dono de negócio (DM, WhatsApp, trecho de call), com as palavras deles |

## Como adicionar material novo

**Referência de criador** → `python tools\roteiros\colher.py <url>` → a ficha nasce em `referencias/`.
Ao fechar 3 a 5 do mesmo perfil, rodar a task `fechar-player` e atualizar o `ESTUDO-GANCHOS.md`.

**Vídeo longo ou material solto** (transcrição de podcast, aula, print) → destilar em `players/<nome>/README.md`.
Nunca colar o material bruto inteiro: o banco guarda **mecânica com nome**, não acervo.

**Aprendizado do próprio Vitor** (o que deu certo nos vídeos dele) → `DESEMPENHO.md`. Esse tem precedência
sobre qualquer player de referência: dado próprio manda mais que dado de terceiro.