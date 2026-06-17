# ESCALONAMENTO DO SQUAD — Operação "PCH Vintage"

> Plano de orquestração multi-agente para construir **o melhor site de carros
> clássicos do mundo**. Define quem faz o quê, em que ordem, com qual entregável,
> qual critério de aprovação (gate) e como o trabalho passa de um agente para o
> próximo (handoff).
>
> Framework: **Synkra AIOX** · Maestro: **@aiox-master (Orion)** · Versão 1.0 · 2026-06-16

---

## 1. Missão & Padrão de Excelência

**Missão:** entregar um site de revenda de carros clássicos que seja referência
mundial em design, experiência e conversão — dark, neon, cinematográfico, rápido
e impecável no mobile.

**Definição de "pronto" (Definition of Done) do projeto:**
- ✅ Visual de tirar o fôlego (dark/neon), 100% fiel ao briefing
- ✅ Vitrine com filtros (marca, estado, preço) e detalhe de veículo com galeria
- ✅ Mobile-first impecável (vem do link na bio do Instagram)
- ✅ Performance: Lighthouse ≥ 90 em Performance/SEO/Acessibilidade
- ✅ Todo caminho converte para contato (`contata.me/pchveiculos`)
- ✅ Dono consegue adicionar carro sozinho (editar `carros.js`)
- ✅ Zero erro de console, links e imagens validados

---

## 2. Organograma do Squad

```
                          ┌──────────────────────────────┐
                          │   @aiox-master · ORION 👑     │
                          │   Maestro / Orquestrador      │
                          │   (governança + handoffs)     │
                          └───────────────┬──────────────┘
            ┌──────────────────┬──────────┼───────────────┬──────────────────┐
            ▼                  ▼           ▼               ▼                  ▼
   ┌────────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
   │ DESCOBERTA     │ │ ESTRATÉGIA   │ │ DESIGN   │ │ ENGENHARIA   │ │ QUALIDADE &  │
   │ & PESQUISA     │ │ & CONTEÚDO   │ │          │ │              │ │ ENTREGA      │
   ├────────────────┤ ├──────────────┤ ├──────────┤ ├──────────────┤ ├──────────────┤
   │ @analyst Alex  │ │ brand-strat. │ │ creative │ │ @architect   │ │ @qa Quinn    │
   │ ux-researcher  │ │ copywriter   │ │ -director│ │   Aria       │ │ cro-analyst  │
   │                │ │ storytelling │ │ web-     │ │ @dev Dex     │ │ seo-special. │
   │                │ │              │ │ designer │ │ frontend-dev │ │ @devops Gage │
   │                │ │              │ │ motion   │ │ @data-eng    │ │ (push/deploy │
   │                │ │              │ │ -designer│ │  Dara (F2)   │ │  EXCLUSIVO)  │
   └────────────────┘ └──────────────┘ └──────────┘ └──────────────┘ └──────────────┘
```

**Dois squads combinados:**
- **AIOX Core** (engenharia, governança, QA, dados, deploy)
- **WebDesign** (estratégia de marca, criação, copy, motion, CRO, SEO, UX research)

---

## 3. Modelo de Orquestração

1. **Orion (@aiox-master)** abre cada fase, seleciona o agente executor e injeta o
   contexto mínimo necessário (handoff compacto, ~380 tokens), nunca a persona
   inteira do agente anterior — economiza contexto e mantém foco.
2. Cada agente entrega um **artefato** + um **handoff** estruturado para o próximo.
3. Entre fases há um **quality gate**: só avança quem passa.
4. **Autoridades exclusivas são respeitadas**: somente **@devops (Gage)** faz
   `git push`, `gh pr create/merge` e deploy. Nenhum outro agente publica.
5. Falha em gate → retorna ao agente responsável com feedback específico
   (loop máximo definido por fase); bloqueio crítico → escala para Orion.

---

## 4. RACI Global

> R = Responsável (executa) · A = Aprova · C = Consultado · I = Informado

