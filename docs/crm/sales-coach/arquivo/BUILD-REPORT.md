> ⚠️ **DOCUMENTO ARQUIVADO — não use como referência.**
> Superado pelo estado atual do sistema. Ponto de entrada: [../README.md](../README.md)
> Mantido só como registro histórico.

# 🌙 Build Report — Sales Coach MVP (build autônomo noturno)

**Data:** 2026-06-27 (madrugada) · Executor: @dev em loop autônomo · Para: Vitor

Bom dia, Vitor. Enquanto você dormia, construí o **v1 inteiro do Sales Coach** (S1→S5). Está tudo no código, validado em demo. Faltam só **3 passos seus** (infra) pra ligar ao vivo.

---

## ✅ O que ficou PRONTO (código completo + validado em demo)
| Story | Entrega | Arquivo | Validação |
|-------|---------|---------|-----------|
| S1 | Tabela `meetings` + RLS + índices (DDL) | `setup-sales-coach-v1.sql` | revisado (não aplicado — precisa do Supabase) |
| S2 | Edge Function `analyze-meeting` (Claude, rubrica 8 dims, JSON estrito, clamp 0-10, trata erro) | `supabase/functions/analyze-meeting/index.ts` | revisado (não deployado — precisa do Supabase + key) |
| S3 | Aba "Coach" + lista (cards, dots de resultado/status, nota por faixa, filtros, empty state, `?demo=1`) | `index.html` | ✅ headless desktop + mobile, JS sem erro |
| S4 | Modal "Nova Reunião" (form, resultado obrigatório, ticket condicional, insert+invoke, Realtime, simulação demo) | `index.html` | ✅ headless |
| S5 | Detalhe da call (8 medidores, nota geral, 4 blocos de insights, editar resultado, reanalisar) | `index.html` | ✅ headless |

**Commits locais (sem push — alçada do @devops):**
`8d08524` (S2+dossiê) · `bd126b3` (S3) · `5d173cf` (S4+S5).

**Validação visual:** prototipei cada UI isolada e fotografei em Chrome headless (390×844 + desktop) — lista, modal de upload e detalhe ficaram 100% no design system do CRM (índigo, dots, Lucide, raio 8px), zero erro de console. Screenshots na pasta de sessão (scratchpad).

---

## ⚠️ O que NÃO pôde ser testado (depende de infra sua)
Tudo que toca o backend real ficou **escrito mas não executado**, porque precisa das suas credenciais:
- Chamada real ao Claude (a análise de verdade gerando notas).
- RLS com usuários reais (closer só vê o seu / admin vê tudo).
- Realtime (card "Analisando…" → "Analisado" sozinho).
- Insert real na tabela `meetings`.

> O fluxo foi **simulado em `?demo=1`** (dados fictícios + `setTimeout` imitando a análise), então a UI e a lógica de tela estão provadas. Só a integração viva falta.

---

## 🚀 Pra LIGAR ao vivo — 3 passos seus (tudo pelo Dashboard, sem CLI)
1. **API key da Anthropic** → Supabase Dashboard → *Project Settings → Edge Functions → Secrets* → adicionar `ANTHROPIC_API_KEY = sk-ant-...`
2. **Criar a tabela** → Supabase → *SQL Editor* → colar a **PARTE MVP** de `docs/crm/setup-sales-coach-v1.sql` → Run (esperado: "Success. No rows returned.")
3. **Deploy da função** → Supabase → *Edge Functions → Create function* → nome `analyze-meeting` → colar o conteúdo de `supabase/functions/analyze-meeting/index.ts` → Deploy.

Depois disso: abrir o CRM → aba **Coach** → **+ Nova reunião** → colar uma transcrição de teste → marcar resultado → **Analisar**. Em ~1-2 min o card vira "Analisado" com as notas. 🎯

> **Testar a UI agora (sem nada disso):** abra o CRM com `?demo=1` na URL → a aba Coach mostra reuniões fictícias e o fluxo simulado.

---

## 📋 Pendências / próximos passos
- **Publicar:** o código está em `docs/crm/index.html` (cópia de trabalho), **não** na produção. Quando você aprovar, o **@devops** sincroniza master→main (fluxo do CRM).
- **Ajustes do @po** já incorporados: clamp 0-10 ✅, reanalisar ✅, ticket condicional ✅. (Tempo assíncrono <2min depende do deploy real.)
- **QA real:** rodar o `sales-coach-qa-plan.md` (segurança SEC-1..5) depois do deploy, antes de usar com dados de cliente.
- **Fase 2+:** Sales Brain (pgvector), modelo cognitivo do closer, evolução longitudinal, coach pré-call — tudo já desenhado em `sales-coach-vision.md`.

---

## 🐛 Notas técnicas
- Edge Function usa modelo `claude-sonnet-4-6` (trocável p/ `claude-haiku-4-5` se quiser mais barato). Key só via `Deno.env` (nunca no front).
- Front escapa HTML (`esc`) em transcrição/insights (anti-XSS).
- Realtime via canal `coach-meetings` (subscreve 1x). Gating por role reusa `applyRole` (cs não vê a aba).
- Nenhum erro de sintaxe no `index.html` (checado com `node` a cada injeção).

**Loop encerrado.** Qualquer ajuste, é só pedir — a estrutura é toda iterável. 🛠️
