# A Física do Card — Arquitetura do gesto de arrastar no CRM ARVEX

> Fable 5 · 2026-07-13 · resposta ao `DRAG-BRIEFING.md`
> **Documento autossuficiente para execução por Opus/Sonnet — não requer reanálise.**
> Alvo: `docs/crm/index.html` · dois boards (pipeline 8 colunas, CS 7 colunas) · usuários em produção

---

## 1. O diagnóstico em uma frase

O CRM tem o **ornamento** do movimento (tilt de 1.5°, sombra, easing curado) aplicado sobre um gesto **fisicamente quebrado**. Decorar um gesto quebrado é a assinatura do amador — o olho percebe a contradição mesmo sem saber nomeá-la. O problema não é falta de polish; é que o card **deixa de existir** três vezes durante o gesto.

## 2. A hierarquia do que o dedo e o olho percebem

Não é uma lista de features. É uma ordem de percepção — e cada nível só importa se o anterior estiver resolvido:

**N1 — Permanência do objeto.** O card que você segura tem de ser **o card**, continuamente, do agarrar ao repousar. Hoje ele morre três vezes: no agarrar (o SO desenha um ghost-bitmap e o original esmaece), durante (o ghost é uma foto estática, sem vida), e no soltar (`board.innerHTML = ...` — o card pisca e **reaparece teleportado**). Enquanto isso acontecer, nenhum spring salva a sensação. *É o defeito nº 1 e a fundação de tudo.*

**N2 — Reconhecimento imediato do toque.** No mobile, os 400ms de long-press são um vazio onde nada responde — o cérebro lê "travado". A solução não é remover a espera (ela desambigua scroll de drag); é **preenchê-la**: o card responde ao dedo desde o milissegundo zero, inflando progressivamente (scale 1.00→1.03) durante o hold. A espera vira "carregando o agarre" em vez de "nada aconteceu".

**N3 — O mundo abre espaço.** A linha azul de 3px é uma *anotação simbólica*; um **vão do tamanho do card** é um *fato físico*. Quando os vizinhos deslizam para abrir o buraco, o cérebro entende "existe um lugar real para isto" antes de você soltar. É o upgrade mais visível de todos.

**N4 — O pouso.** É aqui que mora o "Apple". O momento de soltar é a despedida do gesto — se o card **desliza para o slot com a velocidade que a sua mão tinha**, o objeto está vivo; se ele pisca para a posição, tudo o que veio antes foi teatro. Detalhe decisivo e quase inexistente na web: **injeção de velocidade** — a velocidade do ponteiro no instante do release vira a velocidade inicial do spring de assentamento.

**N5 — Tempero.** Tilt, rampa de sombra, cursor, haptics. **Já existe e está certo** (o CSS atual acertou o vocabulário). Não mexer. Haptics/som na web são penduricalho (Vibration API não funciona no iOS Safari) — descartar.

> **Onde mora a "sensação Apple", então?** Não é um efeito. São três princípios do próprio manual de interfaces fluidas da Apple: (1) manipulação direta — o objeto rastreia o input 1:1, sem intermediário; (2) animações **interrompíveis** — você pode re-agarrar um card que ainda está assentando e ele obedece sem pulo; (3) **transferência de momentum** — o gesto e a animação são um sistema contínuo, a animação herda a física da mão. N1+N4 implementam exatamente isso.

## 3. A arquitetura: um motor, dois boards, zero bibliotecas

### 3.1 Decisão central: matar os DOIS sistemas atuais

HTML5 DnD (desktop) e o touch-drag próprio (mobile) morrem juntos. No lugar, **um único motor sobre Pointer Events** (`pointerdown/move/up` + `setPointerCapture`) — a API que unifica mouse, toque e caneta. Não existe razão técnica para manter caminhos separados; a separação atual é a causa direta de metade dos defeitos.

O fallback de acessibilidade/teclado **já existe e já está em produção**: os chips de status do Lote 3. Não construir um segundo fallback.

### 3.2 O motor (`makeBoardDraggable`) — contrato

Uma função genérica; pipeline e CS a instanciam. A persistência atual (`calcPosicao`, bisseção, `posicao`) **pluga como está** — ela é boa e não é o problema.

