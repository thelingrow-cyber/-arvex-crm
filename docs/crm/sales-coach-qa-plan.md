# Plano de Testes / QA — Sales Coach MVP (arvex-crm)

**Autor:** @qa (Quinn) · Data: 2026-06-27 · Refs: stories + brief + architecture + DDL + UX spec
**Filosofia:** operação interna, sem framework de teste pesado. Confiança via **teste manual guiado + `?demo=1` + Chrome headless + checagens SQL no Supabase**. Foco em segurança (dados de cliente) e no loop ponta-a-ponta.

---

## 1. Estratégia
- **Front (vanilla):** roteiro manual + `?demo=1` (valida UI sem dados reais) + screenshot headless (390×844 e desktop) pra layout/console.
- **Edge Function:** testes de invocação com payloads controlados (transcrição boa, resposta malformada simulada, transcrição vazia).
- **Banco/RLS:** validação via SQL no Supabase + `test-as-user` (impersonar closer vs admin).
- **Console limpo:** zero erro JS no fluxo principal (verificar no headless/DevTools).

## 2. Casos de teste por story

### S1 — Banco / RLS (crítico)
| ID | Cenário | Esperado |
|----|---------|----------|
| S1-1 | `select count(*) from meetings` após setup | 0, tabela existe |
| S1-2 | `pg_policies` em meetings | 4 políticas |
| S1-3 | impersonar Closer A e ler reunião do Closer B | **0 linhas** (RLS bloqueia) |
| S1-4 | impersonar admin | vê todas |
| S1-5 | Closer tenta `delete` | negado; admin consegue |
| S1-6 | insert com `resultado` nulo | rejeitado (NOT NULL + check) |

### S2 — Edge Function `analyze-meeting` (crítico)
| ID | Cenário | Esperado |
|----|---------|----------|
| S2-1 | transcrição válida | JSON com 8 scores + insights; `status=done`; `analyzed_at` setado |
| S2-2 | Claude retorna texto não-JSON / malformado | `status=error`, `erro_msg`; função não quebra |
| S2-3 | nota fora de 0–10 no JSON | **clampada** a 0–10 (NFR — ajuste do @po) |
| S2-4 | invocação sem JWT / não autenticado | rejeitada (401) |
| S2-5 | inspecionar resposta/headers | `ANTHROPIC_API_KEY` **não aparece** em lugar nenhum |
| S2-6 | tempo de resposta | ≤ ~2 min (NFR4) |
| S2-7 | reanalisar reunião já analisada | sobrescreve scores; idempotente |

### S3 — Aba Coach / Lista
| ID | Cenário | Esperado |
|----|---------|----------|
| S3-1 | login closer | vê `nav-coach`, só suas reuniões |
| S3-2 | login admin | vê todas + filtro por closer |
| S3-3 | login cs | **não** vê `nav-coach` |
| S3-4 | `?demo=1` | 3–4 cards fictícios + banner demo |
| S3-5 | sem reuniões | empty state correto |
| S3-6 | dots de resultado/status | cores/labels corretos (ganhou=verde, perdeu=vermelho, analisando=âmbar) |

### S4 — Upload + disparo
| ID | Cenário | Esperado |
|----|---------|----------|
| S4-1 | enviar sem resultado | bloqueado, msg de validação |
| S4-2 | enviar sem transcrição | bloqueado |
| S4-3 | resultado=ganhou | campo ticket aparece |
| S4-4 | submit válido | insere (pending) + invoca função + modal fecha |
| S4-5 | aguardar análise | card vai de **Analisando…→Analisado via Realtime** (sem refresh) |

### S5 — Detalhe
| ID | Cenário | Esperado |
|----|---------|----------|
| S5-1 | abrir call done | 8 medidores + nota geral + 4 blocos de insights |
| S5-2 | editar resultado (dono/admin) | persiste; não-dono não consegue |
| S5-3 | reanalisar | status→processing→done, scores atualizam |

### S6 — Evolução
| ID | Cenário | Esperado |
|----|---------|----------|
| S6-1 | closer com N reuniões | média por dimensão correta (conferir cálculo) |
| S6-2 | tendência | seta ↑/↓ coerente vs período anterior |

## 3. Testes de SEGURANÇA (gate crítico — dados de cliente)
- **SEC-1 RLS sem bypass:** repetir S1-3/S1-4 com usuários reais. **FAIL bloqueia deploy.**
- **SEC-2 service_role:** confirmar que a key service_role está **só na Edge Function** (secret), nunca no `index.html`.
- **SEC-3 XSS:** subir transcrição/insights contendo `<img src=x onerror=alert(1)>` e `<script>` → deve renderizar como **texto escapado**, sem executar. (Transcrição e insights são conteúdo não confiável.)
- **SEC-4 key do Claude:** grep no front e no payload de rede → `ANTHROPIC_API_KEY` não vaza.
- **SEC-5 publishable key:** confirmar que o front só usa a publishable key (padrão atual) e RLS cobre tudo.

## 4. Smoke E2E — FATIA VERTICAL DE HOJE
1. Rodar S1 (SQL) no Supabase.
2. Deploy da Edge Function + secret `ANTHROPIC_API_KEY`.
3. Login como closer → `+ Nova reunião` → colar **transcrição de teste** → resultado=ganhou → Analisar.
4. **Esperado:** card "Analisando…" → em ≤2 min vira "Analisado" (Realtime) → abrir detalhe → 8 notas + insights coerentes.
5. Console sem erro. ✅ = loop provado.

## 5. Gate de qualidade (MVP)
- **PASS:** Smoke E2E ok + SEC-1..SEC-5 ok + console limpo + S1/S2/S4 verdes.
- **CONCERNS:** funciona mas com itens não-críticos (ex.: S6 cálculo a refinar, consistência de nota variando um pouco) → libera com follow-up.
- **FAIL:** qualquer falha de **segurança** (RLS bypass, XSS executando, key vazando) ou o loop E2E não fecha → não sobe.

> Nota de risco: **NFR5 (consistência da nota)** — mesmo com temp 0 pode haver pequena variação. Aceitável no MVP (CONCERNS, não FAIL); monitorar com casos reais.

→ Próximo elo: **@devops (Gage)** — plano de rollout/deploy (SQL + Edge Function + front).
