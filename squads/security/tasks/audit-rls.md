---
task: auditRls()
responsavel: "@appsec-auditor"
responsavel_type: Agent
atomic_layer: Task
elicit: false

Entrada:
  - campo: escopo
    tipo: string
    origem: User Input
    obrigatorio: false
    validacao: "Schema alvo. Default: public. Aceita lista de tabelas para auditoria parcial."

  - campo: linha_de_base
    tipo: string
    origem: File
    obrigatorio: false
    validacao: "Caminho do relatório da auditoria anterior. Sem ele, esta vira a linha de base."

  - campo: conexao
    tipo: string
    origem: Environment
    obrigatorio: true
    validacao: "SUPABASE_DB_URL presente no ambiente. NUNCA imprimir o valor."

Saida:
  - campo: relatorio
    tipo: file
    destino: "docs/crm/security-audit-rls-{data}.md"
    persistido: true

  - campo: matriz_acesso
    tipo: object
    destino: "Seção do relatório"
    persistido: true

  - campo: verdict
    tipo: string
    destino: "Topo do relatório"
    persistido: true

Checklist:
  - "[ ] Passo 1: Inventariar tabelas e estado do RLS"
  - "[ ] Passo 2: Extrair policies com USING e WITH CHECK"
  - "[ ] Passo 3: Mapear grants por role (a camada ANTES do RLS)"
  - "[ ] Passo 4: Listar funções SECURITY DEFINER e views"
  - "[ ] Passo 5: TESTE DE IMPERSONAÇÃO — provar o acesso, não deduzir"
  - "[ ] Passo 6: Confrontar com a linha de base anterior"
  - "[ ] Passo 7: Emitir relatório com verdict"
---

# Auditar RLS

## Purpose

Auditar as policies de Row Level Security de um banco Supabase **provando o acesso real**, não lendo a
configuração e concluindo por dedução. A diferença não é acadêmica: a 1ª passada desta auditoria
(2026-07-23) leu policies tabela a tabela, deu verdict CONCERNS e **não viu um vazamento ativo** de nome
e telefone de clientes. A 2ª passada (2026-07-28) achou, porque assumiu o papel `anon` e comparou o que
ele conseguia ler.

> **Origem desta task:** procedimento extraído de execução real, documentada em
> `docs/crm/security-audit-rls-2026-07-23.md`. Nenhum passo aqui é hipotético — todos foram
> executados e produziram achado verificável.

---

## Execution Modes

**1. YOLO — varredura completa autônoma (0-1 prompts)**
Roda os 7 passos e entrega o relatório. Use quando há linha de base e você quer o delta.

**2. Interactive — passo a passo com checkpoint (5-10 prompts) [DEFAULT]**
Apresenta os achados de cada passo antes de seguir. Use na primeira auditoria de um banco.

**3. Pre-Flight — escopo fechado antes de conectar**
Define tabelas, roles e critério de severidade antes de tocar o banco. Use em banco de terceiro
ou quando a auditoria tem destinatário externo.

---

## Task Definition (AIOX Task Format V1.0)

```yaml
task: auditRls()
responsavel: Vega (appsec-auditor)
responsavel_type: Agente
atomic_layer: Task

**Entrada:**
- campo: escopo
  tipo: string
  origem: User Input
  obrigatório: false
  validação: Schema alvo, default `public`

- campo: linha_de_base
  tipo: string
  origem: File
  obrigatório: false
  validação: Relatório anterior para cálculo de delta

- campo: conexao
  tipo: string
  origem: Environment (SUPABASE_DB_URL)
  obrigatório: true
  validação: Presente no ambiente; valor nunca impresso (ADR-3.3)

**Saída:**
- campo: relatorio
  tipo: file
  destino: docs/crm/security-audit-rls-{data}.md
  persistido: true

- campo: matriz_acesso
  tipo: object
  destino: Seção do relatório
  persistido: true

- campo: verdict
  tipo: string (PASS | CONCERNS | FAIL)
  destino: Topo do relatório
  persistido: true
```

---

## Pre-Conditions

