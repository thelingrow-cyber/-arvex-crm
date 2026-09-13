# ⚙️ Sistema de Conteúdo — a máquina

> **O que este documento é:** a operação que alimenta o [`sistema-de-roteiro.md`](sistema-de-roteiro.md).
> Pesquisa, escala, formatos, distribuição e automação. **O roteiro é o motor; isto é o chassi.**
> **Obedece e não reabre:** [`brand-book-marca-pessoal.md`](brand-book-marca-pessoal.md)
> **Criado em** 2026-09-13.

---

## 00 — A arquitetura em cinco estágios

```
  ①  PESQUISA        →  ②  PAUTA      →  ③  ROTEIRO   →  ④  PRODUÇÃO  →  ⑤  DISTRIBUIÇÃO
  varre a fronteira     filtra e vira     sistema-de-     lote de          multi-canal,
  e a própria obra      lista de temas    roteiro.md      gravação         agendado
  ────────────────      ─────────────     ───────────     ──────────       ─────────────
  agente (§02)          humano, 15min     IA + edição     humano, 90min    agente
```

**O gargalo real nunca é gravar — é decidir o que gravar.** Por isso o estágio ① é o que mais
compensa automatizar, e é onde este documento gasta mais espaço.

---

## 01 — O teto honesto de uma marca

Antes da escala, o número que ninguém diz:

| Plataforma | Teto saudável/dia | Acima disso |
|---|---|---|
| Instagram Reels | **3–5** | alcance despenca; padrão lido como spam |
| TikTok | 3–5 | idem |
| YouTube Shorts | 3–5 | idem |
| LinkedIn | 1–2 | feed pune repetição |
| X / Twitter | 5–10 | tolera mais |

> **Uma marca satura em ~15-20 peças/dia distribuídas.** Não é opinião: é como os feeds tratam
> frequência anômala de uma mesma conta.

**Então 100/dia não é uma conta postando 100. É uma rede.**

| Camada | Contas | Peças/dia |
|---|---|---|
| **Marca pessoal** *(@vitorsimoesb)* | 1 rosto × 5 plataformas | ~15-20 |
| **ARVEX** *(institucional)* | 1 × 4 plataformas | ~10-15 |
| **Viziom · Lingrow** | 2 × 3 plataformas | ~15-20 |
| **Contas temáticas** *(se um dia)* | N | o resto |

**Consequência de projeto:** a máquina precisa produzir **peça reaproveitável entre marcas**, não peça
única. O mesmo fato vira ângulo de founder no perfil pessoal e ângulo de produto na conta da ARVEX.

---

## 02 — A rede de pesquisa 🔍

*O estágio que decide a qualidade de tudo. É aqui que a arbitragem EUA→BR acontece de verdade.*

### 2.1 · As fontes, por tipo de sinal

| Fonte | O que colher | Frequência |
|---|---|---|
| **X / listas curadas** — AI builders, founders solo, VCs de IA | o **gancho** e o termo novo. É onde nasce vocabulário | diária |
| **Newsletters** — Ben's Bites · The Neuron · TLDR AI · The Rundown · Lenny's | dado já filtrado, com fonte | diária |
| **Hacker News** — front page | o que a engenharia está discutindo antes de virar produto | diária |
| **Product Hunt** — categoria agentes/automação | ferramenta nova que baixa custo → matéria de **G5** | 2×/semana |
| **Reddit** — r/AI_Agents · r/SaaS · r/smallbusiness · r/Entrepreneur | **dor real com as palavras deles** → matéria de **G8** | 2×/semana |
| **YouTube US** — canais de IA aplicada a negócio | formato e estrutura de vídeo, nunca conteúdo traduzido literal | semanal |
| **Relatórios** — Gartner, Deloitte, a16z, consultorias | número com fonte → matéria de **G7** | mensal |
| **A própria operação** | o que você construiu esta semana → **G4** | **contínua** |

### 2.2 · Os cinco sinais que valem caçar

1. **Engajamento anômalo** — post com muito acima da média *daquela conta*. Indica que a ideia pegou, não que o autor é grande
2. **Termo novo emergindo** — palavra aparecendo em 3+ fontes independentes na mesma semana
3. **Número inédito** — estatística com fonte primária que ainda não circulou em português
4. **Caso de empresa pequena** — não é a OpenAI fazendo; é uma clínica de 6 pessoas. **É o coração do G1**
5. **Queda de custo** — o que custava caro e agora é barato ou aberto → **G5**

### 2.3 · O filtro — quatro perguntas, qualquer "não" descarta

| # | Pergunta | Por quê |
|---|---|---|
| 1 | **Já existe em português?** | Se já circulou aqui, não é arbitragem — é eco |
| 2 | **Traduz para a dor de um dono de PME?** | *"E daí, para o dono de uma loja de R$200 mil/mês?"* |
| 3 | **Tem número ou mecanismo?** | Opinião gringa traduzida não é conteúdo, é repost |
| 4 | **Cabe na tese?** | Arquitetura × ferramenta plugada. Se não cabe, é notícia de tech |

### 2.4 · Como isto vira agente — e por que importa

**Você tem o AIOX.** Isto não deveria ser trabalho manual:

```
AGENTE: content-scout          (novo, squad research)
  fontes:    lista de RSS, X lists, subreddits, newsletters
  rotina:    1×/dia, manhã
  filtro:    os 5 sinais + as 4 perguntas
  saída:     10 pautas em fila, cada uma com:
             · o fato, com link e data
             · a tradução em uma frase de dono
             · a família de gancho sugerida (G1-G10)
             · o formato sugerido
```

**Três razões para construir isso antes de escalar o volume:**

