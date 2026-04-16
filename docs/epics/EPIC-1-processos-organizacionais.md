# EPIC-1 — Processos Organizacionais da ARVEX
**Status:** Draft
**Prioridade:** Alta
**Owner:** Vitor + Gabriel
**Criado:** 2026-03-27
**PRD de referência:** `docs/prd/arvex-prd.md` — Frente 2

---

## Objetivo do Epic

Sair do caos operacional do WhatsApp para uma operação documentada, delegável e replicável — focando primeiro nos processos que mais consomem tempo de Vitor e Gabriel.

## Problema que resolve

Toda a operação vive na cabeça dos sócios. Nada é documentado, nada é delegável. Crescer assim tem teto baixo.

## Critério de sucesso

- 100% dos processos-chave documentados em SOPs
- Trello configurado e sendo usado ativamente
- Vitor e Gabriel conseguem delegar qualquer processo com base nos documentos

---

## Stories

### Story 1.1 — Mapeamento da Operação Atual
**Como** sócio da ARVEX,
**Quero** ter um mapa completo de tudo que acontece na operação hoje,
**Para** saber exatamente o que precisa ser documentado e priorizado.

**Tarefas:**
- [ ] Listar todas as atividades recorrentes de Vitor e Gabriel
- [ ] Listar todas as atividades da equipe (Sabrina, closer, gestor de tráfego, editora, web designer)
- [ ] Classificar por frequência (diário / semanal / por lançamento)
- [ ] Identificar os 3 processos que mais consomem tempo dos sócios
- [ ] Documentar resultado em `docs/processos/mapa-operacional.md`

**Critério de aceite:** Documento com todas as atividades mapeadas, classificadas e priorizadas.

---

### Story 1.2 — SOP: Fluxo de Vendas (Lead → Fechamento)
**Como** sócio da ARVEX,
**Quero** um processo documentado de vendas do primeiro contato ao fechamento,
**Para** que qualquer pessoa (ou agente SDR) possa seguir sem depender de mim.

**Tarefas:**
- [ ] Documentar jornada completa do lead (onde chega, como é tratado, até o fechamento)
- [ ] Mapear scripts de abordagem SDR atual
- [ ] Mapear scripts de closer atual
- [ ] Documentar critérios de qualificação de lead
- [ ] Documentar objeções mais comuns e respostas
- [ ] Criar SOP em `docs/processos/sop-fluxo-vendas.md`
- [ ] Configurar quadro no Trello: **Pipeline de Vendas**

**Critério de aceite:** SOP completo do fluxo de vendas + quadro Trello configurado.

> **Nota:** Este SOP será a base para o Agente SDR (Epic 2).

---

### Story 1.3 — SOP: Ciclo de Lançamento
**Como** sócio da ARVEX,
**Quero** um processo documentado para executar um lançamento completo,
**Para** que a operação de lançamento seja replicável para qualquer expert parceiro.

**Tarefas:**
- [ ] Documentar todas as etapas de um lançamento (pré, durante, pós)
- [ ] Mapear responsáveis por cada etapa (quem faz o quê)
- [ ] Documentar ferramentas utilizadas em cada etapa
- [ ] Criar checklist de lançamento
- [ ] Criar SOP em `docs/processos/sop-ciclo-lancamento.md`
- [ ] Configurar quadro no Trello: **Lançamentos**

**Critério de aceite:** SOP de lançamento completo com checklist + quadro Trello configurado.

---

### Story 1.4 — SOP: Onboarding de Novo Expert Parceiro
**Como** sócio da ARVEX,
**Quero** um processo de onboarding documentado para novos experts,
**Para** integrar um novo parceiro em menos de 2 semanas sem depender só de mim.

**Tarefas:**
- [ ] Documentar etapas do onboarding (contrato, briefing, configuração, primeiro lançamento)
- [ ] Criar checklist de onboarding
- [ ] Definir materiais que o expert precisa entregar
- [ ] Definir o que a ARVEX entrega nas primeiras 2 semanas
- [ ] Criar SOP em `docs/processos/sop-onboarding-expert.md`
- [ ] Configurar quadro no Trello: **Onboarding Experts**

**Critério de aceite:** SOP completo de onboarding + checklist + quadro Trello configurado.

---

### Story 1.5 — SOP: Gestão Semanal da Operação
**Como** sócio da ARVEX,
**Quero** uma rotina semanal documentada para gerir a equipe e a operação,
**Para** ter visibilidade do que está acontecendo sem precisar ficar no WhatsApp o dia todo.

**Tarefas:**
- [ ] Definir cadência de reuniões (diária rápida, semanal de equipe)
- [ ] Criar template de reunião semanal
- [ ] Definir métricas semanais a acompanhar (leads, vendas, tráfego)
- [ ] Criar SOP em `docs/processos/sop-gestao-semanal.md`
- [ ] Configurar quadro no Trello: **Gestão Semanal**

**Critério de aceite:** Rotina semanal documentada + template de reunião + métricas definidas.

---

### Story 1.6 — Trello: Configuração Final e Ativação
**Como** sócio da ARVEX,
**Quero** o Trello completamente configurado com todos os quadros dos SOPs,
**Para** ter uma central de operação visual e funcional.

**Tarefas:**
- [ ] Revisar todos os quadros criados nas stories anteriores
- [ ] Criar quadro **Equipe & Tarefas** (gestão do time)
- [ ] Criar quadro **Experts Ativos** (status Cindy e Alex)
- [ ] Configurar automações básicas no Trello (Butler)
- [ ] Documentar guia de uso do Trello para Vitor e Gabriel
- [ ] Fazer sessão de uso com Gabriel para alinhar adoção

**Critério de aceite:** Trello completo, funcional e ambos os sócios usando ativamente.

---

## Estrutura de Arquivos Gerada por Este Epic

```
docs/
├── epics/
│   └── EPIC-1-processos-organizacionais.md
└── processos/
    ├── mapa-operacional.md        (Story 1.1)
    ├── sop-fluxo-vendas.md        (Story 1.2)
    ├── sop-ciclo-lancamento.md    (Story 1.3)
    ├── sop-onboarding-expert.md   (Story 1.4)
    └── sop-gestao-semanal.md      (Story 1.5)
```

---

## Dependências

- **Bloqueia:** Epic 2 (Agente SDR) — precisa do SOP de vendas (Story 1.2) antes
- **Independente de:** Epic 3 (Web Designer), Epic 4 (Mentoria ARVEX)

## Estimativa

6 stories — executável em 2-3 semanas com foco de 1-2h por dia.

---

*EPIC-1 — ARVEX | Gerado via Synkra AIOX | 2026-03-27*
