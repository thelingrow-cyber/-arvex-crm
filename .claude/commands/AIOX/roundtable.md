# roundtable

ACTIVATION-NOTICE: Mecanismo de deliberação multi-clone. Não é um agente com persona própria —
é Orion (@aiox-master) conduzindo uma mesa de clones. Leia o YAML e execute a task.

## COMPLETE DEFINITION FOLLOWS

```yaml
activation-instructions:
  - STEP 1: Read THIS ENTIRE FILE
  - STEP 2: Read .aiox-core/development/tasks/roundtable.md — é o protocolo executável, siga à risca
  - STEP 3: |
      Se o usuário passou a questão como argumento (/AIOX:roundtable {questão}), pule o greeting
      e vá direto para a Rodada 0 (enquadramento).
      Se NÃO passou argumento, mostre:
      1. "⚖️ **Roundtable** — mesa de deliberação multi-clone"
      2. "**Elenco:** munger 🧠 · naval 🧭 · gerber 🏗️ · hormozi 💰 · schwartz 🧲 · pittman 📊 · al-ries 🎯 · sinek 🌱 · dan-mall 🎨 · tay 🇧🇷"
      3. "**Uso:** `/AIOX:roundtable {decisão}` · mesa de 3-5, Munger é cadeira permanente"
      4. "Qual a decisão em jogo?"
      e HALT aguardando a questão.
  - CRITICAL: Rodada 1 é CEGA. Escreva o parecer de cada clone logo após carregar os arquivos
    daquele clone, sem reler os pareceres anteriores. Independência é o mecanismo inteiro —
    pareceres em cascata são a mesma opinião cobrada N vezes.
  - CRITICAL: No modo `solo`, a cegueira é disciplina e NÃO garantia (o mesmo modelo escreve
    todos os pareceres, com os anteriores no próprio contexto). Portanto: consenso em `solo` é
    evidência FRACA — trate como hipótese; dissenso em `solo` é evidência FORTE. Sempre declare
    o modo usado no arquivo de saída, e recomende `painel` quando a decisão for irreversível
    ou cara. Nunca venda `solo` como independência real.
  - CRITICAL: Art. IV (No Invention) é gate duro. Cada clone fala SÓ do que está em
    .claude/clones/{id}/. Fora do círculo de competência → "difícil demais, passo", literal.
    Nunca fabricar uma citação, um dado ou uma posição que o clone não sustenta.
  - CRITICAL: O veredito NÃO é votação por maioria. Dissenso irreconciliável é resultado
    legítimo e deve ser preservado nomeando quem defende o quê — não costure para entregar
    resposta limpa.
  - CRITICAL: Modo `painel` (subagentes paralelos) SÓ com pedido explícito do usuário — custa
    N× cota. Padrão é `solo`.
  - CRITICAL: Antes de convocar, cheque se a mesa tem contraditório real. Mesa que concorda
    confirma o que o usuário já queria ouvir — troque uma cadeira e avise.

command:
  name: roundtable
  id: roundtable
  title: Deliberação estratégica multi-clone
  icon: ⚖️
  executor: aiox-master
  whenToUse: 'Decisão estratégica com trade-off real: posicionamento, oferta, priorização entre frentes, matar ou manter um projeto, hipótese aberta que ninguém derruba sozinho. NÃO usar para pergunta factual, execução, bug, ou validação de decisão já tomada.'

args:
  - name: questão
    required: false
    description: 'A decisão em jogo. Sem ela, o comando pergunta.'
  - name: --mesa
    required: false
    description: 'Participantes explícitos (ex: --mesa=munger,naval,al-ries). Sem isso, Orion seleciona por domínio.'
  - name: --modo
    required: false
    description: 'solo (padrão, barato) | painel (subagente por clone na Rodada 1, isolamento real, N× cota)'

protocolo:
  - Rodada 0 — enquadrar a questão em uma frase decidível + opções explícitas; parar se não for decidível
  - Rodada 1 — pareceres CEGOS (posição · razão · o que me faria mudar de ideia)
  - Rodada 2 — confronto: cada um responde só onde discorda, endereçando o argumento alheio
  - Rodada 3 — inversão de Munger: como isso fracassa catastroficamente
  - Veredito — consenso · dissenso preservado · 1 recomendação com a condição que a derruba · modos de falha · o teste que decidiria de vez

saída: 'docs/roundtables/{YYYY-MM-DD}-{slug}.md'

dependencies:
  tasks:
    - .aiox-core/development/tasks/roundtable.md
  clones_dir: .claude/clones/
```

---

## Exemplos

- `/AIOX:roundtable ARVEX deve virar agência de IA nichada ou continuar co-produção de infoprodutos?`
- `/AIOX:roundtable matar o Viziom ou dobrar a aposta? --mesa=munger,naval,gerber,al-ries`
- `/AIOX:roundtable qual beachhead atacar primeiro --modo=painel`

## Relação com outros mecanismos

| Mecanismo | Papel |
|---|---|
| `roundtable` | **Decidir** — perspectivas incompatíveis convergem num veredito |
| squad `research` | **Descobrir** — falta informação. Roda ANTES da mesa, não durante |
| `wave-execute` | **Executar** — paralelizar o que já foi decidido (pendente) |
| clone individual | **Consultar** — uma perspectiva só, sem confronto |
