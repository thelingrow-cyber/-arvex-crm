# 📋 SEMANA LINGROW — 08/09 a 14/09/2026

**Frente:** Lingrow — app de idiomas · **Owner:** Vitor
**Papel na semana:** 🎯 **caminho crítico** — decisão do Vitor em 07/09
**Estado:** app v1.0 no ar desde 17/04, **parado desde 17/08**. Ficha da loja escrita e esperando aprovação.
**Semana anterior:** `lingrow-semana-2026-08-03.md` — nenhum item do caminho crítico saiu em 5 semanas.

> Seleção do `docs/gestao/BACKLOG.md`. Nada aqui é item novo.

---

## 🔴 O caminho crítico de publicação — nesta ordem

### 1. LG-10 · Contrato de apps pagos Apple — 👤 · M · **segunda de manhã, antes de tudo**

Pessoa jurídica · DSA/UE · dados bancários · W-8BEN.

**Por que é o primeiro item da semana e não pode ser o último:** é a **única espera externa** do
caminho. A Apple leva dias para responder, e enquanto isso não está aprovado **o app não cobra** —
todo o resto (RevenueCat, monetização, ficha) fica em cima de um contrato inexistente. Cada dia que
não começa é um dia empurrado no fim, e este já esperou 5 semanas.

- [ ] Submeter o contrato

### 2. LG-12 · Decidir: 600 frases **ou** ajustar a promessa — 👤 · P · **~10 minutos**

**Não é uma tarefa, é uma frase escrita.** A ficha da loja (`app-store-ficha-2026-08.md`, 12/08)
está pronta com um único campo travado, e o documento diz por quê:

> *"contagem de frases travada enquanto a decisão LG-12 estiver aberta"*

Uma decisão de 10 minutos está segurando um documento de ASO inteiro há 26 dias.

- [ ] Decidir e escrever a resposta no doc da ficha

### 3. LG-14 · Aprovar a ficha da loja e os screenshots — 👤 · P · ↳ LG-12

Insumo **já pronto**, não é para escrever nada:

| | Onde |
|---|---|
| Título `Lingrow: Aprender Inglês` (24/30) | `app-store-ficha-2026-08.md` §1 |
| Subtítulo `Flashcards que não somem` (24/30) — **campo hoje vazio, 2º maior peso no ranking** | §2 |
| Keywords (97/100) | §3 |
| Descrição reescrita pela dor, não pelo método | §4 |
| Deck de screenshots (17/08) | `docs/marketing/app-store-screenshots/deck.html` |

- [ ] Ler, aprovar (ou marcar o que muda) e colar no App Store Connect

**Ganho imediato, independente do contrato:** a ficha está em v1.0 de 17/04 — quase 5 meses parada,
e recência pesa no ranking. Publicar a ficha nova não depende da Apple aprovar nada.

### 4. LG-09 · Aplicar a migration 008 no Supabase — 👤 · P · ~1h

`008_secure_app_config_secret.sql`. É pré-requisito de **LG-13 (QA no Expo Go)**, que abre a semana
seguinte. Faz-se em qualquer intervalo.

- [ ] Rodar no SQL Editor e confirmar que subiu

---

## 🤖 O que eu faço em paralelo *(cada um precisa de 1 aprovação sua)*

- [ ] **LG-01** Fechar o documento de linha editorial — o lote 01 de carrosséis (07/08) já provou os formatos na prática; falta virar documento para não depender de memória
- [ ] **LG-02** Escrever os roteiros a partir de LG-01 — alimenta LG-16 (build-in-public)
- [ ] **LG-05** Revisar o PostHog e ler onde as pessoas clicam de fato *(confirmar se "postgate" do backlog é isto)*

---

## 🧊 Fora desta semana, e por quê

| Item | Por quê |
|---|---|
| **LG-11** RevenueCat | ↳ LG-10. Só existe depois de o contrato ser **aprovado**, não submetido |
| **LG-13** QA manual no Expo Go | ↳ LG-09 e é M. Abre a semana seguinte |
| **LG-16 / LG-17 / LG-07** | Demanda antes de o app cobrar é queimar o contato mais caro que você tem |
| **LG-06** melhorias no produto | Escopo indefinido desde abril — não entra em semana nenhuma enquanto não virar lista |
| **LG-08** definir a métrica | Só faz sentido com o app publicado; hoje mediria o quê? |

---

## ✅ A semana valeu se

1. **O contrato Apple foi submetido** (LG-10)
2. **A ficha nova está no App Store Connect** (LG-12 + LG-14)

Duas coisas. Se só a segunda sair, a semana foi metade — porque o contrato é o que tem espera externa.
