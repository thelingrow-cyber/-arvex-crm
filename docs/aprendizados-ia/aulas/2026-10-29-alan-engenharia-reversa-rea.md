# Engenharia reversa com IA (REA) — Alan Nicolas

> Fonte: transcrição da live (~3h) "engenharia reversa de qualquer sistema", recebida em 2026-10-29
> Tipo: aula de método + demonstração ao vivo + venda do app dele (MUR)
> Destilado em: 2026-10-29 · @aiox-master (Orion)

---

## 1. Resumo

### A tese
A técnica de engenharia reversa já existia (Ghidra, Hopper, descompiladores). O que a IA mudou foi a **velocidade**: um trabalho que levava anos agora leva horas. Com isso, **duplicar ficou barato, e o difícil passou a ser manter e distribuir.** Ele usa a analogia da cozinha: todo mundo sabe cozinhar e, mesmo assim, pede iFood.

**Onde fica o fosso (moat) agora:** distribuição, rede já montada (o iFood tem restaurantes, motoboys e usuários) e o **back-end**, que dá para inferir mas não para copiar. O código do front deixou de proteger qualquer coisa.

### O uso que importa: modelar a inteligência, não copiar o ativo
O melhor exemplo da live é o Tower Defense. Ele desmontou os 3 jogos do gênero que mais venderam, pôs outra IA para achar o que eles tinham em comum (**mais de 800 padrões**) e transformou isso num **framework próprio**. Não usou nenhum asset, animação ou script deles. Usou só o padrão.
- Mesma lógica no marketing: fazer a engenharia reversa da página, dos anúncios, da sequência de e-mails e do ticket de quem já vende.
- No app de tokens dele, primeiro fez da própria cabeça. Depois desmontou os 3 concorrentes mais próximos para tirar ideias e leu **mais de 2.000 issues do GitHub** para descobrir do que os usuários reclamam.

### As 5 formas de fazer engenharia reversa (da mais leve à mais pesada)

| # | Fonte | Quando usar | Quanto chega perto |
|---|---|---|---|
| 1 | **Wiki de fãs + 5 vídeos de gameplay** (a IA compara o que construiu com o vídeo) | jogo sem acesso ao binário | ~80% do que importa (mecânica, regras) |
| 2 | **Documentação pública + conta própria navegando** (a IA loga, tira prints, lê HTML/JS, nomes de campos e formulários) | SaaS (o exemplo foi o Salesforce) | o front inteiro; o back só por inferência |
| 3 | **Vídeo do site** (posts no X de quem não divulga a URL) → "refaça esse site igual ao vídeo" | landing, site com efeitos | alto, sem precisar de skill nenhuma |
| 4 | **Baixar o site** (a skill `swipe` dele) → estudar o código e reescrever com assets próprios | efeito visual específico | fiel ao efeito |
| 5 | **Binário** (APK, jogo da Steam) → REA / descompilador | app nativo, jogo | completo, mas o HD explode (600 MB viram 20-60 GB) |

Demo ao vivo: um APK de Bíblia (Kotlin) virou um app nativo de Mac em Swift com **um prompt de uma linha**. Levou 51 min e gastou cerca de 1,5% da cota semanal do plano de US$ 200.

### Regras práticas
- **Modelo:** use Opus, Fable ou Astra. Haiku, Luna e Sol erram nas decisões de qual ferramenta chamar. Em cerca de 20 tentativas com o Sol, o resultado não saiu como ele queria.
- **Diga o objetivo no prompt** ("quero uma versão nativa para Mac"), senão a IA faz engenharia reversa só por fazer.
- **Não precisa de 100%:** em um jogo, de 40% a 50% dos arquivos eram proteção anti-engenharia-reversa (caminhos que não levam a lugar nenhum). Ele reconstrói mais leve: o GTA passou de 2 GB para 300 MB.
- **Gemini** é o melhor para **otimizar 3D e imagem sem perder qualidade** (trajes de 742 MB caíram para 135 MB). No resto, ficou abaixo dos outros.
- **Tarefa mecânica vai para o modelo barato:** o swipe (baixar site) ele roda no Grok, não no Claude.
- **Validar contra a referência:** a IA compara o que construiu com a fonte (vídeo de gameplay, print do efeito).

### Cérebro alimentado pela IA
A cada tarefa, a própria IA grava um **aprendizado curto** (arquivos `.md`, não banco de dados: "a IA trabalha melhor com arquivos"). Exemplo: "porte para Safari no iPhone → cuidado com X". O cérebro é **para a IA, não para ele**, comprimido para gastar poucos tokens. Ele tem cérebros separados por domínio: games, sem dados pessoais, e o **jurídico**, onde ficam os dados pessoais, com acesso só via script e assinatura dele a cada uso. O Obsidian serve só para visualizar.

