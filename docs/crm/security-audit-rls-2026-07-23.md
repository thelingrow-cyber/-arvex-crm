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
3. 2ª passada: `WITH CHECK` dos INSERT (A-4) — ⏳ pendente.

— Vega, squad security 🛡️ · verdict **CONCERNS**
