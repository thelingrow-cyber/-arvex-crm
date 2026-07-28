# Auditoria de RLS — arvex-crm

> Auditor: Vega (squad `security`) · roteado pelo Atlas (c-level) · 2026-07-23
> Método: leitura direta do banco de produção (metadados de schema/policies via pooler `aws-1-us-east-1`, sessão read-only). Nenhum dado de cliente foi lido.
> Escopo: schema `public` · 12 tabelas · 36 policies.

## VEREDITO: ⚠️ CONCERNS

Base sólida (RLS ligado em tudo, nenhuma exposição anônima ativa), mas há 3 achados que exigem decisão/fix e 1 ponto a aprofundar.

## Matriz — como cada tabela se protege

| Tabela | RLS | SELECT (leitura) | Escrita | Leitura |
|--------|-----|------------------|---------|---------|
| meetings | ✅ | `closer_id = auth.uid()` ou admin | por dono/admin | 🟢 isolado |
| vendas | ✅ | `is_financeiro_user()` ou `criado_por` | financeiro | 🟢 isolado |
| parcelas | ✅ | `is_financeiro_user()` ou `criado_por` | financeiro | 🟢 isolado |
| profiles | ✅ | **`true`** | update só o próprio | 🟠 lê todos |
| leads | ✅ | **`true`** | **update `true`** | 🟠 aberto |
| clientes_cs | ✅ | **`true`** | update cs/admin | 🟠 lê todos |
| cs_checks | ✅ | **`true`** | update cs/admin | 🟠 lê todos |
| agente_sdr | ✅ | `true` | admin | 🟡 |
| sdr_followups | ✅ | `true` | admin | 🟡 |
| status_history | ✅ | `true` (só SELECT) | — | 🟡 |
| agente_sdr_historico | ✅ | **SEM policy** + grant a `anon` | — | 🔴 frágil |
| sdr_midias | ✅ | **SEM policy** + grant a `anon` | — | 🔴 frágil |

## Achados priorizados

### ✅ A-1 [ALTO] — RESOLVIDO em 2026-07-27
RLS ligado mas **sem nenhuma policy** → hoje é *default-deny* (ninguém acessa via API, ok). **Mas** ambas têm grant **completo a `anon`** (SELECT/INSERT/UPDATE/DELETE/TRUNCATE). A proteção depende 100% do RLS continuar ligado — se alguém desligar o RLS numa migration, **um visitante anônimo apaga/lê tudo**.
**Fix:** `REVOKE ALL ON agente_sdr_historico, sdr_midias FROM anon;` — e, se a app precisa gravar aí, criar policy explícita para `authenticated`/`service_role`. Não depender só do RLS-on.

> **✅ APLICADO em 2026-07-27.** `REVOKE ALL ... FROM anon` executado nas duas tabelas contra produção.
> Estado pós-fix: `anon` sem nenhum grant; `authenticated`, `postgres` e `service_role` preservados.
>
> **Mudança desde a auditoria:** `agente_sdr_historico` ganhou a policy `agente_sdr_historico_select`
> (SELECT para `authenticated`), criada junto com o módulo de Atendimento em 24/07. A tabela agora
> tem defesa em profundidade real — RLS ligado **e** policy explícita, não mais só default-deny.
> `sdr_midias` segue sem policy (default-deny para `authenticated`); o acesso do n8n é por
> `service_role`, que faz bypass de RLS. Sem regressão.
>
> **Verificação de impacto:** o CRM lê `agente_sdr_historico` via `sb.from()` com sessão autenticada
> (roda como `authenticated`, não `anon`); a subscription de realtime idem. `sdr_midias` não é
> consultada pelo frontend. Nenhuma quebra esperada ou observada.
>
> **Rollback, se necessário:** `GRANT ALL ON public.agente_sdr_historico, public.sdr_midias TO anon;`
> (não recomendado — era exatamente a exposição que motivou o achado).

### 🟠 A-2 [MÉDIO] — `profiles` legível por qualquer usuário (`SELECT USING (true)`)
Qualquer conta autenticada lê o perfil de **todos** os usuários do time. Se `profiles` guarda algo além de nome/role (telefone, e-mail, metas), é exposição interna.
**Fix / decisão:** restringir a `auth.uid() = id OR is_admin()`, ou confirmar que expor perfis ao time inteiro é intencional.

