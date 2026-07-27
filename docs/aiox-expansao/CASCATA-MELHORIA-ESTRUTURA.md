# Cascata de Agentes AIOX — Aprimoramento da Estrutura de Squads

> Prompt executável. Ordem de agentes desenhada para melhorar a estrutura organizacional
> (squads, agentes, cadeia de comando) respeitando Constituição, boundaries L1-L4 e autoridades exclusivas.
> Uso: rodar as fases em ordem. Cada fase entrega um artefato que alimenta a próxima.

## Princípio da cascata

**Decidir → Medir impacto → Desenhar → Governar → Especificar → Implementar → Validar → Publicar.**

O erro que esta cascata previne: começar pelo `@dev` editando arquivo. Estrutura organizacional
tem consumidores (35 agentes, 10 clones, 8 manifestos) — mexer sem análise de impacto quebra
referência silenciosamente. É o mesmo defeito que produziu os 8 clones órfãos.

---

## FASE 0 — DECIDIR (antes de construir)

**Agente:** `@cso` (Vision) — ou `/AIOX:roundtable` se houver trade-off real
**Por quê primeiro:** parte dos "defeitos" é decisão estratégica disfarçada de bug. A assimetria
de alocação (10 agentes em landing, 2 no CRM de produção) não se resolve editando arquivo — se
resolve decidindo o que a estrutura deve priorizar.

```
@cso Temos 4 defeitos estruturais mapeados nos squads. Antes de qualquer execução, priorize:
(1) squads não sabem que respondem ao c-level; (2) board sem cadeira de produto/CTO;
(3) tasks declaradas mas não executáveis nos 35 agentes; (4) alocação não segue risco —
webdesign tem 10 agentes para landing page, security tem 2 para o CRM em produção com dados
reais de clientes. Aplique a regra anti-dispersão: o que entra no ciclo e o que espera.
```

**Entrega:** fila em 3 baldes (agora / depois / não-agora) + foco único do ciclo nomeado.
**Escalar para roundtable se:** a decisão for de sacrificar squad ou fundir papéis — aí há
trade-off real e perspectivas incompatíveis. `/AIOX:roundtable {decisão} --mesa=munger,al-ries,gerber,naval`

---

## FASE 1 — MEDIR IMPACTO (o que quebra se eu mexer)

**Agente:** `@aiox-master` (Orion)
**Comando:** `*ids impact {entity-id}` para cada componente que será tocado

```
@aiox-master *ids impact squads/c-level
@aiox-master *ids impact squads/webdesign
```

**Por quê antes do design:** o IDS traça consumidores diretos e indiretos por BFS no `usedBy`.
Sem isso você descobre a dependência quebrada depois de publicar.
**Entrega:** lista de consumidores + nível de risco por mudança.
**Se o code intelligence estiver indisponível:** o próprio comando degrada com graceful fallback —
prossiga, mas registre que a análise foi parcial.

---

## FASE 2 — DESENHAR (arquitetura organizacional)

**Agente:** `@architect` (Aria)
**Por quê ela:** organograma é arquitetura de sistema e padrão de integração — escopo declarado
dela. E é ela a candidata natural à cadeira de CTO do board (defeito 2), então desenha o próprio lugar.

```
@architect Desenhe o organograma-alvo da estrutura AIOX/ARVEX resolvendo três lacunas:
(1) cadeia de comando bidirecional — hoje o c-level referencia os 7 squads 33 vezes e nenhum
squad referencia o c-level; (2) a engenharia (@dev, @qa, @architect, @data-engineer, @devops,
@pm, @po, @sm) está fora do organograma do COO, apesar de o ativo principal (Viziom/CRM) ser
100% engenharia; (3) cadeira de produto/tecnologia no board — avalie ser convocada como CTO
pelo mesmo princípio IDS que convoca o Sterling (financas) como CFO, sem criar agente novo.
Respeite: boundary L1-L4, autoridades exclusivas (@devops detém push/PR/MCP), e IDS
REUSE > ADAPT > CREATE.
```

**Entrega:** `docs/architecture/organograma-aiox-arvex.md` — diagrama, quem responde a quem,
regra de convocação (quando o CTO/CFO entra na mesa), e o que NÃO muda.

---

## FASE 3 — GOVERNAR (antes de criar qualquer coisa)

**Agente:** `@aiox-master` (Orion)
**Comando:** `*ids check {intent}` por item proposto na Fase 2

