# Ponto de retomada

## ▶ RETOMAR AQUI — 16/10/2026 (Claude Code, Orion): automatizar a máquina de ponta a ponta

**Meta do Vitor:** ele só grava e aprova. Toda manhã recebe os roteiros no WhatsApp → grava → sobe no Drive → a máquina edita no molde certo → manda o vídeo no WhatsApp perguntando "aprovado?" → "pode" = posta/agenda no Instagram, sem ele abrir o app.

**Já ligado (16/10):**
- **Drive:** rclone instalado (winget, v1.75.1), remote `drive:` com escopo **só leitura** na conta thelingrow. Pasta de entrada "Vídeos claude" (nome tem espaço no fim) → usar o ID `1HbNe1b3WuKUBqaosktWyqtrIW3Loedj1` com `--drive-root-folder-id`. ⚠️ O rclone avisou que o client_id compartilhado será desativado em 2026: criar client_id próprio no Google Cloud.
- **WhatsApp:** instância **`maquina-vitor`** criada na Evolution (`wpp.viziom.io`, VPS Hostinger 187.77.206.39, Docker Swarm), conectada ao número pessoal do Vitor, **sem webhook e fora do CRM**. A máquina manda e lê na conversa "Você" (consulta periódica via `chat/findMessages`). A resposta dele chega com `remoteJid` em `@lid`, não no JID do número: o leitor precisa aceitar os dois. Envio e leitura testados.
- Env vars do usuário (Windows): `EVOLUTION_API_URL`, `EVOLUTION_API_KEY` (chave global).
- ⚠️ **Não conectar nada pelo botão de QR do CRM:** o `evolution-proxy` só conhece a instância `arvex-agente-sdr` (da Thalita) e trocaria o número dela.
- ⚠️ A chave global da Evolution passou pelo chat em 16/10: trocar junto com @devops (servidor + secret do Supabase + credencial do n8n, senão a Carol para).

**Próximo, em ordem:**
1. Ligar a etapa 9 ao montador: `maquina.py edicao` grava `edicao.md`, e o `tools/maquina/montar.py` (ainda sem commit) espera `edicao.json`.
2. Criar o maestro: roteiros às 6h → WhatsApp; vigiar o Drive → identificar o roteiro pela fala → corte → montagem → WhatsApp "aprovado?" → ler resposta; avisos de falha; trava para não rodar duas etapas na mesma pasta; vídeo limpo dentro da pasta do rascunho, não em Downloads.
3. Agendador do Windows (coleta a cada 2 dias + manhã).
4. Instagram: Graph API (conta profissional + Página do Facebook, ainda não confirmado), app na Meta com @devops.
5. Montadores por molde (Regra primeiro; depois Negócio/Identidade, Tendência; Bastidor e Referência sem receita).

---

## Retomada anterior — 15/10/2026 (Claude Code, Orion)

**Estado:** a máquina foi construída copiando o fluxo do Fabiano Carvalho (reel `DeSN2nhFZr3`, conferido quadro a quadro, mais o guia/PDF que ele entrega no direct). O mapa está em `docs/conteudo/maquina/README.md`.
- **Scripts:**
  - `tools/maquina/coletar.py`: etapas 1 e 3, concorrentes e banco de ganchos.
  - `maquina.py`: comandos `temas`, `roteiro N`, `revisar`, `reescrever`, `corrigir`, `corte`, `edicao`, `legenda`, `arquivar` e `status`.
  - `checar_voz.py`.
  - `guia_pdf.py`.
- **Como os agentes rodam:** cada etapa é uma sessão nova de `claude -p` lendo uma página, com 7 seções, em `_paginas/`. As regras ficam em `_regras/` (`proibido.md`, `nao-fale-assim.md`, `INCIDENTES.md` com a medição).
- **Rodou de verdade:**
  - coleta: 7 perfis e 73 reels;
  - 13 temas;
  - 42 ganchos;
  - 4 roteiros;
  - o guia em PDF do tema 8.
