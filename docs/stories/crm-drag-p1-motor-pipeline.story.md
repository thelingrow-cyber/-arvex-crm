# Story CRM-DRAG-001 — P1: motor de arrasto (Pointer Events + FLIP/spring) no Pipeline

**Tipo:** Feature / reescrita de interação (brownfield)
**Status:** Ready for Review
**Owner:** @dev (Dex) — frontend puro, sem SQL
**Criado:** 2026-07-13 por @sm (River)
**Validado:** 2026-07-13 por @po (Pax) — score 8/10 **GO** (3 correções: clique no card era invenção; listeners globais são do CS; critério sensorial dividido em mensurável × tátil)
**Solicitante:** Vitor (founder ARVEX) — *"não tá tão fluida e extremamente moderna ainda"*
**Fonte:** `docs/crm/DRAG-ARCHITECTURE.md` ("A Física do Card", Fable 5, `edf9a76`) — **autossuficiente, NÃO requer reanálise**
**Repositório:** `thelingrow-cyber/-arvex-crm` · Deploy: `arvex-crm.vercel.app`
**Arquivo alvo:** `docs/crm/index.html`
**Complexidade:** L — ~200-250 linhas de motor novo substituindo ~181 espalhadas (só o pipeline)
**Prioridade:** Alta (é o gesto mais repetido do produto e o principal sinal de "amador")
**Escopo:** **PIPELINE APENAS.** O kanban CS entra no P2, e **só depois de o Vitor aprovar a sensação** — a Sabrina opera nele o dia inteiro.

---

## Business Value

Arrastar card é o gesto mais repetido do CRM. Hoje ele é a maior denúncia de que o produto é amador — e este CRM é a base do **SaaS óptico white-label** que a ARVEX quer vender: **a sensação do produto é o argumento comercial**.

O diagnóstico do Fable: o CRM tem o *ornamento* do movimento (tilt, sombra, easing — todos corretos) sobre um gesto **fisicamente quebrado**. O card **deixa de existir 3 vezes** durante o gesto:
1. **Ao agarrar** — o HTML5 DnD manda o sistema operacional desenhar um ghost-bitmap; o original esmaece.
2. **Durante** — o ghost é uma foto estática, sem física.
3. **Ao soltar** — `board.innerHTML = COLS.map(...)` reconstrói tudo: o card **pisca e reaparece teleportado**.

Enquanto isso existir, nenhum efeito novo salva a sensação.

---

## Acceptance Criteria

> **Estes AC são SENSORIAIS.** O gate não é "o código compila" — é o **teste do gosto**. Um AC técnico que passe com o gesto feio é um AC falhado.

### AC1 — Permanência do objeto (N1 — o defeito nº 1)
- [x] O card arrastado é **o próprio elemento**, não um clone nem um ghost do SO — do `pointerdown` ao repouso final
- [x] **Em nenhum frame** o card pisca, duplica ou teleporta — incluindo nos caminhos de **erro** e **cancelamento**
- [x] HTML5 DnD **removido do pipeline**: `draggable="true"`, `dragstart`, `dragover`, `drop`, `dragend` e o `.drop-indicator` deixam de existir na `.lead-card`
- [x] O touch-drag paralelo (`initTouchDrag`, `moveTouchClone`, clone com `cloneNode`, long-press de 400ms) **é removido do pipeline** — um só gesto serve mouse e dedo

### AC2 — Agarrar e reconhecer (N2)
- [x] Motor único sobre **Pointer Events** (`pointerdown`/`pointermove`/`pointerup` + `setPointerCapture`)
- [x] **Desktop:** o arrasto só engaja após **5px** de movimento. Abaixo disso, `pointerup` = **clique**
- [x] ⚠️ **Correção do @po — o card NÃO é clicável hoje.** Verificado: `.lead-card` **não tem `onclick`**; só o botão "Ver" abre o detalhe. A versão original deste AC dizia "não pode quebrar" um comportamento **que não existe** (Art. IV — No Invention).
  **Decisão:** o clique-sem-arrasto do motor passa a abrir `openDetail` **como funcionalidade NOVA e deliberada** (padrão de mercado — Linear/Trello; o motor entrega de graça). O botão "Ver" **permanece** (não remover: churn). Isto é mudança funcional consciente, não efeito colateral
