# Story — Handoff Codex ↔ Claude

> Status: **Done**
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
- [x] Existe um check CLI sem dependências externas para validar estrutura,
  referências e padrões de segredo do handoff.
- [x] Mudanças validadas e preparadas em conjunto sem incluir alterações não relacionadas.
- [x] Commits publicados por `@devops` na branch remota
  `codex/whisperflow-handoff`, sem publicar os commits paralelos da `master`.

## File List

- [x] `AGENTS.md`
- [x] `.claude/CLAUDE.md`
- [x] `.claude/rules/agent-handoff.md`
- [x] `docs/sessions/CURRENT.md`
- [x] `docs/sessions/README.md`
- [x] `docs/stories/cross-assistant-handoff.story.md`
- [x] `tools/handoff/check-current.cjs`
- [x] `package.json` — scripts `test` e `handoff:check` (somente este hunk).

## Validação planejada

- Confirmar que todos os arquivos são rastreáveis pelo Git.
- Conferir que o handoff contém as seções obrigatórias.
- Conferir que somente os seis arquivos desta story entram no commit.

## Resultado da validação

- Seis arquivos conferidos: todos existem e são rastreáveis pelo Git.
- Seções obrigatórias do `CURRENT.md` presentes.
- Nenhum padrão de segredo encontrado nos arquivos da entrega.
- `git diff --check` passou.
- `npm test` executa o check real do handoff, substituindo o placeholder que
  sempre falhava.
- Alterações preexistentes fora da story não foram incluídas.
- Branch isolada validada: Python compilou, teste de ativação passou 3/3 e o
  working tree permaneceu limpo.
- Branch remota criada com sucesso em 07/09/2026.