- **Roteiros prontos em `02-Rascunhos/`:**
  - **014 "Quem tá atrasado não pode correr": APROVADO pelo revisor**, é o recomendado.
  - 008 "Quem acerta ganha silêncio": tem capa, legenda e `guia.pdf`.
  - 003 e 004.

**Pendências do Vitor:**
1. Gravar o 014 ou o 008.
2. Aprovar o formato do guia do direct (`Downloads\guia-quem-acerta-ganha-silencio.pdf`).
3. Dar o ok para agendar a coleta a cada 2 dias no Windows.

**Próximo passo técnico, em ordem:**
1. Montagem automática do vídeo a partir do `edicao.md`.
2. Capa em imagem.
3. Postagem e agendamento pela API do Instagram (com @devops, credencial só por env).
4. Corrigir o @ do Speltz, que voltou vazio.
5. Refazer o `voz.md` com os takes de outubro.

**Regras novas (memória):**
- Roteiro avulso não tem IA como assunto, não é historinha e não é preço ou negócio aberto.
- Começa pelas referências do banco, na estrutura da Luana.

**Commits locais (sem push):** de `15918f9` a `8006379`, mais o fechamento desta sessão.

---

# Histórico — sessão 21 a 23/09/2026

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

## Atualização — novo player brasileiro (24/09)

Primeira referência de **Bruno Belissimo (@brunobelissimo.ai)** coletada pelo pipeline local:
Reel `DdXM4m7jDSF`, sobre Character Sheet para consistência de imagens. A ficha completa está em
`docs/conteudo/banco-roteiros/referencias/ref-brunobelissimo-disney-resolveu-isso-1937-DdXM4m7jDSF.md`
e o mapeamento provisório em `docs/conteudo/banco-roteiros/players/bruno-belissimo/README.md`.

Leitura provisória: educação prática de ferramenta + demonstração visual + captura por entregável.
Métricas observadas: 4.537 curtidas e 2.202 comentários; a taxa alta de comentários é contaminada pelo
CTA de palavra-chave para receber sheet e prompts. Não fechar padrão do player com uma peça. Faltam
grade, bio e 3–5 vídeos misturando fortes e fracos. Mecânicas aproveitáveis: problema visual em três
degraus, analogia histórica operacional e método transformado em objeto. Estado local, sem commit.

Segundo Reel do Bruno coletado: `DdSDX76gcrt`, notícia sobre desaceleração da corrida da IA, mercado
e migração de valor para empresas que aplicam a tecnologia. Ficha em
`docs/conteudo/banco-roteiros/referencias/ref-brunobelissimo-comenta-mentoria-pra-candidatar-DdSDX76gcrt.md`.
Comparação provisória: arquivo gratuito gerou 48,5% de comentários/curtida; candidatura para mentoria,
6,6%. Regra adicionada ao `ESTUDO-GANCHOS.md`: CTA por comentário mede também valor e fricção do
entregável. Checagem factual registrou que a abertura de capital da OpenAI foi descrita nas fontes como
adiada para 2027, não cancelada, e que a causalidade financeira apresentada no Reel é interpretação.
Player permanece provisório com duas peças e sem leitura de grade. Estado local, sem commit.

Terceiro Reel do Bruno coletado: `DdFLZ2CCnbM`, sobre a solução proposta pela OpenAI para
Navier–Stokes. Ficha em `docs/conteudo/banco-roteiros/referencias/ref-brunobelissimo-singularidade-tem-forma-tornado-DdFLZ2CCnbM.md`.
Métricas: 17.759 curtidas e 205 comentários. Primeira separação de função com n=3: visão/escala
histórica lidera em alcance aparente; ativo gratuito lidera comentário; candidatura para mentoria
fica abaixo. Constantes de edição nas três são estilo provável, não causa. Hipótese adicionada ao
`ESTUDO-GANCHOS.md`. Checagem factual: solução foi publicada e verificada formalmente pela OpenAI,
mas ainda dependia da avaliação da comunidade/Clay; evitar dizer "resolvido" como fato encerrado.
Player sobe para 🟡, ainda sem leitura de grade. Estado local, sem commit.

