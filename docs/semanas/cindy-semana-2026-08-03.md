# 📋 SEMANA CINDY — 03/08/2026

**Expert:** Cindy Batista — Nicho Ótica
**Semana:** 03/08 a 09/08/2026
**Owner:** Vitor + Gabriel
**Papel na semana:** é a frente que paga o mês. Prioridade quando houver conflito de tempo.

---

## 🔴 Prioridade Alta — Funil (dinheiro parado)

> O diagnóstico de 31/07 mudou a regra do jogo: **o tempo médio do cadastro ao fechamento é de 1 DIA** (o mais lento da história foi 13). Lead parado há mais de duas semanas já está fora da janela pelo padrão da própria operação.

- [ ] **Decisão binária nos 5 leads quentes parados há 17-19 dias** (todos da Cindy, origem "Respondi") — fechar ou enterrar, não deixar apodrecendo
- [ ] **Limpar os 21 leads do bolsão "contato" parados +15 dias** — saem do pipeline vivo
- [ ] **Instituir o ritual diário de funil** (~30 min/dia): todo lead que entrou ontem é tocado hoje. Sem isso, a janela de 1 dia é perdida por construção
- [ ] Fechar o gap nº1 do SOP (aberto desde 31/03): **cadência de follow-up até D+13**, não D+7 — o `sop-fluxo-vendas.md` está desatualizado
- [ ] Confirmar o valor real da venda da **Tamires** (entrou como placeholder no import de junho)

---

## 🟡 CRM — Gates abertos (destravar antes de construir mais)

- [ ] **GATE 1 — confirmar na tela que áudio e imagem tocam no Atendimento** (corrigido na edge v18, ninguém verificou). Falha nova aparece em `_evo_sync_debug` com `acao='media'`. **Não começar a Fase 3 antes disso**
- [ ] **GATE 2 — conferir o prompt da Carol no banco vs. o `.md`**: o separador `||` foi removido do `carol-system-prompt.md` em 02/08, e é ele que quebra a resposta em balões. Verificar (a) o que está em `agente_sdr.instrucoes`, (b) se o splitter tem fallback sem `||`
- [ ] **GATE 3 (P0 não verificado)** — o kernel do n8n checa `agente_pausado`? Se não checar, o botão "Assumir" é decorativo e a Carol responde por cima do humano. Exige abrir o n8n junto

## 🟡 CRM — Construção (só depois dos gates)

- [ ] **Fase 3 — enviar mídia pelo CRM** (anexo + gravar áudio). É o que decide se a Thalita usa o CRM ou volta pro celular
- [ ] **Fase 5 — usar `pushName` como nome quando não há lead** (metade do inbox mostra número cru). Vai junto com a Fase 3
- [ ] Preencher `owner_id` no resto da base — hoje 22 de 253; sem isso não existe leitura por closer

---

## 🟢 Marketing / Workshop

- [ ] **Trocar o Pixel Meta placeholder** na landing do Workshop Ótica Magnética — sem isso, tráfego pago é dinheiro cego
- [ ] Rodar o teste da **variante B** (`index-b.html`) — está pronta e nunca foi ao ar
- [ ] Definir a próxima edição do workshop (data + meta de inscritos)

---

## 📌 Contexto Estratégico

Funil real (253 leads): 25 fechados (9,9%), 154 perdidos (60,9%), 74 vivos, R$ 59.648 registrados. Ticket médio realizado R$ 3.314 — **abaixo do produto mais barato do SOP (R$ 5.000)**, sinal de parcela lançada como valor cheio ou registro incompleto. Campo `ticket` preenchido em só 8% da base, o que impede qualquer priorização por dinheiro.

**A alavanca da semana não é gerar mais lead — é não perder o que já entra.** 61% da base vira perdido; o gargalo é velocidade de resposta, não volume.

## Referências

- `docs/crm/diagnostico-funil-2026-07-31.md`
- `docs/crm/atendimento-inbox-PLANO.md` (fases, ACs, o que foi recusado do benchmark)
- `docs/agente-sdr/carol-system-prompt.md`
- `docs/landing-codigo-do-desejo/` (Workshop Ótica Magnética)
