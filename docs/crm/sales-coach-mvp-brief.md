# Project Brief — Sales Coach (Sales Intelligence) · MVP

**Módulo do arvex-crm** · Autor: @pm (Morgan) · Data: 2026-06-27 · Status: Brief aprovado p/ arquitetura

---

## 1. Objetivo
Dar ao closer, depois de cada reunião, uma **análise objetiva e coaching personalizado** — e acumular um **dataset de reuniões reais rotuladas por resultado** (ganhou/perdeu/ticket). O dataset é o ativo de longo prazo; o coaching é o valor imediato.

**Não é** gravador nem transcritor. É um sistema de melhoria contínua de vendedores, dentro do CRM que já existe.

## 2. Usuários
- **Closer** (Cindy/ARVEX): sobe a transcrição, recebe nota + coaching, acompanha sua evolução.
- **Vitor / CS**: confirma o resultado da reunião e acompanha o time.

## 3. Escopo do MVP

### IN (entra)
1. **Sales Brain** — base de conhecimento indexada (playbook Cindy + frameworks) em Supabase + pgvector.
2. **Upload manual de transcrição** (texto) — funciona em PC e celular.
3. **Pipeline de análise** — n8n monta prompt com contexto do Brain → Claude → resultado estruturado.
4. **Notas por dimensão** + acertos/erros/sugestões.
5. **Persistência** — reunião + scores + insights + **tag de resultado**.
6. **Dashboard** — nova aba "Reuniões/Coach": lista, detalhe da call, evolução do closer.

### OUT (fica pra depois — explícito)
- Extensão Chrome própria de captura (Fase 2)
- Captura/envio automático (Fase 2)
- Transcrição por áudio (Whisper + diarization) (Fase 2/3)
- Comparação entre closers (Fase 3)
- Coach pré-call (Fase 4)
- Co-Pilot tempo real (Fase 5)
- Multi-nicho (advogados, médicos etc.)

## 4. Requisitos Funcionais (FR)
- **FR1** — O closer pode criar uma "Reunião" colando/subindo a transcrição em texto, associando: lead/cliente, data, produto apresentado.
- **FR2** — No momento do upload, o closer marca o **resultado**: `ganhou` / `perdeu` / `em aberto`, e (se ganhou) o **ticket** vendido.
- **FR3** — O sistema dispara a análise (n8n → Claude) usando o **Sales Brain** como contexto.
- **FR4** — A análise retorna **notas (0–10) por dimensão**: rapport, diagnóstico, escuta, construção de valor, controle da reunião, fechamento, transição, tratamento de objeções.
- **FR5** — A análise retorna texto estruturado: **3 acertos**, **3 erros**, **o que faltou (perguntas)**, **sugestões práticas**.
- **FR6** — Tudo é persistido no Supabase (reunião, scores, insights, resultado, ticket, closer).
- **FR7** — Aba "Reuniões/Coach" no CRM: (a) **lista** de reuniões com nota geral + resultado; (b) **detalhe** da call com notas + insights; (c) **evolução do closer** (média por dimensão ao longo do tempo).
- **FR8** — O Sales Brain pode ser alimentado (ingestão) com documentos do playbook/frameworks (admin/Vitor).
- **FR9** — Vitor/CS pode **confirmar/ajustar** o resultado de uma reunião (validação do rótulo).

## 5. Requisitos Não-Funcionais (NFR)
- **NFR1 — Custo:** análise deve custar centavos/reunião (Claude; sem transcrição paga no MVP).
- **NFR2 — Privacidade:** transcrições contêm dados de clientes reais. Acesso restrito por papel (closer vê o seu; Vitor/CS vê tudo) — reusar RLS/roles do CRM existente. Não expor dados a terceiros além da API do LLM.
- **NFR3 — Reuso:** módulo dentro do arvex-crm (login, banco, deploy existentes). Zero produto novo separado.
- **NFR4 — Tempo de análise:** resultado disponível em até ~2 min após upload (assíncrono, sem travar a UI).
- **NFR5 — Consistência da nota:** mesma transcrição → notas estáveis (prompt determinístico, temperatura baixa, rubrica fixa).

## 6. Riscos
- **R1 (ativo) — Disciplina de rótulo:** se o resultado (ganhou/perdeu/ticket) não for preenchido com rigor, o fosso não se forma. Mitigação: rótulo obrigatório no upload (FR2) + confirmação (FR9).
- **R2 — Qualidade/consistência da nota da IA:** rubrica precisa ser explícita e calibrada. Mitigação: rubrica fixa por dimensão no prompt; revisar com casos reais.
- **R3 — Backend novo (n8n) no fluxo do CRM estático:** integração CRM↔n8n↔Supabase precisa de chave/segurança. Decisão do @architect.
- **R4 — Privacidade de dados de cliente** (NFR2): garantir RLS e não vazar transcrição.

## 7. Critérios de sucesso do MVP
- **Hoje (fatia vertical):** 1 transcrição de teste é analisada e aparece no CRM com notas + insights + resultado.
- **Validação real (próximos dias):** ≥10 reuniões reais de closers analisadas e rotuladas; o closer reconhece o coaching como útil.
- **Ativo iniciado:** todas as reuniões no banco têm resultado preenchido.

## 8. Próximo elo
**@architect (Aria):** desenhar arquitetura — modelo de dados (tabelas + pgvector), fluxo n8n, arquitetura do prompt/rubrica, integração com o CRM estático e segurança (chaves, RLS). Depois → @data-engineer (DDL) → @ux (UI da aba) → @sm (stories) → @dev.
