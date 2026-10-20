# Plano de mídia — Workshop Operação Black Recorde (Cindy)

> **Agente:** Buck, Media Buyer (`squads/marketing/agents/media-buyer.md`) · **Modo: co-piloto**.
> Eu monto o plano e o Vitor sobe na Meta. Não tenho acesso à conta, então nenhum número abaixo
> vem de métrica real desta campanha.
> **Fontes:** briefing (`briefing.pdf`) · peças B1–B6 e o protocolo inicial (`criativos-ad-grid.md`) ·
> protocolo e auditoria do +100K (`docs/landing-desafio-otica-100k/`) · diagnóstico de funil
> (`docs/crm/diagnostico-funil-2026-07-31.md`) · produtos do SOP (`docs/processos/sop-fluxo-vendas.md`).
> **Data deste plano:** 20/10/2026 (terça). Evento: **27/10/2026 (terça), 19h30**, horário ainda a confirmar.

**Legenda usada no documento inteiro:** **[DADO]** é o que está escrito numa fonte do repositório.
**[PREMISSA]** é uma hipótese minha, que precisa ser confirmada ou trocada por número real.

---

## 0. Veredito primeiro: 7 dias e R$ 5–7 mil fecham a meta?

**Só com mídia paga, provavelmente não.** Com a oferta ainda indefinida, a conta abaixo (§3) mostra o seguinte:

- No cenário-base (ticket de R$ 5 mil), a meta de R$ 60–70 mil exige **cerca de 1.000 a 1.170 entradas
  no grupo**. Para conseguir isso com R$ 5–7 mil de verba, o custo por entrada precisa ficar
  entre **R$ 4,30 e R$ 7,00**.
- Um custo realista para dono de ótica na Meta está **entre R$ 8 e R$ 15 por entrada [PREMISSA]**:
  público de nicho B2B, com o interesse "ótica" vazando para quem só usa óculos. Nessa faixa, a
  verba compra **330 a 875 entradas**, o que dá **4 a 11 vendas de R$ 5 mil, ou R$ 20 a 55 mil**.
- **O repositório não guarda o custo por entrada do +100K.** Esse número é o que mais mudaria o
  plano. Antes de subir, peça ao gestor o export do Gerenciador de setembro (custo por Lead,
  CTR e entradas no grupo).

**Mesmo assim, 7 dias bastam para a mecânica.** Três conjuntos de anúncios saem da fase de
aprendizado em 2 a 3 dias com essa verba. O que pesa é volume e conversão, não o prazo.

**O que eu mudaria, em ordem de impacto:**

1. **Somar a base ao tráfego pago, desde hoje.** O dinheiro que falta está em quem já conhece a Cindy:
   o **grupo do Desafio +100K, de um mês atrás, com o mesmo ICP**, os leads da Cindy no CRM, o
   Instagram dela (stories diários e uma live de aquecimento) e as indicações das mentoradas. Custo
   zero e tráfego mais quente que qualquer anúncio. Se a base trouxer 400 a 600 entradas, a meta
   volta a ficar ao alcance.
2. **Definir a oferta e o preço até 22/10.** Abaixo de R$ 5 mil, a conta não fecha com esta verba
   (veja a tabela em §3). Ticket de R$ 7 mil com parcelamento é o cenário em que a mídia paga quase
   paga a meta sozinha.
3. **Subir hoje à noite, não amanhã.** Cada dia vale cerca de 14% da captação.
4. **Comparecimento é a alavanca mais barata.** Lembretes no grupo em D-1, no dia às 9h, às 18h30 e
   às 19h25, mais a peça "estamos ao vivo" (§2), movem o comparecimento de 20% para 35%. Isso vale
   mais que 30% de verba extra.
5. **Calls depois do evento.** A janela de venda vai de 27 a 31/10, ou seja, 4 dias **[DADO, briefing]**.
   Isso combina com o dado do CRM (média de 1 dia entre cadastro e fechamento, máximo de 13 **[DADO]**),
   mas 12 a 14 vendas com 30% de fechamento por call **[PREMISSA]** somam **cerca de 40 a 47 calls
   em 4 dias**. Só a Cindy não dá conta: os closers precisam estar escalados antes do dia 27.