Quarto Reel do Bruno coletado: `Dc7Bc0aES57`, sobre o S1 da Skild AI aprendendo uma tarefa por vídeo.
Ficha em `docs/conteudo/banco-roteiros/referencias/ref-brunobelissimo-robo-nao-copiou-ovo-Dc7Bc0aES57.md`.
Métricas: 441 curtidas e 12 comentários, fundo do lote. O caso corrige a hipótese anterior: futuro
tecnológico sozinho não alcança. Navier–Stokes e S1 têm edição e função semelhantes, mas diferem 40×;
a peça forte liga a ruptura a escala histórica e destino humano, enquanto a fraca fica em produto,
benchmark e previsão setorial. Regra adicionada ao CAFEIA no `ESTUDO-GANCHOS.md`: toda notícia precisa
chegar a uma decisão, identidade ou consequência humana do dono. Estado local, sem commit.

Quinto Reel do Bruno coletado: `Dcw2VRWjgKz`, sobre energia, data centers e Amazônia. Ficha em
`docs/conteudo/banco-roteiros/referencias/ref-brunobelissimo-isso-acontecendo-aqui-enquanto-Dcw2VRWjgKz.md`.
Métricas: 3.445 curtidas e 225 comentários. Com cinco peças, o lote mínimo fecha quatro funções:
alcance (escala histórica), captura (ativo gratuito), conversa (ameaça localizada/dilema), oferta e
boletim técnico. O novo caso mostra 6,5% de comentários/curtida sem isca, sugerindo que polêmica
localizada produz conversa. Foram registradas correções factuais sobre Three Mile Island, Amazon e
projeções de água. Mapeamento ainda 🟡 porque falta a grade de visualizações. Estado local, sem commit.

Perfil geral do Bruno lido no Instagram e nos destinos da bio. Dados públicos em 24/09: 845 mil
seguidores, conta verificada; bio “Ajudo criadores a crescer com IA” + Stanford + “Monte sua Máquina
de Conteúdo”. Arquitetura fechada: `IA + Mente` é mídia ampla de ciência/notícia/ferramenta; a
monetização converge para creators via curso Máquina de Conteúdo, mentoria por aplicação, gratuitos e
afiliados de ferramentas. Nove Reels recentes medidos por curtidas/comentários; mediana 1.148/82.
Sem login, Instagram não expôs views. Contraste registrado: Bruno explica o que a IA está fazendo;
Vitor mostra o que uma empresa deve construir por causa disso. Estado local, sem commit.
## Atualização — CAFEIA episódio 2 (24/09/2026)

- Selecionadas duas pautas para gravação em 25/09/2026, com fontes primárias de 23/09/2026.
- Roteiros salvos em `docs/conteudo/pautas/2026-09-25-cafeia-episodio-2.md`.
- Peça 1: ChatGPT Ads, função conversa, tensão busca × conversa.
- Peça 2: agentes do Claude em pesquisa biológica, função alcance, tensão geração × critério.
- Limites factuais preservados: anúncios não implicam acesso do anunciante à conversa; função do sistema enzimático ainda é desconhecida.
## Atualização — edição CAFEIA Amazon × Muse (24/09/2026)

