# 📋 SEMANA VIZIOM — 03/08/2026

**Produto:** Viziom — SaaS do nicho óptico (CRM + WhatsApp + IA + campanhas)
**Semana:** 03/08 a 09/08/2026
**Owner:** Vitor
**Papel na semana:** é o ativo (produto), não o caixa. A semana serve para **responder se ele está vivo**, antes de investir mais.

---

## 🔴 Prioridade Alta — Responder o gate que trava tudo

- [ ] **G4: existe ótica usando o Viziom de verdade hoje?** Levantar número real (contas ativas, último login, mensagens trocadas) — não impressão
  - Sem esse número, não dá para vender o produto nem decidir o beachhead da agência
- [ ] Decidir com base na resposta: **operar agora** (tem uso → vender) ou **parquear** (não tem → congela e volta depois do caixa)

---

## 🟡 Se for operar — Comercial

- [ ] Definir o que exatamente se vende: pacote, preço, prazo de implantação
- [ ] Definir quem vende (você, Gabriel ou closer) e de onde vêm os leads de ótica
- [ ] Primeira lista de óticas-alvo *(a Cindy é a ponte — ver gate G3: ela sabe da jogada?)*

## 🟡 Se for operar — Marca / Instagram

- [ ] Linha editorial do @viziom (dono de ótica é o leitor, não o infoprodutor)
- [ ] Primeiros posts / bio / destaque de prova

---

## 🔒 Infra e Segurança (independe da decisão acima)

- [ ] **Rotacionar a API Key Global do Evolution** — ela apareceu em texto no chat em 14/07 e nunca foi trocada (mesmo padrão do ADR-3.3)
- [ ] Mapear o que a ARVEX depende da infra Viziom hoje: `wpp.viziom.io` (Evolution), `back.viziom.io` (n8n, webhook real), `app.viziom.io` (SaaS HUBLABEL)
  - **Risco:** o atendimento da Cindy roda em cima dessa infra. Se o Viziom for parqueado, isso não pode cair junto

---

## 📌 Contexto Estratégico

O motor de IA **já foi extraído** — a Carol no `arvex-crm` (F1+F2 publicados, IA respondendo) é o resultado disso. Essa parte está feita e é da frente CINDY, não daqui.

**Multi-tenant no `arvex-crm` está descartado** (decisão de 07/07, over-engineering para o momento). Não reabrir F5 nem framing de "óticas-clientes" dentro do CRM da ARVEX sem pedido explícito.

O que resta de Viziom como projeto próprio é: **produto revendável + marca + IG**. E isso depende inteiramente de haver uso real. Uma semana inteira aqui sem responder o G4 é a definição de dispersão.

## Referências

- `docs/crm/VIZIOM-INTEGRATION-PLAN.md` (F0-F4 — F5 desatualizado, ignorar)
- `docs/ecossistema/hipotese-agencia-ia-vertical.md` (gates G1-G6)