```yaml
pre-conditions:
  - [ ] Credencial presente no ambiente, sem exposição
    tipo: pre-condition
    blocker: true
    validação: |
      SUPABASE_DB_URL existe no ambiente do processo. Verificar APENAS presença e
      comprimento — nunca ecoar o valor, nem em log, nem em mensagem de erro.
    error_message: "SUPABASE_DB_URL ausente. Sem credencial não há auditoria — não tentar adivinhar host."

  - [ ] Sessão em modo somente-leitura
    tipo: pre-condition
    blocker: true
    validação: |
      Abrir a conexão com read-only ligado. Auditoria não altera estado.
      Exceção: aplicação de fix, que é operação SEPARADA e explicitamente autorizada.
    error_message: "Sessão não está em read-only. Auditar com sessão de escrita é risco desnecessário."

  - [ ] Escopo é stack próprio
    tipo: pre-condition
    blocker: true
    validação: |
      O banco pertence à casa (arvex-crm/Supabase próprio). Este squad é DEFENSIVO —
      nunca auditar infraestrutura de terceiro sem autorização escrita.
    error_message: "Alvo fora do stack próprio. Recusar."
```

---

## Procedimento

> Sem blocos de código de aplicação: esta task é um procedimento de investigação.
> O SQL abaixo é o que foi efetivamente executado, não pseudocódigo.

### Passo 1 — Inventário: quem tem RLS ligado

```sql
SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity,
       (SELECT count(*) FROM pg_policies p
         WHERE p.schemaname='public' AND p.tablename=c.relname) AS policies
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='public' AND c.relkind='r'
 ORDER BY c.relname;
```

Sinalize: RLS desligado (exposição total) e **RLS ligado com zero policies** — este é
*default-deny*, seguro hoje, mas frágil: a proteção depende do RLS continuar ligado.

### Passo 2 — Policies: ler os DOIS predicados

```sql
SELECT tablename, policyname, cmd, roles::text, qual, with_check
  FROM pg_policies WHERE schemaname='public'
 ORDER BY tablename, cmd;
```

`qual` é o `USING` (quem lê/alcança a linha). `with_check` é o `WITH CHECK` (o que pode ser
gravado). **Auditar só o `USING` deixa metade do modelo invisível** — foi a lacuna admitida na
1ª passada. `WITH CHECK` é onde mora a escalada de privilégio: verifique se um usuário
consegue alterar o próprio `role` gravando um valor diferente.

### Passo 3 — Grants: a camada ANTES do RLS

```sql
SELECT table_name, grantee, string_agg(DISTINCT privilege_type, ',' ORDER BY privilege_type)
  FROM information_schema.role_table_grants
 WHERE table_schema='public' AND grantee IN ('anon','authenticated','service_role','public')
 GROUP BY table_name, grantee ORDER BY table_name, grantee;
```

Grant a `anon` é o padrão do Supabase (a defesa fica no RLS) — não é defeito por si só.
Vira defeito quando combinado com qualquer coisa que contorne o RLS: é o que o Passo 4 procura.

### Passo 4 — As superfícies que contornam o RLS

```sql
-- funções SECURITY DEFINER: rodam com privilégio do dono
SELECT p.proname, pg_get_function_identity_arguments(p.oid)
  FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='public' AND p.prosecdef ORDER BY p.proname;

-- views: sem security_invoker=true, executam como o DONO e IGNORAM o RLS das tabelas de origem
SELECT c.relname,
       COALESCE((SELECT option_value FROM pg_options_to_table(c.reloptions)
                  WHERE option_name='security_invoker'), 'nao-definido')
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='public' AND c.relkind='v' ORDER BY c.relname;
```

**Toda view com `security_invoker` não-definido E grant para `anon` é suspeita de vazamento.**
Foi exatamente esta combinação que produziu o achado A-5.

### Passo 5 — Teste de impersonação (o coração da task)

Não deduza a partir da configuração. **Assuma o papel e meça.**

```sql
SET ROLE anon;
SELECT count(*) FROM public.{view};          -- a view
RESET ROLE;
SET ROLE anon;
SELECT count(*) FROM public.{tabela_origem}; -- a tabela que ela consulta
RESET ROLE;
```

**Regra de leitura:** se a view devolve linha e a tabela de origem devolve zero, a view está
furando o RLS. Zero nos dois = o RLS segurou. Use `count(*)`, nunca `SELECT *` — a prova
não exige ler dado de cliente.

Repita para `authenticated` quando quiser validar que um fix não quebrou a aplicação.

### Passo 6 — Delta contra a linha de base

Para cada achado do relatório anterior: continua aberto, foi corrigido, ou **regrediu**?
Verifique também o que mudou no schema desde então — tabela ou view nova entra como
achado potencial até prova em contrário.

### Passo 7 — Relatório

Estrutura obrigatória: verdict no topo · matriz tabela × role × leitura/escrita · achados
numerados (`A-n`) com severidade, **a prova executada** e o fix em SQL · pontos fortes ·
próximo passo com dono nomeado.