- Vídeo bruto copiado de Downloads para `videos/cafeia-amazon-muse/input.mp4`; original preservado.
- Transcrição local com timestamps em `videos/cafeia-amazon-muse/transcript.json`.
- Depuração reduziu 74,8s para 50,6s, removendo recomeço do Muse, silêncio entre tomadas e tentativas repetidas do fechamento; a última formulação correta foi preservada.
- Montagem final em `videos/cafeia-amazon-muse/CAFEIA-amazon-muse-final-v2.mp4`.
- Edição: 9:16, tela dividida, demonstração oficial do Muse publicada pela Meta, cards Amazon × Meta, legendas, cortes secos, correção leve de brilho/contraste/saturação e áudio normalizado.
- Validação: H.264 1080×1920, ~30 fps, AAC estéreo 48 kHz, 50,63s; decodificação completa sem erros e revisão por folha de contato.
- Limitação: o scaffold do HyperFrames falhou com erro de acesso no caminho Windows; a renderização foi concluída localmente com FFmpeg usando o plano visual definido.
- Revisão posterior: removida pausa de 2,52s entre “o motivo pode” e “mudar”. Arquivo vigente: `videos/cafeia-amazon-muse/CAFEIA-amazon-muse-final-v3.mp4`, 48,12s. A análise dos 9s iniciais agora encontra apenas uma respiração natural de 0,37s.
- Correção de naming solicitada: selo de abertura e legenda agora usam `COFFEE IA`. Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final.mp4`.
- Validação final: 48,116s, H.264 1080×1920, uma faixa AAC estéreo 48 kHz e decodificação completa sem erros. O corte da pausa inicial foi preservado.
- Segunda revisão visual e de ritmo: abertura estática substituída por motion editorial sobre retrato desfocado, com entradas separadas de Amazon, Meta, tensão e manchete; removido o aspecto de slide/cartões da abertura.
- Oito respiros internos foram encurtados, preservando pausas naturais de aproximadamente 0,15–0,20s. A duração caiu de 48,116s para 46,167s; não restaram silêncios maiores que 0,30s além de uma pausa natural de 0,319s no fechamento.
- Novo arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v2.mp4`. Validado em H.264 1080×1920, AAC 48 kHz e decodificação completa sem erros.
- Terceira revisão: o retrato desfocado/transparente da abertura foi substituído por uma imagem editorial opaca de logística × agente de compras, gerada com a ferramenta nativa de imagem e salva em `videos/cafeia-amazon-muse/opener-background-v2.png`. Motion e tipografia foram preservados sobre a nova base.
- Auditoria de fala refeita no bruto e na montagem: as retomadas de “O Muse...” e as múltiplas tentativas de “porque agora a sua empresa...” foram removidas, mantendo as formulações posteriores completas. A transcrição da versão entregue não contém frase duplicada.
- Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v3.mp4`, 46,20s, H.264 1080×1920, uma faixa AAC 48 kHz; decodificação completa sem erros e abertura revisada por folha de contato.
- Quarta revisão: removido o movimento lateral/senoidal da imagem inicial; a base agora permanece estabilizada e recebe somente as entradas dos elementos gráficos.
- Criado sting de marca `COFFEE IA — Negócios em movimento`, exibido no painel visual superior quando o nome da série é falado, sem cobrir o rosto nem as legendas.
- Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v5.mp4`, 46,20s; abertura e sting revisados em quadros, decodificação completa sem erros.
- Revisão profissional de ritmo e sincronização: a fala foi acelerada em 1,06× sem mudança de tom; 17 intervalos entre palavras foram comprimidos pelas bordas da transcrição e os dois vazios residuais acima de 0,20s foram removidos.
- A assinatura `COFFEE IA` agora começa junto da frase “Esse é o COFFEE IA” e termina antes de “O Muse”; sincronização conferida em quadros.
- Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v7.mp4`, 40,967s, H.264 1080×1920, uma faixa AAC 48 kHz. Não há silêncio detectável acima de 0,20s e a decodificação completa terminou sem erros.
- Revisão pedida pelo usuário: o intervalo sem fala após “o motivo” foi cortado; a primeira ocorrência de “compra” foi removida, mantendo a segunda após “depois”. A transcrição local dos trechos revisados confirma a sequência “e o motivo pode mudar” e uma única ocorrência de “depois compra”.
- O card preto “#1” foi substituído por mapa dos Estados Unidos e uma captura da demonstração oficial do Muse; o trecho anterior usa a demonstração do produto. Arte em `videos/cafeia-amazon-muse/us-muse-rank.png`, gerada a partir de `us-map-background.png` e `muse-phone-list.png`.
- Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v9.mp4`, renderizado localmente com sucesso e confirmado no disco (~20,4 MB). A versão intermediária v8 teve decodificação completa, 39,733s, H.264 1080×1920 e AAC 48 kHz; v9 altera somente uma microtransição de áudio de 12 ms no corte de “compra”. A decodificação adicional de v9 foi impedida por limite de uso na revisão automática de ferramentas, sem avaliação de risco. Próximo passo opcional: reprodução integral de v9 no app pelo usuário.
- Nova revisão: reconstrução da camada do apresentador a partir de `input.mp4`, com mapeamento dos cortes em `videos/cafeia-amazon-muse/timeline_map.py`. Legenda refeita por palavra em `render_v10.py` e `captions-v10-words.json`, com uma ocorrência de “e depois compra com a sua autorização” conferida por ASR local. A transição para o enquadramento inteiro ocorre em 33,03s e o retorno anterior ao plano inteiro em 6,20s. Marca `COFFEE IA` centralizada durante a fala, entre 6,79s e 7,55s; marca antiga fora da transição seguinte. Arquivo vigente: `videos/cafeia-amazon-muse/COFFEE-IA-amazon-muse-final-v10.mp4`, 39,733s, H.264 1080×1920, AAC estéreo, 1192 quadros. Vídeo e áudio decodificados sem erros; áudio tem o mesmo hash de pacotes da versão v9. Entrada/saída da marca e transição em 33,03s conferidas quadro a quadro.

