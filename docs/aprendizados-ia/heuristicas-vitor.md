# Heurísticas do Vitor — Catálogo v1

> Extraído de 780 mensagens reais em 39 sessões (ARVEX, AIOX/Lingrow, SAASOPTICO, SecondBrain) · @analyst (Atlas) com Fable 5 · 2026-07-05
> **Escrito para IA consumir.** Cada heurística: gatilho → regra → evidência. Use como lente de decisão em QUALQUER tarefa para o Vitor.

---

## A — Páginas, produto e visual (onde o modelo mais falhou)

### A1. Referência é contrato, não inspiração
**Gatilho:** Vitor manda print/link de referência.
**Regra:** Replicar a estrutura da referência fielmente e só trocar o conteúdo. NÃO "melhorar", NÃO adicionar elementos, NÃO mudar proporções. Desvio da referência = retrabalho garantido.
**Evidência:** *"te mandei tanta referencia […] muita coisa ficou ruim"*, *"olha as refencias, nao acha melhor seguir ela?"*, *"headline ridiculamente grande, alem de nao ta a mesma copy que combinamos"*.

### A2. Mobile é o juiz
**Gatilho:** qualquer página/UI entregue.
**Regra:** Validar no viewport mobile ANTES de entregar. Vitor testa por print de celular; corte após botão, linha fantasma, headline estourando = reprovação. Primeira dobra mobile deve conter headline+CTA sem scroll.
**Evidência:** *"foca no mobile"*, *"print do celular"*, *"mudei e ficou a mesma coisa […] no mobile"*.

### A3. Correção de UI é micro-passo, nunca pêndulo
**Gatilho:** feedback tipo "um pouco mais escuro/claro/menor".
**Regra:** Aplicar ajuste PEQUENO (5-15%), nunca inverter para o extremo oposto. Ele calibra por iteração fina.
**Evidência:** *"um pouco mais escuro, so um ppuco"*, *"agora tu deixou ela mais escura do que a parte de cima"* (pêndulo = erro).

### A4. Cirurgia, não reforma
**Gatilho:** pedido de alteração pontual.
**Regra:** Mexer SÓ no que foi pedido. Trocar logo/paleta/copy não solicitados quebra confiança.
**Evidência:** *"voce nao entendeu, nao é para trocar a logo […] so a mesma paleta, e a headline é a mesma so para readaptar"*.

### A5. Integrado > flutuando
**Gatilho:** foto/elemento em página.
**Regra:** Foto integrada ao fundo (máscara, degradê SUAVE, mesma tonalidade entre seções). Cutout flutuando = "amador". Transição brusca = refazer.
**Evidência:** *"ta horrivel a foto dela ali flutuando"*, *"faça que essa transição do botao para a foto seja mais suave"*, *"deixe com a mesma tonalidade da foto para parecer uma so sessao"*.

### A6. Headline: benefício + mecanismo + emoção, tangível e curta
**Gatilho:** escrever/avaliar headline ou copy.
**Regra:** Avaliar por esse trio explícito. Valor tangível (número: "100k", "2X em 5 dias"). Curta. Clareza > "premium".
**Evidência:** *"cmo avalia essa headline? tem beneficio, tem mecanismo e tem emoção? para de ficar pensando que tudo tem que ser premium"*, *"a headline tem que ser mais tangivel com algum valor"*.

### A7. Página se julga por conversão, não por beleza
**Gatilho:** avaliar/redesenhar landing.
**Regra:** O critério é dado real de tráfego (leads→entradas). Se conversão ruim: simplificar (1 seção, menos atrito), não embelezar.
**Evidência:** *"16 leads marcados mas so 8 entraram, algo esta errado"*, *"a conversao ta bem ruim […] vou mandar 2 referencias"*.

---

## B — Trabalhando com o Vitor (protocolo de sessão)

### B1. Retomada = recuperar estado ANTES de agir
**Gatilho:** sessão nova com "lembra de X?", "qual etapa estamos?", "puxe o status".
**Regra:** Buscar em memória/git/docs o estado real e apresentar em 3-5 linhas ANTES de propor qualquer coisa. Não achar = esforçar ("se esforce para encontrar isso"), nunca fingir.
**Evidência:** ~12 sessões abrem assim; *"acordei, voltei, resumo o q fez"*.

### B2. "Commit, vou fechar" = ritual de checkpoint
**Gatilho:** *"commit"*, *"vou fechar a sessao"*, *"nao quero esquecer de nada"* (aparece 15+×).
**Regra:** Commit imediato com mensagem descritiva + confirmar em 1 linha o que foi salvo e o ponto de retomada. Sem discurso.

### B3. Pergunta curta = resposta curta
**Gatilho:** *"foi?"*, *"deu certo?"*, *"ja ta la?"*, *"cade?"*.
**Regra:** Responder em 1-3 linhas: status + próxima ação se houver. Parágrafos aqui = ruído.

### B4. Nunca declarar consertado sem evidência
**Gatilho:** bug reportado (especialmente com print).
**Regra:** Investigar causa-raiz, corrigir, VERIFICAR de fato, e mostrar a evidência. Afirmar "resolvido" sem prova é a quebra de confiança mais grave.
**Evidência:** *"como podemos resolver isso sem mentir? analisar mesmo o problema?"*, *"nao arruma isso nunca, meu deus, arrume isso, acione o agente correto"*.

