# Sales Coach V2 — Diagnóstico profundo + arquitetura de melhoria (Fable, 2026-07-19)

> Base: código de produção lido (branch `main:index.html` + `supabase/functions/analyze-meeting`
> + `coach-chat`) + banco de produção consultado + `sales-coach-fase3-ARCHITECTURE.md` (Aria,
> 06/07 — continua válido; este doc NÃO o substitui, ele o reordena com dado real e adiciona o
> que faltava). **Executor: @dev (Sonnet/Opus), fases em série. Todas as decisões estão tomadas.**
>
> ⚠️ **ONDE MEXER:** o front do Sales Coach vive em `index.html` da RAIZ, branch **`main`**
> (produção Vercel). `docs/crm/index.html` (master) NÃO tem o módulo — editar lá não muda nada
> do coach. Regra da casa: publicar = cópia manual, nunca merge master↔main sem reconciliar.

---

## 1. Diagnóstico com o banco real na mão (consultado 2026-07-19)

```
meetings: 7 total · 7 done · 0 "ganhou" · 1 closer distinto · período 28/06–07/07
das 7: 4 são lixo de teste (4, 51, 219, 393 chars) · 2 são a MESMA call duplicada (55KB, Gabriel)
       · 1 call média (21KB, nota 3) · chat usado em exatamente 1 reunião
stats_closer(): NÃO existe no banco · closer_profiles: NÃO existe
```

**Conclusão central: o gargalo do Sales Coach não é análise — é INGESTÃO.** Em 3 semanas
entraram ~2 calls reais. Nenhuma virou "ganhou" (embora o CRM tenha vendas registradas em
junho — o elo meeting→venda não existe). Com esse fluxo de dados, construir `closer_profiles`,
relatório mensal ou qualquer camada longitudinal seria analytics de dataset vazio — o erro
clássico. A prioridade inverte: **primeiro fazer TODA call cair aqui sozinha, depois
enriquecer o que se vê de cada call, e SÓ ENTÃO agregar.**

### Defeitos objetivos encontrados no código (independem de estratégia)

| # | Defeito | Onde | Efeito |
|---|---------|------|--------|
| D1 | `coach-chat` corta o transcript em **14.000 chars** | `coach-chat/index.ts:28` | Numa call real de 55KB, o chat "grounded" enxerga só os primeiros ~25% da call. O diretor responde sem ter visto o fechamento — exatamente a parte mais perguntada ("onde perdi a venda?") |
| D2 | `coach-chat` e `analyze-meeting` **sem autenticação real** | ambas as functions | `verify_jwt=false` + service_role + "UUID não-adivinhável" como única barreira. Qualquer pessoa com a anon key (pública por definição) e um meeting_id gasta crédito Anthropic e lê transcript alheio. Mesmo padrão do CRITICAL-1 já corrigido no `ingest-meeting` — a lição não foi propagada |
| D3 | Nenhuma validação de transcript no insert manual | `saveMeeting()` (main) | 4 das 7 linhas do banco são teste/lixo analisado pela IA (custo real, dataset poluído); transcript de 4 chars foi pro Claude |
| D4 | Sem dedupe no insert manual | `saveMeeting()` | A mesma call de 55KB existe 2× (2 análises pagas, dataset duplicado). O `client_key` só existe no caminho do plugin |
| D5 | Sem delete de reunião na UI | modal detalhe | O lixo de teste é impossível de limpar sem SQL na mão |
| D6 | `resultado` é manual e morre "aberto" | fluxo inteiro | 0 "ganhou" no banco apesar de vendas reais no CRM. Sem resultado confiável, QUALQUER métrica de conversão/ganho-vs-perda que se construa em cima será mentira |
| D7 | `loadCoach()` faz `select('*')` | main | Puxa transcripts de 55KB pra renderizar cards. Inócuo com 7 linhas, ruim com 200 |

## 2. Benchmark — o que Gong/Fireflies/tl;dv/Attention ensinam (e o que ignorar)

- **Gong** (referência da categoria): o produto NÃO é a análise — é o pipeline automático de
  captura (bot entra em toda call; ninguém cola transcrição). Em cima disso: métricas
  DETERMINÍSTICAS por call (talk ratio, monólogo mais longo, nº de perguntas, interatividade,
  quem falou por último) + alertas de deal (sem próximo passo marcado, single-threaded) +
  dashboards de gestor separados da visão do rep. Lição: **métrica determinística é comparável
  entre calls; nota de LLM é ruidosa** — Gong usa LLM pra narrativa, números vêm de código.
- **Fireflies / tl;dv**: venceram no low-end por UMA razão — captura sem fricção zero-setup.
  Confirma a prioridade da ingestão.
- **Attention**: scorecards customizáveis por metodologia + follow-up automático pós-call
  (e-mail pro rep). Lição: o coaching vira hábito quando CHEGA no fluxo do closer, não quando
  mora numa aba que ele precisa lembrar de abrir.
