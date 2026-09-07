# Story — Handoff Codex ↔ Claude

> Status: **Ready for Review**
> Data: 2026-09-07
> Origem: pedido do Vitor para continuar no Codex após atingir o limite do
> Claude e permitir retomada posterior sem perder o contexto operacional.

## Objetivo

Criar um ponto de retomada versionado e compartilhado entre Codex e Claude,
separando corretamente conversa, contexto local e estado publicado no Git.

## Acceptance Criteria

- [x] Existe um arquivo versionado e único para o contexto operacional atual.
- [x] Existe um protocolo versionado de início, encerramento, publicação e concorrência.
- [x] Codex é instruído a ler e atualizar o arquivo compartilhado.
- [x] Claude é instruído a ler e atualizar o arquivo compartilhado.
- [x] O protocolo local `.aiox/handoffs/` continua preservado e sua limitação
  para Cloud fica documentada.
- [x] O handoff não contém segredos nem transcript integral.
- [x] Mudanças validadas e preparadas em conjunto sem incluir alterações não relacionadas.
- [ ] Commit publicado por `@devops` para ficar acessível ao Claude Cloud.

## File List

- [x] `AGENTS.md`
- [x] `.claude/CLAUDE.md`
- [x] `.claude/rules/agent-handoff.md`
- [x] `docs/sessions/CURRENT.md`
- [x] `docs/sessions/README.md`
- [x] `docs/stories/cross-assistant-handoff.story.md`

## Validação planejada

- Confirmar que todos os arquivos são rastreáveis pelo Git.
- Conferir que o handoff contém as seções obrigatórias.
- Conferir que somente os seis arquivos desta story entram no commit.

## Resultado da validação

- Seis arquivos conferidos: todos existem e são rastreáveis pelo Git.
- Seções obrigatórias do `CURRENT.md` presentes.
- Nenhum padrão de segredo encontrado nos arquivos da entrega.
- `git diff --check` passou.
- Alterações preexistentes fora da story não foram incluídas.