---

## 1. Estrutura da conta

### Objetivo de otimização: **Leads, conversão no site, evento `Lead`, que dispara no clique do CTA**

| Opção | O que a Meta otimiza | Veredito |
|---|---|---|
| **Leads, conversão no site (`Lead`)** | Quem clica no botão do grupo | ✅ **Escolhido.** É o sinal mais próximo da entrada no grupo que existe. O pixel e o disparo no clique já foram feitos no +100K **[DADO]** |
| Tráfego (clique no link / visualização da página) | Quem clica no anúncio | ❌ A Meta acha quem clica em tudo e desiste. Fica barato no clique e caro na entrada |
| Mensagem (clique para WhatsApp) | Quem abre uma conversa 1:1 | ❌ Abre conversa privada, não entra no grupo. Exige SDR mandando o link para cada pessoa, o que não escala em 7 dias. A única vantagem seria pôr o telefone no CRM, e a decisão do +100K já aceitou abrir mão disso |
| Engajamento | Curtida e comentário | ❌ Não tem relação com entrar no grupo |

**Limite assumido:** o `Lead` mede o clique, não a entrada. O WhatsApp não devolve evento para a Meta.
A distância entre os dois foi de 50% no +100K (16 cliques, 8 entradas **[DADO]**, amostra minúscula) e
é medida à mão (§4, contagem diária do grupo).

### Campanhas, conjuntos e anúncios

Uso orçamento por conjunto (ABO), não CBO. Em 7 dias preciso **controlar** quanto vai para cada
temperatura e guardar a reserva do fim. Com CBO, a Meta despeja tudo no frio barato e o remarketing
fica sem verba.

```
CAMPANHA 1 — CB_BLACKREC_2610_CAPTACAO_LEADS_ABO        (21/10 → 27/10 15h)
├─ AS1 FRIO-A  | Advantage+ público com sugestões de interesse
│    └─ B1 (vídeo Cindy) · B3 (voz clonada, entra D2/D3) · B2 vídeo (entra D2/D3)
├─ AS2 FRIO-B  | Lookalike 1–3% da base Cindy
│    └─ B6 (carrossel) · B2 estático · B1
└─ AS3 MORNO   | Engajamento Cindy + quem clicou no +100K
     └─ B4 (vídeo Cindy) · B1

CAMPANHA 2 — CB_BLACKREC_2610_REMARKETING_LEADS_ABO     (23/10 → 27/10)
├─ AS4 RMKT    | Visitou a página / viu 50% dos vídeos B* e não clicou
│    └─ B5 · B4 · B7 "faltam 2 dias" (a produzir)
└─ AS5 EVENTO  | AS4 + AS3, só em 27/10
     └─ B8 "é hoje" (até 19h30) · B9 "estamos ao vivo" (19h30–21h)
```

**B7, B8 e B9 não existem ainda.** São stories curtos (Cindy no celular, 10–15 s). A copy é do
Halbert (copy-chief), não minha. Tem que estar pronta até 24/10.

### Públicos detalhados

| Conjunto | Inclui | Exclui | Observação |
|---|---|---|---|
| **AS1 Frio-A** | Brasil, 25–60 anos, português. Advantage+ público com sugestões: Óptica, Optometria, Lentes oftálmicas, Essilor, Zeiss, Hoya, Varilux, Transitions, Varejo, Pequenas empresas + comportamento "Administradores de página de negócio" | Leads Black Recorde 30d (a partir de D3) · lista de alunas/mentoradas | O interesse "ótica" vaza para consumidor final. Quem filtra é a primeira linha da peça ("na rua da **sua** ótica"). Por isso o Frio-A só roda peças que se dirigem ao dono |
| **AS2 Frio-B** | Lookalike 1–3% BR de: telefones/e-mails dos leads da Cindy no CRM + membros do grupo +100K + compradoras/mentoradas. **Se a lista casar menos de 100 pessoas, não cria;** vira semente de engajamento IG 365d | Mesmas do AS1 | A semente mais valiosa é quem **comprou**. Se der para separar, faça uma semente só de compradoras |
| **AS3 Morno** | Engajou com o IG/FB da Cindy em 180d · viu 50% de vídeo da Cindy em 60d · visitou o site cindyb.com.br em 60d · **disparou `Lead` no +100K (página de setembro)** | Leads Black Recorde 7d | É o público que mais deve converter: já clicou num evento dela há um mês |
| **AS4 RMKT** | Visitou a página Black Recorde 7d · viu 50% de B1/B3/B4 em 7d · engajou com os anúncios em 7d | `Lead` Black Recorde 7d (proxy de quem já entrou) | Só liga quando o público passar de ~1.000 pessoas (deve acontecer em D3) |
| **AS5 Evento** | AS4 + AS3 | `Lead` Black Recorde 14d | Frequência alta é aceita: é um dia só |

