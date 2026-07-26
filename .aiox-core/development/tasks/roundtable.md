---
id: roundtable
name: Roundtable — Deliberação Multi-Clone
agent: aiox-master
category: decision
complexity: medium
---

# Task: Roundtable — Deliberação Multi-Clone

**Purpose**: Submeter uma decisão estratégica a N clones com perspectivas incompatíveis entre si
e convergir (ou não) num veredito auditável.

**Elicit**: true — a Rodada 0 PARA e devolve ao usuário se a questão não for decidível, e a
composição da mesa é confirmada antes de começar. Não pule por eficiência.

> Executor padrão: `@aiox-master` (Orion). Constituição: Art. IV (No Invention) é gate duro.

## Quando usar

| Situação | Roundtable? |
|---|---|
| Decisão estratégica com trade-off real (posicionamento, oferta, priorização, matar/manter um projeto) | ✅ Sim |
| Escolha entre caminhos que exigem perspectivas incompatíveis | ✅ Sim |
| Hipótese aberta que ninguém consegue derrubar sozinho | ✅ Sim |
| Pergunta factual, tarefa de execução, bug, implementação | ❌ Não — use o agente de domínio |
| Decisão já tomada e o usuário quer validação | ❌ Não — isso é teatro de aprovação |

**Anti-padrão:** roundtable não é para *descobrir* o que fazer quando falta informação.
Falta de informação → `@analyst` ou squad `research` primeiro. A mesa julga, não pesquisa.

## Elenco disponível

| Clone | Convocar quando a decisão envolve |
|---|---|
| `charlie-munger` 🧠 | Qualidade de julgamento, risco de ruína, incentivos, vieses. **Cadeira permanente** — ver Rodada 3 |
| `naval-ravikant` 🧭 | Alavancagem, ativo vs serviço, escala sem headcount, tempo do fundador |
| `michael-gerber` 🏗️ | Sistematizar, sair do papel de operador, processo replicável |
| `alex-hormozi` 💰 | Oferta, preço, valor percebido, funil de aquisição |
| `eugene-schwartz` 🧲 | Copy, nível de consciência do mercado, mecanismo único |
| `molly-pittman` 📊 | Tráfego pago, criativo, aquisição paga |
| `al-ries` 🎯 | Posicionamento, categoria, foco vs extensão de linha |
| `simon-sinek` 🌱 | Propósito, narrativa institucional, porquê |
| `dan-mall` 🎨 | Design systems, processo de design |
| `tay-dantas` 🇧🇷 | Contexto de mercado BR, creator/infoproduto |

## Seleção da mesa

**3 a 5 participantes. Nunca todos.** Uma mesa de 10 produz ruído, não sinal — e queima cota.

Critérios, nesta ordem:
1. **Munger é cadeira permanente** (a inversão é obrigatória — ver Rodada 3).
2. **2 a 4 clones cujo domínio toca o eixo real da decisão.**
3. **Pelo menos um que provavelmente discorda dos outros.** Mesa que concorda não decide nada — confirma o que você já queria ouvir. Se todos os convocados puxam para o mesmo lado, troque um.

Declare a mesa e o motivo de cada cadeira ANTES de começar. Se o usuário nomeou os participantes, use os dele — mas avise se faltar contraditório.

## Protocolo

### Rodada 0 — Enquadramento
Reescreva a questão em uma frase decidível, com as opções explícitas e o que está em jogo.
Se a questão não for decidível (vaga, múltipla, ou já respondida), **pare e devolva ao usuário**.
Registre também: qual informação está faltando e como cada cadeira deve tratar essa lacuna.

### Rodada 1 — Pareceres cegos (independência)
Cada participante responde **sem ver os pareceres dos outros**. Este é o ponto do mecanismo:
opiniões em sequência viram eco por ancoragem, e você paga N vezes pela mesma opinião.

Cada parecer traz, no máximo em ~200 palavras:
- **Posição** — o que faria, sem hedge
- **Razão** — o modelo/heurística própria que sustenta (do `heuristics.md`/`beliefs.md` do clone)
- **O que me faria mudar de ideia** — a evidência que derrubaria a posição

Gate Art. IV: o clone fala **só** do que está nos seus arquivos. Fora do círculo de competência
→ registrar literalmente "difícil demais, passo" e sair da questão. Parecer fabricado invalida a mesa.

### Rodada 2 — Confronto
Cada participante vê os outros pareceres e responde **apenas onde discorda**, endereçando o
argumento do outro (não repetindo o próprio). Quem não discorda de nada, cala — silêncio é dado.

