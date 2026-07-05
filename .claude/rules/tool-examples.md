# Tool Selection — Input Examples

Exemplos concretos para escolher a tool certa. Aplicam-se só a tools always-loaded (Tier 1/2) e Tier 3 essenciais (ADR-5); as demais via tool search.

- **context7** (docs de bibliotecas): `resolve-library-id("react")` → `get-library-docs` topic "server components". Mesmo padrão p/ supabase (RLS), jest (mocks).
- **coderabbit** (review automatizado, roda em WSL): pre-commit `wsl bash -c 'cd /mnt/c/.../aiox-core && ~/.local/bin/coderabbit --prompt-only -t uncommitted'` · pre-PR: idem com `--base main`.
- **supabase** (migrations): `supabase db push` · `supabase migration list`.
- **github-cli** (@devops exclusivo p/ push/PR): `gh pr create --title 'feat: ...'` · `gh issue list --state open --label bug` · `gh pr view 123 --json reviews,statusCheckRollup`.
- **git** (estado local): `git diff --stat` · `git log --oneline -10` · `git diff main...HEAD --stat`.
- **nogic** (code intelligence, essencial): cadeia de imports de um módulo; usages de uma função.
- **code-graph** (essencial): árvore de dependências com profundidade configurável; detecção de dependências circulares.
- **docker-gateway** (infra MCP, @devops): `docker mcp server ls` · health: `curl http://localhost:8080/health`.
- **browser** (testes web): abrir `http://localhost:3000` e checar erros de console.

Registry completo: `.aiox-core/data/mcp-tool-examples.yaml` · `.aiox-core/data/tool-registry.yaml`
