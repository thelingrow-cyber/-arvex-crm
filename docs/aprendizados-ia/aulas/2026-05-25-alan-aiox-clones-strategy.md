# AIOX — Framework Completo: Squads, Agentes e Clones

> Análise consolidada dos prints do Alan (Academia Lendária) + estratégia de clones para ARVEX
> Baseado na conversa de 2026-05-22 a 2026-05-25

---

## 1. As 3 Camadas do AIOX (diferença real)

### Agente AIOX Padrão
- **Tamanho:** 300–500 linhas de YAML
- **Estrutura:** Sistema operacional completo — persona, comandos (`*help`, `*create-story`...), dependências, tasks, workflows
- **Exemplos:** `@dev`, `@qa`, `@architect`, `@pm`, `@devops`
- **Quando usar:** Operações estruturadas, desenvolvimento de software, fluxos com gates de qualidade
- **Limitação:** Genérico — não tem expertise de um domínio específico fora de TI

### Squad Agent
- **Tamanho:** 50–150 linhas de Markdown
- **Estrutura:** Persona + escopo + comandos — namespace próprio (ex: `WebDesign:agents:creative-director`)
- **Exemplos:** `WebDesign:agents:copywriter`, `WebDesign:agents:cro-analyst`
- **Quando usar:** Time especializado em um domínio (design, vendas, curadoria de editais)
- **Limitação:** Só funciona dentro do workflow do squad; qualidade depende do conteúdo injetado

### Clone
- **Tamanho:** 4 arquivos leves (system + beliefs + heuristics + context), ~17–70 tokens cada
- **Estrutura:** Destilação do raciocínio de um expert real — frameworks, vocabulário, heurísticas
- **Exemplos:** `hormozi`, `tay-dantas`, `gary-halbert`
- **Quando usar:** Consulta rápida em qualquer contexto, sem workflow fixo
- **Vantagem:** Funciona em qualquer conversa, qualquer projeto, qualquer tarefa

---

## 2. A Ratio do Alan — Por Que Mais Clones que Squads

Nos prints da live o Alan tinha:
- **~40 clones**
- **3–4 namespaces de squads**

**Por quê?**

| | Squad | Clone |
|--|-------|-------|
| Contexto de uso | Workflow específico | Qualquer contexto |
| Portabilidade | Só naquele squad | Qualquer projeto |
| Criação | Complexo (wizard + blueprint) | Simples (4 arquivos MD) |
| Qualidade | Depende do conteúdo das tasks | Depende das fontes do expert |
| Exemplo | Squad WebDesign para landing pages | Clone Gary Halbert para qualquer copy |

**Insight:** Clone é mais versátil. Squads são úteis para workflows repetíveis e complexos. Clones funcionam como lentes de perspectiva que você coloca em qualquer situação.

---

## 3. Estrutura Completa dos Clones do Alan (prints)

### Business / Estratégia
| Clone | Expert | Domínio |
|-------|--------|---------|
| `hormozi-offers` | Alex Hormozi | Criação de ofertas Grand Slam |
| `hormozi-content` | Alex Hormozi | Estratégia de conteúdo |
| `hormozi-copy` | Alex Hormozi | Copywriting no método Hormozi |
| `ray-dalio` | Ray Dalio | Princípios de decisão e gestão |
| `naval-ravikant` | Naval Ravikant | Filosofia de negócios e liberdade |
| `charlie-munger` | Charlie Munger | Mental models e pensamento lateral |
| `simon-sinek` | Simon Sinek | Liderança e propósito (Golden Circle) |

### Copy / Persuasão
| Clone | Expert | Domínio |
|-------|--------|---------|
| `gary-halbert` | Gary Halbert | Resposta direta, headlines, leads |
| `joe-sugarman` | Joe Sugarman | Triggers psicológicos, copy longa |
| `eugene-schwartz` | Eugene Schwartz | Níveis de consciência, breakthrough |

### Tráfego Pago
| Clone | Expert | Domínio |
|-------|--------|---------|
| `molly-pittman` | Molly Pittman | Estratégia de paid social |
| `depesh-mandalia` | Depesh Mandalia | Performance Facebook/Meta |
| `ralph-burns` | Ralph Burns | Escala de campanhas pagas |

