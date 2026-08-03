---
description: Abre, fecha ou alimenta a semana a partir do backlog mestre de todas as frentes
argument-hint: "[abrir | fechar | add <item> | status]"
---

# /semana — o ritual de gestão das frentes

Fonte única: `docs/gestao/BACKLOG.md`. Semanas: `docs/semanas/{frente}-semana-{AAAA-MM-DD}.md`.

**Regra inegociável:** a semana é sempre uma **seleção do backlog**. Nunca crie um item na semana que não exista no backlog — se surgir algo novo, adicione ao backlog primeiro (com ID) e só depois selecione.

Argumento recebido: `$ARGUMENTS` (vazio = `abrir`).

---

## `abrir` — montar a semana

1. Leia `docs/gestao/BACKLOG.md` inteiro.
2. Leia a semana anterior em `docs/semanas/` e traga o que ficou por fazer (item que atravessa 3 semanas sem sair vira candidato a congelar `[~]` — pergunte).
3. **Aplique os gates**: nenhum item `🔒` entra se o bloqueador dele não estiver `[x]` ou não estiver selecionado antes dele na mesma semana.
4. **Respeite o teto humano** — este é o filtro que faz o sistema funcionar:
   - máximo **5 itens 👤** na semana (é o gargalo real: gravar, call, testar, treinar, conversar)
   - máximo **2 itens G/XG** em execução ao mesmo tempo, somando todas as frentes
   - itens 🤖 não contam para o teto, mas cada um precisa de uma aprovação sua — não passe de 8
   - itens ⚪ PESSOAL são livres (não competem)
5. **Priorize nesta ordem**, e diga em voz alta qual regra aplicou:
   1. dinheiro parado (lead quente, venda em aberto)
   2. desbloqueadores (item que destrava 3+ outros — ex.: OF-01)
   3. itens P que estão parados há semanas (custo ridículo, alívio alto)
   4. o build ativo do momento — **um só de cada vez**
   5. recorrentes (postar, gravar, calls)
6. Escreva/atualize um arquivo por frente + a `AGENDA-semana-{data}.md` com blocos por dia, seguindo o formato já existente em `docs/semanas/`.
7. Feche com **as 3-4 entregas que definem se a semana valeu** e com a **ordem de corte** se a semana atrasar.
8. Commit: `docs(semanas): planejamento {dd/mm}-{dd/mm}`.

## `fechar` — revisão (fazer no domingo)

1. Pergunte, frente por frente, o que saiu — não presuma pelos checkboxes.
2. Marque no **backlog** (`[x]` / `[>]` / `[~]`), não só na semana.
3. Reporte, de forma factual e sem suavizar:
   - o que foi entregue
   - **o que não saiu e por quê** (falta de tempo? travado? escopo mal definido?)
   - itens que atravessaram 3+ semanas → propor congelar ou quebrar em pedaços menores
   - **se o teto de 5 👤 foi estourado** — se foi, foi a causa provável do que não saiu
4. Só então rode `abrir` para a semana seguinte.

## `add <item>` — capturar

Adicione ao `BACKLOG.md` na frente certa, com: ID sequencial da frente, executor (🤖/👤/👥), tamanho (P/M/G/XG), máquina (M1-M5) e bloqueador se houver. Confirme em uma linha. Não crie arquivo novo.

## `status` — leitura rápida

Sem reescrever nada, responda: quantos itens por frente, quantos travados e por quem, quais os 3 desbloqueadores de maior alcance, e o que está `[>]` há mais tempo.

---

## Princípios (por que este sistema é assim)

- **O gargalo é presença e decisão, não execução.** Metade do backlog é executável por mim. O teto da semana é o número de coisas que exigem o Vitor.
- **Uma fonte só.** Já morreram: `docs/semanas/` de abril (nada revisitava) e o backlog Notion+Obsidian (adiado). O que falhou não foi a ferramenta — foi não existir ritual de fechamento. O `fechar` é a metade que importa.
- **Não construir ferramenta de gestão.** Nada de app novo, board novo ou banco novo: markdown no repo + este comando. Se sobreviver 4 semanas de uso real, aí sim discutir uma aba no CRM.
- **Dispersão é a ameaça declarada nº1.** Ao propor a semana, se as 4+ frentes estiverem todas ativas, diga isso uma vez, com a ordem de corte — e depois execute o que o Vitor decidir, sem reabrir o assunto.
