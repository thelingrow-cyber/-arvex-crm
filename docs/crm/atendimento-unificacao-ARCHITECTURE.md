# Atendimento × Carol — Unificação da fonte de conversa (ADR)

**Data:** 2026-07-24 · **Autor:** Aria (@architect) · **Status:** Fase 1 aprovada, aguardando RLS (Dara) + impl (Dex)

## Problema (verificado no banco de produção)

O módulo Atendimento tem **duas fontes de verdade desconectadas**:

| Store | Conteúdo real | Quem escreve | Quem lê hoje |
|-------|---------------|--------------|--------------|
| `agente_sdr_historico` | **100 msgs / 9 conversas** vivas (Carol) | n8n (Carol) via `service_role` | ninguém no CRM |
| `leads.activities` | 42 eventos antigos, **todos sem autor** (notas de maio) | RPC `registrar_evento_lead` (não é chamada pelo n8n) | CRM (`conversasAtendimento`) |

**Smoking guns:**
- `leads.activities`: **0** eventos com `autor` (`lead`/`agente`/`humano`) em toda a base.
- `agente_sdr_historico`: **RLS habilitado + 0 policies = deny-all** → a chave anon do navegador não consegue ler.
- Nenhum trigger liga as duas. A RPC-ponte existe mas o n8n não a chama.

Efeito: o chat do CRM é cego pra conversa viva; a mensagem que o operador envia (edge `send` → `registrar_evento_lead`) cai num rail que ninguém exibe.

## Formato de `agente_sdr_historico`

- Colunas: `id int`, `session_id varchar` (= telefone, dígitos), `message jsonb`.
- `message = {type:'ai'|'human', content, additional_kwargs, response_metadata, ...}` (LangChain).
- `content` usa `||` como separador de múltiplos balões.
- `type:'ai'` = Carol · `type:'human'` = cliente.

## Decisão — Fase 1 (unificar na fonte viva)

Fonte de verdade da conversa = `agente_sdr_historico`. `leads.activities` volta a ser só notas internas do lead.

1. **RLS (Dara):** `SELECT` em `agente_sdr_historico` restrito a staff autenticado (PII). `service_role` (Carol) inalterado; INSERT do operador também é `service_role` (edge) → não precisa de policy de write pro browser.
2. **CRM lê historico (Dex):** loader agrupa por `session_id`, join `leads` por `tel` pro nome/id; render: `ai`→Carol (ou "Você"/nome se `additional_kwargs.operator`), `human`→cliente; split `content` por `||`.
3. **Envio operador (Dex, edge `send`):** insere turno em `agente_sdr_historico` como `{type:'ai', content, additional_kwargs:{operator:<email-do-login>}}` para `session_id = tel`. Assim aparece como "Você" e a Carol (ao retomar) não repete nem lê como fala do cliente. Mantém `agente_pausado`.

### Riscos / notas
- **Normalização de telefone:** `session_id` vs `lead.tel` — casar por dígitos (`regexp_replace`). Alguns tel têm 9º dígito/DDI variável; padronizar no join.
- **Realtime:** assinar `agente_sdr_historico` (em vez de `leads`) pra atualizar o inbox ao vivo.
- **Carol repetir:** ao retomar após takeover, validar que a memória inclui o turno do operador (esperado em memória Postgres LangChain).

## Fase 2 (norte, depois)

Store canônico `mensagens` (lead_id, direção, sender_type cliente/agente/operador, texto, ts, `wa_message_id` p/ dedup) alimentado pelo **webhook do Evolution** como ponto único de ingestão; Carol e CRM leem dele. Event-sourced, RLS, independente do formato LangChain.

## Cadeia de execução
`@architect (design) → @data-engineer (RLS) → @dev (CRM read + edge send) → @qa → @devops (push/deploy)`