```js
makeBoardDraggable({
  board,                 // '#pipeline-board' | '#cs-board'
  cardSelector,          // '.lead-card' | '.cs-card'
  colSelector,           // '.col-drop-zone'
  getItems(colId),       // itens ordenados da coluna (cache existente)
  onCommit(id, colId, posicao),  // async → bool (reusa updateLeadField/updateCSField)
  onClick(id),           // clique sem arrasto (openDetail / openCSDetail)
})
```

### 3.3 O ciclo de vida do gesto

**AGARRAR.** `pointerdown` no card ≠ arrasto: cards são clicáveis. Desktop: arrasto só engaja após **5px de movimento** (abaixo disso, no `pointerup`, é clique → `onClick`). Mobile: janela de intenção de ~180ms **com feedback progressivo** (N2) — se o dedo se move verticalmente antes de engajar, o gesto é devolvido ao scroll nativo; se segura ou move horizontal, engaja (`setPointerCapture` + `preventDefault` em listener non-passive). *Esta desambiguação scroll-vs-drag é a única zona de risco real do projeto — é onde a verificação em aparelho físico é obrigatória.*

**LEVANTAR.** O card real — não um clone — vira camada fixa (`position:fixed` a partir do seu `getBoundingClientRect`), com o tilt/sombra já existentes. No seu lugar fica o vão (placeholder invisível com a mesma altura). **Geometria congelada aqui**: mede-se uma vez os rects de todas as colunas e cards; durante o gesto, hit-testing é aritmética pura sobre esse cache — zero leitura de DOM por frame (recalcular apenas quando o auto-scroll mover o mundo).

**SEGUIR.** `pointermove` só grava `x, y` e alimenta o estimador de velocidade. Um único loop `requestAnimationFrame` aplica `transform: translate3d(...)`. Input e render desacoplados = 60fps garantidos mesmo com o board pesado.

**ABRIR ESPAÇO (N3).** Nada de `insertBefore` durante o gesto — mutar DOM a cada movimento é a receita do jitter. O índice-alvo sai da aritmética; os vizinhos abaixo do ponto de inserção recebem `transform: translateY(alturaDoCard + gap)`. Como já têm `transition: transform var(--dur) var(--ease)`, o vão **desliza** aberto e fechado sozinho, de graça, com o easing da casa. O `.drop-indicator` morre.

**SOLTAR (N4).** FLIP + spring: mede-se onde o card está (camada fixa) e onde o slot está (vão); anima-se o delta com um **spring criticamente amortecido, semeado com a velocidade do release**. Sem biblioteca — o integrador é ~15 linhas:

```js
// s: deslocamento restante · v: velocidade (px/s) · k≈170 (rigidez) · c≈26 (amortecimento)
function spring(s, v, dt) { const a = -k*s - c*v; v += a*dt; s += v*dt; return [s, v] }
// no release: s = slotRect - cardRect · v = velocidade do ponteiro projetada no delta
```

O DOM real só é reordenado **uma vez**, embaixo da animação (padrão FLIP: muta, inverte, anima até zero). Contadores e `R$` das colunas atualizam otimisticamente neste momento — o board inteiro parece saber o que aconteceu.

**Interrompível:** `pointerdown` num card em assentamento cancela o spring e re-agarra do ponto atual, herdando a posição — princípio Apple nº 2.

### 3.4 A verdade do banco (pergunta 4)

**Otimismo visual, honestidade física.** O assentamento acontece no release, sem esperar rede; `onCommit` roda em paralelo (as funções já retornam bool — regra da casa desde o Lote 1: *sucesso só após o banco confirmar*).

- **Banco recusa** → o card **volta de spring para a origem** + toast de erro. A recusa vira um evento físico — o card "não aceitou ficar ali". Nenhum concorrente comunica erro assim; um toast sozinho é abstrato, um card que volta é inequívoco.
- **Realtime durante o gesto** → re-renders de realtime ficam **suspensos enquanto há drag ativo** (flag; aplica-se o último estado no release). Se o próprio card arrastado mudou por baixo (outro usuário), no release: spring de volta + toast "este lead acabou de ser movido por X".
- **Transições com modal (perdido/call/followup/fechado)** → não interromper a física: o card **assenta primeiro** na coluna, o modal do Lote 1 abre por cima; **cancelar = o card volta de spring** para a coluna de origem (hoje cancelar = teleporte por re-render — é o momento mais quebrado do fluxo atual, e vira o mais elegante).