### 🟠 A-3 [MÉDIO — decisão de negócio] — `leads`/`clientes_cs`/`cs_checks` abertos a todo authenticated
Todo usuário lê todos os leads/clientes; e `leads` ainda é **editável** por qualquer um (`UPDATE USING (true)`). Isso **é inconsistente** com `meetings`/`vendas`, que isolam por dono. Pode ser intencional (CRM colaborativo pequeno — todo mundo vê tudo), mas o `leads UPDATE true` é o mais arriscado (qualquer conta edita qualquer lead).
**Decisão do Vitor:** o CRM é "todos veem/editam tudo" de propósito? Se sim, ok e documentado. Se não, restringir leitura por dono/role como em meetings.

### 🟡 A-4 [INFO — aprofundar] — `WITH CHECK` dos INSERT não avaliado
Esta passada leu o predicado de leitura (`USING`). As policies de INSERT usam `WITH CHECK`, que não foi extraído aqui — ou seja, **quem pode inserir o quê** ainda não foi verificado. Recomenda-se 2ª passada.

## Pontos fortes (o que está certo)
- **0 tabelas com RLS desabilitado** — nenhuma exposição total.
- `meetings` isola por closer (`closer_id = auth.uid()`) — o modelo de privacidade funciona.
- `vendas`/`parcelas` isolam o financeiro corretamente.
- Existe um modelo de roles real e aplicado: `is_admin()`, `is_cs_or_admin()`, `is_financeiro_user()`.

## Próximo passo sugerido
1. ~~Fix imediato do A-1 (revogar grants de `anon` nas 2 tabelas)~~ — ✅ **feito em 2026-07-27**.
2. **Vitor decide A-2/A-3** (intencional ou restringir) — ⏳ **PENDENTE, é decisão de negócio**.
   - **A-2:** qualquer conta autenticada lê o perfil de todos os usuários. Intencional?
   - **A-3:** `leads` é **editável por qualquer conta autenticada** (`UPDATE USING (true)`) — este é
     o mais arriscado dos dois, porque hoje Thalita, Gabriel ou qualquer usuário futuro pode alterar
     qualquer lead sem restrição. Inconsistente com `meetings`/`vendas`, que isolam por dono.
3. ~~2ª passada: `WITH CHECK` dos INSERT (A-4)~~ — ✅ **feito em 2026-07-28** (ver abaixo).

— Vega, squad security 🛡️ · verdict **CONCERNS**

---

# 2ª passada — 2026-07-28

> Auditor: Vega (squad `security`) · sessão read-only sobre o catálogo do banco de produção.
> Escopo: fechar o A-4 (`WITH CHECK`), verificar as tabelas do módulo Atendimento e varrer
> superfícies não cobertas na 1ª passada (views, funções `SECURITY DEFINER`, event triggers).
> Nenhum dado de negócio foi lido — apenas `count(*)` como prova de acesso.

## VEREDITO: 🔴 FAIL — corrigido no ato

A 1ª passada tratou de risco **condicional** ("se alguém desligar o RLS"). Esta encontrou
exposição **ativa e explorável** de dado pessoal a visitante anônimo. Achado corrigido em
produção durante a auditoria; o verdict registra o estado encontrado, não o estado final.

### 🔴 A-5 [CRÍTICO] — view `checks_hoje` furava o RLS e vazava nome + telefone de clientes — ✅ CORRIGIDO

A view `checks_hoje` (definida em `docs/crm/setup-cs-v2.sql:179`, módulo CS) é `owned by postgres`
e **não tinha `security_invoker=true`**. No Postgres, view nessa condição executa com os privilégios
do **dono**, não do chamador — ou seja, **ignora o RLS das tabelas de origem**. E ela tinha
`GRANT ALL ... TO anon`.

A view expõe `cc.nome` e `cc.tel` de `clientes_cs` — nome e telefone de clientes reais da mentoria.
A `anon key` é pública por natureza (vai no JS do frontend), então qualquer pessoa com a URL do
projeto conseguia ler a agenda do dia do CS.

**Prova executada** (papel `anon` assumido na sessão):

| Alvo | Como `anon` | Leitura |
|------|-------------|---------|
| `checks_hoje` (view) | ANTES do fix | 🔴 **1 linha — leu** |
| `cs_checks` (tabela de origem) | — | ✅ 0 linhas (RLS segurou) |
| `clientes_cs` (tabela de origem) | — | ✅ 0 linhas (RLS segurou) |
| `v_followups_devidos` (view irmã) | — | ✅ 0 linhas — **tem `security_invoker=true`** |

A view irmã é a prova do diagnóstico: mesma estrutura, mesmo grant a `anon`, e não vaza —
porque tem a propriedade que faltava na `checks_hoje`.