1. **É o gargalo real.** Roteiro e gravação escalam com esforço; decidir o que gravar, não
2. 🎯 **É dogfooding** — você usa o próprio produto para construir a própria marca. E isso **vira conteúdo**: *"o agente que escolhe minhas pautas"* é um Diário de Obra pronto
3. **É prova ambulante.** Quando alguém perguntar o que você instala, a resposta pode ser *"isto aqui, que eu uso todo dia"*

---

## 03 — Os formatos, por custo de produção

*Ordenados pelo que rende mais peça por minuto investido.*

| Formato | Produção | Rende | Pilar | Fonte |
|---|---|---|---|---|
| **Frase autoral** — texto na tela, sem rosto | **5-10 min** | 1 | Provocação | banco de frases |
| **Corte de vídeo longo** | 15-20 min | 1 | todos | podcast, live, YouTube |
| **Talking head curto** — 30-90s | 20-30 min | 1 | Visão, Provocação | pauta do scout |
| **Bastidor / build** | 10-15 min | 1 | Processo | sua operação |
| **Dado surpreendente** | 30-45 min | 1 | Dado | relatórios |
| **Carrossel** | 30-60 min | 1 | Educação | pauta ou tese |
| **Vídeo longo (30-40 min)** | 2-3h | **8-12 cortes** | todos | o mais eficiente por peça |

> **O multiplicador não é criar mais pauta — é extrair mais peça da mesma pauta.**
> Um fato rende G1, G2, G5 e G8: quatro vídeos, quatro entradas, um insumo.

**A regra do lote:** grave **por família de gancho**, não por tema. Cinco G1 seguidos saem em 20
minutos; alternar formato a cada vídeo custa o dobro em troca de nada.

---

## 04 — A escala, por patamar

*Cada patamar só abre quando o anterior roda por duas semanas sem quebrar.*

| Fase | Peças/dia | O que muda | O gargalo desta fase |
|---|---|---|---|
| **F1 · Ritmo** *(sem 1-2)* | **3-5** | você grava, edita e posta. Sem sistema | criar o hábito e o filtro |
| **F2 · Máquina** *(sem 3-4)* | **8-12** | scout roda · lote de gravação · edição em template | ter pauta suficiente |
| **F3 · Multiplicação** *(mês 2)* | **20-30** | 1 vídeo longo/semana virando 10 cortes · distribuição multi-canal | edição |
| **F4 · Rede** *(mês 3+)* | **50-100** | múltiplas contas · reaproveitamento cruzado · edição automatizada | operação, não criação |

**O erro que mata a escala:** pular de F1 para F3. Sem o filtro estabelecido, o volume só multiplica
o conteúdo errado — e aí você tem 100 peças por dia que ninguém salva.

**O sinal de que pode subir de fase:** duas semanas cumprindo o patamar sem furo **e** com a métrica
de qualidade estável (§06).

---

## 05 — A operação da semana

### Bloco único de segunda — 3h

| # | Etapa | Tempo | Como |
|---|---|---|---|
| 1 | **Colheita** | 20 min | ler a fila do `content-scout`, aprovar 10-15 pautas |
| 2 | **Pautas** | 15 min | distribuir por formato e dia |
| 3 | **Roteiros** | 40 min | IA gera do esqueleto (`sistema-de-roteiro.md` §03); você **edita, não escreve** |
| 4 | **Gravação em lote** | 75 min | por família de gancho, mesma roupa, mesma luz |
| 5 | **Fila** | 20 min | edição em template + agendamento da semana |

**Diário — 15 min:** ler o que o scout trouxe · responder DM · capturar o build do dia *(o Diário de
Obra é a única peça que não dá para produzir em lote)*.

### O que é humano e o que não é

| Humano — insubstituível | Automatizável |
|---|---|
| aprovar pauta | varrer fontes |
| a fala e o rosto | rascunho de roteiro |
| decidir o gancho | legenda, corte, template |
| responder DM | agendamento e distribuição |
| **o julgamento do filtro** | métricas e relatório |

---

## 06 — O que medir

**Nos primeiros 90 dias — nesta ordem:**

1. **DMs de perfil do ICP** — o indicador que importa
2. **Qualidade dos comentários** — founder e empresário, ou iniciante pedindo dica?
3. **Salvamentos** — utilidade real, mais que curtida
4. **Conversas que viraram call**
5. **Semanas com a grade cumprida**

**Não medir agora:** seguidores. Está registrado como desvio nº10 no brand book.

**Métrica de qualidade que autoriza subir de fase:** salvamentos por peça estável ou subindo
enquanto o volume cresce. **Se o volume sobe e o salvamento por peça despenca, o sistema está
produzindo ruído** — trave a fase e conserte o filtro.

---

## 07 — Os riscos declarados

| Risco | Antídoto |
|---|---|
| **Volume sem filtro** — 100 peças que ninguém salva | métrica de salvamento por peça trava a subida de fase |
| **Spam de plataforma** — alcance punido | teto de 3-5/dia por conta; volume vem de rede, não de repetição |
| **Conteúdo de IA genérico** | a regra é **AI-assisted, não AI-generated** — o rascunho é da máquina, o julgamento e a fala são seus |
| **Colapso por volume** *(Munger, modo 2)* | o piso da semana ruim: 3 peças. Nunca zero |
| **Sotaque de dev** | o filtro nº2 do roteiro: um dono entende sem saber o que é LLM? |

---

## 08 — O que este documento não resolve

- **O mecanismo observável** — segue aberto no brand book §07
- **A grade em conflito** — 6 pilares com peso × 2 registros VISÃO/OBRA. **Escolher uma antes da F2**
- **A oferta que o conteúdo vende** — depende de OF-01
- **Edição fina e ritmo de corte** — outro ofício

---

*Sistema de Conteúdo v1 — 2026-09-13. Ajusta com dado de campo, não com nova deliberação.*