### 3.5 O que isto pode ter que Pipedrive, Attio e Trello não têm (pergunta 5)

Resposta honesta: **"melhor do mercado" em drag de CRM web é uma barra mais baixa do que parece** — os CRMs grandes tratam kanban mobile como cidadão de segunda classe (a maioria empurra para app nativo; os web mostram spinner no drop). É alcançável, e por três diferenciais concretos, todos já desenhados acima:

1. **Momentum transfer no release** — quase ninguém na web faz; é o detalhe que registra como "vivo".
2. **Zero-blink absoluto** — por ser single-file com cache em memória, o gesto inteiro roda sem nenhuma espera de rede visível, incluindo contadores e somas. Pipedrive não entrega isso.
3. **Erro e cancelamento como física** — o card que volta de spring quando o banco recusa ou o modal é cancelado. É assinatura própria, decorrência natural da arquitetura, custo marginal zero.

O que **não** tentar para "diferenciar": multi-select drag, arrastar entre views, gestos com dois dedos. O caso de 99% é um card, uma mão. Perfeição no caso único > features no caso raro.

## 4. O que NÃO fazer (pergunta 6)

1. **Não adotar SortableJS/dragula/interact.js via CDN.** Além de violar a constraint, a sensação "web amador" que se quer abandonar é literalmente a sensação default dessas bibliotecas.
2. **Não animar propriedades de layout** (`top/left/margin/height`). Só `transform` e `opacity`. Um DOM de 235KB re-layoutando por frame é jank garantido.
3. **Não mutar o DOM durante o gesto.** Uma mutação, no commit, sob o FLIP. O resto é transform.
4. **Não adicionar ornamento novo** (parallax, blur, glow). O tempero atual está certo; o prato é que estava cru.
5. **Não manter o HTML5 DnD como "fallback".** Dois sistemas era a doença. O fallback é o chip (já no ar).
6. **Não calibrar o spring por argumento.** k e c se calibram **com o dedo no aparelho real**, uma tarde de ajuste fino. Partir de `k=170, c=26` (assentamento ~300ms, overshoot sutil) e a janela de intenção mobile entre 150-220ms — mas a decisão final é tátil, não teórica.
7. **Não fazer big-bang nos dois boards.** Pipeline primeiro (o board do Vitor — o degustador). CS um ciclo depois, quando o motor tiver um dia de uso real — a Sabrina opera nele o dia inteiro.

## 5. Forma de execução (para a squad)

- **Uma story, dois incrementos:** (P1) motor + pipeline; (P2) CS + remoção definitiva dos dois sistemas antigos. O motor nasce ao lado do código velho e o substitui board a board — nunca os dois quebrados ao mesmo tempo.
- Tamanho estimado do motor: ~200-250 linhas, substituindo ~360 espalhadas. Saldo próximo de zero em bytes; abismo em sensação.
- **Critério de aceite não é técnico, é sensorial** — o "teste do gosto": (a) em nenhum frame o card pisca, duplica ou teleporta — do agarrar ao repousar, incluindo erro e cancelamento; (b) no mobile, algo responde ao dedo em <50ms; (c) o vão abre antes do release; (d) o pouso herda a velocidade da mão; (e) re-agarrar durante o assentamento funciona. Verificação em desktop E aparelho físico, com o Vitor aprovando a sensação antes do P2.
- Riscos a vigiar no QA: a desambiguação scroll-vs-drag no mobile (única zona genuinamente difícil), o clique-sem-arrasto (cards abrem detalhe), `stopPropagation` dos botões internos dos cards, e o auto-scroll de borda (manter o atual, que funciona).

---

*A ordenação por bisseção, o vocabulário de easing e os guards de "sucesso só com banco" desta série de lotes são exatamente as fundações que este motor precisa — o trabalho de hoje não foi desperdiçado; foi o pré-requisito.*
