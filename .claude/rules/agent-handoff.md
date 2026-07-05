# Agent Handoff — Context Compaction

Ao trocar de agente (`@agent` ou `/AIOX:agents:*` com outro agente ativo), compactar o agente anterior num artefato de handoff (~380 tokens) em vez de reter a persona completa (~3-5K tokens).

## Protocolo

1. **Saída (agente atual):** gerar artefato YAML com `from_agent`, `to_agent`, `story_context` (story_id, path, status, current_task, branch), `decisions` (máx 5), `files_modified` (máx 10), `blockers` (máx 3), `next_action`.
2. **Entrada (novo agente):** recebe seu perfil completo + o artefato compacto. NUNCA carrega persona, comandos, dependências, tools ou greetings do agente anterior.
3. **Limites:** artefato ≤500 tokens; reter no máximo 3 handoffs (descartar o mais antigo na 4ª troca).
4. **Preservar sempre:** story ativa (ID+path), task atual, branch, decisões arquiteturais, arquivos modificados, blockers ativos.

## Storage

`.aiox/handoffs/handoff-{from}-to-{to}-{timestamp}.yaml` (runtime, gitignored).
Template completo: `.aiox-core/development/templates/agent-handoff-tmpl.yaml`