## Atualização — 01 a 03/10/2026 (Claude Code)

**Objetivo:** produção de conteúdo da marca pessoal — análise de players, roteiros e edição.

**Feito:**
- Players analisados: Vitor M. Guerrero (60 reels, `banco-roteiros/players/vitor-guerrero/`), Herman Lind (manifesto, `ref-herman-1ind-…-Dd42Xg8MIEi.md`), Alex Sidhu (3 leituras com página real atrás, `ref-alexbsidhu-…-Dd50M91xspO.md`).
- Postados: manifesto "timidez é covardia" (~5k, público misto); Reagan/sócio que não trabalha (eleição, edição `tools/video-recut/videos/2026-10-reagan-socio/`); "3 leituras de IA" (molde Alex, `videos/2026-10-tres-leituras-ia/montar.py` — recorte desde o início, pessoa se move, páginas reais rolando, gancho em grade 2×2, CTA direct). Postado 03/10 03:30.
- Semana com 2 virais (segundo o Vitor). Ritmo atual: 2–3 vídeos/dia há 3 semanas.

**Decisões:**
- IA é o eixo; filosofia/política entram como lente. Estrutura Elias/Tay: tema aberto → ponte (~75%) → tese com slogan fixo → fecho sem lamento.
- Formato "página real atrás" = captura (medir por directs), 1×/semana; não é formato de alcance.

**Próximo passo (04/10):** estruturar de vez os formatos para subir o volume com qualidade (meta da grade = 5/dia, `docs/conteudo/CALENDARIO-EDITORIAL.md`): fixar 4–6 moldes com roteiro-modelo + receita de edição de baixo custo cada; definir o slogan/tese (3 opções a partir do brand book v2). Pendentes: resumos PT dos 3 textos para os directs; números dos 3 posts.

**Sem commit:** pastas novas em `tools/video-recut/videos/2026-10-*` e fichas novas de referência.

## Objetivo ativo

Preparar para 07/10/2026 um carrossel da marca pessoal do Vitor que complemente o vídeo “Se eu fosse presidente” sobre o Brasil virar potência em IA.

## Estado atual

