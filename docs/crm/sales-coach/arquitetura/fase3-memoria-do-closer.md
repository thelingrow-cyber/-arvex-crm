# Sales Coach — Fase 3: Memória do Closer (arquitetura técnica)

> Autor: @architect (Aria) · 2026-07-06 · análise com Sonnet 5
> Executor previsto: @data-engineer (schema) + @dev (Edge Functions/UI) — com Sonnet/Opus
> Base: `sales-coach-vision.md` (produto/visão, já escrito por Vitor+Orion 27/06) — este doc traduz a visão em schema, algoritmo e sequência executável. Não redefine o QUÊ, define o COMO.

---

## 1. O que já existe (não mexer)

- `meetings`: 1 linha por reunião, `scores` (8 dimensões 0-10), `insights` (acertos/erros/faltou/sugestoes), `resultado` (ganhou/perdeu/aberto), `closer_id`. **Já é forward-compatible** — o dataset pra Fase 3 já está sendo acumulado desde o MVP.
- Edge Function `analyze-meeting` (Claude, rubrica fixa, JSON estrito) — reusar o mesmo padrão de disciplina de prompt.
- **Plugin Meet Transcriber (`docs/plugin-meet-transcriber/`)** — já captura transcrição AO VIVO com timestamp real. Achado: isto resolve de graça a dependência que a visão aponta pro "Replay Timeline" ("exige timestamps — texto colado não tem"). Ligar a saída do plugin como fonte de `meetings.transcript` (com timestamps embutidos) desbloqueia a camada 3 da experiência sem trabalho extra de captura.

## 2. Achado de sequenciamento (recomendação que muda a ordem da visão)

A visão lista "Fase 3 = longitudinal + relatório mensal + `closer_profiles` + 11 blocos" como um bloco só. Mas dentro dela, o **"Chat com a IA sobre a call"** (camada 4 da experiência v2) é:
- **Muito mais barato** que o modelo cognitivo completo — não precisa de agregação histórica nem job assíncrono, só a call já analisada.
- **Não depende de acúmulo de dados** — funciona desde a 1ª call já no MVP.
- É o item que o próprio doc chama de **"feature mais viciante"**.

**Recomendação: construir o Chat ANTES do `closer_profiles`.** Maior valor percebido por menor esforço, entrega rápido, e valida o padrão de "conversar com a análise" antes de investir na parte cara (memória evolutiva).

## 3. Arquitetura — 2 camadas (a mesma distinção que a visão já definiu, agora com o COMO)

### Camada A — Determinística (SQL puro, sem IA, correta desde a 1ª call)
Comparação longitudinal é **subtração de médias já armazenadas** em `meetings.scores` — não precisa de IA nem de tabela nova:

```sql
create or replace function stats_closer(p_closer_id uuid, p_n int default 20)
returns jsonb language sql stable as $$
  select jsonb_object_agg(dim, avg_nota) from (
    select dim, round(avg((scores->>dim)::numeric), 1) as avg_nota
    from (select * from meetings where closer_id = p_closer_id and status = 'done'
          order by data_reuniao desc limit p_n) m,
         jsonb_object_keys(m.scores) as dim
    group by dim
  ) t;
$$;
```
Chamar com `p_n=5` (curto prazo) e `p_n=20` (referência) e subtrair no frontend/relatório = "+8% rapport". **Zero custo de IA, zero risco de alucinação.**

### Camada B — Narrativa (IA, só pra padrões qualitativos, em lote — não por call)

**`closer_profiles`** (tabela nova):
```sql
create table if not exists closer_profiles (
  closer_id             uuid primary key references auth.users(id) on delete cascade,
  padroes               jsonb default '[]',   -- [{padrao, confianca(1-5), desde, evidencia_meeting_ids[]}]
  resumo_narrativo       text,                 -- 2-3 frases estilo "diretor comercial"
  proximo_salto          text,                 -- 1 recomendação, não lista
  calls_analisadas_total integer default 0,
  calls_desde_ultima_att integer default 0,     -- reseta a cada atualização de perfil
  updated_at             timestamptz default now()
);
```

**AD-1 — Perfil NUNCA é reescrito do zero.** A IA recebe o `resumo_narrativo` + `padroes` ANTERIORES junto com os insights (não transcrições completas — caro e desnecessário) das últimas ~30-60 calls, e responde: *"o que mudou desde a última leitura? o que se confirma? o que é ruído de 1 call isolada?"* — merge, não substituição. Evita "perfil amnésico" e evita o modelo inventar um padrão novo a cada rodada.

**AD-2 — Atualização em LOTE, não por call.** Trigger: `calls_desde_ultima_att >= 5` (configurável) dispara a atualização — não a cada reunião analisada. Isso é barato (1 chamada de IA a cada 5 calls, não a cada 1) e evidencia mudança real de padrão, não ruído de uma call atípica.

**AD-3 — Execução:** Edge Function `update-closer-profile`, chamada por `pg_cron` (diário, verifica quais closers cruzaram o threshold) ou disparada no fim de `analyze-meeting` quando o contador bate — reusa a mesma disciplina de prompt do MVP (JSON estrito, temp 0).

### Camada C — Chat com a call (prioridade #1 desta fase, ver seção 2)
Endpoint simples, sem RAG: `chat-meeting(meeting_id, pergunta)` → busca a MEETING específica (transcript + scores + insights, já no banco) → 1 chamada Claude com esse contexto + a pergunta → resposta. Não precisa de pgvector nem histórico — o contexto de 1 call cabe inteiro no prompt.

## 4. Relatório mensal
Composição, não geração do zero: agregados SQL (conversão = `count(resultado='ganhou')/count(*)`, ticket médio, objeções mais frequentes = contagem de texto em `insights->erros`/`insights->faltou` agrupado) + **1 chamada de IA por closer por mês** só pra narrar o resumo executivo em cima dos números já calculados. Barato, best-effort na primeira versão (pode ser texto simples, sem novo schema).

## 5. Fases de implementação (em série)

| Fase | O quê | Dependência |
|------|-------|-------------|
| **3a** | `stats_closer()` (Camada A) + exibir "+X% vs últimas 20" no relatório pós-call já existente | Nenhuma — dados já existem |
| **3b** | Chat com a call (Camada C) | Nenhuma — maior valor/menor esforço, priorizar |
| **3c** | `closer_profiles` + Edge Function de atualização em lote (Camada B) | 3a (usa os mesmos agregados como sinal de quando atualizar) |
| **3d** | Relatório mensal | 3a |
| **3e** | Conectar Meet Transcriber plugin como fonte de transcript com timestamp → desbloqueia Replay Timeline (camada 3 da experiência) | Plugin já existe; só integrar o envio pro `meetings.transcript` |

## 6. O que NÃO fazer agora

- ❌ pgvector/RAG pra memória do closer — o volume de calls por closer ainda não justifica busca vetorial; agregados SQL + janela de contexto direto resolvem até centenas de calls.
- ❌ Recalcular perfil a cada call — caro e instável; lote de 5 é o ponto de equilíbrio inicial (ajustável).
- ❌ Fase 4 (coach pré-call) e Fase 5 (copilot tempo real) — dependem de volume de dados acumulado e de streaming dedicado respectivamente; não antecipar.
