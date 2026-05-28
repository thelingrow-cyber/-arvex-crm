# Módulo CS — Customer Success Cindy Batista

**Versão:** v4 (setup-cs-v4.sql) | **Última atualização:** 2026-05-28
**Owner técnico:** @data-engineer (Dara) + @dev (Dex)
**Owner operacional:** Sabrina (CS) + Cindy Batista (Expert)

> Este documento descreve a **arquitetura técnica** do módulo CS no CRM ARVEX.
> Para o **processo operacional** (responsáveis, templates, gates), ver [sop-cs-cindy.md](../processos/sop-cs-cindy.md).

---

## Arquitetura — 3 camadas

```
SOP (humano)  →  Banco (clientes_cs + cs_checks + triggers)  →  Kanban (index.html)
```

A regra de negócio mora **no banco** (triggers + funções RPC). O frontend é renderização + chamadas RPC.

---

## Banco — `setup-cs.sql` v1 → v4

### Histórico de versões

| Versão | Arquivo | Mudança principal |
|--------|---------|-------------------|
| v1 | `setup-cs.sql` | Tabelas iniciais, RLS, triggers básicos |
| v2 | `setup-cs-v2.sql` | `data_prevista` calculada, log de `tentativas` jsonb, view `checks_hoje`, função `registrar_tentativa()` |
| v3 | `setup-cs-v3.sql` | **CRÍTICO** — checks D+X só criados ao entrar em Campanha (trigger UPDATE, não INSERT) |
| v4 | `setup-cs-v4.sql` | `mover_lead_para_cs` preserva `leads.status='fechado'` + idempotente (card aparece em Fechado E no CS) |

### Tabela `clientes_cs`

1 row por aluno em CS.

| Grupo | Campos | Notas |
|-------|--------|-------|
| Vínculo | `lead_id` → leads | preserva histórico comercial |
| Estado | `cs_stage` | onboarding \| triagem \| campanha \| gate_cindy \| ativo \| risco_churn |
| Datas | `data_fechamento`, `data_triagem`, `data_campanha_inicio/fim`, `data_reuniao_cindy`, `ultimo_contato`, `ultima_tentativa` | `ultimo_contato` = quando respondeu; `ultima_tentativa` = qualquer tentativa |
| Gate Cindy | `aula_assistida`, `campanha_rodou`, `resultado_coletado` (boolean) | 3 critérios pra liberar reunião |
| Meta | `meta_oficial` | preenchida pela Cindy na reunião |
| Diagnóstico | 18 campos `diag_*` | região, lojas, sócio, faturamento, captação, IG, equipe, exame, armações, lentes, crediário, tráfego, sistema |
| Churn | `churn_flag` (ok\|amarelo\|vermelho), `churn_dias_sem_resp`, `tentativas_sem_resp` | calculado automaticamente |
| Histórico | `activities` jsonb | log de sub-etapas marcadas (`{fase, sub, data, por}`) |

### Tabela `cs_checks`

N rows por aluno (a cadência D+2, D+4, D+6, D+8, D+10, D+13, D+16).

| Campo | Tipo | Notas |
|-------|------|-------|
| `cliente_cs_id` | uuid | FK cascade |
| `dia_relativo` | int | 2, 4, 6, 8, 10, 13, 16 |
| `semana` | int | 1 ou 2 |
| `entregavel` | text | "Confirmar acesso...", "Grupo VIP...", etc. |
| `data_prevista` | date | `data_triagem + dia_relativo` |
| `status` | text | pendente \| respondido \| sem_resposta |
| `tentativas` | jsonb | array `[{data, hora, resultado, obs}]` |
| `data_resposta`, `resposta_obs`, `executado_por` | — | preenchidos quando respondido |

### Triggers automáticos

Rodam no banco — **frontend não precisa coordenar**.

| Trigger | Evento | Função |
|---------|--------|--------|
| `cs_updated_at` | BEFORE UPDATE | atualiza `updated_at` |
| `cs_churn_flag` | BEFORE INSERT/UPDATE | calcula `churn_flag` a partir de `ultima_tentativa` (3d=🟡, 5d=🔴) |
| `cs_criar_checks_campanha` | AFTER UPDATE | **v3** — cria os 7 checks D+X **só quando** `cs_stage` muda para `campanha` |
| `cs_recalcular_datas` | AFTER UPDATE | se `data_triagem` mudar, recalcula `data_prevista` de todos os checks |

### Funções RPC (chamadas pelo frontend)

**`mover_lead_para_cs(p_lead_id uuid) → uuid`**
- v4: **idempotente** (retorna id existente se já houver `cliente_cs` pro lead)
- v4: **preserva** `leads.status='fechado'` (não muda para `'cs'` como na v1)
- Resultado: card aparece em Fechado (Pipeline) E no Kanban CS simultaneamente

**`registrar_tentativa(p_check_id, p_resultado, p_obs, p_executado_por)`**
- Append em `cs_checks.tentativas` (jsonb)
- Atualiza `status` do check
- Se respondido: zera contador churn, atualiza `ultimo_contato`
- Se sem_resposta: incrementa `tentativas_sem_resp`, atualiza `ultima_tentativa`

### View

**`checks_hoje`** — agenda do dia: todos checks com `data_prevista = current_date` e `status = 'pendente'`, joined com `clientes_cs` (nome, tel, churn_flag).

---

## Frontend — Kanban (`index.html`)

### 6 colunas (`CS_COLS` — linha ~1729)

```
Onboarding 🟢 → Triagem 🔵 → Campanha 🟡 → Gate Cindy ⭐ → Ativo ✅ → Risco Churn 🔴
```

