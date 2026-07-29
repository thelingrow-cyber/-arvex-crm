# Loops, Goals e Schedule — a anatomia de um agente que trabalha sozinho — Alan Nicolas

> Fonte: vídeo curto Alan Nicolas (transcrição colada em 2026-07-29) · material extra prometido na descrição (doc de anatomia + prompts + árvore de decisão + simulador) — **não recebido ainda**
> Tipo: aula de método/operação de harness
> Destilado em: 2026-07-29 · com @aiox-master (Orion)

---

## 1. Resumo

- **A tese em uma frase:** se você não usa loop, **você é o loop**. Você vira o motorzinho humano que digita "sim, sim, não, sim" e fica refém do terminal — não pode fechar o notebook porque a IA pode parar esperando resposta. Loop bem-feito = você manda um áudio na rua, volta 2h depois e metade do trabalho está pronta.
- **Anatomia mínima (é só isso):** um **cron** (quando roda) + uma **condição** (se continua ou para). O harness lê o estado → decide continuar/parar → age (chama tools) → verifica. Analogia dele: despertador (roda todo dia às 8h; enquanto você aperta soneca, ele volta em 5 min; se aperta desligar, sai do loop menor e volta ao loop maior do dia). Máquina de lavar, microondas, iluminação pública — tudo é loop. Não nasceu ontem: AutoGPT/React em 2022-23 (modelos ruins na época), virou febre em 2025 com o "Half/Hive Loop".
- **As 3 primitivas e quando usar cada uma:**
  | Primitiva | O que encerra | Roda onde | Usar quando |
  |---|---|---|---|
  | **loop** | **ritmo/tempo** (a cada N min) | sua máquina | você sabe que aquilo precisa ser reverificado de X em X tempo |
  | **goal** | **condição/objetivo atingido** (julgado pela LLM) | sua máquina | você sabe o FIM que quer, mas não o caminho nem quantos passos |
  | **schedule** | rotina fixa recorrente | **nuvem/servidor** | você não vai estar com o computador aberto |
- **Loop fixo vs dinâmico:** intervalo fixo (5, 10, 40 min) verifica em janela travada. **Ele prefere dinâmico** — a própria LLM calcula quanto tempo aquilo costuma levar e escolhe quando acordar. Como ativar: **não passar o valor de tempo**; sem a variável, é dinâmico.
- **Goal > loop (a opinião mais forte da aula):** o goal é regido pelo objetivo, não pelo relógio; e **um goal cria loops internos sozinho** pra chegar ao fim. Diferença visual: goal trabalha **sem parar** até terminar; loop trabalha → dorme → acorda no despertador. Nuance boa: se o despertador toca e ele **ainda está trabalhando**, não recomeça — pula aquele ciclo e continua de onde parou (só acorda de verdade se estiver dormindo).
- **A regra prática mais acionável: não escreva você o prompt do loop — peça pra IA criar.** Ela conhece a mecânica melhor que você e vai gerar um goal muito mais rico. O prompt dele, na íntegra, foi só: *"crie uma meta que continuará aplicando, revisando e aplicando de novo, desde que não comprometa dados importantes ou o funcionamento da aplicação"* — e a IA devolveu um goal detalhado (revisão profunda, aplicação incremental, priorizar falhas confirmadas), que rodou **4h+** sozinho. Contra-exemplo de meta que você não saberia escrever: *"reduz o tempo de resposta do endpoint /search para menos de 200ms com critério de benchmark X"* — você não sabe que é 200ms; a IA sabe.
- **O caso de uso que ele demonstrou ao vivo: matar doc rot.** Doc rot = documentos velhos e desatualizados que continuam sendo injetados na janela de contexto, fazendo a IA reler decisões antigas e **causar regressão** — você pede coisa nova e o resultado piora. O goal dele: enquanto houver documento incoerente com o código, limpa/edita e continua procurando; quando não achar mais nada, para. Resultado relatado: **+100 arquivos mortos eliminados**, testes passando, CodeRabbit em paralelo.
- **Os avisos (metade da aula é aviso, não hype):**
  - "A maioria dos loopings que você criar vai **só torrar token**." O que OpenAI/Anthropic mais querem é você rodando loop.
  - **Quanto mais tempo roda sem critério de parada bem definido, mais a IA regride e estraga o código.** Não use loop/goal se você não sabe muito bem o que está fazendo.
  - Condição mal definida = **roda eternamente**.
  - **Desative workflow/ultra-code e cuidado com subagentes** dentro de goal: multiplica consumo sem garantir o objetivo.
  - Claude, segundo ele, **cai em execuções longas** (erros de API — ele mostrou dois na própria tela e teve que pedir "continue"); ele não confia nele pra rodar horas.
- **Comparativo dele entre ferramentas** *(opinião/afirmação do autor — ver "não verificado" abaixo)*: **Codex 5.6 (sol)** = melhor em maratona (5-12h) e "caxias"/criterioso; **Grok** = melhor juiz de objetivo (usa outra LLM pra escrever o goal e **6 checagens** com outro modelo pra validar se cumpriu) e nem deixa você escrever o prompt na mão; **Claude** = onde a prática nasceu, tem as 3 primitivas, mas instável em long-run. Codex e Grok só têm goal (Grok tirou o loop recentemente).
- **Limite citado:** loop vive no máximo **7 dias** (depois morre e você recria); pra recorrência maior, schedule. Ele nunca passou de ~4 dias.