| Atividade | Orion | Analyst | WebDesign | Architect | Dev | QA | DevOps |
|-----------|:-----:|:-------:|:---------:|:---------:|:---:|:--:|:------:|
| Discovery & referências | A | R | C | I | I | I | I |
| Estratégia de marca & copy | A | C | R | I | I | I | I |
| Design system & layout | A | I | R | C | C | I | I |
| Arquitetura técnica | A | I | C | R | C | I | I |
| Implementação front | A | I | C | C | R | I | I |
| Modelo de dados / backend (F2) | A | I | I | C | C | I | — |
| QA / CRO / SEO | A | I | C | I | C | R | I |
| Deploy / publicação | A | I | I | I | I | C | **R** |

---

## 5. Pipeline de Execução (fase a fase)

Cada fase segue o mesmo formato: **Objetivo → Agente → Recebe → Faz → Entrega →
Gate → Passa para**.

### FASE 0 — Orquestração & Setup  ·  @aiox-master (Orion) 👑
- **Objetivo:** consolidar briefing, definir escopo, montar este plano e abrir o board.
- **Recebe:** áudio transcrito + referências + contatos (já coletados).
- **Faz:** valida decisões (stack vanilla F1 + Supabase F2), cria `carros.js`,
  `PLANO.md`, `ESCALONAMENTO.md`, define cronograma.
- **Entrega:** plano aprovado + board de tarefas + dados-base.
- **Gate G0:** Vitor aprova o plano. ✅
- **Passa para:** Descoberta.

### FASE 1 — Descoberta & Pesquisa  ·  @analyst (Alex) + ux-researcher
- **Objetivo:** entender o público de clássicos e o que faz um site do nicho
  converter; benchmark mundial (não só as 2 referências do cliente).
- **Recebe:** briefing + referências (Païto, Armazém do Vovô).
- **Faz:** análise de concorrentes globais de carros clássicos, padrões de
  vitrine premium, jornada do colecionador, personas (colecionador, investidor,
  entusiasta), gatilhos de confiança (procedência, originalidade, história).
- **Entrega:** `research.md` (insights + personas + benchmark + recomendações).
- **Gate G1:** insights acionáveis e personas claras.
- **Handoff →** Estratégia & Conteúdo.

### FASE 2 — Estratégia de Marca & Conteúdo  ·  brand-strategist + storytelling-expert + copywriter
- **Objetivo:** posicionar a PCH e escrever toda a copy que vende clássico.
- **Recebe:** `research.md`.
- **Faz:**
  - *brand-strategist:* posicionamento ("PCH Vintage — clássicos com procedência"),
    tom de voz, big idea, hierarquia de mensagens.
  - *storytelling-expert:* narrativa do site e arco de cada veículo (a história
    vende mais que a ficha técnica — alinhado ao pedido do dono).
  - *copywriter:* headlines do hero, CTAs, textos de Quem Somos/Missão/Valores,
    microcopy, templates de "história do carro".
- **Entrega:** `copy.md` (todos os textos prontos) + guia de tom de voz.
- **Gate G2:** copy aprovada, sem invenção de fatos (Art. IV — No Invention).
- **Handoff →** Design.

### FASE 3 — Direção de Arte & Design  ·  creative-director → web-designer → motion-designer  (+ @ux-design-expert Uma)
- **Objetivo:** transformar estratégia em um design de classe mundial.
- **Recebe:** `copy.md` + `research.md`.
- **Faz:**
  - *creative-director:* conceito visual ("showroom noturno em neon"), moodboard,
    direção de arte, padrão de fotografia dos clássicos.
  - *web-designer / @ux-design-expert:* design system (tokens dark/neon),
    wireframes e layout de todas as páginas (home, estoque, veículo, sobre),
    componentes (card de carro, filtros, galeria), estados responsivos.
  - *motion-designer:* especificação de animações (hero glow, scroll reveal,
    hover dos cards, transição da galeria) — sofisticado, nunca exagerado.
- **Entrega:** `design-spec.md` + tokens + especificação de componentes e motion.
- **Gate G3:** design aprovado pelo Vitor; mobile validado; fiel ao briefing.
- **Handoff →** Arquitetura/Engenharia.