---

## 2. Divisão da verba (por dia e por conjunto)

**Lógica:** concentrar no começo (aprendizado e formação do público de remarketing), deslocar
para o remarketing em 25–26/10 e fechar com o dia do evento. A **reserva de contingência** paga as
peças que entram atrasadas (B2 vídeo, B3) e o reforço do vencedor depois de 72h. Até 24/10, os
valores por conjunto são o ponto de partida; **depois de 72h, as regras do §4 redistribuem**.

### Cenário R$ 5.000

| Dia | AS1 Frio-A | AS2 Frio-B | AS3 Morno | AS4 RMKT | AS5 Evento | **Total** |
|---|---:|---:|---:|---:|---:|---:|
| Qua 21/10 (D1) | 250 | 200 | 150 | — | — | **600** |
| Qui 22/10 (D2) | 250 | 200 | 150 | — | — | **600** |
| Sex 23/10 (D3) | 250 | 200 | 150 | 50 | — | **650** |
| Sáb 24/10 (D4) ← leitura 72h | 270 | 200 | 150 | 80 | — | **700** |
| Dom 25/10 (D5) | 200 | 150 | 100 | 250 | — | **700** |
| Seg 26/10 (D6) | 150 | 100 | 100 | 350 | — | **700** |
| Ter 27/10 (D7) | 100 (até 15h) | — | — | — | 400 | **500** |
| **Subtotal** | **1.470** | **1.050** | **800** | **730** | **400** | **4.450** |
| Contingência | | | | | | **550** |
| **Total** | | | | | | **5.000** |

Reserva do fim: **remarketing em 25–26/10 = R$ 600** · **dia do evento = R$ 400** (R$ 250 "é hoje"
até 19h + R$ 150 "ao vivo" das 19h30 às 21h). Juntos, 20% da verba.

### Cenário R$ 7.000

| Dia | AS1 Frio-A | AS2 Frio-B | AS3 Morno | AS4 RMKT | AS5 Evento | **Total** |
|---|---:|---:|---:|---:|---:|---:|
| Qua 21/10 (D1) | 350 | 280 | 200 | — | — | **830** |
| Qui 22/10 (D2) | 350 | 280 | 200 | — | — | **830** |
| Sex 23/10 (D3) | 350 | 280 | 200 | 70 | — | **900** |
| Sáb 24/10 (D4) ← leitura 72h | 380 | 280 | 200 | 100 | — | **960** |
| Dom 25/10 (D5) | 280 | 200 | 150 | 350 | — | **980** |
| Seg 26/10 (D6) | 200 | 150 | 130 | 500 | — | **980** |
| Ter 27/10 (D7) | 150 (até 15h) | — | — | — | 550 | **700** |
| **Subtotal** | **2.060** | **1.470** | **1.080** | **1.020** | **550** | **6.180** |
| Contingência | | | | | | **820** |
| **Total** | | | | | | **7.000** |

Reserva do fim: **remarketing em 25–26/10 = R$ 850** · **dia do evento = R$ 550** (R$ 350 + R$ 200).

**Os R$ 2 mil a mais não compram 40% a mais de entradas.** Num público de nicho, o custo por entrada
sobe com a verba, porque a frequência aumenta e a Meta vai buscar gente pior. Conte com uns 25% de
entradas extras **[PREMISSA]**. Se a decisão for entre R$ 7 mil em mídia e R$ 5 mil em mídia mais
R$ 2 mil em produção de B7/B8/B9 e operação da base, **eu fico com a segunda**.