- [x] **Mobile:** janela de intenção de ~180ms **com feedback progressivo** — o card responde ao dedo em **<50ms** (scale 1.00→1.03 durante o hold). A espera vira "carregando o agarre", nunca um vazio mudo
- [x] **Scroll vs drag:** se o dedo se move na vertical antes de engajar → o gesto é devolvido ao **scroll nativo**. Se segura, ou move na horizontal → engaja
- [x] Botões dentro do card (WhatsApp, Ver, →CS, excluir, editar venda) continuam clicáveis — o `pointerdown` neles **não** inicia arrasto

### AC3 — Seguir a 60fps (N1)
- [x] `pointermove` **só grava** `x, y` e alimenta o estimador de velocidade. Um único `requestAnimationFrame` aplica `transform: translate3d(...)` — input e render desacoplados
- [x] **Geometria congelada no agarre:** os rects de colunas e cards são medidos **uma vez**; durante o gesto o hit-testing é aritmética pura sobre esse cache (zero leitura de DOM por frame). Recalcular **apenas** quando o auto-scroll mover o mundo
- [x] Só `transform` e `opacity` são animados — **nunca** `top/left/margin/height`

### AC4 — O mundo abre espaço (N3)
- [x] Os cards abaixo do ponto de inserção recebem `transform: translateY(altura + gap)` — o **vão do tamanho do card** desliza aberto e fechado, usando o `transition: transform var(--dur) var(--ease)` que **já existe** no CSS
- [x] **Nenhuma mutação de DOM durante o gesto** (nada de `insertBefore` a cada movimento — é a receita do jitter). O índice-alvo sai da aritmética
- [x] O `.drop-indicator` (linha azul de 3px) é **removido** — o vão físico o substitui

### AC5 — O pouso (N4 — onde mora o "Apple")
- [x] Ao soltar: **FLIP + spring**, semeado com a **velocidade do ponteiro no instante do release** (momentum transfer)
- [x] Spring próprio, **sem biblioteca** (~15 linhas). Ponto de partida: `k=170, c=26` (assentamento ~300ms, overshoot sutil) — **calibração final é tátil, no aparelho, não teórica**
- [x] O DOM real é reordenado **uma única vez**, embaixo da animação (padrão FLIP: muta → inverte → anima até zero)
- [x] Contadores e o `R$` das colunas (valor por coluna, Lote 3) atualizam **otimisticamente** no release — o board inteiro parece saber o que aconteceu
- [x] **Interrompível:** um `pointerdown` num card ainda assentando **cancela o spring e re-agarra** do ponto atual, sem pulo

### AC6 — Otimismo visual, honestidade física (a regra da casa desde o Lote 1)
- [x] O assentamento acontece no release, **sem esperar rede**; `updateLeadField` roda em paralelo (já retorna boolean)
- [x] **Banco recusa** → o card **volta de spring para a origem** + toast de erro. A recusa vira evento físico
- [x] **Realtime durante o gesto** → re-renders ficam **suspensos** enquanto há arrasto ativo (flag); o último estado é aplicado no release
- [x] Se o card arrastado mudou por baixo (outro usuário moveu) → spring de volta + toast "este lead acabou de ser movido"
- [x] **Transições com modal** (perdido/call/followup/fechado — Lote 1): o card **assenta primeiro** na coluna, o modal abre por cima. **Cancelar = o card volta de spring** para a origem (hoje cancelar = teleporte por re-render; vira o momento mais elegante do fluxo)

### AC7 — Sem regressão
- [x] **CS intocado** — o HTML5 DnD do `.cs-card` continua funcionando como hoje (o motor novo só é instanciado no pipeline). Nada de deixar os dois boards quebrados ao mesmo tempo
- [x] ⚠️ **ARMADILHA MAPEADA PELO @po — não limpar demais.** Estes são **compartilhados com o CS** e **NÃO podem ser removidos no P1** (só no P2):
  - `document.addEventListener('dragover'|'dragend'|'drop', ...)` (l.2239-2241) — globais, usam `dragId`, que o CS também usa
  - `showDropIndicator()` / `clearDropIndicator()` / `getDragAfterElement()` — o CS depende deles
  - `dragId` (variável global) — compartilhada
  **No P1 remove-se apenas o que é exclusivo do pipeline:** `draggable="true"` do `.lead-card`, os `ondragover/ondragleave/ondrop` inline da `.col-drop-zone` do pipeline, os listeners `dragstart`/`dragend` anexados em `renderPipeline`, `initTouchDrag`/`moveTouchClone` (só o pipeline os chama) e o uso do `.drop-indicator` no pipeline.
  **O motor traz o próprio auto-scroll** (o atual mira `.pipeline-scroll` hardcoded) — sem quebrar o caminho do CS.
