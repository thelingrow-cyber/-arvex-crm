# Movimentação de Card + Escalação — desenho consolidado

> Arquiteto: Aria (@architect) · 2026-07-15
> Fecha as decisões pro @dev modificar o F2 (PUBLICADO, Carol ATIVA) com protocolo seguro.
> Princípio-guia: o caminho crítico (responder o lead) é sagrado — a escalação roda DEPOIS
> do envio e NUNCA pode atrasar ou derrubar a resposta.

## Contexto verificado
- F2 hoje: `... AI Agente → Formatar Resposta → Enviar Balão 1 → Enviar Balão 2 → Registrar Resposta no CRM → Responder 200`. O `Responder 200` já é respondido cedo (debounce), então o fim do fluxo é livre pra pós-processar.
- Colunas prontas: `leads.status` (enum tem `qualificado`, fase SDR do kanban), `leads.agente_pausado` (takeover), `agente_sdr.notificar_ativo` (bool), `agente_sdr.notificar_contato` (text, **NULL hoje** — número da Thalita).

## Decisões (ADRs)

### ADR-ESC-1 · Marcadores estruturados, extraídos e removidos antes de enviar
A Carol emite, **na última linha da resposta e sozinho**, um de:
- `[QUALIFICADO]`
- `[ESCALAR] motivo curto`

O `Formatar Resposta` (Code node já existente) passa a: (1) detectar via regex `/\n*\[(QUALIFICADO|ESCALAR)\]\s*([^\n]*)\s*$/i`; (2) guardar `sinal` (`qualificado`|`escalar`|`null`) e `motivo`; (3) **remover o marcador** do texto antes de `balao1/balao2`. O lead nunca vê o marcador. Se a IA não emitir marcador, `sinal=null` e nada muda (comportamento atual preservado).

### ADR-ESC-2 · [QUALIFICADO] → move o card + notifica
Pós-envio: `PATCH leads?id=eq.{lead_id}` com `status='qualificado'` **apenas se o status atual for `contato`** (guard `&status=eq.contato` no PATCH — não atropela um lead que um humano já moveu). Depois, notifica (ADR-ESC-4). A Carol move Contato→Qualificado; daí o humano/closer assume pra marcar a call.

### ADR-ESC-3 · [ESCALAR] → pausa a Carol + notifica com motivo
Pós-envio: `PATCH leads?id=eq.{lead_id}` com `agente_pausado=true`. A Carol para de responder aquele lead (o gate de takeover do F2 já respeita `agente_pausado`). Notifica com o `motivo` (ADR-ESC-4). O card **NÃO se move** (fica em contato, aguardando humano) — escalar ≠ qualificar.

### ADR-ESC-4 · Notificação: gated, no-op se sem número (Art. IV — No Invention)
Envia via Evolution (mesma instância) para `agente_sdr.notificar_contato` **somente se** `notificar_ativo = true` **E** `notificar_contato` não-nulo. Texto: `🔔 [Carol] {nome} ({tel}) — {qualificado: bora marcar a call | escalado: motivo}. Abrir no CRM.`. Se faltar número → **no-op silencioso** (só loga). **Nunca inventar número.** Quando o Vitor der o número da Thalita, é só preencher `notificar_contato` — zero mudança no workflow.

### ADR-ESC-5 · Onde entra no fluxo: pós-envio, à prova de falha
Depois de `Registrar Resposta no CRM`, um `Switch`/`IF` por `sinal`:
- `qualificado` → PATCH status (guarded) → Notificar
- `escalar` → PATCH agente_pausado → Notificar
- `null` → fim

Todos os PATCHs e o Notificar com `onError=continueRegularOutput` — se a escalação falhar, o lead **já recebeu a resposta** e o erro não propaga. Caminho crítico intocado.

### ADR-ESC-6 · Prompt da Carol (delegado ao dev/conteúdo)
As `instrucoes` ganham uma seção "SINALIZAÇÃO INTERNA": *quando você tiver coletado interesse claro + preferência de horário, termine com `[QUALIFICADO]` numa linha só. Quando travar (objeção que não resolve, pedido explícito de humano, algo fora do seu escopo), mande uma última mensagem tranquilizadora e termine com `[ESCALAR] motivo`. Esses marcadores são internos, o lead não os vê.* Aplicado no banco (`agente_sdr.instrucoes`), não é código.

## Handoffs

### → @dev (Dex) — protocolo seguro (F2 ao vivo)
1. Editar `Formatar Resposta` (via store Pinia): extrair+remover marcador, expor `sinal`/`motivo`. Manter `balao1/balao2/texto_resposta`.
2. Adicionar pós-`Registrar Resposta no CRM`: Switch por `sinal` → 2 PATCHs (guarded) + nó Notificar Thalita (gated, onError continue).
3. Buscar `notificar_ativo/notificar_contato` — reusar o `Buscar Config Agente` que já roda no F2 (os campos vêm no mesmo GET; confirmar que o select traz tudo — é `select=*` implícito? validar).
4. Ajustar `agente_sdr.instrucoes` com a seção de sinalização (ADR-ESC-6).
5. Testar com Execute/mensagem sintética ANTES de republicar. **Não publicar** até o Vitor validar.

### → @qa (Quinn)
Casos: marcador removido do texto enviado (lead não vê); [QUALIFICADO] move só se status=contato; [ESCALAR] pausa e não move; notificação no-op com contato NULL; sinal=null não altera nada (regressão do fluxo atual); falha no PATCH não derruba a resposta.

— Aria, arquitetando o futuro 🏗️