**Se subir hoje (20/10) à noite:** cada conjunto roda com 50% do valor de D1. Isso sai da contingência.

---

## 3. Funil reverso

### Premissas (todas trocáveis)

| Etapa | Valor usado | Tipo | De onde vem |
|---|---|---|---|
| Meta de faturamento em outubro | R$ 60–70 mil | **[DADO]** | Briefing §07 (meta, não projeção) |
| Ticket da oferta | R$ 3 mil / **5 mil** / 7 mil | **[PREMISSA]** | A oferta não está definida (briefing §08). O SOP lista R$ 5, 7 e 10 mil **[DADO]**. O ticket médio realizado no CRM é R$ 3.314, contaminado por parcela lançada como valor cheio **[DADO]** |
| Clique no CTA → entra no grupo | 50% | **[DADO, n = 16]** | Auditoria do +100K, amostra pequena demais para confiar |
| Grupo → presente na live | 30% (base) · 20% (pessimista) | **[PREMISSA]** | Live gratuita de 3–4 h numa terça às 19h30. Não há dado de comparecimento do +100K no repositório |
| Presente → venda (até 31/10) | 4% (base) · 2,5% (pessimista) | **[PREMISSA]** | Venda de ticket alto via call depois da live. O CRM fecha 9,9% dos leads **[DADO]**, mas é outro funil (lead já qualificado) |
| **Grupo → venda** | **1,2%** (base) · **0,5%** (pessimista) | derivado | 30% × 4% · 20% × 2,5% |
| Custo por entrada de mercado | R$ 8–15 | **[PREMISSA]** | Sem histórico no repositório. **Substituir pelo export do +100K** |

### Quantas vendas, presentes e entradas a meta exige

| Ticket | Vendas (60k / 70k) | Presentes, base (60k / 70k) | Entradas, base 1,2% | Entradas, pessimista 0,5% |
|---|---|---|---|---|
| R$ 3.000 | 20 / 24 | 500 / 600 | **1.667 / 2.000** | 4.000 / 4.800 |
| **R$ 5.000** | **12 / 14** | **300 / 350** | **1.000 / 1.167** | 2.400 / 2.800 |
| R$ 7.000 | 9 / 10 | 225 / 250 | **750 / 834** | 1.800 / 2.000 |

### Qual custo por entrada fecha a conta

São dois limites diferentes, e o que manda é o de **volume**:

**a) Custo por entrada de volume** = verba ÷ entradas necessárias (cenário-base), supondo que toda
entrada venha da mídia paga:

| Ticket | Verba R$ 5 mil (60k / 70k) | Verba R$ 7 mil (60k / 70k) |
|---|---|---|
| R$ 3.000 | R$ 3,00 / 2,50 | R$ 4,20 / 3,50 |
| **R$ 5.000** | **R$ 5,00 / 4,30** | **R$ 7,00 / 6,00** |
| R$ 7.000 | R$ 6,70 / 6,00 | R$ 9,30 / 8,40 |

**b) Custo por entrada econômico** = receita por entrada ÷ ROAS 3 (cenário-base). Ticket de R$ 3 mil
dá **R$ 12**, ticket de R$ 5 mil dá **R$ 20**, ticket de R$ 7 mil dá **R$ 28**.

**Leitura:** a campanha dá lucro mesmo com custo por entrada alto. Cada entrada vale R$ 36 a R$ 84
de receita esperada. **O problema não é retorno, é escala.** A verba não compra entradas suficientes
dentro do prazo. Isso justifica duas coisas: puxar a base (§0) e, se o custo por entrada vier abaixo
de R$ 8, **aumentar a verba durante a campanha**, porque cada real a mais se paga. Essa é a
decisão de escala mais importante da semana (§4).

**Custo-alvo operacional usado nas regras abaixo: R$ 6 por entrada no grupo**, ou seja, cerca de
**R$ 3 por `Lead`** com 50% de passagem. Se a oferta sair a R$ 7 mil, o alvo sobe para R$ 8.

---

## 4. Regras de decisão

### O que medir e onde

