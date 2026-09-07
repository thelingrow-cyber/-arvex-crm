# RETOMAR AQUI — Lançamento Desafio Ótica +100K

> **Sessão encerrada em 04-05/09/2026.** Este arquivo é o ponto de retomada: o que está pronto,
> onde exatamente paramos e o que fazer no próximo passo.

---

## O evento

**Desafio Ótica +100K** — 22, 23 e 24 de setembro de 2026 (terça, quarta e quinta). **3 dias**,
ao vivo, gratuito. Público: donos de ótica. Objetivo da campanha: encher o grupo VIP de WhatsApp,
que é onde a oferta é feita e de onde saem as calls com a Cindy (fluxo Webinário do
`docs/processos/sop-fluxo-vendas.md`).

**Headline oficial da página:**
> Crie em 3 dias comigo a estratégia que vai colocar a sua loja na rota dos +100K por mês.

---

## O que está PRONTO

| | Entrega | Onde |
|---|---|---|
| ✅ | **Nome do evento** (CD-12, fechado 02/09) | Aplicado em tudo |
| ✅ | **Data e formato**: 22-24/09, 3 dias | Aplicado nas 13 peças e no plano |
| ✅ | **Swipe destilado** das 2 peças que já converteram | `docs/materiais-cindy/swipe-criativos.md` |
| ✅ | **13 criativos** prontos, sem variável aberta | `criativos-ad-grid.md` (M1-M11 + C5, C6) |
| ✅ | **Ad Grid** 3 avatares × 6 hooks — 12 células ainda não escritas, guardadas | `criativos-ad-grid.md` |
| ✅ | **Plano de mídia**: 4 ad sets, 6 peças no ar, R$ 50/dia, 5 dias antes de ler | `criativos-ad-grid.md` |
| ✅ | **Headline da página** | `PAGINA-PLANO.md` §5 |
| ✅ | **Estrutura da página** fechada pelo CRO — 5 blocos, 2 CTAs | `PAGINA-PLANO.md` §4 |
| ✅ | Plano da live dos 100 dias (04/09) e banco de temas | `docs/materiais-cindy/` |

---

## ONDE PARAMOS — o próximo passo exato

**A página está construída** (07/09). `index.html` tem os 5 blocos da estrutura do CRO, copy
escrita, sistema visual aplicado e o clique instrumentado. Passos 3, 4, 5 e 6 do fluxo, feitos.

**Falta só o passo 7: teste em mobile real e publicar.** E antes de subir tráfego, destravar os
3 bloqueios abaixo — todos estão marcados com comentário `BLOQUEIO N` dentro do próprio HTML.

### O que a página faz hoje

| Bloco | Conteúdo |
|---|---|
| Topbar | Carrega a **data** (`Ao vivo · 22, 23 e 24 de setembro`), não mais "Desafio ao vivo · Online" |
| 1. Primeira dobra | Logo · eyebrow `Online e gratuito · para donos de ótica` · headline fechada · subhead · CTA. **Sem animação** — nada na primeira dobra espera IntersectionObserver |
| 2. O que você sai tendo | 3 cards: a campanha montada · a direção do próximo passo · vendas que não dependem da rua |
| 3. Prova de par | Fran/Curitiba (+R$ 9 mil em 10 dias) · Kesia (100 no grupo em 20 dias) · Rafaela/Floripa (R$ 10-12k → R$ 22k) + nota de que resultado não é promessa |
| 4. Quem é a Cindy | Foto **local** integrada com mask · bio de 3 linhas · 3 selos (+8 anos, +500 óticas, método Ótica 10X) |
| 5. CTA final | Data · "o desafio acontece dentro do grupo" · botão repetido |

**Correções aplicadas:** saiu "vagas limitadas", saiu o eyebrow "Sua ótica faturando 2x", saiu
"5 dias" (agora 3), saíram as duas imagens hospedadas em `cindyb.com.br` (agora `cindy-dinheiro.jpg`
e `cindy-foto.jpg`, locais). Entrou a data, entrou prova, entrou autoridade.

**O clique está instrumentado** — era o pré-requisito nº1 do CRO. Cada CTA dispara `fbq Lead` +
`fbq trackCustom ClickGrupoVIP` + `gtag generate_lead` + `dataLayer.push`, todos carregando a
posição (`hero` ou `final`). É isso que vai dizer se a perda dos 50% é na página ou na passagem
para o WhatsApp.

