# Loops, Goals e agentes de longa duração — Alan Nicolas

> Fontes: **(1)** transcrição do vídeo (recebida 2026-07-29) · **(2)** material escrito de apoio — *"Pare de ser a coisa dentro do loop"*, `oalanicolas.news/loops-goals-e-agentes-de-longa-duracao` (recebido 2026-07-31)
> Tipo: aula de método/operação de harness
> Destilado em: 2026-07-29 · **revisado 2026-07-31 com o material escrito** · @aiox-master (Orion)

> ⚠️ **O material escrito é muito superior ao vídeo e corrige o vídeo em pontos importantes.** Onde os dois divergem, vale o escrito. A correção mais séria está na seção 2.

---

## 1. Resumo

### A tese
Se você não usa loop, **você é o loop** — o motorzinho humano que digita "sim, sim, não" e não pode fechar o notebook. E a frase que organiza a aula inteira: *quase todo erro de automação com agentes vem de **usar a primitiva errada*** — polling onde o disparo era evento, sessão local onde precisava de nuvem, loop temporal onde o fim era condição.

**Três perguntas resolvem a escolha:** (1) precisa sobreviver ao laptop fechado? (2) o que encerra o trabalho — tempo, condição ou evento? (3) quem decide o ritmo — você ou o modelo?

### A anatomia
**Loop = cron + um decisor no corpo.** Cron job executa script fixo; loop executa um *modelo* que lê o estado → decide → age (tools) → **verifica** → decide se continua. A decisão é do agente, não um `if` hardcoded seu.

> A caixa **verifica** é o que separa loop confiável de máquina de gerar erro confiante. *"Loop sem feedback compõe erros na mesma velocidade em que compõe commits."*

### As 7 primitivas (o vídeo falava de 3)

| # | Primitiva | Encerra por | Sobrevive ao laptop fechado | Limites documentados |
|---|---|---|---|---|
| 1 | `/loop 5m` (tempo fixo) | ritmo | ❌ morre com a sessão | mín. 1 min · máx. 50 crons/sessão · jitter até 30 min · **expira em 7 dias** · só roda com sessão idle, sem catch-up |
| 2 | `/loop` (dinâmico) | ritmo escolhido pelo modelo | ❌ | modelo chama `ScheduleWakeup`, **entre 1 min e 1 h** · em Bedrock/Vertex/Foundry não existe → vira fixo de 10 min |
| 3 | `/goal` | **condição verificável** | ❌ | avaliador = modelo pequeno (Haiku) que **só lê, não executa** · máx. 4.000 caracteres · exige trust dialog |
| 4 | `/schedule` | rotina (relógio/webhook/API) | ✅ **única nativa que sobrevive** | mín. **1 hora** entre execuções · exige plano Pro/Max/Team/Enterprise · sessão *fresh* numa VM da Anthropic clonando a branch default, **sem herança de contexto** · MCP connectors sim, **MCP servers locais não** |
| 5 | `Monitor` / `run_in_background` | **evento** (linha de log, processo terminando) | ❌ | indisponível em Bedrock/Vertex/Foundry e com telemetria off |
| 6 | subagents / workflows / Agent Teams | fan-out paralelo (não recorrente) | ❌ | subagent não spawna subagent · Teams experimental, 1 time por sessão |
| 7 | Agent SDK | **seu código** é o `while` | ✅ (é você quem hospeda) | durabilidade vem de **artefatos persistidos** (git/arquivos/banco), não da sessão · padrão Anthropic: agente *initializer* + agente *worker* incremental |

### Os dois gatilhos (a distinção-chave)
- **`/goal` responde: quando PARAR.** Dispara uma vez, manual; repete até a validação passar; tem fim, mas não tem gatilho próprio.
- **`/schedule` responde: quando COMEÇAR.** O relógio dispara; uma passada por tick; dorme; não tem fim.
- **O loop de orquestração é a fusão:** o relógio dispara, e a cada disparo um decisor roda **até concluir a unidade de trabalho** — barras que começam no tick mas têm largura variável. É por isso que "é só um cron job" está meio certo e meio errado.

### O validador (a parte que o vídeo não explicou)
`/goal` só fecha quando um avaliador **separado, menor, de contexto limpo** confirma. Quatro princípios:
1. **Quem faz não é quem avalia** — verificar é mais barato que produzir, e "depois de vinte voltas o executor está contaminado pelas próprias racionalizações". O juiz chega frio.
2. **Julga evidências, não opiniões** — suíte verde? build passou? diff no escopo? Sem evidência executável, vira "um segundo palpiteiro".
3. **A qualidade do veredito é a qualidade da meta** — "o validador só decide o que você tornou decidível". Escrever meta validável ≈ critério de QA, não prompt bonito.
4. **O validador desconfia** — modo de falha clássico é **reward hacking**: o executor deleta o teste que falhava, marca skip, hardcoda a resposta. Meta boa protege a integridade da evidência (o nº de testes diminuiu? algum assert enfraqueceu? o diff saiu do escopo?).

**Condição boa vs ruim:** boa = `npm test exits 0 and typecheck is clean`; ruim = "o código está bom e bem organizado" (subjetiva → o goal nunca fecha, ou fecha errado). **Regra de bolso: condição de goal é o que um estagiário confirmaria olhando o terminal.**

### Os 3 freios de produção
> "A versão romântica: mil agentes constroem sua empresa enquanto você dorme. A versão de produção: a maior parte do trabalho é garantir que eles param."