| Métrica | Fonte | Frequência |
|---|---|---|
| Custo por `Lead` (clique no CTA) por anúncio e por conjunto | Gerenciador | diária, às 10h |
| **Membros do grupo** | contagem manual no WhatsApp | **diária, às 10h, na planilha** |
| Passagem `Lead` → entrada | membros novos do dia ÷ `Lead` do dia | diária |
| Taxa de gancho (views de 3 s ÷ impressões), CTR de link, frequência | Gerenciador | na leitura de 72h |

### Antes de 72h (só emergência)

- Anúncio que gastou **R$ 20 sem nenhum `Lead`** → pausa. É a única exceção à regra de não mexer.
- Reprovação ou bloqueio de anúncio → corrigir no mesmo dia.
- Passagem `Lead` → entrada **abaixo de 35% no D2** → o problema está na tela do grupo (nome,
  foto, descrição, mensagem de boas-vindas; veja a auditoria do +100K §4), **não na mídia**. Corrigir
  antes de mexer em verba.

### Leitura de 72h — sábado, 24/10, às 10h

**Anúncio (dentro de cada conjunto)**

| Situação | Ação |
|---|---|
| Custo por `Lead` > 1,5× a média do conjunto e gasto ≥ R$ 40 | **Pausa** e a verba fica no conjunto |
| Taxa de gancho < 20% (vídeo) | **Troca o criativo**: o hook não segura. Entra a próxima célula do grid |
| Gancho ≥ 25% e CTR de link < 0,8% | O corpo do vídeo não leva ao clique: **troca a CTA ou o corte** |
| CTR ≥ 1,2% e `Lead` ÷ visualização da página < 25% | **Furo de ad scent ou página**, não de anúncio. A página precisa prometer o mesmo mecanismo (calendário · oferta · campanha) |
| Frequência > 3 no Morno ou RMKT | Entra a peça seguinte (B7 no RMKT) |

**Conjunto**

| Custo por entrada no grupo (estimado) | Ação |
|---|---|
| **≤ R$ 6** (≤ R$ 3 por `Lead`) | **Escala +25% por dia**, nunca mais de 30% de uma vez para não reiniciar o aprendizado. Puxa da contingência |
| R$ 6 a R$ 9 | Mantém e troca o pior anúncio |
| **> R$ 9 com gasto ≥ R$ 150** | **Corta** e move a verba para o melhor conjunto |

**Campanha inteira (regra que decide a semana)**

| Custo por entrada médio em 72h | Leitura | Decisão |
|---|---|---|
| ≤ R$ 6 | A mídia paga fecha a conta do ticket de R$ 5 mil | Gastar a verba toda. **Propor ao Vitor liberar +R$ 2–3 mil**: cada real se paga (§3b) |
| R$ 6 a R$ 10 | Faltam entradas | Manter a mídia e **acionar a base com força total** (grupo +100K, CRM, IG) |
| **> R$ 10** | A mídia sozinha entrega no máximo uns 40% da meta | Segurar a verba no Morno e RMKT, cortar o Frio-A e **avisar a operação que a meta depende da base e do ticket** |

### Log de decisões (preencher a cada mexida)

| Data | O que mudou | Por quê (número) | O que observar e até quando |
|---|---|---|---|
| | | | |

---

## 5. Checklist técnico antes de subir

### Pixel e evento

- [ ] **A página nova está no mesmo site do PixelYourSite** (pixel `904293195276149`, injetado no
      site inteiro **[DADO, comentário em `index.html` do +100K]**). Não inicializar o pixel de novo
      na página (evita PageView duplo).
- [ ] **Trocar o `content_name` do script de clique.** No +100K ele está fixo em `'Otica 100K'` e
      `pagina:'captura-100k'`. Se a página for copiada sem essa troca, os dois lançamentos se misturam
      no Gerenciador. Usar `content_name:'Black Recorde'` e `pagina:'captura-blackrecorde'`.
- [ ] Todo CTA com `data-cta` dispara `fbq('track','Lead')` + `trackCustom ClickGrupoVIP`. Testar no
      **Gerenciador de Eventos → Testar eventos**, pelo celular, nos dois botões.
