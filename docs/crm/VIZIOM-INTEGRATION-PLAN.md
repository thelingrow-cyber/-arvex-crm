# Integração Viziom → CRM ARVEX — Agente IA/SDR

> Autor: @architect (Aria) · 2026-07-05 · análise com Fable 5 (janela)
> Executores previstos: @data-engineer (schema) + @dev (n8n/edge/UI) + @qa (gate) — com Opus/Sonnet
> Objetivo do Vitor: atendimento por agente IA/SDR no WhatsApp, **agendamento direto no CRM**, **follow-up automático** e **lead evoluindo sozinho na pipeline** — usando a infra Viziom que ele já possui.

---

## 1. Inventário (medido em 2026-07-05)

### Mundo A — CRM ARVEX (`arvex-crm`, Supabase + single-file)
- Pipeline: `novo → contato → qualificado` (fase SDR) `→ call → followup → quente` (closer) `→ fechado | perdido` (index.html l.1196-1204).
- `leads`: tel, expert, origem, status, closer, ticket, data_call, proximo_passo, **activities jsonb** (log de eventos já padronizado).
- `meetings`: alimenta a view "Reuniões"/Sales Coach.
- **`agente_sdr` (a costura já existe):** ativo ("N8N só responde se true"), expert, instrucoes (prompt), conhecimento (base de treino) — com UI própria (`view-agente-sdr`). O CRM já nasceu pra ser o painel de controle do agente.

### Mundo B — Viziom/HUBLABEL (VPS Hostinger do Vitor, n8n)
- Workflow V6.0.0: **510 nodes** — um SaaS inteiro (login, conexões, disparos individuais/grupos, dashboard).
- Peças prontas que vamos REUSAR: **agente LangChain** (1×) com **memória de chat em Postgres** e **RAG vetorial no Supabase** (embeddings OpenAI), **transcrição de áudio**, **análise de imagem**, Redis (cache/sessão), S3, scheduleTrigger.
- WhatsApp via **Evolution API em `wpp.viziom.io`** (sendText/sendMedia/sendWhatsAppAudio/instances/groups), com `server_url` parametrizado por conexão. Front SaaS em `app.viziom.io`.
- ⚠️ Evolution NÃO é controlado pelo Vitor (dependência do fornecedor). Meta API oficial já foi configurada em outra frente.

## 2. Decisões arquiteturais

- **AD-1 — Não fundir, não reescrever.** Os 510 nodes do HUBLABEL ficam INTOCADOS (é produto de revenda). Criar **workflow novo e enxuto `agente-sdr-arvex`** no MESMO n8n da VPS, reusando credenciais/instâncias Evolution existentes.
- **AD-2 — CRM Supabase é a fonte de verdade comercial.** O n8n fala com o Supabase do CRM via REST usando **service_role key** (vive só no n8n, server-side). **Pré-requisito obrigatório: Fase 1 do REFACTOR-PLAN (RLS)** — não expor o banco com policies `using(true)`.
- **AD-3 — O CRM comanda o agente.** A cada conversa, o n8n lê `agente_sdr` (ativo? instrucoes? conhecimento? por expert) — cache Redis 5 min. Vitor liga/desliga e re-treina o agente pela UI que JÁ existe, sem tocar no n8n.
- **AD-4 — Log em `leads.activities` (padrão existente) + tabela nova `sdr_followups`** (fila de cadência) + coluna `cadencia jsonb` em `agente_sdr`. DDL detalhado: @data-engineer.
- **AD-5 — Pipeline auto só na fase SDR e só PRA FRENTE.** `novo→contato→qualificado→call`. Fases de closer/ganho/perda são humanas. Nunca regredir status automaticamente; toda transição do agente logada em activities com autor `agente`.
- **AD-6 — Provider WhatsApp abstraído.** Um node "Enviar Mensagem" único parametrizado por `server_url` (padrão que o próprio HUBLABEL já usa). Se a Evolution do fornecedor cair/fechar: trocar pela Meta API oficial sem redesenhar o fluxo.

## 3. Os 4 fluxos

### F1 — Atendimento inbound
`WhatsApp → webhook Evolution → n8n:` identificar lead por `tel` no CRM (não existe → cria com origem `whatsapp-inbound`) → se `status='novo'` → **auto: `contato`** → carregar config `agente_sdr` + histórico (memória Postgres por telefone) → agente LangChain responde (áudio? transcreve antes) → gravar troca em `activities`.