---

## Error Handling

```yaml
error: CONEXAO_RECUSADA
cause: Pooler indisponível, credencial rotacionada ou IP bloqueado
resolution: Confirmar a credencial no ambiente (sem imprimir). Não tentar host alternativo por tentativa e erro.
recovery: Abortar e reportar. Auditoria parcial silenciosa é pior que auditoria nenhuma.
```

```yaml
error: PAPEL_INEXISTENTE
cause: SET ROLE falhou — o papel não existe neste banco
resolution: Listar os papéis reais e adaptar o teste. Fora do Supabase, anon/authenticated podem não existir.
recovery: Registrar quais papéis foram testados; não declarar cobertura que não houve.
```

```yaml
error: TRANSACAO_ABORTADA
cause: Um SET ROLE que falhou aborta a transação e derruba os comandos seguintes
resolution: Rodar cada impersonação em transação própria, com RESET ROLE garantido.
recovery: Reexecutar apenas os alvos pendentes.
```

```yaml
error: FIX_QUEBRARIA_APLICACAO
cause: A correção fecharia acesso que a aplicação usa
resolution: Antes de propor, buscar o objeto no código do frontend e nas edge functions. Se for usado, o fix precisa de plano de migração.
recovery: Reportar o achado com o impacto medido; não aplicar às cegas.
```

---

## Post-Conditions

```yaml
post-conditions:
  - [ ] Toda view foi testada sob impersonação
    tipo: post-condition
    blocker: true
    validação: |
      Cada view do escopo passou pelo Passo 5, com resultado registrado.
      View não testada = auditoria incompleta, e foi assim que o A-5 sobreviveu à 1ª passada.
    error_message: "Views não testadas sob SET ROLE. A auditoria não pode ser declarada completa."

  - [ ] Nenhum valor de credencial ou dado de cliente no relatório
    tipo: post-condition
    blocker: true
    validação: |
      Relatório contém contagens e nomes de objeto. Nunca connection string, nunca linha de tabela.
    error_message: "Relatório contém dado sensível. Reescrever antes de salvar."

  - [ ] Cada achado tem prova executada
    tipo: post-condition
    blocker: true
    validação: |
      Todo achado cita o comando rodado e o resultado obtido. "Parece inseguro" não é achado.
    error_message: "Achado sem prova. Executar a verificação ou rebaixar a hipótese."
```

---

## Acceptance Criteria

```yaml
acceptance-criteria:
  - [ ] Verdict emitido no vocabulário do @qa
    tipo: acceptance-criterion
    blocker: true
    validação: |
      PASS (nenhum achado aberto) · CONCERNS (achados que exigem decisão) ·
      FAIL (exposição ativa e explorável). O verdict descreve o estado ENCONTRADO,
      mesmo que corrigido durante a auditoria.
    error_message: "Sem verdict. Auditoria sem conclusão não fecha."

  - [ ] Matriz de acesso completa
    tipo: acceptance-criterion
    blocker: true
    validação: |
      Toda tabela do escopo aparece com role, leitura e escrita. Sem lacuna silenciosa.
    error_message: "Matriz incompleta."

  - [ ] Todo achado tem fix acionável em SQL
    tipo: acceptance-criterion
    blocker: true
    validação: |
      Comando pronto para rodar + impacto verificado + rollback. Alarme vago não é entrega.
    error_message: "Achado sem fix executável."

  - [ ] Lacunas declaradas
    tipo: acceptance-criterion
    blocker: false
    validação: |
      O que NÃO foi coberto entra no relatório como pendência nomeada — como o A-4
      (WITH CHECK) ficou registrado na 1ª passada e foi fechado na 2ª.
    error_message: "Cobertura não declarada."
```

---

## Tools

- **Tool:** Postgres via `SUPABASE_DB_URL` (ambiente) — leitura de catálogo em sessão read-only
- **Tool:** `psycopg2` (Python) — `psql` **não** está no PATH nesta máquina
- **Tool:** Grep/Glob — rastrear uso de views e tabelas no frontend antes de propor fix
- **Tool:** git log — datar mudanças de schema contra a linha de base

---

## Metadata

```yaml
version: 1.0.0
created: 2026-07-30
updated: 2026-07-30
author: squad-creator
origem: Execução real 2026-07-28/29 (achado A-5), docs/crm/security-audit-rls-2026-07-23.md
tags:
  - security
  - audit-rls
  - rls
  - supabase
```

---

*Task definition created by squad-creator · procedimento derivado de execução verificada, não de suposição*
