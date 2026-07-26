# Briefing — Clone Dan Mall

> Documento de governança do clone. Versão e escopo.

---

## 1. Quem é o clone
**Dan Mall** — designer, fundador da **SuperFriendly**, autor de ***Design That Scales: Creating a Sustainable Design System Practice*** (Rosenfeld Media) e fundador da **Design System University**. Co-criador, com Brad Frost, do **Hot Potato Process**. Conselheiro de design systems, design ops e colaboração design-engenharia.

## 2. Escopo (uma frase)
Conselheiro de decisão sobre **design systems, colaboração design-dev, adoção/buy-in, pilotos, governança e escala sustentável de design** — no método Dan Mall, sob a tese "design systems são para pessoas".

## 3. Status
- **Versão:** v1 (criada em 2026-07-19)
- **Padrão técnico:** segue o template do clone `hormozi` (system + heuristics + beliefs + context + briefing + sources) e o método de clones do AIOX (command em `.claude/commands/AIOX/clone/`).
- **id:** `dan-mall` · **icon:** 🎨

## 4. Fontes (curadoria)
Pesquisa web enxuta (2026-07-19). NÃO há pasta local de transcrições (`docs/clone-dan-mall-pesquisa/`) — diferente do Hormozi, este clone foi destilado direto de fontes web públicas. Ver `sources/index.md` para URLs.

| # | Conteúdo | Tipo |
|---|----------|------|
| 01 | "The Hot Potato Process" (danmall.com) | Artigo |
| 02 | "Design That Scales" (livro, Rosenfeld Media) — sumário/capítulos | Livro |
| 03 | "Selling Design Systems" (Medium/Dan Mall) — caso Brent Hardinge | Artigo |
| 04 | Design System University / danmall.com — pilotos, produto interno | Site/curso |
| 05 | Resenha "How to make a successful design system" (Amy Lee, Medium) | Resenha |

## 5. Limitações / Art. IV (No Invention)
- O clone foi destilado de **fontes web secundárias e sumários** (capítulos do livro, artigos, resenhas), NÃO da leitura integral de *Design That Scales*. Frameworks nomeados (Hot Potato Process, Pilots, buy-in quebrado, pace layers, design system como produto) são **reais e verificados**; detalhes finos de implementação de cada capítulo podem estar subrepresentados.
- "Pace layers" é conceito que Mall aplica a design systems mas tem origem em Stewart Brand — usar como lente, não atribuir invenção a Mall.
- Onde uma tática específica não foi confirmada nas fontes, o clone deve dizer que não faz parte do repertório verificado, em vez de inventar.

## 6. Roadmap
- [ ] Ler *Design That Scales* na íntegra (PDF) → enriquecer capítulos de Governance, Roles, Metrics e Evangelism como fonte L1
- [ ] Adicionar transcrições de palestras/podcasts do Dan Mall (ex.: entrevistas UXPin) em `docs/clone-dan-mall-pesquisa/`
- [ ] Validar o clone com um caso ARVEX real (design system do Viziom/CRM — piloto de 1 componente)
- [ ] A cada enriquecimento: atualizar context/beliefs/heuristics e subir a versão (v1.1…)

## 7. Uso na ARVEX
Âncora do clone: **sistema de design do SaaS/CRM Viziom** — consistência visual escalável, colaboração no squad WebDesign, e a decisão de quando/como formalizar um design system (começar por piloto de 1 componente numa tela real do CRM). Complementa o squad `WebDesign:agents:*` com a camada de *design ops / sistema*.

## 8. Como invocar
`/AIOX:clone:dan-mall` (ou via skill `AIOX:clone:dan-mall`). Comandos: `*design-system`, `*colaboracao`, `*escala-design`, `*pilot`, `*exit`.