Sete lâminas 1080 × 1350, contact sheet, fonte de renderização e legenda estão em `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/`. Story em `docs/stories/conteudo-presidente-ia-carrossel-2026-10-07.story.md` está Ready for Review. QA independente revisou os PNGs e considerou conteúdo e visual prontos para revisão do Vitor. Nada foi publicado.

## Commits relevantes

Nenhum commit criado nesta entrega. As alterações locais preexistentes foram preservadas.

## Validação

Os sete PNGs foram gerados, reabertos em tamanho integral e na contact sheet, e confirmados em 1080 × 1350. `node --check` e renderização com `node output/carrossel-marca-pessoal/presidente-ia-2026-10-07/build.cjs` passaram. O dado “entre os três maiores mercados do ChatGPT por usuários ativos semanais” foi checado na publicação oficial da OpenAI de 27/08/2026; ranking composto de 2023 e pesquisas não específicas de IA foram excluídos. `npm test` passou (checagem de integridade do handoff). `npm run lint` e `npm run typecheck` não existem no `package.json`.

## Bloqueios e riscos

A proposta de fundos de pensão é opinião, não política em vigor; a arte explicita parcela limitada, diversificação e controle de risco. Imagens conceituais geradas estão rotuladas sobre as lâminas 4 e 6. A comparação foi feita com roteiro v8 e transcrição do bruto, não com a montagem final publicada; a checagem humana do vídeo publicado permanece aberta.

## Próximo passo recomendado

Vitor revisar a contact sheet e conferir as três propostas com o vídeo publicado; então publicar as lâminas 01–07 na ordem e usar a legenda do README, se aprovada.

## Como retomar

Abrir `output/carrossel-marca-pessoal/presidente-ia-2026-10-07/contact-sheet.png` e `README.md`; qualquer ajuste visual pode ser feito em `build.cjs` e reexportado pelo comando acima. Consultar a story para checklist e limites de verificação.

## Atualização — 08/10/2026 (Claude Code, encerrada por desligamento)

- **Pauta do dia** montada a partir do `BACKLOG.md` (não gravada na AGENDA): 5 vídeos MP (MP-03/MP-13), VZ-02, LG-12; OF-12 se houver roteiro. Pendente: Vitor dizer o que saiu de 05–07/10 para marcar no backlog (3ª semana sem `fechar`); OF-08 (Letícia) candidata a `[~]`.
- **Linha editorial vigente = v3** (`LINHA-EDITORIAL-FORMATOS.md`): 2 formatos — 3× Regra dita como lei + 2× Tendência → negócio. Encaixe do estoque: Regra = César/Rubicão, Muhammad Ali, Yerkes-Dodson; Tendência = CAFEIA "nem quem fez garante" + **1 a escrever**. Platão e "quando estiver pronto" são curtos demais (reserva). Roteiros precisam das 2 frases fixas (dobradiça + assinatura).
- **WhisperFlow:** daemon OK; desde o boot de 08/10 toda gravação é descartada por silêncio. Mic padrão Realtek, não mudo, vol 56%, permissão OK, mas RMS ~0,001 (limiar 0,015). Suspeita: fone/headset de ontem desconectado ou tecla de mudo do notebook. Retomar re-medindo o mic.
- **Commit:** tudo exceto mídia pesada (mp4/mov/m4a/wav/bin) — vídeos ficam só locais.

**Próximo passo:** escrever a 2ª Tendência + ajustar os 5 roteiros à v3; confirmar o mic.

## Atualização — 13/10/2026 (Claude Code): engenharia reversa dos players e grade de 10 por dia

**Objetivo:** fechar a engenharia reversa de Luana, Tay e Elias e definir a grade para a meta da semana, 10 vídeos por dia.

