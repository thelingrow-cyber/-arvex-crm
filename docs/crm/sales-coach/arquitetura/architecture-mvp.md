# Arquitetura — Sales Coach (MVP) · arvex-crm

**Autor:** @architect (Aria) · Data: 2026-06-27 · Brief: `sales-coach-mvp-brief.md`
**Princípio:** reusar 100% dos padrões do CRM existente (Supabase + RLS + roles + views `goTo` + Realtime). Operação interna, pragmático, **mínimo de peças** (sem serviços externos).

> **Decisão de arquitetura (2026-06-27):** backend = **Supabase Edge Function** (NÃO n8n). Tudo numa plataforma só (DB + Auth + RLS + Function + Secrets + Realtime + pg_cron). n8n cortado — não é necessário em nenhuma fase até a 4. Verificado capacidade por capacidade.

---

## 0. Padrões existentes a reusar (não reinventar)
- Front estático `docs/crm/index.html`, Supabase via CDN UMD: `sb = createClient(SUPA_URL, SUPA_KEY)` (publishable key, RLS protege).
- Roles em `profiles.role`: `admin | cs | sdr | closer`. Gate por `applyRole()` + `nav-xxx`/`view-xxx` + `goTo()`.
- SQL idempotente rodado no Supabase SQL Editor (padrão `setup-*.sql`). Realtime já em uso (`subscribeRealtime`).
- `leads` já tem `closer`, `ticket`, `status`, `motivo_perda` → a reunião **referencia** o lead.

---

## 1. Modelo de dados (DDL detalhado fica com @data-engineer)

### Tabela `meetings`
| campo | tipo | nota |
|------|------|------|
| id | uuid PK default gen_random_uuid() | |
| lead_id | uuid FK→leads(id) null | reaproveita lead existente |
| closer_id | uuid FK→auth.users(id) | dono da reunião |
| closer_nome | text | denormalizado p/ exibir |
| cliente_nome | text | |
| produto | text | o que foi apresentado |
| data_reuniao | date | |
| transcript | text | **dado sensível de cliente** |
| resultado | text check in ('ganhou','perdeu','aberto') **not null** | **o ativo** (FR2) |
| ticket | numeric null | se ganhou |
| status | text default 'pending' check in ('pending','processing','done','error') | estado da análise |
| nota_geral | numeric null | média ponderada das dimensões |
| scores | jsonb null | `{rapport:8.5, diagnostico:7,...}` (8 dimensões) |
| insights | jsonb null | `{acertos:[],erros:[],faltou:[],sugestoes:[]}` |
| erro_msg | text null | se status='error' |
| created_at | timestamptz default now() | |
| analyzed_at | timestamptz null | |

> scores/insights como **jsonb** (não normalizado) — MVP enxuto, 8 dimensões fixas. Evolução do closer calculada no front. Normalizar só na Fase 3.

### Tabela `sales_brain_docs` (Fase 2)
| campo | tipo | nota |
|------|------|------|
| id | uuid PK | |
| titulo | text | |
| tipo | text | 'playbook'/'framework'/'script'/'objecao'/'case' |
| conteudo | text | chunk |
| embedding | vector(1536) | pgvector |
| created_at | timestamptz | |
- `create extension if not exists vector;` + índice ivfflat/hnsw cosine + função RPC `match_brain(query_embedding, k)`.

### RLS (reusa o modelo do CRM)
- `meetings`: closer SELECT/INSERT só do próprio (`closer_id = auth.uid()`); admin vê tudo (subquery em `profiles`). UPDATE resultado: dono OU admin (FR9).
- `sales_brain_docs`: SELECT autenticados; INSERT/UPDATE só admin.
- Edge Function usa **service_role** (server-side, bypassa RLS) — key só como secret, nunca no front.

---

## 2. Backend = Supabase Edge Function `analyze-meeting`
**Sem n8n. Sem serviço externo. Sem segredo no front.**