- **Sybill**: leitura de intenção/emoção do comprador. Ignorar — profundidade que não paga no
  estágio atual.
- **O que NÃO copiar:** deal boards paralelos (o kanban do CRM já é a fonte de verdade),
  biblioteca de snippets de vídeo (não há vídeo), scorecard configurável por UI (a rubrica
  fixa de 8 dimensões + persona diretor já é MELHOR calibrada pro contexto Cindy/óticas do que
  um builder genérico).

**Vantagem estrutural da ARVEX que nenhum benchmark tem:** o coach mora DENTRO do CRM que já
tem leads, vendas e WhatsApp (evolution-proxy). Gong gasta milhões integrando com Salesforce;
aqui o join é uma foreign key. A V2 deve explorar isso, não imitar a superfície dos gringos.

## 3. Arquitetura V2 — decisões (ADR-18 a 23)

### ADR-18 — Segurança e higiene primeiro (corrige D1-D5)
1. `coach-chat` e `analyze-meeting` passam a validar JWT: extrair user do header
   `Authorization`, checar `meeting.closer_id === user.id` OU role admin (mesma checagem de
   role que o front já usa, via query em `profiles`/`user_roles` — seguir o padrão existente
   do CRM). O caminho plugin→`ingest-meeting` continua com `x-arvex-key` (já resolvido).
2. `coach-chat`: limite de transcript sobe de 14.000 → **180.000 chars** (55KB da call real ≈
   15k tokens; cabe com folga no contexto do Claude; o corte vira proteção de borda, não
   mutilação sistemática).