### Comportamento por coluna

**Campanha** é especial — única que mostra os checks D+X automáticos do banco:

| Dia | Entregável |
|-----|-----------|
| D+2 | Confirmar acesso à plataforma |
| D+4 | Grupo VIP criado — solicitar link |
| D+6 | Primeiras mensagens disparadas — print |
| D+8 | Campanha no ar — print da oferta |
| D+10 | Resultado parcial de vendas — número |
| D+13 | Resultado parcial da campanha |
| D+16 | Campanha encerrada — resultado final |

**Demais colunas** — sub-etapas manuais (`CS_SUBS`) clicáveis:

| Coluna | Sub-etapas |
|--------|-----------|
| Onboarding | Boas-vindas / Acesso liberado / Triagem agendada |
| Triagem | Reunião realizada / 11 perguntas / Materiais + datas / Aula indicada |
| Gate Cindy | Aula assistida / Campanha rodou / Resultado coletado |
| Ativo / Risco Churn | sem sub-etapas — acompanhamento contínuo |

Sub-etapas marcadas vão pra `clientes_cs.activities` (jsonb) — `{fase, sub, data, por}`.

### Sinais visuais no card (`renderCSCard` — linha ~1811)

- **Badge churn** no canto: 🟢 Ativo / 🟡 Xd / 🔴 Xd sem resp
- **Próxima ação** com botões ✅ Respondeu / ❌ Sem resposta (só em Campanha)
- **⏰ HOJE** / **⚠️ ATRASADO** no check pendente
- **✨ Pronto para avançar** quando todos checks/sub-etapas estão completos
- **🎯 Meta** em dourado quando `meta_oficial` preenchida

### Banner "Hoje" (`renderHoje` — linha ~1895)

No topo do Kanban. Lista todos clientes com check vencendo hoje. 3 botões por linha: WhatsApp / ✅ Respondeu / ❌ Sem resposta. Atualiza via realtime (postgres_changes em `clientes_cs`).

### Realtime

Subscription em `clientes_cs` (linha ~1150) — qualquer mudança recarrega cache + re-renderiza Pipeline e CS.

---

## Roles & Acesso

| Role | E-mails | Acesso |
|------|---------|--------|
| `admin` | viktorsimoess@gmail.com, arvexdigital@gmail.com | Tudo |
| `cs` | sabrinavieirasouza25@gmail.com | Só aba CS |
| `sdr` | qualquer outro | Pipeline + Leads |

Definida no JS (linha ~1080) por lista de e-mails — `csOnly` e `admins`. Não vem do banco.

**Adicionar usuário CS:**
1. Supabase → Authentication → Add user (e-mail + senha)
2. Rodar SQL:
   ```sql
   insert into profiles (id, name, role)
   select id, email, 'cs' from auth.users where email = 'email@aqui.com'
   on conflict (id) do update set role = 'cs';
   ```
3. Adicionar e-mail em `csOnly` no `index.html`

> Trigger `handle_new_user` foi removido (causava erro ao criar usuários). Insert manual via SQL acima.

---

## Fluxo end-to-end

```
1. Lead avança no Pipeline → coluna "Fechado"

2. SDR/Closer clica "→ CS" no card
   → RPC mover_lead_para_cs(lead_id)
   → cria row em clientes_cs (cs_stage='onboarding')
   → lead PERMANECE em Fechado (v4)

3. Sabrina vê card novo em Onboarding
4. Sabrina marca sub-etapas (boas-vindas, acesso, triagem agendada)
5. Arrasta para Triagem → executa reunião + 11 perguntas → preenche data_triagem
6. Arrasta para Campanha
   → trigger cs_criar_checks_campanha dispara
   → cria 7 checks D+2..D+16 com data_prevista calculada
7. Sabrina executa checks dia a dia via banner "Hoje"
   → RPC registrar_tentativa() em cada ação
8. Quando aula+campanha+resultado feitos → arrasta para Gate Cindy
9. Cindy faz reunião → define meta_oficial → arrasta para Ativo
10. Se 5+ dias sem resposta em qualquer fase → churn vermelho (automático)
```

---

## Arquivos

```
docs/crm/
├── index.html                  ← CRM completo (single-file vanilla JS + Supabase)
├── setup-cs.sql                ← v1: tabelas + RLS + triggers iniciais
├── setup-cs-v2.sql             ← v2: data_prevista, tentativas, view checks_hoje
├── setup-cs-v3.sql             ← v3: checks só ao entrar em Campanha
├── setup-cs-v4.sql             ← v4: preserva status=fechado + idempotente
├── MODULO-CS.md                ← este arquivo
└── transcricoes/               ← transcrições das reuniões de triagem

docs/processos/
└── sop-cs-cindy.md             ← SOP humano (responsáveis, templates, gates)

docs/stories/
└── crm-quente-pre-fechado-cs.story.md  ← story que motivou v4
```

---

## Pontos de extensão futura

Gaps documentados no [SOP](../processos/sop-cs-cindy.md#gaps-a-resolver-v20):

1. **Automatizar disparo dos checks** — integrar com Agente SDR (Carol) ou WhatsApp API pra reduzir carga manual da Sabrina
2. **Escopo formal do contrato** — diferenciar acompanhamento padrão vs. extra
3. **Biblioteca de templates** — mensagem por check (D+2, D+4...)
4. **Integração Financeiro** — vincular `clientes_cs` com vendas/parcelas pra dashboard 360°

---

*ARVEX CRM — Módulo CS | v4 | 2026-05-28*