### B5. Ações manuais fora do terminal: 1 passo literal por vez
**Gatilho:** WordPress/Elementor, FTP, Play Console, App Store, painel Supabase, Meta — qualquer coisa que ELE executa na tela dele.
**Regra:** UM passo por mensagem, com o texto/valor EXATO para colar, no formato Windows (`set VAR=x`, caminhos com aspas). Ele cola o resultado; aí vem o próximo passo. Blocos de 10 passos = erro dele no passo 2.
**Evidência:** *"me passe 1 por 1"*, *"manda aqui o certinho que eu subo"*, *"porra, me passa certinho o que tenho que colocar ali"*; erros reais com `set`/caminhos no cmd.

### B6. Ausência anunciada = loop autônomo com auto-revisão
**Gatilho:** *"vou dormir"*, *"vou deitar"*, *"não vou poder aprovar"*.
**Regra:** Montar execução autônoma completa (fazer → revisar → melhorar → commitar), zero permission prompts, relatório pronto pra quando voltar.
**Evidência:** *"quero que seja em loop […] preciso disso pronto enquanto durmo"*, *"nao me peça permição de nada, nada"*.

### B7. Squad certo, e ele quer VER a escalação
**Gatilho:** tarefa multi-etapa.
**Regra:** Nomear o agente/especialista que assume ("estou falando com o melhor agente para isso?"). Ele confia mais quando a orquestração é explícita: quem faz o quê, em que ordem.
**Evidência:** *"escale o time completo na ordem certa"*, *"ative os agentes e encadeamento certo"*, *"chame o agente mais qualificado"*.

### B8. Token é dinheiro
**Gatilho:** tarefa que não exige o modelo topo / leitura de material bruto grande.
**Regra:** Usar/recomendar a via mais barata que entrega ~o mesmo, e AVISAR proativamente ("essa tarefa dá pra fazer com Sonnet"). Material bruto grande → subagente lê, contexto principal recebe só o destilado.
**Evidência:** *"que isso, tanto tokens para isso?"*, *"me avisa quando alguma tarefa for melhor aplicar com outro modelo que gaste menos e entregue quase o mesmo"*, *"consegue um demo sem gastar token?"*.

### B9. Typos são ruído, intenção é sinal
**Gatilho:** mensagem rápida com erros de digitação ("camonho cerrto", "coomit", "healine").
**Regra:** Interpretar a intenção e agir. Só pedir esclarecimento quando a AMBIGUIDADE muda o resultado — nunca pelo typo em si.

---

## C — Decisão de negócio (como ele pensa)

### C1. Uma recomendação, decisão em segundos
**Gatilho:** encruzilhada de caminho.
**Regra:** Apresentar 1 recomendação com o porquê (máx. 2 alternativas se genuíno trade-off). Ele responde "vamos de A", "mete bala". Menu longo/re-litigar = *"ja esta chato, quero definir isso de uma vez"*.

### C2. Ownership > aluguel
**Gatilho:** decisão build vs buy vs assinar.
**Regra:** Default dele: possuir a infra/ferramenta (plugin próprio vs Tactiq, servidor próprio, "supabase é meu", "posso baixar depois ne?"). Recomendar aluguel só com razão forte.

### C3. Simplicidade corta camada
**Gatilho:** arquitetura com peça intermediária (n8n, serviço extra).
**Regra:** Perguntar "funciona sem?". Se sim, cortar. *"precisa mesmo do n8n? o claude nao consegue fazer tudo isso? nao podemos apenas usar o supabase?"* — mas com a trava dele: *"só corte se de fato todo o sistema funcionar sem ele"*.

### C4. Ship primeiro, polir depois — com teste grátis antes de cobrar
**Gatilho:** lançamento/feature nova.
**Regra:** Subir a versão funcional já ("sobe logo para a principal mesmo sem demo, qualquer coisa eu resolvo"), liberar grátis por dias pra validar, depois cobrar. Perfeccionismo trava = inimigo.

### C5. Estratégia fala por analogia de players reais
**Gatilho:** discussão de posicionamento/oferta/modelo.
**Regra:** Ancorar propostas em players que ele referencia: G4 (Tallis/Alfredo), Érico Rocha, Tay Dantas (Vincy Society), Hormozi, Duolingo. Proposta abstrata sem âncora não gruda.

### C6. Lead/cliente se julga pelo caixa e qualificação, sem dó
**Gatilho:** negociação, oferta, precificação.
**Regra:** Ancorar alto e iterar (12k→5k→2500 piso); desqualificar rápido quem não sustenta o valor (*"pra pagar 1000? muito desqualificada"*). O caixa da operação vem primeiro (*"preciso desse dinheiro para rodar a operação"*).

### C7. Dispersão é a ameaça — e ele sabe
**Gatilho:** ele mesmo abre a 3ª frente na mesma sessão ("RAPIDINHO MUDANDO DE ASSUNTO…").
**Regra:** Atender o desvio rápido E devolver o foco explicitamente ("voltando ao X, estávamos em Y"). Ele agradece o freio: *"vamos voltar ao foco"*. Ideia nova → registrar em memória/backlog, não abrir build paralelo.

---

## D — Meta

- **Fonte:** corpus em scratchpad (`corpus-vitor.txt`, 667k chars) — regenerável com `extract-user-msgs.js`.
- **Atualização:** repetir extração a cada ~1-2 meses ou quando surgir fricção nova recorrente; heurística nova entra aqui + vira memória se mudar comportamento do agente.
- **Relação com memórias:** A1/A5→[[feedback_landing_pages]] [[feedback_landing_cindy_sistema_visual]] · B6→[[feedback_autonomia_deploy]] · B7→[[feedback_rigor_squad_agentes]] · B8→[[feedback_destilar_material_grande]] [[feedback_reusar_nao_recriar]] · C1→[[feedback_velocidade_paginas]] · C7→[[project_ecossistema_venture_builder]].
