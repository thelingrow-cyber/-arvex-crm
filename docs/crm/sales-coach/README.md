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
| Disparo em lote | `tools/sales-coach/analisar-pendentes.js` | ✅ analisa tudo que está `pending`/`error` sem passar pela UI |
| Estado do sistema | `tools/sales-coach/estado.js` | ✅ lê o banco e reporta |
| Desfecho real | colunas + trigger de venda + UI no modal | ✅ data, motivo da perda, ciclo e cobrança após 14 dias |

**Regra de deploy:** o front do coach vive em `index.html` da **raiz, branch `main`** (produção Vercel).
`docs/crm/index.html` (branch master) **não** tem o módulo. Edge functions: editar em
`supabase/functions/` na master e deployar com `npx supabase functions deploy <nome> --no-verify-jwt`.

## O que NÃO existe ainda (roadmap, em ordem)

| # | O quê | Por quê importa |
|---|---|---|
| 1 | Métricas determinísticas (`meetings.metrics`) — talk ratio, monólogo, nº de perguntas | Código, custo zero, comparável entre calls. Teria pego os monólogos de 15-25 min sozinho |
| 2 | Briefing pré-call | Muda o coach de retrovisor para copiloto |
| 3 | `stats_closer()` + aba Direção | Comparar time, conversão real |
| 4 | Notificação pós-call (WhatsApp via `evolution-proxy`) | O coaching indo até o closer |
| 5 | Evolução do cérebro com aprovação | Hoje a curadoria é 100% manual |

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

**Analisar o que ficou parado** (importar NÃO analisa — este é o passo que faltava)
```
$env:SUPABASE_ACCESS_TOKEN = (Get-ItemProperty -Path 'HKCU:\Environment').SUPABASE_ACCESS_TOKEN
node tools\sales-coach\analisar-pendentes.js
```

**Ver a verdade do sistema**
```
node tools\sales-coach\estado.js
```

---

## Pendências conhecidas (dívida honesta)

- ~~6 reuniões pendentes de análise~~ **RESOLVIDO 2026-08-13:** as 6 foram analisadas com o cérebro de 11
  blocos (`tools/sales-coach/analisar-pendentes.js`). **10/10 `done`.** O disparo não depende mais de clique.
  Primeira leitura agregada das 8 dimensões (10 calls): rapport 6,2 · controle 4,8 · escuta 4,3 · valor 4,2 ·
  objeções 3,6 · fechamento 3,2 · **transição 3,0 · diagnóstico 2,9**. O padrão que os casos já sugeriam
  agora está medido: conecta bem, não escava a dor, apresenta cedo, não fecha. A única call GANHA (Wal, 5,9)
  é a nota mais alta do acervo — e mesmo nela o diagnóstico ficou raso.
- **Só 3 de 10 reuniões têm `lead_id`** — sem isso o desfecho automático não funciona.
- **O SOP de vendas está desatualizado**: `docs/processos/sop-fluxo-vendas.md` lista R$5.000/7.000/10.000;
  as calls reais mostram R$4.997, R$2.500 (Express) e R$12.500. **Qual é a oferta válida hoje é decisão
  do Vitor** — e o coach julga a apresentação de preço contra essa tabela.
- **Duplicação de verdade no prompt**: a "sequência vencedora" está hardcoded no SYSTEM do
  `analyze-meeting` e também no bloco DEF do cérebro. Uma regra, duas fontes.
- **Sem avaliação de qualidade**: ninguém mediu se a análise com cérebro é melhor que sem. O gold-standard
  (`conhecimento/casos/caso-02-aline-coelho.md`, validado pelo Vitor em 28/06) é o material para esse teste.