```
Front (closer logado)
  1. insere meeting (status=pending) via sb.from('meetings').insert(...)   [RLS: só o próprio]
  2. chama sb.functions.invoke('analyze-meeting', { body:{ meeting_id } })  [manda o JWT do login automaticamente]
        ↓
  Edge Function analyze-meeting (Deno/TS):
     a. valida o JWT (usuário autenticado)
     b. UPDATE status='processing'
     c. lê transcript (service_role)
     d. [Fase 2] embedding da transcrição → RPC match_brain (pgvector) → top-K chunks do Brain
     e. monta prompt (rubrica fixa + contexto Brain + transcript) → API Claude (temp 0, JSON estrito)
     f. parseia/valida JSON
     g. UPDATE meetings SET scores, insights, nota_geral, status='done', analyzed_at=now()
        (erro → status='error', erro_msg)
     h. retorna o resultado
        ↓
  Front: Realtime (já existe) OU o próprio retorno do invoke atualiza a tela.
```

- **Secrets no Supabase:** `ANTHROPIC_API_KEY` (e `OPENAI_API_KEY` p/ embeddings na Fase 2).
- **Saída do Claude (JSON estrito, via tool use):**
```json
{ "nota_geral": 7.4,
  "scores": {"rapport":8.5,"diagnostico":7,"escuta":6.5,"valor":7,"controle":8,"fechamento":5,"transicao":7,"objecoes":6},
  "insights": {"acertos":["..."],"erros":["..."],"faltou":["..."],"sugestoes":["..."]} }
```
- **Deploy:** Supabase CLI (`supabase functions deploy analyze-meeting`) ou editor de funções no Dashboard.

### Por que Edge Function e não n8n (verificado)
Disparo, leitura/escrita, chamada Claude com key segura, embeddings+pgvector, Realtime, agendamento (pg_cron), retry — **tudo nativo do Supabase**. n8n seria peça extra pra hospedar/manter. Co-Pilot tempo real (Fase 5) precisaria de streaming dedicado de qualquer jeito (n8n também não resolveria).

---

## 3. Prompt / rubrica (consistência — NFR5)
- **System:** "Você é um coach de vendas consultivas especialista. Avalie a reunião contra a rubrica e o playbook. Responda SOMENTE JSON no schema."
- **Rubrica fixa 0–10 por dimensão** (âncoras explícitas) hardcoded no prompt → notas estáveis.
- **temperature 0** + JSON forçado (tool use do Claude).
- **Modelo:** Claude Sonnet (qualidade) no MVP; Haiku como opção barata. ~US$0,05–0,30/reunião.

## 4. Embeddings (Fase 2)
- **OpenAI `text-embedding-3-small`** (1536 dims, ~US$0,02/1M — desprezível). Alt: Voyage AI. Gerado dentro da Edge Function.

## 5. Segurança / privacidade (NFR2)
- Transcrição = dado de cliente → RLS estrita (closer só o seu; admin tudo).
- `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` = **secrets da Edge Function** (server). Publishable key no front (padrão, RLS protege).
- Front nunca toca a API do Claude direto. Dados vão só pra API do Claude/embeddings (sem terceiros).

---

## 6. ⚡ Caminho MAIS ENXUTO pra fatia vertical HOJE
| Componente | Hoje (slice) | Fase 2 |
|-----------|--------------|--------|
| Tabela `meetings` + RLS | ✅ criar | — |
| `sales_brain_docs` + pgvector | ⏭️ pular | ✅ |
| Contexto no prompt | **playbook Cindy curto hardcoded** na função | RAG via pgvector |
| Edge Function `analyze-meeting` | ✅ (chamada síncrona pelo front) | + Database Webhook async |
| Análise Claude (rubrica+JSON) | ✅ | — |
| Aba "Reuniões/Coach" | ✅ lista + detalhe (upload, resultado, notas, insights) | + evolução/gráfico |

**Resultado esperado hoje:** 1 transcrição de teste → Edge Function → Claude → grava no Supabase → aparece no CRM com notas + insights. Loop provado, **zero infra além do Supabase**.

**Infra necessária pra ligar hoje:** (1) `ANTHROPIC_API_KEY`; (2) rodar o SQL no Supabase; (3) deploy da Edge Function (CLI ou Dashboard).

---

## 7. Handoff
- **@data-engineer (Dara):** DDL idempotente (`setup-sales-coach-v1.sql`) de `meetings` + RLS (+ `sales_brain_docs`/pgvector marcado Fase 2).
- → **@dev (Dex):** Edge Function `analyze-meeting` + aba "Reuniões/Coach" no `index.html` (reusando padrões `view-`/`goTo`/Realtime).
- → **@qa** → **@devops** (deploy front + função).