| Freio | Pergunta | Como aplicar |
|---|---|---|
| **Limite de iterações** | e se nunca convergir? | `or stop after 25 turns` no goal; contador no SDK. No teto: pare e chame um humano |
| **Detecção de estagnação** | e se girar em falso? | comparar estado entre ticks (diff, hash de artefato); abortar se idêntico 3 voltas |
| **Teto de custo** | e se a conta explodir? | orçamento por execução e por dia. A expiração de 7 dias do `/loop` **é este freio, embutido** |

### A escada histórica
ReAct (2022) → AutoGPT (2023) → ralph loop (2025, Geoffrey Huntley) → `/goal` e `/loop` produtizados com validador (2026) → orquestração (loops supervisionam loops). O próprio material traz uma **"nota de honestidade intelectual"**: a linhagem é real, mas os números virais que circulam (259 PRs em 30 dias, teto de gastos da Uber) são *relatos do discurso, sem fonte primária verificada*.

### A provocação final (o melhor pedaço)
> **O loop é encanamento; o ativo é a skill que ele chama.** Um loop sem skills reutilizáveis é *"um `while true` em volta de um estranho"* — re-deriva tudo e queima dinheiro. Um loop que chama uma biblioteca de skills nomeadas, testadas e afiadas é um sistema que compõe.
> **Regra prática: fez algo mais de uma vez? Vira skill. Fez algo difícil? Vira skill depois.**

---

## 2. Delta de aplicação — o que muda pro MEU sistema

### 🔴 Correção do destilado de 29/07

Eu escrevi que **`/goal` não existia** nesta instalação. **Estava errado.** Eu inferi a ausência do fato de `goal` não aparecer na minha lista de *skills* — mas comandos nativos do CLI (`/help`, `/clear` e afins) **não são skills e não aparecem nessa lista**. Ausência ali não é prova de ausência no CLI. O material documenta `/goal` com avaliador Haiku, limite de 4.000 caracteres e trust dialog.

**Confirmação de 5 segundos, que só você pode fazer:** digitar `/` no prompt e ver se `goal` aparece.

O que **se confirmou** do que eu tinha levantado sozinho: o wakeup dinâmico é mesmo **1 min – 1 h**, e por isso "a cada 2 horas" não é `/loop` dinâmico. Só que o motivo certo é outro: `/loop` **morre com a sessão**; o que sobrevive ao laptop fechado é `/schedule`.

### A regra de escolha, na minha realidade

| Situação minha | Primitiva |
|---|---|
| Notebook fechado / rodar de madrugada | `/schedule` (mín. 1h, exige Pro/Max — você tem) |
| Condição verificável e eu por perto | `/goal` + bound |
| Vigilância contínua com sessão aberta | `/loop` (dinâmico se o ritmo é incerto) |
| Reagir a log/processo (ex.: dev server) | `Monitor` / `run_in_background` |
| Trabalho grande de uma vez (migração, fan-out) | subagents/workflow — **não é loop** |

### Onde isso aterrissa aqui

1. 🔴 **Restrição que mata metade da ação âncora:** `/schedule` roda numa **VM da Anthropic, sessão fresh, clonando a branch default, e MCP/servidores locais não funcionam.** Minha auditoria "repo × produção" depende de acesso ao Supabase por variável de ambiente **local** — que não existe lá. Então a versão nuvem só consegue comparar o que é **público** (o `index.html` que está no ar) contra o repo; **edge functions ficam de fora**. A auditoria completa tem que rodar como `/loop` local, com a sessão aberta. Isso muda o desenho da ação e eu não sabia disso antes deste material.
2. 🎯 **O doc rot ganha a forma segura que eu queria:** vira `/goal` com critério binário e **escopo protegido no diff** — exatamente o padrão anti-reward-hacking da receita 9. Isso responde ao meu freio de "goal que deleta documentação": não é confiança no modelo, é **critério + bound + escopo**.
3. 🧠 **A provocação final bate direto na minha tese de agente.** Meu critério registrado é que agente só vale com *fonte + ferramenta + escopo estreito*; persona sozinha não produz nada. O Alan chega ao mesmo lugar por outro caminho: **loop sem skill é `while true` em volta de um estranho.** Eu tenho a biblioteca de skills (12 agentes AIOX, squad WebDesign, clones) — o que falta é o encanamento que as chama sozinho.
4. ⚠️ **"Subagent não spawna subagent"** e Teams experimental: confirma, por limite técnico, a regra que já está no meu harness.
5. ✅ **15 receitas prontas** vieram no material — copiáveis, trocando os substantivos. Subidas pro vault em `B05 Systems`.

**Ruído pro meu momento:** os 8 cenários de prática (exercício, não conteúdo), o simulador interativo, e do vídeo: os 120 agentes, o ranking Codex-vs-Grok-vs-Claude (o material escrito nem menciona) e a demo "organiza meu desktop".

---

## 3. Ação aplicada

- ✅ Destilado criado (29/07) e **revisado com o material escrito (31/07)**, com a correção do `/goal` explícita.
- ✅ Receitas prontas subidas ao vault: `B05 Systems/RECEITAS - Loops, Goals e Schedule (Claude Code).md`.
- 🎯 **Ação âncora (re-desenhada com o que aprendi hoje):** auditoria de divergência **repo × produção**, agora dividida pela restrição real —
  - **parte nuvem** (`/schedule`, roda com o notebook fechado): compara o que está público em produção contra a branch e me reporta;
  - **parte local** (`/goal` ou `/loop` com sessão aberta): edge functions e banco, que exigem os secrets locais.
- ⏳ **Backlog:** `/goal` de doc rot em `docs/` — com critério binário, `or stop after N turns` e **diff restrito**, em modo relatório na primeira rodada.
- ❌ **Descartado:** goal longo com permissão de escrita e sem bound. O material me deu o nome do que eu temia — *reward hacking* e *loop-que-não-para* — e os três freios que evitam.