- [ ] **Conversão personalizada** "Lead – Black Recorde": evento `Lead` + URL contém o slug da
      página. A campanha otimiza **por ela**, não pelo `Lead` genérico (o site inteiro também dispara Lead).
- [ ] API de Conversões: se o PixelYourSite for Pro, ligar a CAPI com deduplicação por `event_id`.
      Se não for, seguir só com pixel. Não bloqueia.
- [ ] Domínio verificado e `Lead` priorizado na Mensuração de Eventos Agregados.
- [ ] Públicos criados **antes** de subir: visitantes da página 7d, `Lead` Black Recorde 7/14/30d,
      engajamento IG/FB 180d, vídeo 50% 60d, `Lead` da página +100K, lookalike 1–3%.

### Grupo de WhatsApp (a "segunda página de captura")

- [ ] **Limite de 1.024 membros por grupo do WhatsApp.** A meta pede mais de 1.000 entradas. Vai ser
      preciso **um segundo grupo** e um jeito de virar o link quando o primeiro encher: redirecionador
      com rotação ou troca manual do link na página. Definir antes de subir. Sem isso, a campanha
      paga entradas que batem em "grupo cheio".
- [ ] Nome do grupo = "Operação Black Recorde" (ou o nome validado) · foto da identidade · descrição
      com a data e o horário · mensagem de boas-vindas configurada · só admins enviam.
- [ ] Link do grupo nos dois CTAs da página, com a página testada no celular e no 4G.

### UTMs por peça

Parâmetros fixos em todos os anúncios (campo "Parâmetros de URL" do anúncio):

`utm_source=meta&utm_medium=paid_social&utm_campaign=blackrecorde_out26&utm_term={{adset.name}}&utm_content=<valor da tabela>`

| Peça | `utm_content` |
|---|---|
| B1 — A mesma promoção (vídeo Cindy) | `b1-mesma-promocao_vid` |
| B2 — Não começa em novembro (estático) | `b2-nao-comeca-novembro_est` |
| B2 — Não começa em novembro (vídeo, voz clonada) | `b2-nao-comeca-novembro_vid` |
| B3 — Sexta à noite (voz clonada + cenas) | `b3-sexta-a-noite_vid` |
| B4 — Os dois melhores meses (vídeo Cindy) | `b4-dois-melhores-meses_vid` |
| B5 — Mais um evento (vídeo Cindy) | `b5-mais-um-evento_vid` |
| B6 — Direcionamento (carrossel) | `b6-direcionamento_car` |
| B7 / B8 / B9 (a produzir) | `b7-faltam-2-dias_sto` · `b8-e-hoje_sto` · `b9-ao-vivo_sto` |

A UTM mede até a página. **A entrada no grupo não é atribuível por anúncio.** O WhatsApp corta o
rastro, e o `Lead` por peça é a melhor leitura disponível.

### Nomenclatura

| Nível | Padrão | Exemplo |
|---|---|---|
| Campanha | `CB_BLACKREC_2610_<FUNÇÃO>_<OBJETIVO>_<ORÇAMENTO>` | `CB_BLACKREC_2610_CAPTACAO_LEADS_ABO` |
| Conjunto | `AS<n>_<TEMPERATURA>_<PÚBLICO>_<IDADE>` | `AS2_FRIO-B_LAL1-3-BASE_25-60` |
| Anúncio | `<peça>_<slug>_<formato>_v<n>` | `B1_mesma-promocao_vid_v1` |

Usar o mesmo slug do `utm_content`, para cruzar o Gerenciador com o Analytics sem tabela de-para.

### Bloqueios que impedem subir (herdados do grid)

- [ ] Data e horário confirmados (B4 e B5 citam a data).
- [ ] Nome validado (só B4 cita o nome).
- [ ] Página publicada + link do grupo + segundo grupo definido.
- [ ] **Oferta e preço definidos até 22/10.** Não trava a mídia, mas trava a conta do §3 e a escala de closers.
- [ ] Autorização da Cindy para a voz clonada (B2 vídeo, B3).

---

*Buck · Media Buyer · modo co-piloto. Os números de custo por entrada e de conversão são premissas
até chegar o export do +100K. Com ele em mãos, refaço o §3 em 10 minutos.*