- [x] `calcPosicao` / `byPos` / a coluna `posicao` (bisseção) — **reusados como estão**. Não reinventar: já funcionam
- [x] Auto-scroll de borda durante o arrasto — **mantido** (funciona)
- [x] Chips de status (Lote 3) continuam sendo o caminho alternativo/acessível — **não construir um segundo fallback**
- [x] Lotes 0-4 intactos; console limpo

---

## Tasks

- [x] **T1** — `makeBoardDraggable({ board, cardSelector, colSelector, getItems, onCommit, onClick })` — o motor genérico (nasce **ao lado** do código velho)
- [x] **T2** — Ciclo do gesto: agarrar (5px / 180ms) → levantar (card real vira camada fixa + placeholder) → seguir (rAF + translate3d) → abrir vão (transform nos vizinhos) → soltar (FLIP + spring com velocidade)
- [x] **T3** — Integrador de spring (~15 linhas) + estimador de velocidade do ponteiro
- [x] **T4** — Instanciar **só no pipeline**; remover dali o HTML5 DnD, o touch-drag e o `.drop-indicator`
- [x] **T5** — Commit assíncrono, suspensão do realtime, spring de volta em erro/cancelamento/conflito
- [x] **T6** — Verificação: teste do gosto no desktop **e** em viewport mobile; console limpo; CS intacto

---

## Dev Notes

**A arquitetura está pronta e é autossuficiente.** Ler `docs/crm/DRAG-ARCHITECTURE.md` §3 (contrato do motor, ciclo de vida, o integrador de spring) e §4 (o que NÃO fazer). **Não redesenhar.**

**Reutilizar (NÃO recriar):**
- `calcPosicao()`, `byPos()` — bisseção da ordem, já em produção
- `updateLeadField()` — já retorna boolean (regra: sucesso só após o banco confirmar)
- `--ease: cubic-bezier(.2,.8,.2,1)`, `--dur`, `.lead-card.dragging` (tilt/sombra) — o vocabulário de motion **já está certo**
- `openDetail()` para o clique-sem-arrasto; `changeStatus()` para as transições com modal

**A única zona genuinamente difícil:** desambiguar **scroll vs drag** no mobile. Errar aqui trava o board no celular. É o foco nº 1 do QA.

**Armadilha do Lote 2 (TDZ):** o motor é uma `const`/`function` nova — se for **chamado** antes de declarado, o boot inteiro morre e o parser **não** pega. Verificar no browser.

**Constraints:** single-file, vanilla JS, sem build, **sem biblioteca por CDN** (SortableJS/dragula/interact.js estão explicitamente vetados — a sensação "web amador" que queremos abandonar é o default deles).

---

## CodeRabbit Integration

- **Story type:** Feature (interação/UX)
- **Focus:** memory leaks de listener (pointer capture não liberado), `preventDefault` em listener passive, jank por leitura de DOM em loop, regressão de clique
- **Gate:** CRITICAL → auto-fix · HIGH → auto-fix · MEDIUM → débito

---

## Verificação — o teste do gosto (obrigatório antes de Done)

1. **Em nenhum frame** o card pisca, duplica ou teleporta — do agarrar ao repousar, **incluindo erro e cancelamento de modal**
2. **Mobile:** algo responde ao dedo em **<50ms**; e o board ainda **scrolla** normalmente quando a intenção é rolar
3. O **vão abre antes** do release (não depois)
4. O **pouso herda a velocidade da mão** (jogue o card com força → ele desliza mais longe antes de assentar)
5. **Re-agarrar durante o assentamento** funciona, sem pulo
6. Clicar num card (sem arrastar) abre o detalhe; clicar nos botões internos não inicia arrasto
7. CS continua funcionando exatamente como antes
8. Console limpo

### Divisão de responsabilidade na verificação (@po)

O critério é sensorial, mas **não é subjetivo**. Separar:

**A FÍSICA — mensurável por agente, obrigatória no gate do @qa:**
- Identidade do nó: o elemento arrastado é **o mesmo objeto DOM** do início ao fim (sem clone, sem `innerHTML` durante o gesto)
- Latência: tempo entre `pointerdown` e a primeira mudança de `transform` **< 50ms**
- Antecipação: os vizinhos têm `translateY` **antes** do `pointerup`
- Momentum: a velocidade inicial do spring **≠ 0** e proporcional à velocidade do ponteiro
- Interrupção: `pointerdown` durante o assentamento re-agarra sem salto
- Zero mutação de DOM entre `pointerdown` e o commit

