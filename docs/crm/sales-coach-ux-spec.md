# UX/UI Spec — Sales Coach (aba "Coach") · arvex-crm

**Autor:** @ux-design-expert (Uma) · Data: 2026-06-27 · Refs: brief + architecture + `design-direction.md`
**Regra de ouro:** herdar 100% o design system do CRM (Linear/Attio). Acento = índigo `--blue #5B6CFF`; dourado **reservado à marca** (não espalhar); **status = dot 8px + label**, nunca fundo colorido; ícones Lucide via helper `icon()`; raio 8px cards / 6px inputs; transições `--dur ease`. Mobile-first.

---

## 1. Entrada no menu + gating
- **Seção:** "Comercial" (junto de Dashboard/Pipeline/Leads).
- **Item nav:** `nav-coach` → `view-coach`, label **"Coach"**, ícone Lucide **`graduation-cap`** (identidade de evolução/coaching; distinto do `headset` do CS).
- **Navegação:** reusa `goTo('coach', el)`.
- **Gating (`applyRole`):**
  - `closer` / `sdr`: vê a aba, **só as próprias reuniões** (RLS garante no banco; UI esconde filtro de closer).
  - `admin` (Vitor): vê **todas**, com filtro por closer.
  - `cs`: **não vê** (esconder `nav-coach`).

---

## 2. Tela LISTA (`view-coach`)
Cabeçalho de página (padrão CRM): título "Coach" 20/700 + subtítulo `--text-2` "Análise das suas reuniões" + botão primário **`+ Nova reunião`** (índigo) à direita.

**Barra de filtros** (chips/inputs discretos): busca por cliente · resultado (todos/ganhou/perdeu/aberto) · período · [admin] closer.

**Cards de reunião** (grid responsivo, `--surface-1`, raio 8px, hover `--surface-2`):
```
┌────────────────────────────────────────────────┐
│ Marília · Consultoria              ● Ganhou  7.4 │  ← dot verde + label; nota tabular-nums
│ 24/06 · Closer: João                            │  ← meta --text-3
│ ────────────────────────────────────────────── │
│ ● Analisado            R$ 12.000   [ Ver call ] │  ← status dot done; ticket se ganhou
└────────────────────────────────────────────────┘
```
- **Resultado** = dot + label: `Ganhou` (verde `--green`), `Perdeu` (vermelho `--red`), `Aberto` (cinza `--text-3`).
- **Status da análise** = dot + label: `Pendente` (info `--info`), `Analisando…` (âmbar `--orange`, dot pulsa), `Analisado` (verde), `Erro` (vermelho).
- **Nota geral**: número 22/700 tabular-nums; cor sutil por faixa (≥7 verde / 5–6,9 dourado / <5 vermelho) — só o número, sem caixa.
- Card **não** abre detalhe se status≠done → mostra "Analisando…" no lugar de "Ver call".

**Empty state:** ícone `graduation-cap` grande `--text-3` + "Nenhuma reunião ainda" + "Suba a transcrição da sua primeira call e receba a análise." + botão `+ Nova reunião`.

**Demo mode (`?demo=1`)** — ver [[feedback_demo_mode_pattern]]: injeta 3–4 reuniões fictícias (1 ganha nota alta, 1 perdida nota baixa, 1 em análise) pra validar layout sem dados reais. Banner discreto "Modo demonstração".

---

## 3. Modal NOVA REUNIÃO (upload)
Modal `--surface-2`, raio 8px, sombra `--shadow-2`. Campos:
1. **Transcrição** — textarea grande (obrigatório), placeholder "Cole aqui a transcrição da reunião (do Meet, Tactiq, etc.)".
2. **Cliente** — input texto.
3. **Produto apresentado** — input texto.
4. **Data da reunião** — date.
5. **Lead vinculado** (opcional) — select dos `leads` existentes (autocomplete por nome).
6. **Resultado** *(obrigatório)* — 3 botões-segmento: `Ganhou` · `Perdeu` · `Em aberto`. (Default nenhum → validação bloqueia envio.)
7. **Ticket** — numérico, **aparece só se Resultado = Ganhou**.

**Ação:** botão `Analisar reunião` (índigo). Ao enviar:
- insere `meetings` (status=pending) → chama Edge Function → fecha modal.
- Card aparece na lista com `Analisando…` (dot âmbar pulsando). Realtime troca pra `Analisado` quando concluir (sem refresh).

**Microcopy de validação:** "Selecione o resultado da reunião" · "Cole a transcrição para analisar".

---

## 4. Tela/Modal DETALHE DA CALL
Aberta ao clicar "Ver call" (status=done). Layout:

**Topo:** cliente · produto · data · closer · badges (resultado dot+label, ticket). **Nota geral** em destaque (número 34/700 tabular-nums com anel fino colorido por faixa).

**Notas por dimensão** (8) — lista de medidores horizontais:
```
RAPPORT              ███████████░░░  8.5
DIAGNÓSTICO          █████████░░░░░  7.0
ESCUTA               ████████░░░░░░  6.5
CONSTRUÇÃO DE VALOR  █████████░░░░░  7.0
CONTROLE             ██████████░░░░  8.0
FECHAMENTO           ██████░░░░░░░░  5.0
TRANSIÇÃO            █████████░░░░░  7.0
OBJEÇÕES             ████████░░░░░░  6.0
```
- Label 11px UPPERCASE `--text-3`; barra preenchida em `--blue` (acento único, sem arco-íris); valor tabular-nums `--text-1`.

**Insights** — 4 blocos card, cada um com ícone Lucide:
- `check` **Acertos** (3) · `x` **Erros** (3) · `help-circle` **O que faltou** (perguntas) · `lightbulb` **Sugestões práticas**.
- Itens como lista; tom construtivo.

**Ações:** [admin/dono] editar resultado/ticket (FR9) · `Reanalisar`.

---

## 5. EVOLUÇÃO DO CLOSER
Painel no topo da lista (quando é a visão do próprio closer) **ou** aba interna "Minha evolução":
- **Média por dimensão** (todas as reuniões do closer) nos mesmos medidores horizontais.
- **Tendência**: seta ↑/↓ + delta vs. período anterior (ex.: Fechamento ↑ +0,8). Calculado no front (volume pequeno).
- Frase-resumo gerada simples: "Seu ponto forte é Rapport. Foque em Fechamento."
- [admin] versão comparativa entre closers fica para a **Fase 3** (fora do MVP).

---

## 6. Microcopy & estados
- **Pendente:** "Na fila…" · **Processando:** "Analisando sua reunião… (até ~2 min)".
- **Erro** (status=error): card com dot vermelho "Erro na análise" + `erro_msg` discreto + botão **`Reanalisar`** (re-invoca a função).
- **Sucesso:** toast discreto "Análise pronta".
- Acessibilidade: foco visível ring `--blue`, contraste AA, dots sempre acompanhados de texto (não depender só de cor).

---

## 7. Componentes a reusar (nada novo)
Card, badge/dot de status, botão primário/ghost, input/select/textarea, modal, helper `icon()` — todos **já existem** no `index.html`. A aba é composição desses átomos. Único componente novo: **medidor horizontal de nota** (barra simples), trivial em CSS.

## 8. Handoff
→ **@sm (River):** quebrar em stories (lista, upload+invoke, detalhe, evolução, demo mode, estados de erro). Depois → @po valida → @dev implementa no `index.html` + Edge Function.