### FASE 4 — Arquitetura Técnica  ·  @architect (Aria)
- **Objetivo:** definir como construir de forma sólida e escalável.
- **Recebe:** `design-spec.md`.
- **Faz:** estrutura de arquivos, estratégia de render (cards via JS a partir de
  `carros.js`), roteamento do detalhe (`veiculo.html?id=`), plano de performance
  (lazy-load de imagens, otimização), e o **caminho de evolução para a Fase 2
  (Supabase)** sem retrabalho de modelagem.
- **Entrega:** `architecture.md` (decisões + estrutura + contrato de dados).
- **Gate G4:** arquitetura coerente, performática, evolutiva.
- **Handoff →** Implementação.

### FASE 5 — Implementação Front-end  ·  @dev (Dex) + frontend-developer
- **Objetivo:** construir o site, pixel-perfect e rápido.
- **Recebe:** `design-spec.md` + `architecture.md` + `copy.md` + `carros.js`.
- **Faz:** `index.html`, `estoque.html`, `veiculo.html`, `sobre.html`,
  `assets/style.css`, `assets/app.js` (render, filtros, galeria, fallback de foto),
  header/footer/botão flutuante, meta tags + Open Graph, favicon.
- **Entrega:** site funcional completo (Fase 1) + `README.md` de manutenção.
- **Gate G5:** roda sem erro de console; bate com o design; responsivo.
- **Handoff →** Qualidade.

### FASE 6 — Qualidade, CRO & SEO  ·  @qa (Quinn) + cro-analyst + seo-specialist
- **Objetivo:** garantir que está impecável e que converte e é achável.
- **Recebe:** site implementado.
- **Faz:**
  - *@qa:* checklist de qualidade (responsividade, links, imagens, acessibilidade,
    console, cross-browser), Lighthouse.
  - *cro-analyst:* revisão de conversão (posição/contraste de CTAs, fricção,
    clareza da jornada até o contato).
  - *seo-specialist:* títulos, meta description, dados estruturados, OG, sitemap,
    performance de imagem.
- **Entrega:** `qa-report.md` com veredito **PASS / CONCERNS / FAIL**.
- **Gate G6:** PASS (Lighthouse ≥ 90; zero bug crítico). FAIL → volta ao @dev
  (máx. 2 ciclos), depois escala para Orion.
- **Handoff →** Deploy.

### FASE 7 — Publicação  ·  @devops (Gage) 🔒 EXCLUSIVO
- **Objetivo:** colocar no ar com segurança.
- **Recebe:** site aprovado no G6.
- **Faz:** versionamento, deploy (Netlify/Vercel/GitHub Pages), configuração de
  domínio, HTTPS, e — quando houver repositório — `git push` / PR.
- **Entrega:** **site no ar** + URL.
- **Gate G7:** site acessível, HTTPS ok, formulários/CTAs funcionando em produção.

### FASE 8 (futuro) — Painel Admin & Backend  ·  @data-engineer (Dara) + @dev + @devops
- **Objetivo:** o dono sobe foto e cadastra carro por um painel (sua prioridade nº 1).
- **Faz:** schema Supabase + Storage + Auth, `admin.html` com upload, migração
  de `carros.js` → banco, deploy.
- **Gate G8:** dono cadastra e publica um carro com foto, fim a fim.

---

## 6. Quadro de Handoffs (fluxo do trabalho)

```
Vitor ▶ Orion(F0) ▶ Analyst(F1) ▶ Brand/Copy(F2) ▶ Design(F3) ▶ Architect(F4)
        ▶ Dev(F5) ▶ QA/CRO/SEO(F6) ▶ DevOps(F7) ▶ [Futuro] Data-Eng(F8)
                          ▲                  │
                          └──── reprovou ────┘  (volta ao Dev, máx. 2 ciclos)
```

Cada seta carrega um **handoff artifact** (artefato de passagem) com: contexto,
decisões-chave, arquivos gerados, próximo passo. Armazenados em `.aiox/handoffs/`.

---

## 7. Detalhamento dos Agentes