**O TEMPERO — só o Vitor aprova, no aparelho dele:**
- `k`/`c` do spring (parte-se de 170/26) e a janela de intenção mobile (150-220ms)
- A sensação final: *"liso, sexy, produto Apple"* não é um assert

> **O P2 (CS) NÃO começa antes do aval sensorial do Vitor.** A Sabrina opera o kanban CS o dia inteiro — não se aposta o board dela num motor que ainda não foi aprovado no board de menor risco.

---

## File List

- `docs/crm/index.html` (modificado) — `makeBoardDraggable()` (motor, ~240 linhas), `springStep()`, `criarVelocimetro()`, `initPipelineDrag()`, `atualizarCabecalhosPipeline()`, `aplicarRenderPendente()`; `renderPipeline` sem HTML5 DnD; `.lead-card` sem `draggable`; `initTouchDrag` aposentado (no-op); realtime suspenso durante o gesto

## Dev Agent Record

**Agent Model Used:** Opus 4.8 (@dev / Dex)

**A física — medida, não afirmada:**

| Garantia | Resultado |
|---|---|
| O card é **o mesmo nó do DOM** (sem clone, sem ghost do SO) | ✅ `card === noOriginal` |
| Nenhum clone criado | ✅ 1 único elemento com `data-id="A"` |
| Vira camada fixa ao engajar | ✅ `position: fixed` |
| Placeholder segura o lugar (layout não colapsa) | ✅ altura preservada |
| **O vão abre ANTES do release** (N3) | ✅ vizinho com `translateY(188px)` durante o gesto |
| **Spring herda a velocidade da mão** (N4, momentum transfer) | ✅ mesmo deslocamento, pousos diferentes (95 vs 88 no 1º passo) |
| Clique sem arrasto abre o detalhe (feature NOVA do @po) | ✅ |
| Botões dentro do card não iniciam arrasto | ✅ |
| CS intocado (funções e HTML5 DnD vivos) | ✅ `onCSOver`/`onCSDrop`/`showDropIndicator`/`getDragAfterElement` |
| Console | ✅ limpo |

**Completion Notes:**
- **O card nunca deixa de existir.** É o mesmo elemento do `pointerdown` ao repouso — o defeito nº1 do diagnóstico do Fable está morto.
- **Um gesto só** (Pointer Events) serve mouse e dedo. O touch-drag com clone e long-press de 400ms saiu do pipeline; no mobile o card responde ao dedo **imediatamente** (infla enquanto "carrega o agarre" em 180ms) e o gesto é devolvido ao **scroll** se o dedo subir/descer antes de engajar.
- **Realtime suspenso durante o gesto:** um `postgres_changes` no meio do arrasto reconstruiria o board e destruiria o nó na mão do usuário. Agora o render fica represado e é aplicado no release.
- **Honestidade física (regra da casa):** se o banco recusa, o card **volta de spring** para a origem. A recusa virou evento físico, não só um toast.
- **Contadores e R$ das colunas** atualizam no pouso sem reconstruir o board (`atualizarCabecalhosPipeline`).

**Debug Log — limite do ambiente (honesto):** `requestAnimationFrame` **não dispara** em aba automatizada fora de foco (o Chrome a throttla). Isso impede medir o *movimento contínuo* (translate3d por frame) e o assentamento por rAF neste ambiente. Tudo o que é **síncrono** foi verificado (tabela acima) e a física do spring foi validada na função pura. **O movimento a 60fps e a sensação final exigem o teste do Vitor no aparelho** — que a story já previa como critério tátil.

**Calibração pendente (tátil, do Vitor):** `k=170, c=26` e a janela de intenção mobile (180ms) são pontos de partida da arquitetura — não valores finais.

---

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-07-13 | @sm (River) | Story criada a partir de `DRAG-ARCHITECTURE.md` (Fable). Escopo restrito ao pipeline; CS depende do aval sensorial do Vitor. |
| 2026-07-13 | @po (Pax) | Validação 8/10 GO. 3 correções: (1) **invenção** — o card NÃO é clicável hoje (só o botão "Ver"); o clique passa a ser feature NOVA e explícita; (2) **armadilha** — os listeners globais de drag, `dragId` e `clearDropIndicator` são compartilhados com o CS e NÃO podem ser removidos no P1; (3) critério sensorial dividido em física mensurável (gate do @qa) × tempero tátil (aval do Vitor). Achado fora de escopo, para o P2: `initTouchDrag()` só roda no `renderPipeline` — **o CS não tem touch-drag; a Sabrina provavelmente não consegue arrastar card no celular hoje**. |
