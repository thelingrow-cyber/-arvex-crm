# Migrations do Sales Coach — registro de aplicação

Banco: Supabase `arvex-crm` (ref `sgeoikzyahhdrncesbpn`).
Aplicar com acesso direto ao Postgres (`SUPABASE_DB_URL`), não pelo SQL Editor do navegador
(corrompe aspas em copy-paste — ver `reference_supabase_db_direto`).

**Ordem importa.** Rodar sempre em sequência numérica.
A partir da 011, título é único em `sales_knowledge`: reaplicar migration é no-op, e migration nova
deve usar `on conflict (titulo) do nothing`.

| # | Arquivo | O que faz | Aplicada |
|---|---|---|---|
| 001 | `001-setup-sales-coach-v1.sql` | Tabela `meetings`, RLS, colunas do MVP | ✅ 2026-06-27 |
| 002 | `002-cerebro-tabela-e-blocos-iniciais.sql` | Tabela `sales_knowledge` + RLS + 4 blocos (ICP v1, oferta, conta da base, objeções) | ✅ 2026-08-04 |
| 003 | `003-blocos-hormozi-100m-offers.sql` | Equação de valor, reversão de risco, escassez | ✅ 2026-08-04 |
| 004 | `004-icp-v2-lives-da-cindy.sql` | ICP v2 (3 calls + 15 lives) · desativa ICP v1 · cicatriz de mentoria · autoridade · payback da base | ✅ 2026-08-05 |
| 005 | `005-o-que-a-call-que-fechou-fez.sql` | Comparativo das 4 calls (1 ganha) | ✅ 2026-08-05 |
| 006 | `006-decisor-ausente-e-ancora.sql` | Decisor ausente + âncora de preço externa | ✅ 2026-08-05 |
| 007 | `007-spin-e-def.sql` | SPIN (perguntas + régua avanço/continuação) e DEF (arquitetura) · funde 3 blocos de objeção · desativa escassez | ✅ 2026-08-06 |
| 008 | `008-closer-hormozi.sql` | Framework CLOSER + taxonomia das 5 objeções · absorve o bloco do decisor · enxuga equação de valor | ✅ 2026-08-07 |
| 009 | `009-ajuste-de-teto.sql` | Enxuga o bloco da autoridade para caber no teto | ✅ 2026-08-07 |
| 010 | `010-objecoes-loop-acq.sql` | Loop de isolamento (ACQ) + respostas prontas por objeção + BAMFAM | ✅ 2026-08-07 |
| 011 | `011-guard-titulo-unico.sql` | Índice único em `titulo` — impede migration reaplicada de duplicar bloco | ✅ 2026-08-07 |
| 012 | `012-normaliza-closer-nome.sql` | Normaliza `meetings.closer_nome` pelo profile (o mesmo closer aparecia como duas pessoas) | ✅ 2026-08-07 |
| 013 | `013-desfecho-real.sql` | `desfecho_em`, `motivo_perda`, `desfecho_origem` + trigger de venda carimbando data/origem + backfill retroativo | ✅ 2026-08-07 |

## Como aplicar uma nova

```powershell
$env:SUPABASE_DB_URL = (Get-ItemProperty -Path 'HKCU:\Environment' -Name 'SUPABASE_DB_URL').SUPABASE_DB_URL
$env:NODE_PATH = 'c:\Users\Vitor Simões\Desktop\ARVEX\node_modules'
node -e "const fs=require('fs'),{Client}=require('pg');const c=new Client({connectionString:process.env.SUPABASE_DB_URL,ssl:{rejectUnauthorized:false}});(async()=>{await c.connect();await c.query(fs.readFileSync(process.argv[1],'utf8'));console.log('ok');await c.end()})()" docs\crm\sales-coach\migrations\0XX-nome.sql
```

Depois: `node tools\sales-coach\estado.js` para conferir, e **atualizar esta tabela**.