| Agente | Persona | Squad | Missão no projeto | Entregável-chave |
|--------|---------|-------|-------------------|------------------|
| @aiox-master | Orion 👑 | AIOX | Orquestrar, validar gates, governança | Plano + board |
| @analyst | Alex | AIOX | Pesquisa de nicho e benchmark | `research.md` |
| ux-researcher | — | WebDesign | Jornada e personas | personas |
| brand-strategist | — | WebDesign | Posicionamento e tom | guia de marca |
| storytelling-expert | — | WebDesign | Narrativa do site e dos carros | arco narrativo |
| copywriter | — | WebDesign | Toda a copy | `copy.md` |
| creative-director | — | WebDesign | Conceito e direção de arte | moodboard/conceito |
| web-designer | — | WebDesign | Layout e design system | `design-spec.md` |
| @ux-design-expert | Uma | AIOX | UX/UI, acessibilidade | revisão UX |
| motion-designer | — | WebDesign | Animações e micro-interações | spec de motion |
| @architect | Aria | AIOX | Arquitetura técnica | `architecture.md` |
| @dev | Dex | AIOX | Implementação front | site (F1) |
| frontend-developer | — | WebDesign | Apoio de implementação/refino | componentes |
| @data-engineer | Dara | AIOX | Backend/Supabase (F2) | schema + storage |
| @qa | Quinn | AIOX | Qualidade e Lighthouse | `qa-report.md` |
| cro-analyst | — | WebDesign | Otimização de conversão | recomendações CRO |
| seo-specialist | — | WebDesign | SEO técnico e on-page | checklist SEO |
| @devops | Gage 🔒 | AIOX | Deploy e push (EXCLUSIVO) | site no ar |

---

## 8. Quality Gates (resumo)

| Gate | Fase | Critério de aprovação | Se falhar |
|------|------|-----------------------|-----------|
| G0 | Plano | Vitor aprova escopo e plano | revisar plano |
| G1 | Pesquisa | Insights + personas acionáveis | reaprofundar |
| G2 | Copy | Textos prontos, sem invenção | reescrever |
| G3 | Design | Aprovado + fiel + mobile ok | redesenhar |
| G4 | Arquitetura | Sólida, performática, evolutiva | rever |
| G5 | Build | Sem erro, bate com design | corrigir |
| G6 | QA/CRO/SEO | Lighthouse ≥ 90, zero bug crítico | volta ao Dev (×2) |
| G7 | Deploy | No ar, HTTPS, CTAs ok | rollback |
| G8 | Backend | Cadastro fim a fim funciona | corrigir |

---

## 9. Cronograma

| Modo | Descrição | Duração |
|------|-----------|---------|
| **Sprint Relâmpago** (hoje) | Orion executa F2–F6 condensadas com a referência visual definida, acionando especialistas em pontos de revisão. Entrega o site estático completo. | ~1–2h |
| **Squad Completo** | Cada fase com seu especialista dedicado e gates formais. Máxima qualidade. | ~1–2 dias |
| **Fase 2 (backend)** | Painel Supabase + upload de foto. | ~3–5h |

> Recomendação para "fazer história agora": **Sprint Relâmpago** para colocar o
> site no ar hoje, e depois rodar o **Squad Completo** por fase para elevar ao
> nível "melhor do mundo" e plugar o backend.

---

## 10. Autoridades Exclusivas & Escalação

- 🔒 **@devops (Gage)** é o único que faz `git push`, `gh pr create/merge`, deploy
  e gestão de MCP. Qualquer outro agente que precise publicar **delega para ele**.
- **Escalação:** agente travado → Orion; gate reprovado 2× → Orion decide
  (reescopo, troca de abordagem ou waiver consciente); conflito de fronteira
  entre agentes → Orion media.

---

## 11. Riscos & Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Fotos reais do dono atrasam | Site "vazio" | Demo com 6 clássicos reais já no ar; fallback "Foto em breve" |
| Escopo inflar (vira ERP) | Estoura prazo | Fases fechadas; backend só na F8 |
| Dono não consegue editar | Abandono | `carros.js` simples + `README` + F2 com painel |
| Performance de imagem | SEO/UX ruim | Lazy-load + compressão (F4/F6) |
| Direitos das fotos demo | Legal | Fotos demo são de acervo livre (Wikimedia); serão substituídas pelas do dono |

---

*Documento de orquestração — Synkra AIOX · Operação PCH Vintage · conduzido por Orion 👑*