```
@aiox-master *ids check "cadeira de CTO no squad c-level"
@aiox-master *ids check "tasks executáveis para squads"
```

**Gate constitucional:** Art. IV (No Invention) + hierarquia IDS. Se a recomendação for CREATE,
exige justificativa registrada: padrões avaliados, motivo da rejeição de cada um, capacidade nova.
**Entrega:** REUSE / ADAPT / CREATE por item, com justificativa.
**Resultado esperado aqui:** a maioria deve dar REUSE ou ADAPT. Se der CREATE em tudo, o design
da Fase 2 está inflado — volte.

---

## FASE 4 — ESPECIFICAR

**Agentes:** `@pm` (Morgan) → `@po` (Pax)

```
@pm *create-epic Estrutura organizacional AIOX/ARVEX — fechamento da cadeia de comando
```
Morgan traduz o design da Fase 2 em epic com requisitos rastreáveis (FR-*/NFR-*/CON-*).
Gate do Art. IV: toda afirmação do spec rastreia a um requisito ou a um achado das fases anteriores.

```
@po *validate-story-draft
```
Pax roda o checklist de 10 pontos. **GO (≥7) ou NO-GO com correções nomeadas.**

**Entrega:** epic validado. Se NO-GO, volta ao @pm — não avance com story fraca.

---

## FASE 5 — QUEBRAR EM STORIES

**Agente:** `@sm` (River)

```
@sm *draft
```
**Entrega:** `{epicNum}.{storyNum}.story.md` em Draft, com AC testáveis e File List prevista.
**Regra:** uma story por defeito estrutural. Não empacote os quatro numa só — o gate de QA
não consegue dar verdict parcial.

---

## FASE 6 — IMPLEMENTAR

**Agente:** `@dev` (Dex)

```
@dev *develop-story
```
**Modo recomendado:** `Interactive` para edição de manifesto de agente (decisões de redação
importam), `YOLO` só se a story for puramente mecânica.
**Autoridade:** Dex pode `git add/commit` local. **NÃO** pode push nem PR.
**Obrigatório:** atualizar checkboxes e File List da story conforme conclui.

---

## FASE 7 — VALIDAR

**Agente:** `@qa` (Quinn)

```
@qa *qa-gate
```
Sete checks, verdict **PASS / CONCERNS / FAIL / WAIVED**.

⚠️ **Instrução específica para estrutura** (aprendida no QA gate de 2026-07-22): não aceitar
auto-relatório de subagente como evidência. Verificação estrutural real — contar arquivos,
conferir colisão de nome/ícone/namespace, e **rodar grep de referência cruzada nos dois sentidos**.
Foi exatamente o grep reverso que revelou os clones órfãos e a cadeia unidirecional.

**FAIL → volta ao @dev com feedback específico.** Máx 5 iterações (QA Loop), depois escala.

---

## FASE 8 — PUBLICAR

**Agente:** `@devops` (Gage) — **EXCLUSIVO**

```
@devops *push
```
Nenhum outro agente empurra. Se qualquer fase anterior tentar, é violação de autoridade.

---

## Gate de proporcionalidade (leia antes de rodar tudo)

A cascata completa é para mudança **multi-camada** — que toca vários squads, o c-level e o core.
Para escopo menor, comprima:

| Escopo | Cascata |
|---|---|
| Multi-camada (organograma, cadeia de comando, novo papel) | **Completa: 0 → 8** |
| Um squad só, sem tocar outros | 0 → 2 → 6 → 7 → 8 |
| Edição pontual de manifesto (adicionar fonte a um agente) | `@dev` direto → `@devops` |

Referência: o padrão observado é ~15% SDC completo, ~15% lite, ~80% `@dev` direto.
**Não rode a cascata inteira por hábito** — o CSO da Fase 0 existe para impedir isso.

---

## Ordem de ataque recomendada para os 4 defeitos atuais

1. **Defeito 2 (referência reversa)** — cascata lite. É edição de manifesto em 7 arquivos.
2. **Defeito 3 (cadeira de CTO)** — cascata completa. Muda o organograma e cria regra de convocação.
3. **Defeito 4 (tasks executáveis)** — **não fazer para os 35.** Fazer só para as 2-3 tasks do
   squad que for de fato usado primeiro. Antecipar é a dispersão que o CSO existe para barrar.
4. **Assimetria de alocação** — Fase 0 apenas. É decisão, e a recomendação em aberto é
   *reduzir* o webdesign, não inflar o security.