### F2 — Agendamento
Tool do agente `agendar_reuniao(data, hora)`: valida janela → **insere em `meetings`** + atualiza `leads.data_call` + **auto: `qualificado→call`** → confirma pro lead no WhatsApp. (Google Calendar = fase posterior; o CRM já exibe em "Reuniões".)

### F3 — Follow-up automático
`scheduleTrigger` (15 min) → busca `sdr_followups` vencidos → cadência default (configurável em `agente_sdr.cadencia`): sem resposta **+4h → toque 1**, **+24h → toque 2**, **+48h → toque 3**, **+72h → marca `obs='sem resposta'` e encerra fila** (lead fica pra ação humana). Cada resposta do lead zera/reprograma a fila. Espelha o padrão de checks D+X que o módulo CS já validou.

### F4 — Evolução automática na pipeline
Regras de transição (autor `agente`): lead respondeu → `contato` · qualificação completa (agente coletou respostas-chave: nicho/faturamento/interesse, definidas em `instrucoes`) → `qualificado` · reunião marcada → `call`. Kanban do CRM reflete sem mudança de UI (single-file relê do banco).

## 4. Fases de implementação (em série)

| Fase | O quê | Executor | Verificação |
|------|-------|----------|-------------|
| **F0** | RLS do CRM (Fase 1 do REFACTOR-PLAN) — bloqueia tudo se não feito | @dev | SDR não deleta CS via API |
| **F1** | Ponte: workflow `agente-sdr-arvex` no n8n + credencial Supabase CRM + lead match/create + log em activities (SEM IA — eco) | @dev | Mandar zap → lead aparece/loga no CRM |
| **F2** | Cérebro: agente LangChain lendo `agente_sdr` (ativo/instrucoes/conhecimento), memória por telefone, resposta real | @dev | Conversa real ponta-a-ponta; `ativo=false` silencia |
| **F3** | Agendamento (tool→meetings) + transições F4 | @dev | Marcar reunião por zap → card move p/ Call + aparece em Reuniões |
| **F4** | Follow-up: `sdr_followups` + cadência + scheduleTrigger | @data-engineer (DDL) + @dev | Lead mudo recebe toques 4h/24h/48h e encerra em 72h |
| **F5** | ~~SaaS-ready: multi-tenant por `expert`/instância — vira produto do nicho óptico~~ — **DESCARTADO (2026-07-07):** framing errado, esta integração não tem relação com nicho óptico; multi-tenant/produto revendável é ambição distante, não escopo atual. Não reabrir sem pedido explícito do Vitor. | — | — |

Cada fase = 1-2 sessões @dev com Sonnet/Opus. **Não abrir fase seguinte sem a anterior verificada.**

## 5. Riscos

1. **Evolution de terceiro** (`wpp.viziom.io`): mitigado por AD-6 (provider abstraído) + Meta oficial como plano B. Monitorar: healthcheck no scheduleTrigger.
2. **VPS/n8n down = agente mudo:** heartbeat a cada execução do trigger grava `last_seen` no CRM; UI mostra badge "agente offline" se >30 min (F4).
3. **Custo OpenAI do agente:** manter modelo atual do HUBLABEL no início (funciona); otimizar depois com dados reais de volume.
4. **Mega-workflow frágil:** jamais editar o V6.0.0 original — só o workflow novo. Export/backup antes de qualquer mudança no n8n.

## 6. O que NÃO fazer

- ❌ Reescrever HUBLABEL ou migrar o SaaS de banco — revenda fica como está.
- ❌ Realtime/websockets no CRM — o padrão atual (reler do banco) atende.
- ❌ Google Calendar, áudio de resposta, multi-idioma na V1 — fila de melhorias.
- ❌ Reativar o fluxo Carol do Railway — este plano o substitui (HUBLABEL é a base superior, como já decidido).

## 7. Pré-requisitos operacionais (Vitor, ~15 min, guiado 1 passo por vez)

1. Acesso ao n8n da VPS ativo (login).
2. Service key do Supabase do CRM em mãos (Settings → API).
3. Uma instância Evolution dedicada pro número do agente (não misturar com disparos do SaaS).