### Onde vai o dinheiro (MUR, o app que ele estava vendendo)
- Ver, por projeto e somando todos os provedores, quantos tokens foram gastos e qual a **relação entre o que a assinatura entrega e o que custaria em API**. Ele cancelou o plano de US$ 300 do Grok, que equivalia a US$ 10 de API.
- Detector de desperdício: por exemplo, "o Python falhou 29 vezes num caminho que não existe = 4M de tokens". A saída disso vira regra no CLAUDE.md/AGENTS.md ou um script.
- **Um processo que deu certo com o Opus vira skill → o Sonnet repete mais barato.**
- Ele tem mais de 200 heurísticas próprias, e por isso a IA dele "não faz mais perguntas".

### Segurança (dica que ele deu)
Houve vazamentos recentes (Railway, GitHub, sites em PHP/WordPress). Ele teve um gasto indevido de cerca de US$ 2.000 em API por causa de uma chave antiga. A dica: **apagar todas as chaves de API e gerar de novo.**

---

## 2. Delta de aplicação — o que muda para o MEU sistema

| A aula ensina | Onde eu estou |
|---|---|
| Modelar o padrão de vários líderes → framework próprio | **Viziom** precisa disso contra os CRMs de ótica (VZ-18 está parado esperando eu escolher o concorrente) |
| Documentação + conta navegando (forma 2) | É exatamente o escopo do REA que eu já cadastrei (web/JS, sem binário) |
| Vídeo/print → recriar o efeito | Landings (Cindy, Workshop): hoje eu mando URL e descrevo. Mandar **o vídeo** da referência é mais fiel |
| Ler as issues/reclamações dos concorrentes | Viziom: ler as avaliações dos CRMs de ótica (Google Play, Reclame Aqui) antes da spec |
| Cérebro que a IA alimenta sozinha | Meu `MEMORY.md` + memórias de feedback já fazem isso; falta separar por domínio |
| Mais de 200 heurísticas | Eu tenho 23 em `heuristicas-vitor.md` |
| Processo bom vira skill → modelo barato | Bate com `project_squads_tasks_executaveis` (109 tasks declaradas, só 1 existe) |
| Trocar todas as chaves | **A Carol rodou na Railway**, que vazou. Há chaves antigas lá |

**Sinais acionáveis:**
1. 🔴 **Segurança, hoje:** revisar as chaves que passaram pela Railway (Carol/Epic 3) e qualquer chave antiga (Supabase service role, Evolution, Zernio, Groq, Kie). Gerar de novo as que estiverem expostas, sempre por env/secret local, nunca colando no chat (`feedback_processo_deploy_secrets`).
2. 🎯 **Viziom / VZ-18:** usar a forma 2 (docs + conta + avaliações) em 2 ou 3 CRMs de ótica, e com isso tirar um **framework de padrões**, não uma cópia.
3. 🖼️ **Landings:** passar a mandar vídeo ou print da referência e pedir "fidelidade ao efeito, com assets próprios".
4. 🧠 **Heurísticas:** o catálogo de 23 pode crescer extraindo das conversas salvas (a mesma ideia do Fable de 03/07, ainda não feita).

**O que NÃO adotar (e por quê):**
- As táticas de **contornar a recusa do modelo**: dar ESC duas vezes, "é só experimento local" e depois publicar, pôr senha e pedir a outro modelo para tirar, apagar memórias para a IA "esquecer" que recusou. Isso é enganar a ferramenta para fazer o que ela sinalizou como problema, e o risco jurídico fica comigo. Se a IA recusa, a pergunta certa é **se aquilo deveria ser feito.**
- Uma skill de swipe que **ignora robots.txt e passa por Cloudflare/anti-bot.** Isso fere os termos de uso. A regra da casa no REA continua valendo: entender não é copiar; respeitar os termos.
- Publicar app ou jogo derivado com assets ou marca de terceiros (o GTA na web dele vai cair). Para mim, só serve o uso "modelar o padrão".
- Agente com cartão de crédito ou que se passa por mim em atendimento: não é para agora.

**Ruído agora:** GTA, games, a casa 3D, o óculos VR, a futurologia de agentes que compram roupa, a venda do MUR.

---

## 3. Ação aplicada

- [ ] **Segurança:** listar as chaves que já passaram pela Railway e gerar de novo as expostas. Precisa do Vitor no painel de cada provedor.
- [ ] **VZ-18:** o Vitor escolhe 1 CRM de ótica concorrente e 1 funcionalidade, e roda a 1ª análise (forma 2) com o REA.
  - Obs.: em 29/10 o MCP `rea` falhou ao conectar (timeout), então é preciso reconectar antes.
