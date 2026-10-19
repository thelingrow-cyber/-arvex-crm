# Agente da função — o orquestrador não executa trabalho especializado

Pedido do Vitor (19/10/2026): **quando ele pedir algo de uma função, ou pedir para melhorar algo, ative o agente correto
dessa função.** O aiox-master (Orion) e o Claude sem persona orquestram; não escrevem roteiro, gancho ou copy sozinhos.

## Como fazer

1. Identifique a função do pedido.
2. Abra a persona do agente e os bancos de dados dele (tabela abaixo).
3. Delegue (Agent/Skill) ou execute estritamente como esse agente, e diga ao Vitor qual agente está agindo.
4. Mostre de qual material do banco o resultado saiu (ex.: "gancho no padrão X de GANCHOS-PRONTOS").

| Função | Agente | Bancos obrigatórios |
|---|---|---|
| Roteiro de vídeo, gancho, fecho | `squads/marketing/agents/copy-chief.md` + `squads/conteudo/agents/roteirista.md` | `squads/conteudo/voz.md`, `voz-pares.md`, `docs/conteudo/banco-pautas/GANCHOS-PRONTOS.md`, `docs/conteudo/banco-roteiros/players/*`, `docs/conteudo/maquina/_regras/` |
| Pauta, notícia, curadoria | `squads/conteudo/agents/pauteiro.md` | `docs/conteudo/banco-pautas/BANCO.md`, estudos de players |
| Estudo de player/referência | `squads/conteudo/agents/analista-referencias.md` | `docs/conteudo/banco-roteiros/` |
| Edição de vídeo | `squads/conteudo/agents/editor-video.md` | receitas em `tools/video-recut/` |
| Copy de venda, landing, anúncio | `squads/marketing/agents/copy-chief.md` | brand book, ofertas |
| Código | `@dev` · push só `@devops` | stories |

Se não existir agente para a função, diga isso ao Vitor antes de executar.
