# Briefing para o Fable — a sensação de mover cards no CRM ARVEX

> Preparado por Opus 4.8 · 2026-07-13 · **input para arquitetura, não uma spec**
> Alvo: `docs/crm/index.html` (single-file, vanilla JS, sem build) · produção: `arvex-crm.vercel.app`

---

## Por que este documento existe

O Vitor arrasta cards no pipeline e no kanban CS todo dia — é o gesto mais repetido do produto. Ele descreve a sensação atual como **"não tão fluida, não extremamente moderna"**, e quer chegar em **"liso, funcional, sexy — como produto Apple"**, com a ambição declarada de ter **a melhor mobilidade de card do mercado de CRM**.

Cinco lotes de UX foram entregues hoje (métricas honestas, modais no design system, undo, ícones, deep-link, chips). **Nenhum deles tocou no drag.** A sensação de arrastar nunca foi analisada.

---

## O estado real, medido (não narrado)

### Existem DUAS implementações de arrasto, em paralelo

| Caminho | Como funciona | Onde |
|---|---|---|
| **Desktop** | HTML5 Drag & Drop nativo (`draggable="true"`, `dragstart`/`dragover`/`drop`) | `onDragOver`, `onDrop` (pipeline) · `onCSOver`, `onCSDrop` (CS) |
| **Mobile** | Implementação própria: `touchstart` com **long-press de 400ms** → clona o card (`cloneNode`) → `position:fixed` seguindo o dedo → `elementFromPoint` no `touchend` | `initTouchDrag`, `moveTouchClone` |

Isso é ~181 linhas só no pipeline, e o CS repete a estrutura.

### O que a arquitetura atual produz

1. **No desktop, quem desenha o card arrastado é o sistema operacional.** O HTML5 DnD gera um "ghost" que a página não controla: sem física, sem inércia, cursor às vezes vira "proibido" no Windows.
2. **Os cards vizinhos não abrem espaço.** Existe um `.drop-indicator` — uma linha azul de 3px (`showDropIndicator`) — mas os cards não se deslocam para revelar o buraco.
3. **No soltar, o board inteiro é reconstruído:** `board.innerHTML = COLS.map(...)`. O card **não desliza** para o destino — ele pisca e reaparece lá.
4. **Mobile tem um caminho totalmente separado**, com long-press de 400ms antes de qualquer feedback (é o que o Vitor sente como "travado" no celular).
5. A ordenação já é resolvida (`calcPosicao`, ranking fracionário por bisseção, coluna `posicao` no banco) — **isso funciona e não precisa ser reinventado.**

### O que JÁ existe de vocabulário de movimento (reaproveitável)

```css
--ease: cubic-bezier(.2,.8,.2,1);   --dur: .18s;
.lead-card, .cs-card { transition: transform var(--dur) var(--ease), box-shadow ...; will-change: transform }
.cs-card.dragging, .lead-card.dragging { opacity:.55; transform: rotate(1.5deg) scale(1.02); box-shadow: var(--shadow-2) }
.drop-indicator { height:3px; background: var(--blue); animation: dropIn .12s var(--ease) }
```
Ou seja: já há intenção de motion — ela só não governa o gesto principal.

---

## Constraints inegociáveis

- **Single-file, vanilla JS, sem build step, sem framework.** Publicar = copiar `docs/crm/index.html` para `index.html` na raiz. Nada de npm/bundler.
- **Sem biblioteca externa por CDN** se puder ser evitado — cada dependência é superfície de risco num arquivo que roda direto no browser dos usuários.
- **Usuários reais em produção agora:** Vitor (admin), Sabrina (CS — vive no kanban), SDRs. O kanban CS **não pode quebrar**.
- **Dois boards distintos** compartilham a mesma mecânica: pipeline comercial (8 colunas) e CS (7 colunas). O que for feito precisa servir aos dois sem duplicar código.
- A persistência de ordem (`posicao`, bisseção) **já funciona** — não é o problema.
- Paleta e layout estão aprovados; a mudança é de **movimento**, não de aparência estática.

---

## As perguntas abertas (é aqui que preciso de você)

1. **O que separa, de verdade, um drag "amador" de um drag que dá prazer de usar?** Não a lista de features — a *hierarquia* do que importa: o que o dedo/olho percebe primeiro, o que é ruído, o que é assinatura.
2. **Onde mora a "sensação Apple" num kanban?** É física (spring, momentum)? É antecipação (o espaço abrindo antes de você soltar)? É a ausência de latência? É som/haptic? O que dessa lista é essencial e o que é penduricalho?
3. **Qual a arquitetura certa para um único gesto servir desktop e mobile?** Vale unificar em Pointer Events, ou há razão para manter caminhos separados?
4. **Como reconciliar movimento fluido com a realidade do banco?** O card precisa parecer instantâneo, mas a gravação é assíncrona e há realtime (outro usuário pode mover o mesmo card). Onde fica o otimismo, e o que acontece quando o banco recusa?
5. **O que este CRM pode ter que Pipedrive, Attio, Trello e Linear NÃO têm?** A ambição declarada é "a melhor mobilidade do mercado" — isso é alcançável ou é retórica? Se é alcançável, por onde?
6. **O que NÃO fazer** — que armadilhas de "modernização de drag" custam caro e entregam pouco?

---

## Contexto estratégico (pode mudar sua resposta)

- Este CRM é a **base do SaaS óptico white-label** que a ARVEX pretende vender. A sensação do produto **é** o argumento comercial.
- O CS da Sabrina roda no celular. O pipeline, no desktop.
- O time é 1 pessoa + agentes. Complexidade que exige manutenção contínua é dívida, não ativo.
