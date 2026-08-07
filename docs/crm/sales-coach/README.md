# Sales Coach — mapa do sistema

> **Este é o ponto de entrada.** Se você (ou um agente) vai mexer no coach, comece aqui.
> Última revisão: 2026-08-07.
>
> ⚠️ **Documentação envelhece, banco não.** Antes de confiar em qualquer coisa escrita aqui:
> ```
> $env:SUPABASE_DB_URL = (Get-ItemProperty -Path 'HKCU:\Environment' -Name 'SUPABASE_DB_URL').SUPABASE_DB_URL
> $env:NODE_PATH = 'c:\Users\Vitor Simões\Desktop\ARVEX\node_modules'
> node tools\sales-coach\estado.js
> ```

---

## O que é

Um coach de closer dentro do arvex-crm (aba **Reuniões**). Recebe a transcrição de uma call de venda e
devolve análise no padrão "diretor comercial": julgamento central, 8 notas, dor dominante, erro
estratégico e **uma** missão para a próxima call. Conversa sobre a call no chat. Acompanha cada closer ao
longo do tempo.

O diferencial não é a IA — é o **cérebro**: conhecimento curado do comprador (dono de ótica), da oferta
da casa e do método de call, extraído de calls reais e material destilado. É o que separa este coach de
um consultor genérico de vendas.

## O que roda hoje (produção)

| Peça | Onde | Estado |
|---|---|---|
| Análise da call | Edge Function `analyze-meeting` | ✅ Sonnet 4.6, JWT + ownership, cérebro + histórico injetados |
| Chat com a call | Edge Function `coach-chat` | ✅ mesmo cérebro e histórico |
| Destilar material | Edge Function `distill-knowledge` | ✅ material bruto → bloco operável (só admin) |
| Cérebro | tabela `sales_knowledge` | ✅ 11 blocos ativos, teto 28.000 chars |
| Histórico do closer | query nas `meetings` do mesmo `closer_id` | ✅ últimas 12 análises, injetadas no prompt |
| UI | `index.html` (branch **main**, raiz) | ✅ aba Reuniões, tela "Cérebro do coach", seletor por closer (admin) |
| Importação em lote | `tools/coach-import/import.js` | ✅ .vtt/.txt/.md, dedupe por hash |
| Estado do sistema | `tools/sales-coach/estado.js` | ✅ lê o banco e reporta |

**Regra de deploy:** o front do coach vive em `index.html` da **raiz, branch `main`** (produção Vercel).
`docs/crm/index.html` (branch master) **não** tem o módulo. Edge functions: editar em
`supabase/functions/` na master e deployar com `npx supabase functions deploy <nome> --no-verify-jwt`.

## O que NÃO existe ainda (roadmap, em ordem)

| # | O quê | Por quê importa |
|---|---|---|
| 1 | **Desfecho real** (trigger venda→meeting + campo com data e motivo) | O coach analisa e nunca descobre se acertou. Pré-requisito de tudo abaixo |
| 2 | Métricas determinísticas (`meetings.metrics`) — talk ratio, monólogo, nº de perguntas | Código, custo zero, comparável entre calls. Teria pego os monólogos de 15-25 min sozinho |
| 3 | Briefing pré-call | Muda o coach de retrovisor para copiloto |
| 4 | `stats_closer()` + aba Direção | Comparar time, conversão real |
| 5 | Notificação pós-call (WhatsApp via `evolution-proxy`) | O coaching indo até o closer |
| 6 | Evolução do cérebro com aprovação | Hoje a curadoria é 100% manual |

Detalhamento e comparativo de mercado: **[AUDITORIA-2026-08-07.md](AUDITORIA-2026-08-07.md)**.

---

## Estrutura das pastas

```
sales-coach/
├── README.md               ← você está aqui
├── AUDITORIA-2026-08-07.md ← notas por camada, comparativo Gong/Attention, plano
├── migrations/             ← SQL numerado, na ordem de aplicação (+ APLICADAS.md)
├── conhecimento/           ← o que vira (ou virou) cérebro
│   ├── icp-dono-de-otica.md      perfil do comprador (3 calls + 15 lives)
│   ├── icp-fontes/               destilados brutos por lote de lives
│   ├── metodo-def.md             arquitetura de call (revisão externa destilada)
│   ├── roteiro-call.md           roteiro operacional do closer — VERSÃO VIVA
│   └── casos/                    caso-01 a caso-07 (análises de calls reais)
├── arquitetura/            ← decisões e specs vivas
├── transcricoes/           ← calls transcritas (fonte)
└── arquivo/                ← superado. Não usar como referência
```

## Como fazer as coisas

**Importar calls em lote**
```
node tools\coach-import\import.js <arquivo|pasta> --closer <email> --cliente "Nome" --data AAAA-MM-DD
```
Aceita `.vtt` (Zoom), `.txt` (plugin/Tactiq) e `.md`. Dedupe por hash em `client_key` — reimportar é no-op.

**Adicionar conhecimento ao cérebro**
1. Pela UI: aba Reuniões → **Cérebro do coach** → cola material bruto → *Destilar* → revisa → salva.
2. Por migration: novo arquivo em `migrations/` com número sequencial e `on conflict (titulo) do nothing`.

⚠️ **O cérebro tem teto de 28.000 caracteres** (`KB_MAX_CHARS` nas duas edge functions). Acima disso o
excedente é silenciosamente cortado. **Bloco novo exige dizer qual sai** — isso é decisão de curadoria,
não acidente: acima de ~7k tokens de contexto fixo a atenção do modelo dilui.

**Ver a verdade do sistema**
```
node tools\sales-coach\estado.js
```

---

## Pendências conhecidas (dívida honesta)

- **6 reuniões pendentes de análise.** O cérebro atual (11 blocos, SPIN/DEF/CLOSER) **nunca rodou uma
  análise** — está armado e não disparado. Depende de abrir Reuniões e clicar em *Reanalisar*.
- **`closer_nome` inconsistente**: algumas reuniões gravaram o e-mail em vez do nome ("Vitor" ×
  "viktorsimoess@gmail.com"). Não quebra nada (o histórico usa `closer_id`), mas polui relatório.
- **Só 2 de 9 reuniões têm `lead_id`** — sem isso o desfecho automático não funciona.
- **O SOP de vendas está desatualizado**: `docs/processos/sop-fluxo-vendas.md` lista R$5.000/7.000/10.000;
  as calls reais mostram R$4.997, R$2.500 (Express) e R$12.500. **Qual é a oferta válida hoje é decisão
  do Vitor** — e o coach julga a apresentação de preço contra essa tabela.
- **Duplicação de verdade no prompt**: a "sequência vencedora" está hardcoded no SYSTEM do
  `analyze-meeting` e também no bloco DEF do cérebro. Uma regra, duas fontes.
- **Sem avaliação de qualidade**: ninguém mediu se a análise com cérebro é melhor que sem. O gold-standard
  (`conhecimento/casos/caso-02-aline-coelho.md`, validado pelo Vitor em 28/06) é o material para esse teste.