### Rodada 3 — Inversão (Munger)
Munger fecha: **como esta decisão fracassa catastroficamente?** Lista os modos de falha e o que
tornaria cada um impossível. Roda mesmo que Munger tenha passado na Rodada 1.

### Veredito (Orion sintetiza)
**Não é votação.** Maioria de clones não é evidência — três clones concordando podem só
compartilhar o mesmo ponto cego. A síntese expõe:

- **Consenso** — onde a mesa convergiu, e se convergiu por razões iguais ou diferentes
  (convergência por razões diferentes é forte; por razão idêntica é um único argumento repetido)
- **Dissenso irreconciliável** — onde não houve acordo, nomeando quem defende o quê. **Não resolver
  à força.** Dissenso preservado é o produto mais valioso da mesa
- **Recomendação** — uma, com a condição que a derrubaria
- **Modos de falha** — da Rodada 3, com mitigação
- **O que decidiria isso de vez** — o teste/dado que encerraria o dissenso

## Modos de execução

| Modo | Como roda | Independência | Custo | Quando |
|---|---|---|---|---|
| `solo` (padrão) | Orion carrega os arquivos de cada clone e escreve os pareceres em sequência | **Parcial** — ver limitação abaixo | Baixo | Maioria dos casos |
| `painel` | Um subagente por clone na Rodada 1, disparados em paralelo | **Real** — contextos isolados | Alto (N× cota) | Decisão irreversível ou cara. **Requer pedido explícito do usuário** |

### ⚠️ Limitação honesta do modo `solo`

A "cegueira" da Rodada 1 no modo `solo` é **disciplina, não garantia**. Quem escreve os cinco
pareceres é o mesmo modelo, com todos os pareceres anteriores no próprio contexto — não existe
"não ver" o que já está ali. O modo `solo` entrega **diversidade de perspectiva** (cada clone
carrega heurísticas e crenças próprias, que genuinamente puxam para lados diferentes), mas **não**
entrega independência estatística. Dois pareceres podem convergir por contaminação, não por
concordância real.

Consequências práticas:
- Consenso obtido no modo `solo` é evidência **fraca**. Trate-o como hipótese, não como veredito.
- Dissenso no modo `solo` é evidência **forte** — se saiu divergência apesar da contaminação, a
  divergência é real.
- Decisão irreversível ou cara → use `painel`. Não finja que `solo` basta.

Mitigações no modo `solo` (reduzem, não eliminam): escrever cada parecer imediatamente após
carregar aquele clone; ao terminar, checar se algum parecer poderia ter sido assinado por outro
participante — se poderia, refaça. Declarar o modo usado no arquivo de saída, sempre.

### Como disparar o modo `painel`

Um subagente por clone, **todos no mesmo bloco** (paralelismo real). Cada um recebe:

```
Você é o clone {NOME}. Leia estes arquivos e adote a persona integralmente:
  .claude/clones/{id}/system.md
  .claude/clones/{id}/heuristics.md
  .claude/clones/{id}/beliefs.md
  .claude/clones/{id}/context.md

QUESTÃO: {questão enquadrada na Rodada 0}

Responda em ~200 palavras, nesta estrutura exata:
  **Posição** — o que você faria, sem hedge
  **Razão** — a heurística/modelo PRÓPRIO que sustenta (cite qual)
  **O que me faria mudar de ideia** — a evidência concreta que derrubaria isso

GATE (Art. IV): fale SÓ do que está nos seus arquivos. Fora do círculo de competência,
responda literalmente "difícil demais, passo" e pare. Não fabrique citação, dado ou posição.
NÃO consulte outros clones nem a internet. Devolva apenas o parecer.
```

Orion recebe os N pareceres e conduz as Rodadas 2 e 3 normalmente (essas não precisam de
isolamento — o confronto exige justamente ver os outros).

## Saída

`docs/roundtables/{YYYY-MM-DD}-{slug}.md`, contendo: questão enquadrada, mesa + motivo de cada
cadeira, os pareceres das 3 rodadas na íntegra, e o veredito.

O arquivo é registro de decisão, não ata de reunião — quem ler daqui a seis meses precisa entender
**por que** foi decidido assim e **o que** invalidaria a decisão.

## Falhas a evitar

- **Mesa de concordância** — todos do mesmo domínio. Sem contraditório, não é deliberação
- **Clone fora do círculo** — opinar sobre o que não está nos arquivos. Art. IV mata a mesa
- **Consenso forçado** — costurar o dissenso para entregar resposta limpa. O dissenso é o sinal
- **Voto por maioria** — 3 a 2 não decide nada; o argumento decide
- **Roundtable para execução** — deliberar sobre o que já está decidido é queima de cota