3. `saveMeeting()`: transcript < **500 chars** → bloquear com mensagem ("transcrição curta
   demais pra análise"). Dedupe: hash simples (tamanho + primeiros/últimos 200 chars) contra
   as meetings existentes do mesmo closer → aviso "essa call parece já enviada" com opção de
   prosseguir.
4. Botão **Excluir reunião** no modal (owner ou admin), com confirmação. Depois de deployado:
   limpar as 4 linhas de teste do banco (1 SQL, executor faz).

### ADR-19 — Resultado automático via elo meeting→venda (corrige D6; pré-requisito de TUDO que é indicador)
`meetings.lead_id` já existe. Decisão: trigger no INSERT de venda (tabela de vendas do CRM)
— se existe meeting com o mesmo `lead_id` e `resultado='aberto'`, seta `resultado='ganhou'` e
copia o ticket. No front, quando o card do lead move pra "perdido", oferecer atualizar a
meeting vinculada. O select de lead no modal "Nova reunião" vira campo com busca (hoje é
`<select>` com todos os leads — inutilizável com centenas). **Regra: `resultado` deixa de ser
um campo que o closer preenche por disciplina e vira consequência do CRM — é isso que os
benchmarks chamam de deal intelligence, e aqui custa uma trigger.**

### ADR-20 — Métricas determinísticas por call (código, não LLM, custo zero por análise)
Novo campo `meetings.metrics jsonb`, calculado DENTRO do `analyze-meeting` (TypeScript puro,
antes da chamada ao Claude — roda mesmo se a IA falhar):
- `talk_ratio_closer` (% de chars/tempo do closer), `longest_monologue_s` (com timestamps do
  plugin `[hh:mm:ss]`; sem timestamps, proxy por blocos de chars), `question_count_closer`
  (linhas do closer terminadas em `?`), `first_question_at_s`, `who_spoke_last`,
  `duration_s` (último timestamp), `word_count`.
- Identificação do closer no transcript: match do prefixo de speaker contra `closer_nome` +
  heurística "Você/Closer:" — documentar o mapeamento no código.
- Exibição no modal: régua de talk-ratio (alvo 40-45% closer — âncora Gong), monólogo mais
  longo, nº de perguntas. **São os indicadores comparáveis entre calls que as notas de IA não
  dão.** Backfill: reanalisar as 2 calls reais existentes recalcula metrics de graça.

### ADR-21 — Fase 3a executa agora (já especificada, ficou no papel)
`stats_closer()` do doc da Aria entra como está (SQL, security definer com checagem, ou
invoker + grant). No modal da call: linha "vs suas últimas 20: rapport +0.8 · fechamento -1.2"
(subtração no front, como especificado). É a única peça longitudinal que JÁ funciona com
pouco dado e melhora sozinha conforme o dataset cresce.

### ADR-22 — Aba "Direção" (os indicadores que só o Vitor vê)
Nova entrada na sidebar visível apenas para `currentRole === 'admin'` (Vitor e Gabriel; se
quiser literalmente só Vitor um dia, trocar o gate por email — decisão adiada de propósito,
role basta agora). Conteúdo do V1 da aba (lista fechada):
1. **Tabela por closer** (todos — admin não é filtrado pela RLS): calls no período, nota média,
   tendência (Δ últimas 5 vs 20 via `stats_closer`), talk-ratio médio, conversão REAL
   (ganhou/total — só faz sentido pós ADR-19).
2. **Radar de dimensões do time**: média das 8 dimensões, pior dimensão destacada ("o time
   inteiro está fraco em transição").
3. **Objeções recorrentes**: agregação de `insights.objecao.tipo` + contagem de temas em
   `erros`/`faltou` (SQL `GROUP BY`, sem IA).
4. **Fila de risco**: meetings `resultado='aberto'` com nota < 5 ou `objecao.tipo='falsa'` —
   as calls que merecem revisão do gestor.
Dados: 1 RPC `stats_direcao(periodo)` retornando o JSON da aba inteira (1 round-trip). Sem IA
nesta aba no V1 — tudo determinístico, sempre correto, custo zero.

### ADR-23 — Fechar o loop de hábito: resumo pós-call no WhatsApp
Quando `analyze-meeting` termina com sucesso: enviar via `evolution-proxy` (já deployado, já
seguro) mensagem ao closer com `resumo_diretor` + `missao` + link do CRM. Config por closer
(campo `notificar_whatsapp` em profiles, default off até validar com a Thalita/Gabriel).
É a versão ARVEX do follow-up automático da Attention — o coaching chega onde o closer vive,
em vez de esperar ele abrir a aba. **Custo: 1 chamada HTTP; nenhuma IA nova.**

### O que fica explicitamente ADIADO (gate de dados, não de vontade)
- `closer_profiles` (3c) e relatório mensal (3d): **gate = ≥15 calls reais analisadas de um
  mesmo closer.** Hoje há 2. Construir antes é análise de dataset vazio.
- Troca de modelo (`claude-sonnet-4-6` → Sonnet 5): permitido no P0 SE o executor reanalisar o
  gold-standard (caso-01) e o output mantiver o nível — senão mantém. Não é prioridade.
- Replay timeline visual, pgvector/RAG, scorecards configuráveis, análise de vídeo/emoção.

## 4. Plano de execução (fases em série, commits `feat(coach): P{n} — {resumo}`)

### P0 — Higiene + segurança (ADR-18) — ½ sessão
- [ ] JWT + ownership/admin nas 2 functions; testar: token de closer A não abre meeting do B (403); admin abre.
- [ ] Chat numa call de 55KB responde sobre o FINAL da call (prova do fix dos 14k).
- [ ] Insert < 500 chars bloqueado; duplicata avisada; botão excluir funciona; banco limpo das 4 linhas de teste.

### P1 — Elo meeting→venda (ADR-19) — ½ sessão
- [ ] Trigger criada; registrar venda de lead com meeting aberta → meeting vira "ganhou" com ticket.
- [ ] Select de lead com busca no modal.

### P2 — Métricas determinísticas (ADR-20) — 1 sessão
- [ ] `metrics` calculado nas novas análises E via "Reanalisar" nas 2 calls reais.
- [ ] Modal exibe talk-ratio/monólogo/perguntas; call SEM timestamp degrada pra proxies sem quebrar.

### P3 — stats_closer + tendência no modal (ADR-21) — ½ sessão
- [ ] RPC no banco; modal mostra Δ vs últimas 20 quando há ≥3 calls do closer.

### P4 — Aba Direção (ADR-22) — 1-1½ sessão
- [ ] Sidebar item só aparece pra admin; closer logado não vê (testar com role comercial).
- [ ] 4 blocos renderizando de `stats_direcao()`; conversão bate com as vendas reais do CRM.

### P5 — Notificação WhatsApp pós-call (ADR-23) — ½ sessão
- [ ] Análise done → mensagem chega no WhatsApp do closer (testar com o próprio Vitor primeiro, flag off pros outros).

**Dependência externa que multiplica tudo isso:** o Meet Transcriber (plano §7 do
`DEEP-ANALYSIS-FABLE.md` dele) é quem enche este dataset sem depender de disciplina humana.
As duas frentes se encontram no `ingest-meeting`. A call ADR-10 + push de lá continuam sendo
o desbloqueio de maior alavancagem do sistema inteiro.

## 5. Estrutura de abas — resposta direta à pergunta "outra aba?"

- **Reuniões** (existe): continua sendo a casa do CLOSER — cards, análise, chat, missão. Ganha
  métricas determinísticas e tendência pessoal. Não muda de lugar.
- **Direção** (nova, ADR-22): a casa do GESTOR — agregados, comparação entre closers, risco,
  conversão real. Invisível pra quem não é admin.
- NÃO criar terceira superfície (relatórios/BI separado) — com duas personas, duas abas esgotam
  a taxonomia. Relatório mensal (quando o gate de dados abrir) nasce DENTRO de Direção.