---

## 2. Delta de aplicação — o que muda pro MEU sistema

**Primeiro, a checagem que a aula não faz: o que existe DE VERDADE no meu Claude Code hoje.** Conferi na instalação deste repo, não na palavra do Alan:

| O que a aula diz | O que eu tenho aqui (verificado) |
|---|---|
| `/loop` com intervalo | ✅ existe — `/loop 5m <prompt>` |
| Loop **dinâmico** (LLM escolhe quando acordar) | ✅ existe — `/loop <prompt>` **sem** intervalo; o agendamento é feito via `ScheduleWakeup` |
| `/goal` (barra meta) | ❌ **não existe como comando nesta instalação.** O mais próximo é o `/loop` dinâmico |
| `/schedule` na nuvem | ✅ existe — routines em cron (inclui execução única) |
| "loop dura 7 dias" | ⚠️ não verificável aqui |
| "modelo inferior lê o estado e julga se atingiu" / "Grok faz 6 checagens" | ⚠️ afirmação do autor, não verificada |

**Precisão que vale mais que a aula inteira, pro meu caso:** o wakeup do loop dinâmico é **limitado a 1 hora** por ciclo. Então o exemplo dele de *"a cada 2 horas organiza meu desktop"* **não** se faz com loop dinâmico aqui — isso é `/schedule`. Regra prática que tiro disso: **intervalo ≤ 1h → loop; > 1h ou laptop fechado → schedule.**

**Onde isso aterrissa no que eu já opero:**

1. 🎯 **O caso do doc rot é o MEU caso, não o dele.** `docs/` deste repo acumulou camada geológica: specs de fases já entregues, Epic 3/Carol-Railway **abandonado por pivô**, arquiteturas de coisas que mudaram de dono (Viziom multi-tenant descartado), aulas, dossiês encerrados (óculos anti-scroll = NO-GO). Isso é exatamente o material que volta na janela e me faz reler decisão morta como se fosse viva.
2. 🔴 **MAS: goal autônomo que deleta arquivo é a receita do meu pior incidente.** Já tomei o despejo de 76k linhas no banco por automação com escopo mal definido, e a regra que ficou foi *travar antes de agir*. Loop que apaga documentação sem revisão humana viola isso frontalmente. **Se eu rodar doc rot, roda em modo relatório** (lista candidatos + justificativa), eu aprovo, aí deleta.
3. ✅ **O encaixe perfeito, risco zero, valor alto: a divergência repo × produção.** Tenho um alerta *recorrente* de que master/main e o que roda em produção divergem sozinhos, e eu sempre descubro **tarde**, no meio de outro diagnóstico. Isso é literalmente uma condição verificável em intervalo, read-only, sem poder de escrita: comparar e me avisar. É o schedule que eu deveria ter criado há um mês.
4. 🧠 **"Peça pra IA criar o loop" bate com o que eu já pratico** — decidir e executar, não pedir menu. Reforça: eu descrevo a **dor**, o agente escreve o critério de parada.
5. ⚠️ **"Desative subagentes/workflow em goal"** confirma, por outro caminho, a regra que já está no meu harness (não spawnar subagente sem pedido). Loop + subagente livre = torrar token em paralelo.

**Ruído pra mim agora:** os 120 agentes simultâneos, a história AutoGPT/React 2022-23, o ranking Codex-vs-Grok-vs-Claude (eu opero Claude Code; ranking não muda minha ferramenta), a demo "organiza meu desktop", o pedido de engajamento e as 5 aulas avançadas do upsell.

**Pendência de material:** ele promete na descrição o doc de anatomia, os prompts prontos (babá de PR, acompanhar deploy, manter branch integrável, subir cobertura, zerar dívida de tipos), a árvore de decisão e o simulador. **Não tenho esses arquivos.** Se chegarem, vão pro `inbox/` — os prompts prontos são a parte reutilizável.

---

## 3. Ação aplicada

- ✅ Destilado criado (aula veio colada no chat, não passou pelo `inbox/`).
- 🎯 **Ação âncora proposta (1 só, em série):** criar **um `/schedule` diário read-only de sanidade repo × produção** — compara master/main com o que está no ar (index.html + edge functions do arvex-crm) e me entrega um relatório curto com as divergências. Escopo: **só leitura e relatório, zero escrita, zero deploy.** É o loop de menor risco e maior retorno do meu contexto, e ataca um alerta que já me custou tempo mais de uma vez.
- ⏳ **Backlog (não fazer agora — 1 build por vez):** goal de doc rot em `docs/`, obrigatoriamente em modo *report-only* na primeira rodada.
- ❌ **Descartado:** rodar goal longo com permissão de escrita/delete sem revisão. Incompatível com as travas que eu mesmo instalei depois do incidente das 76k linhas.
