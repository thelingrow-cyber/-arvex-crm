# Ponto de retomada — sessão 21 a 23/09/2026

> Atualizado em 2026-09-23, fim da sessão. Ferramenta: Claude Code (Opus 5).

## Objetivo da sessão

Construir a máquina de conteúdo da marca pessoal: editar vídeos sem editor, mapear o que funciona
no conteúdo dos players e transformar isso em roteiros graváveis.

## O que ficou pronto

### Os dois arquivos que travavam o squad de conteúdo
- **`squads/conteudo/voz.md`** — como o Vitor fala, extraído da **transcrição literal de 5 takes dele**
  (`tools/video-recut/work/*/words.json`), não de descrição inventada. Traz o ritmo, a assinatura
  (verbo repetido 3×, não tríade abstrata), a ordem obrigatória (admissão danosa antes do diagnóstico),
  o léxico, as palavras proibidas e 6 testes de roteiro.
- **`squads/conteudo/cliente.md`** — para quem o roteiro fala, com **nível de evidência por afirmação**
  (🟢 palavra real de lead · 🟡 hipótese da pesquisa · 🔴 lacuna). Fonte: call real da Letícia + pesquisa.
- ⚠️ Uma primeira versão do `cliente.md` foi montada sobre transcrições de lives da Cindy e **descartada
  a pedido do Vitor** — material de mentoria de terceiro não é fonte, nem para pesquisa interna.
  A regra ficou em `squad.yaml → fontes_proibidas` e no README do squad.

### Banco de pautas (`tools/roteiros/pautas.py`)
Combinatória no molde do método do Hulisses, com a fonte trocada: **fonte própria × 9 famílias de
gancho medidas**. Hoje: 10 livros · 90 capítulos · 11 artefatos · 8 dores · 3 inimigos.
Saída em `docs/conteudo/banco-pautas/` (`BANCO.md`, `GANCHOS-PRONTOS.md`, `INSIGHTS-LIVROS.md`).

### Biblioteca (`docs/conteudo/biblioteca/CURADORIA.md`)
Estante de IA para empresas em 4 tiers, com o que entra, o que fica de fora e por quê.
**Lidos de verdade: 1** ($100M Offers, do PDF, na pesquisa do clone). Faltam do Tier 1:
**Power and Prediction** e **Prediction Machines**. Pasta `.biblioteca/` criada e **gitignorada**
(arquivo de livro nunca vai pro repositório).

### Editor de vídeo — dois recursos novos
- **elemento `lista`** (`camadas.py`): título fixo em faixa no topo + lista numerada que se preenche,
  com os números visíveis desde o primeiro quadro. Sai como `.mov` único (13 PNGs em loop estouravam
  a RAM de 6 GB).
- **correção:** `"legenda": null` derrubava a renderização; agora desliga a legenda corretamente.

### Vídeos entregues
| Arquivo | Estado |
|---|---|
| `2026-09-plano-vs-prova.mp4` | **postado e aprovado** |
| `2026-09-agua-do-mar.mp4` | pronto — 6 cards, 2 em foto real (CC0), adaptação do Jett |
| `2026-09-leis-do-universo.mp4` | pronto — formato lista da Mila, 6 inserções intercaladas |

### Pesquisa de conteúdo (`docs/conteudo/`)
`ESTUDO-GANCHOS.md` (50 aberturas medidas, 9 famílias que funcionam, 5 que afundam) ·
`DOSSIE-ROTEIROS.md` · `banco-roteiros/referencias/` (~70 fichas) · `banco-roteiros/players/`.

## Regras de fonte que passaram a valer

1. **Material de mentoria de terceiro não é fonte** — nem para vocabulário interno.
2. **Foto de terceiro só com licença conferida** (CC0 / domínio público), origem anotada no
   `gerar-artes.py` de cada vídeo.
3. **Livro: título, autor e ano são fato; conteúdo do capítulo não.** Os "insights" em
   `INSIGHTS-LIVROS.md` são leitura própria provocada pelo título — o arquivo abre com a tabela do
   que é real e a lista do que é proibido falar na câmera.
4. **Número inventado não entra em roteiro.** Um mecanismo ("a pessoa teve o resultado primeiro e
   gravou depois") é mais forte que um dado estimado.

## Roteiros prontos para gravar

Em `docs/conteudo/banco-pautas/`: `ROTEIROS-LOTE-2.md` (5 roteiros), `GANCHOS-PRONTOS.md` (25 ganchos)
e `roteiro-dentista-suposicao-fatal.md` (final, com o histórico das 4 correções que o Vitor pediu).

## Próximo passo

1. Comprar **Power and Prediction** e **Prediction Machines**; jogar em `.biblioteca/` para virar
   ficha de leitura real (molde: `docs/clone-hormozi-pesquisa/resumos/livro-100m-offers.md`).
2. Coletar vocabulário real (DMs, transcrição das próximas calls) — hoje o `cliente.md` tem **um**
   lead como fonte verificada.
3. Decidir: oferta vigente (há 2 documentos) e posicionamento vigente (há 3 versões).
4. Regravar a frase "lei do terminal" no vídeo das 11 leis — o nome não existe (erro herdado da
   transcrição do vídeo original em inglês); o conceito é a lei do pensamento dominante.

## Decisões e limites registrados

- **Saída da Cindy é confidencial** — nunca em roteiro público.
- **Ótica é vertical bloqueada** publicamente; bastidor sim, nome do nicho no conteúdo não.
- **Roteiro que ele grava precisa soar falado** (ver `voz.md` e a memória `feedback-roteiros-sem-vicios-ia`).
- **O clone opina, o roteirista escreve.** Clone como consultor dá a lente; se o clone escrevesse,
  sairia o autor traduzido. Provado em `squads/conteudo/EXEMPLO-PIPELINE.md`.
- **Não usar material de terceiro dentro do vídeo publicado.** Arte original ou foto CC0 resolve.

## Frente paralela — carrossel institucional ARVEX (23/09)

Versão vigente para avaliação: `output/branding-arvex/carrossel-ter-ia-nao-basta-v2/`.
Contexto em `docs/carrossel-arvex/direcao-visual-v1-proposta.md` e
`docs/stories/arvex-instagram-rebrand-v1.story.md`. **Bloqueio:** aprovação visual da direção v2
ainda pendente; Georgia e Bahnschrift são fontes de trabalho, não famílias oficiais aprovadas.
