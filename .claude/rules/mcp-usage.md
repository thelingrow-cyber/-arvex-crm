---
paths: **/*
---

# MCP Usage — AIOX

**Governança:** infra MCP é EXCLUSIVA de @devops (`*search-mcp` · `*add-mcp` · `*list-mcps` · `*remove-mcp` · `*setup-mcp-docker`). Os demais agentes são consumidores — delegar gestão a @devops.

## Prioridade: SEMPRE tools nativas antes de MCP

Read/Write/Edit/Bash/Glob/Grep para toda operação local (ler/escrever/buscar/executar no host). NUNCA docker-gateway para isso — ele roda em container Linux e causa path mismatch no host Windows.

## Quando usar cada MCP

| MCP | Uso | Acesso |
|-----|-----|--------|
| playwright (direto) | SÓ browser: automação, screenshots, interação/teste web | tools playwright |
| EXA (Docker) | Busca web, research, análise de concorrentes | `mcp__docker-gateway__web_search_exa` |
| Context7 (Docker) | Docs atualizadas de bibliotecas/APIs | `mcp__docker-gateway__resolve-library-id` → `get-library-docs` |
| Apify (Docker) | Scraping de site específico, redes sociais, e-commerce, RAG web | `search-actors` · `call-actor` · `fetch-actor-details` · `get-actor-output` · `apify-slash-rag-web-browser` · `search/fetch-apify-docs` (prefixo `mcp__docker-gateway__`) |

docker-gateway só quando: usuário pedir explicitamente docker/container/Desktop Commander, a task exigir operação em container, ou para acessar os MCPs acima.
Busca geral → EXA · site específico → Apify · docs de lib → Context7.

## Known issue — Docker MCP secrets (dez/2025)

`docker mcp secret set` NÃO passa credenciais ao container (sintoma: `docker mcp tools ls` mostra "(N prompts)" em vez de "(N tools)"; auth falha; `-e ENV_VAR` sem valor). Workaround: editar `~/.docker/mcp/catalogs/docker-mcp.yaml` com env hardcoded (`env: [{name: API_TOKEN, value: '...'}]`). Afeta MCPs autenticados (Apify, Notion, Slack). EXA funciona pois a key vive em `~/.docker/mcp/config.yaml → apiKeys`. Detalhes: task `*add-mcp` / @devops.