**Feito:**
- `players/{luana-carolina,tay-dantas,elias-maman}/ESTUDO.md` ganharam duas seções cada: a máquina (bio, oferta, funil, onde entra o CTA, crenças que os vídeos instalam) e como gravam (folhas de contato dos maiores, em `tools/roteiros/work/estudo/<usuario>/folhas/`, fora do git).
- Correções no que o estudo afirmava: os dois maiores "cortes" da Luana são tela dividida "19 anos × 25 anos" (falta reclassificar em `classificacao.json` e regerar anexos); a "dobradiça" da Tay aparece literal em só 2 de 50 reels (corrigido no estudo e na `SINTESE-FORMATOS.md`).
- `docs/conteudo/LINHA-EDITORIAL-FORMATOS.md` virou **v4**: 10 por dia = 2 referências + 2 negócio com IA no meio + 2 regras + 2 identidade + 1 tendência + 1 bastidor. Portão ganhou 3 itens (um assunto só, conclusão dita, chegada concreta).

**Decisões do Vitor:**
- Herói = dono de negócio que sente que está sempre atrasado; paralelo = Tay; "AI Native" no fim, não como assunto.
- Sem dobradiça nem frase-assinatura fixa por ora.
- "Você não comprou errado, comprou a peça que vem antes" é brusca como fecho; vira uma Regra inteira.
- Processo: a IA gera o cardápio (~25 linhas), ele aprova por voz e grava.

**Limites do que foi visto:** formulários de aplicação da Tay e do Elias não abriram; stories de nenhum dos três; folhas só dos 6 a 8 maiores de cada um; as tabelas de crenças são leitura do agente.

**Pendências com o Vitor:** o que pode aparecer na tela no Bastidor; o que ele vende hoje, para quem e por quanto; o que está de fato funcionando para mostrar (o dossiê e a memória divergem sobre o agente de atendimento); as 2 referências de cada dia.

**Próximo passo:** montar o primeiro cardápio na grade v4 (lista de crenças do herói → Regras; fatos do dia com fonte → Negócio e Tendência). Matheus Gomes ainda não passou pelo mesmo aprofundamento de funil.

**Estado:** commit local; nada publicado no remoto.

## Atualização — 14/10/2026 (Claude Code): 2 vídeos editados e molde de edição aprovado

**Feito:**
- Roteiro "Chegue atrasado" (Regra, molde Luana) escrito com o Vitor em várias rodadas; ele gravou e o vídeo foi editado: `tools/video-recut/videos/2026-10-chegue-atrasado/montar.py` (topo fixo com título, pares de imagens nas laterais, página do repositório REA no topo no trecho em que ele fala dele).
- Vídeo "Rei do gelo" (Frederic Tudor) editado em 4 versões até ele aprovar ("perfeito"): `tools/video-recut/videos/2026-10-rei-do-gelo/montar.py`. Saídas em `Downloads\` (mídia fica local).
- **Molde aprovado** (registrado na memória): pintura clássica histórica/filosófica FIXA no topo, cantos retos; título em Bebas Neue; legenda uma palavra por vez em Montserrat ExtraBold com contorno; inserções reais nas laterais, alternando. Reprovado: borda redonda, logo em fundo branco, imagem genérica, Segoe de 3 palavras.
- Fontes livres em `tools/video-recut/assets/fontes/` (Bebas Neue, Montserrat).

**Players (14/10, tarde):** `players/CATALOGO-MOLDES.md` (todos os moldes de cada player, com veredito e variantes por vaga); fichas completas dos moldes 3–5 e edição por molde na linha editorial; Luana reclassificada; **novo player Fabiano Carvalho** (`players/fabiano-carvalho/ESTUDO.md`): concorrente direto (vende IA ao dono), ~7 posts/dia num relógio fixo, pedido de comentário em 48/50, e descreve o próprio fluxo de agentes.
**Próximo projeto decidido pelo Vitor:** depois de terminar a estruturação, instalar esse fluxo de agentes de conteúdo (ver seção 1 do estudo do Fabiano).

**Pendências:** créditos das imagens (CREDITOS.txt de cada vídeo) para a legenda do post; no "Chegue atrasado", o Vitor ainda não rodou o REA (primeiro uso pendente); cardápio da grade v4 segue por montar.
