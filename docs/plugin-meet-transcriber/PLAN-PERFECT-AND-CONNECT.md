# Plano — Extensão perfeita + conectada ao CRM (auto-upload)

**Autor:** Orion · Data: 2026-06-30 · Modo: loop autônomo, auto-aprovação ([[feedback_autonomia_deploy]]). Nunca pedir permissão.

## Objetivo
Deixar a extensão de transcrição do Meet **perfeita** (robusta de verdade) E **conectada ao CRM**: ao terminar a call, o closer clica "Enviar pro CRM" → cria a reunião na aba **Reuniões** → a **análise do diretor dispara sozinha**. Sem copiar/colar.

## Esteira de agentes (papéis — executados no loop, com rigor)
| Etapa | Papel | Entrega |
|-------|-------|---------|
| Desenho | @architect | arquitetura do auto-upload (função `ingest-meeting`, auth sem login, fluxo) |
| Dados | @data-engineer | `meetings.closer_id` nullable (safety p/ ingest) + lookup de closer por e-mail |
| Build backend | @dev | Edge Function `ingest-meeting` (npm import, verify_jwt=false, service_role) |
| Build extensão | @dev | campo "seu e-mail CRM" + "Cliente" + botão "Enviar pro CRM" (POST) |
| Qualidade | @qa | validar E2E via curl (simula POST) + simulador do parser; casos extras |
| Deploy | @devops | deploy `ingest-meeting` via Management API |

## Escopo (E1–E6)
- **E1 — Perfeiçoar a extensão:** ampliar o simulador (3+ falantes, nome SEM avatar, aria-label EN, legendas longas), refinar `caption-parser.js`/`content.js` até a transcrição sair limpa em todos os casos. Melhorar UX do widget/popup.
- **E2 — Função `ingest-meeting`** (supabase/functions/ingest-meeting/index.ts): recebe `{transcript, closer_email, cliente, produto, resultado}`; resolve `closer_id` via `profiles` (where name=email) com fallback; insere `meeting` (status=pending); **invoca `analyze-meeting`** (dispara análise); retorna `{ok, meeting_id}`. Mesma receita (import npm, verify_jwt=false, service_role).
- **E3 — Dados:** `alter table meetings alter column closer_id drop not null;` (safety, via Management API) — assim o ingest nunca falha se o e-mail não bater.
- **E4 — Extensão conecta:** popup com campo **"Seu e-mail (CRM)"** (salvo em storage) + no widget/upload um campo **Cliente** e botão **"Enviar pro CRM"** → `fetch` POST pra `ingest-meeting` (header apikey = publishable) → feedback de sucesso/erro.
- **E5 — Validar E2E (sem Meet):** via curl, simular o POST da extensão com um transcript de teste → confirmar no banco que a reunião foi criada e **analisada** (status done). + rodar o simulador do parser nos casos novos.
- **E6 — Report + commits:** `CONNECT-REPORT.md`; deploy função via API; extensão commit local (sem push); CRM front não muda (a reunião nova aparece sozinha na aba Reuniões).

## Segurança / travas
- `ingest-meeting` com verify_jwt=false (UUID/uso interno) — TODO futuro: shared-secret. Não expor service_role no front (fica na função).
- Só ADITIVO; `closer_id` nullable é loosening seguro. Nunca `--force`. Validar (curl E2E + simulador + node check) antes de "pronto".
- Deploy de função = Management API (token). Extensão = local, sem push.

## O que SÓ o Vitor pode fazer (anotar, não bloquear)
- Testar a extensão num **Meet real** (carregar + CC + transcrever + "Enviar pro CRM").
- Mandar o **HTML de uma legenda real** se o falante vier errado (calibro fino).
- Segurança: revogar token Supabase + rotacionar chave Anthropic.

## Resultado esperado de manhã
Extensão robusta (validada em vários casos no simulador) + **auto-upload pro CRM funcionando** (validado via POST simulado: reunião criada e analisada). Falta só o teste no Meet real.