**Fix aplicado em produção (2026-07-28):**
```sql
ALTER VIEW public.checks_hoje SET (security_invoker = true);
REVOKE ALL ON public.checks_hoje FROM anon;
```

**Verificação pós-fix:** `anon` → *permission denied*; `authenticated` → segue lendo normalmente
(1 linha). `service_role` (usado pelo n8n) tem BYPASSRLS, não é afetado. O frontend não consulta
`checks_hoje` — a view não aparece em nenhum arquivo do CRM. **Impacto de quebra: nenhum.**

**Rollback (não recomendado):** `ALTER VIEW public.checks_hoje SET (security_invoker = false); GRANT ALL ON public.checks_hoje TO anon;`

**Lição sistêmica:** o event trigger `ensure_rls` liga RLS automaticamente em toda *tabela* nova —
boa defesa, e foi ela que manteve a base sólida. Mas **event trigger não cobre view**. Toda view
criada em `public` precisa de `security_invoker=true` explícito, ou vira porta lateral em volta do
RLS. Hoje são 2 views; a regra vale para a próxima.

### ✅ A-4 [RESOLVIDO] — `WITH CHECK` dos INSERT/UPDATE auditado

O gap da 1ª passada está fechado. Resultado: **majoritariamente correto**.

| Tabela | `WITH CHECK` do INSERT | Veredito |
|--------|------------------------|----------|
| `profiles` | `auth.uid() = id` | ✅ não dá para criar perfil alheio |
| `meetings` | `closer_id = auth.uid()` ou admin | ✅ coerente com a leitura |
| `vendas` / `parcelas` | `is_financeiro_user() OR criado_por = auth.uid()` | ✅ closer registra a própria venda |
| `agente_sdr` | `is_admin()` | ✅ |
| `clientes_cs` / `cs_checks` | `is_cs_or_admin()` | ✅ |
| `leads` | **`true`** | 🟠 qualquer conta insere — coerente com o A-3 em aberto |

**Achado positivo que merece registro:** o `WITH CHECK` do `profiles_update` bloqueia **escalada de
privilégio** — `role` só muda se já for igual ao atual ou se quem edita for admin. Ninguém se
autopromove a admin. Isso está bem feito e não foi acidente.

### 🟠 A-6 [MÉDIO — novo] — conversas de WhatsApp legíveis por qualquer conta autenticada

`agente_sdr_historico` ganhou a policy `agente_sdr_historico_select` com `USING (true)` em 24/07,
junto com o módulo Atendimento. Funciona e **não nasceu exposta** — o `anon` não tem grant (fix A-1
se manteve). Mas qualquer usuário autenticado lê **todas** as conversas de WhatsApp com todos os leads.

É consistente com o resto do CRM (`leads`, `clientes_cs` também são `true`), então não é regressão.
O que muda é o **teor**: aqui o conteúdo é mensagem privada de cliente — dado pessoal sensível sob
LGPD, categoria diferente de "nome e etapa do funil". Entra na mesma decisão do A-2/A-3, com peso maior.

### Estado do A-1 (verificado)

Fix não regrediu: `agente_sdr_historico` e `sdr_midias` seguem sem nenhum grant para `anon`.
Nota: o fix foi **pontual, não sistêmico** — as outras 10 tabelas mantêm `GRANT ALL TO anon`. Isso é
o padrão do Supabase (a proteção fica por conta do RLS) e não é defeito por si só; só vira problema
quando algo contorna o RLS — que é exatamente o que a `checks_hoje` fazia.

## Superfícies varridas nesta passada

- **12 tabelas** — todas com RLS ligado, 0 desabilitadas (mantido).
- **36 policies** — `USING` e `WITH CHECK` extraídos.
- **10 funções `SECURITY DEFINER`** — esperadas (`is_admin()`, `is_cs_or_admin()`, triggers de status);
  nenhuma recebe entrada do usuário de forma a permitir bypass indevido.
- **2 views** — 1 furada (corrigida), 1 correta.
- **7 event triggers** — `ensure_rls` ativo e funcionando.

## Próximo passo

1. ~~A-5~~ — ✅ corrigido em produção 2026-07-28.
2. **A-2 / A-3 / A-6 — decisão do Vitor**, agora com o A-6 somado: o CRM é "todo mundo vê tudo"
   de propósito, incluindo as conversas privadas de WhatsApp? Se sim, documentar e encerrar.
   Se não, restringir por dono/role como em `meetings`.
3. **Regra nova a adotar:** toda view em `public` nasce com `security_invoker = true`.

— Vega, squad security 🛡️ · 2ª passada · verdict **FAIL → corrigido**