### Branding / Storytelling
| Clone | Expert | Domínio |
|-------|--------|---------|
| `miller-sticky-brand` | Donald Miller | StoryBrand, mensagem clara |
| `dan-harmon` | Dan Harmon | Story Circle, estrutura narrativa |
| `joseph-campbell` | Joseph Campbell | Jornada do Herói |

### Outros identificados
- `tay-dantas` — Marca pessoal de creator, audiência, posicionamento
- `copy-chief` — Clone funcional (não um expert real) de chefe de copy

---

## 4. Como um Clone é Construído

### Estrutura de arquivos
```
.claude/clones/{nome}/
├── system.md      # Identidade, escopo, como pensa, como responde
├── beliefs.md     # Crenças fundamentais do expert
├── heuristics.md  # Heurísticas de decisão (frameworks, regras)
└── context.md     # Vocabulário, casos, referências, checklist
```

### Arquivo de comando (ativa o clone)
```
.claude/commands/AIOX/clone/{nome}.md
```

Instrui o Claude a: ler os 4 arquivos na ordem, adotar a persona completamente, não se apresentar como Claude, abrir com a pergunta característica do expert.

### Como criar (método)
1. **Coletar fontes:** transcrições de vídeos, podcasts, livros, entrevistas do expert
2. **Salvar fontes:** `docs/clone-{nome}-pesquisa/` (transcrições + resumos)
3. **Criar index:** `.claude/clones/{nome}/sources/index.md`
4. **Destilar:** Extrair frameworks, vocabulário, heurísticas → preencher os 4 arquivos
5. **Criar comando:** `.claude/commands/AIOX/clone/{nome}.md`

**Qualidade = qualidade das fontes.** Quanto mais material real do expert, mais preciso o clone.

---

## 5. Estratégia de Clones da ARVEX

### O que já existe
| Clone | Expert | Status |
|-------|--------|--------|
| `hormozi` | Alex Hormozi | ✅ Ativo (6 vídeos + livro $100M Offers) |
| `tay-dantas` | Tay Dantas | ✅ Ativo (múltiplas fontes) |

### Roadmap — Prioridade por Gap de Negócio

**ARVEX precisa:** co-produção de infoprodutos (Dr. Alex / Cindy), lançamentos, landing pages (WebDesign squad pronto), SDRs, closers.

#### Prioridade 1 — Gap crítico imediato

| # | Clone | Expert | Por quê agora |
|---|-------|--------|---------------|
| 1 | `donald-miller` | Donald Miller | Mensagem clara antes de qualquer copy. Pré-requisito para Cindy e Dr. Alex. |
| 2 | `gary-halbert` | Gary Halbert | Copy para landing pages (WebDesign squad está pronto e precisa de copy real). |
| 3 | `russell-brunson` | Russell Brunson | Estrutura de funil e lançamento — ARVEX é agência de lançamento. |

#### Prioridade 2 — Gap importante a médio prazo

| # | Clone | Expert | Por quê |
|---|-------|--------|---------|
| 4 | `eugene-schwartz` | Eugene Schwartz | Níveis de consciência do avatar. Complementa Halbert. |
| 5 | `joseph-campbell` | Joseph Campbell | Jornada do Herói para narrativas de transformação dos experts. |

#### Prioridade 3 — Expansão futura

| # | Clone | Expert | Por quê |
|---|-------|--------|---------|
| 6 | `molly-pittman` | Molly Pittman | Tráfego pago quando escalar campanhas. |
| 7 | `ray-dalio` | Ray Dalio | Princípios de decisão para gestão da ARVEX. |

---

## 6. Sequência Lógica dos Clones

```
Mensagem (Miller) → Copy (Halbert) → Funil (Brunson)
      ↓                   ↓               ↓
  Clareza da        Landing pages    Webinário +
  proposta          que convertem    sequência de
  do expert                          lançamento
```

O Hormozi já cobre: oferta + precificação + value stack
A Tay já cobre: marca + posicionamento do creator

---

## 7. Roadmap do Hormozi (pendências)

- [ ] Processar $100M Leads (livro) → adicionar como fonte L2
- [ ] Validar com casos reais: oferta Dr. Alex e oferta Cindy
- [ ] A cada nova fonte: atualizar heuristics/beliefs e subir versão (v1.1, v1.2...)

---

*Gerado em 2026-05-26 | ARVEX / AIOX*
