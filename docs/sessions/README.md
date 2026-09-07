# Ponte de contexto Codex ↔ Claude

Codex e Claude não compartilham o histórico privado de suas conversas. A ponte
entre eles é formada por dois artefatos do próprio projeto:

1. **Git** transporta código, documentação e commits.
2. **`CURRENT.md`** transporta o contexto operacional que não cabe no código.

## Protocolo de início

Antes de alterar o projeto:

1. Ler `CURRENT.md`.
2. Conferir branch, `HEAD` e working tree.
3. Confirmar se o commit citado no handoff existe localmente.
4. Se estiver no Cloud, confirmar se o commit existe no remoto; não assumir que
   mudanças locais já foram publicadas.

## Protocolo de encerramento

Ao concluir um bloco relevante, antes de compactar ou trocar de ferramenta:

1. Atualizar `CURRENT.md` com o estado final observado.
2. Registrar somente decisões que alteram a continuação do trabalho.
3. Listar commits, validações, bloqueios e uma próxima ação executável.
4. Conferir que o arquivo não contém segredos, dados pessoais ou transcript.
5. Incluir o handoff no mesmo commit da entrega, quando fizer parte da tarefa.
6. Publicar pelo fluxo `@devops`. Até o push terminar, marcar explicitamente o
   trabalho como local.

## Separação de responsabilidades

- `.aiox/handoffs/`: troca curta entre agentes locais; efêmero e ignorado pelo Git.
- `docs/sessions/CURRENT.md`: estado corrente compartilhado entre ferramentas.
- Stories e documentos do produto: histórico durável e detalhado por iniciativa.
- Commits: prova exata do que mudou.
- Conversas: privadas a cada fornecedor; nunca são a fonte de verdade do projeto.

## Concorrência

`CURRENT.md` descreve apenas o trabalho ativo principal. Se duas iniciativas forem
executadas ao mesmo tempo, cada uma deve manter seu próprio documento de retomada
na pasta do projeto e `CURRENT.md` deve apontar para ambos. Antes de editar, reler
o arquivo para evitar sobrescrever uma atualização mais nova da outra ferramenta.

## Frase de retomada

> Leia `docs/sessions/README.md` e `docs/sessions/CURRENT.md`, confira o Git e
> continue da próxima ação sem reabrir decisões já registradas.
