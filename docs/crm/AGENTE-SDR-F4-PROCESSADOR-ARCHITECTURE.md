# F4 — Processador de Follow-up (desenho consolidado para build)

> Arquiteto: Aria (@architect) · 2026-07-15
> Fecha as decisões abertas do esboço (`AGENTE-SDR-F2-ARCHITECTURE.md` §4) para o @dev
> implementar sem re-decidir. Delega DDL a @data-engineer, implementação n8n a @dev.
> Princípio-guia: reusar a infra do F2 (boring technology), não inventar pipeline novo.

## Contexto (o que já existe, verificado)

- `sdr_followups` (fila): `lead_id, tel, tentativa, agendado_para, status(pendente|concluido|cancelado)`. Unique parcial 1-por-lead-pendente. Poll index em `(status, agendado_para)`.
- `agente_sdr.cadencia` = `{"toques_horas":[4,24,48,168],"encerra_horas":192}` (4 toques: 4h, 24h, 48h, 7 dias; arquiva em 8 dias).
- A fila é POPULADA (pelo outbound e — decisão nova — deve passar a ser populada também pela abordagem do form / F2 quando o lead não responde). **Ninguém a CONSOME hoje.**
- `leads.agente_pausado` (takeover) já existe. O F2 já cancela a fila quando o lead responde (nó "Cancelar Followup Pendente").

## Decisões de arquitetura (ADRs)

### ADR-F4-1 · Texto do toque: **a IA gera** (não template fixo)
O processador reusa o **mesmo cérebro do F2** (Claude + `memoryPostgresChat`, `sessionKey = tel`, tabela `agente_sdr_historico`) com um **system prompt de FOLLOW-UP** próprio: *"A conversa parou há um tempo. Gere UM follow-up curto e natural pra reengajar, retomando o último assunto que vocês tocaram. Não pareça cobrança nem repita o que já disse. Sem travessão."*
- **Por quê:** a Carol tem a memória da conversa inteira daquele lead. Um toque que cita o contexto real ("ficou alguma dúvida sobre o horário que você comentou?") converte mais e não soa robô. Zero trabalho de template pro Vitor. Custo de API é irrelevante (poucos toques/dia).
- **Consequência:** o F4 tem seu próprio nó `AI Agente` + `Anthropic` + `Postgres Chat Memory` (mesma tabela/sessão do F2). O prompt de follow-up sai de `agente_sdr` — nova coluna `prompt_followup` (nullable; se vazio, usa um default embutido no workflow).

### ADR-F4-2 · Gates antes de cada toque (ordem importa)
Para cada linha `pendente` com `agendado_para <= now()`, ler o lead e checar, NESTA ordem:
1. `lead.agente_pausado = true` → **cancela a fila** (humano assumiu, não atropelar). status=`cancelado`.
2. `lead.status <> 'contato'` → **cancela** (lead avançou pra qualificado/call/fechado/perdido, ou voltou pra novo). status=`cancelado`.
3. Última activity do lead é `autor='lead'` posterior ao último `autor='agente'` → **cancela** (respondeu; o F2 já assume). status=`cancelado`.
   *(defensivo — o F2 já cancela ao responder, mas o poll pode pegar a janela entre a resposta e o cancelamento).*
Só se passar nos 3 gates é que dispara o toque.

### ADR-F4-3 · Avanço e encerramento (ler o array, nunca índice fixo)
```
toques = agente_sdr.cadencia.toques_horas          // [4,24,48,168]
proximo = tentativa + 1
se proximo < toques.length:
    gerar+enviar toque (ADR-F4-1) · registrar no CRM · agente
    UPDATE fila: tentativa=proximo, agendado_para = now() + toques[proximo]h, updated_at=now()
senão:
    // esgotou os 4 toques
    UPDATE lead: obs = 'sem resposta (cadência esgotada)'
    UPDATE fila: status='concluido'
    // NÃO move o card (D-1: lead frio ≠ perdido; fica em 'contato' pra re-ataque manual)
```

### ADR-F4-4 · Movimentação de card: **o F4 NÃO move**
O lead permanece em `contato` durante toda a cadência. Novo→Contato é do form/outbound; Contato→Qualificado é do F2 (quando a Carol qualifica). O F4 só toca o WhatsApp e, no fim, escreve `obs`. Isso mantém responsabilidade única por transição e evita corrida de escrita no `status`.

### ADR-F4-5 · Layout: **workflow n8n separado**, cron 15 min
Não é branch do outbound nem do F2 — é um 3º workflow (`Agente SDR ARVEX - F4 Processador`). Motivo: ciclo de vida e cadência de execução próprios (poll de 15min), isolamento de falha (se o F4 quebra, F1/F2 seguem), e legibilidade. Usa `SplitInBatches(1)` + jitter anti-ban entre leads, igual ao outbound.

### ADR-F4-6 · Envio: reusa o splitter de balões
Mesmo padrão do F2 (balão 1 + delay do Evolution). O follow-up costuma ser 1-2 balões curtos, então o splitter simples já serve.

## Handoffs

### → @data-engineer (Dara)
1. Adicionar coluna `agente_sdr.prompt_followup text` (nullable) — o prompt de sistema do follow-up, editável pela UI depois. Aditivo/idempotente.
2. Criar **view `v_followups_devidos`**: `select f.*, l.status as lead_status, l.agente_pausado, l.nome, l.activities from sdr_followups f join leads l on l.id=f.lead_id where f.status='pendente' and f.agendado_para <= now()`. `security_invoker` (herda RLS de leads). Simplifica o poll do n8n para 1 GET.
3. Confirmar que o poll index cobre `(status, agendado_para)` — já existe (`sdr_followups_poll_idx`). Nada a fazer, só validar.

### → @dev (Dex) — depois do Dara
Construir `docs/crm/n8n-agente-sdr-f4-processador-v1.json`:
- Cron 15min → GET `v_followups_devidos` → SplitInBatches(1) →
- Code "Gates" (ADR-F4-2): decide cancelar vs seguir; se cancelar, PATCH fila `status=cancelado` e pula.
- AI Agente follow-up (ADR-F4-1: Claude + Postgres Memory sessionKey=tel + system prompt de follow-up de `prompt_followup`).
- Enviar Evolution (splitter) → registrar_evento_lead(autor='agente') →
- Code "Avança ou Encerra" (ADR-F4-3): PATCH fila (avança) ou PATCH fila+lead (encerra).
- Wait jitter → volta ao loop.
- **DRAFT até o número definitivo** (dispara pra leads reais). Gate de `agente_sdr.ativo` no começo (se inativo, não processa).

### → @qa (Quinn) — depois do Dev
Testar com linhas sintéticas na fila (`agendado_para` no passado): (a) toque normal avança tentativa+agenda próximo; (b) lead com `agente_pausado` → cancela; (c) lead que avançou de status → cancela; (d) 4º toque → encerra + obs; (e) `ativo=false` → não processa. Limpar sintéticos após.

### → @devops (Gage)
Push dos commits (SQL do Dara + JSON do Dev + este doc). Exclusivo dele.