**Decisão que eu tomei sozinho e você pode reverter:** escrevi o bloco 3 com os 3 casos reais do
ICP (nome, cidade, número), não com placeholder. A fonte é `icp-dono-de-otica.md` §5, lote 3 de
lives. Está marcado no HTML como BLOQUEIO 2 — se a Cindy não autorizar algum nome, é trocar o
texto do card, não refazer o bloco.

---

## Bloqueios — o que impede subir

| | Bloqueio | Impede | De quem depende |
|---|---|---|---|
| 1 | **Link do grupo VIP** — os 2 CTAs apontam para `chat.whatsapp.com/Lpn1xk…`, do evento anterior. Marcado no HTML como `BLOQUEIO 1`, em 2 lugares | Publicar | Vitor / Cindy |
| 2 | **Prova nomeável** — os 3 casos já estão escritos no bloco 3; falta a Cindy autorizar nome e confirmar número. Marcado como `BLOQUEIO 2` | Subir tráfego com a página como está, e os criativos M6 e C6 | Cindy |
| 3 | **Pixel Meta** — ainda `PIXEL_ID` placeholder. Marcado como `BLOQUEIO 3` | Subir tráfego e todo o retargeting (M5, M2, M10) | Vitor |
| 4 | **Imagens e vídeos** dos 13 criativos | A campanha, depois da página | Produção |
| 5 | **Formato dia a dia do evento** — o criativo M10 promete "cada dia termina com uma coisa feita" | Se as lives forem expositivas, essa peça mente na entrega | Cindy |

---

## Decisões tomadas nesta sessão (não reabrir sem motivo)

1. **CTA vai direto para o grupo**, sem formulário de captura. Consequência aceita: o contato não
   entra no CRM; a lista vive no grupo. Se um dia quiserem a lista, coletar **dentro** do grupo,
   não devolver formulário para a página.
2. **3 dias**, não 4 nem 5.
3. **Sem "vagas limitadas"** e sem contador — escassez fabricada em evento gratuito online derruba
   credibilidade num público já queimado por mentoria.
4. **Animação só do bloco 2 para baixo** — `reveal` com delay atrasa a primeira dobra no 4G.
5. **Foto local**, não a URL de `cindyb.com.br`.

---

## Duas correções de rumo que valem lembrar

**Sobre números na copy.** A regra "não usar 10X nem número redondo" estava errada. As peças que
converteram usam os dois. A distinção real: número como **prova de terceiros** ou **promessa
hedgeada** funciona; **promessa direta ao leitor** queima. Por isso o nome "+100K" não é risco —
ele vem da peça vencedora.

**Sobre promessa em página × em anúncio.** As páginas da Cindy sempre prometeram resultado direto
("recorde de faturamento", "dobrar"), e isso não é erro — é a função da página. No anúncio a
promessa direta queima porque ela está no scroll; na página ela já clicou e a promessa é o que faz
entrar no grupo. O que precisa bater entre os dois é o **mecanismo**, não o nível de promessa.

**Um vício a evitar:** eu estava voltando obsessivamente ao mecanismo da "campanha na base parada"
em toda peça e em toda headline. Ele é o mecanismo mais forte que temos, mas não pode ser a única
coisa que a marca sabe dizer.

---

## O achado do CRO que ainda não foi executado

O benchmark do funil é **16 leads marcados, 8 entraram** — mas não existe evento de clique no CTA,
então não se sabe se a perda é na página (ela não clica) ou na passagem para o WhatsApp (clica e
não entra). São problemas com soluções opostas. **Instrumentar o clique é meia hora e vem antes de
qualquer otimização.**

---

## Commits desta sessão

`2852684` nome do evento · `ce277fa` swipe + criativos v2 · `1408494` +6 criativos ·
`c11aa55` Ad Grid · `721ffaa` plano da live · `a3bb4f3` separa os 4 estágios ·
`a578ae8` corte do Chief · `cf4706d` plano da página · `8335971` data fechada ·
`21f01b9` headline · `df03bd7` estrutura do CRO

Tudo em `master`, **não pushado** (push é do @devops).
