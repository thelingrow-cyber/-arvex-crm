# Diagnóstico de Funil — arvex-crm

> Blake (squad `comercial`) · 2026-07-31 · leitura direta do banco de produção, sessão read-only
> Base: 253 leads · nenhum telefone ou nome completo reproduzido aqui
> Confrontado com `docs/processos/sop-fluxo-vendas.md` e `docs/processos/playbook-rotina-sdr.md`

## GARGALO #1 — a janela de fechamento é de 1 dia, e não existe cadência para quem não fecha nela

Este é o número que reorganiza todo o resto:

| Tempo do cadastro até o fechamento | Valor |
|---|---|
| Média | **1 dia** |
| Mais rápido | 0 dias |
| Mais lento | 13 dias |
| Amostra | 27 fechamentos registrados |

**Quem fecha, fecha no impulso do primeiro contato.** Nenhuma venda da base levou mais de 13 dias.
Isso significa que todo lead parado há mais de duas semanas já está, pelo padrão histórico da própria
operação, fora da janela — e é exatamente aí que 61% da base foi parar.

## O funil como ele está

| Status | Leads | % |
|---|---|---|
| perdido | 154 | 60,9% |
| contato | 55 | 21,7% |
| fechado | 25 | 9,9% |
| call | 5 | 2,0% |
| followup | 5 | 2,0% |
| qualificado | 4 | 1,6% |
| quente | 3 | 1,2% |
| novo | 2 | 0,8% |

**74 leads vivos.** Receita registrada nos fechados: **R$ 59.648** (18 dos 25 fechados têm valor lançado).

## Onde está o dinheiro parado — e por que não dá para responder direito

**O campo `ticket` está preenchido em 19 de 253 leads (8%).** Não existe base para priorizar por valor
com dado real. Todo valor abaixo é **estimativa marcada**, calculada sobre o ticket médio dos fechados
(R$ 3.314) — e mesmo esse está contaminado: há um fechado com `ticket = 1`.

Os produtos do SOP são R$ 5.000 / R$ 7.000 / R$ 10.000. O ticket médio realizado de R$ 3.314 fica
**abaixo do produto mais barato**, o que indica ou parcelamento lançado como valor cheio, ou registro
incompleto. Não dá para afirmar qual sem olhar o financeiro.

## Os quentes esquecidos

Cinco leads passaram pela qualificação, estão vivos, e **pararam há quase três semanas**:

| # | Lead | Status | Parado há | Expert | Origem |
|---|---|---|---|---|---|
| 1 | Cin*** | qualificado | 19 dias | Cindy Batista | Respondi |
| 2 | Thi*** | qualificado | 19 dias | Cindy Batista | Respondi |
| 3 | Lar*** | qualificado | 18 dias | Cindy Batista | Respondi |
| 4 | Raf*** | qualificado | 18 dias | Cindy Batista | Respondi |
| 5 | Kel*** | quente | 17 dias | Cindy Batista | Respondi |

Os outros 12 leads em etapa avançada foram movimentados hoje — a operação está viva no que é recente.
Estes cinco ficaram para trás. Todos da mesma expert e da mesma origem.

## O bolsão de "contato" (55 leads)

| Parado há | Leads |
|---|---|
| até 7 dias | 34 |
| 15 a 21 dias | 9 |
| mais de 21 dias | 12 |

**21 leads passaram da janela de 13 dias.** Eles não são pipeline — são estatística inflando o número.

## O que o SOP manda e não está sendo feito

O SOP v1.0 (31/03) já listava como **gap nº 1, prioridade alta**:

> *"Follow-up sem cadência definida — leads quentes esfriando sem contato"*
> Ação necessária: definir cadência (ex: D+1, D+3, D+7)

Quatro meses depois, a cadência continua indefinida, e os dados mostram o preço: 5 qualificados parados
há 18 dias e 21 leads mortos no bolsão de contato.

**Correção que os dados impõem ao SOP:** a cadência proposta (D+1, D+3, D+7) está certa em espírito e
**curta demais em cobertura** — ela cobre a primeira semana, mas a janela real vai até D+13. Falta o
fecho: um D+13 que decide entre reengajar e marcar perdido.

Os outros dois gaps altos do SOP (SDR sem script, aquecimento manual do grupo) não são mensuráveis
por este diagnóstico.

## Ressalva sobre responsáveis

**Não atribuí nada a pessoas, de propósito.** Os campos `resp`, `closer` e `atendente` são texto livre
inconsistente (`Vitor`, `Gabriel`, `Closer`, `Victor P`) e 205 dos leads não têm nenhum preenchido.
Qualquer leitura por closer aqui seria ficção. A coluna `owner_id`, criada em 29/07, tem 22 leads
preenchidos — quando cobrir a base, o diagnóstico por pessoa passa a ser possível.

## As 3 ações da semana

**1. Decidir os 5 quentes esquecidos — hoje.**
São os únicos leads que já passaram pelo filtro de qualificação e ainda estão vivos. Contato com
decisão binária: reengaja ou marca perdido. Manter alguém em "qualificado" há 19 dias é mentira de
pipeline. *Valor estimado em risco: ~R$ 16.500 (estimativa marcada — 5 × ticket médio realizado).*

**2. Limpar os 21 leads de "contato" parados há mais de 15 dias — esta semana.**
Não é follow-up, é higiene. Uma última tentativa em lote e o que não responder vira perdido. Sem isso,
todo diagnóstico futuro mede um funil que não existe.

**3. Tornar o `ticket` obrigatório na entrada do lead.**
Com 8% de cobertura, ninguém consegue responder "onde está o dinheiro" — nem eu, nem você. Não é
burocracia: é a condição para qualquer priorização por valor daqui para frente.

## Próxima ação e responsável

- Ações 1 e 2 → **@sdr-playbook-manager (Cady)**: transformar D+1/D+3/D+7/**D+13** em cadência escrita,
  já que o gap é de processo e não de esforço.
- Ação 3 → decisão do Vitor (mudança de campo obrigatório no CRM).

— Blake, squad comercial 🎯
