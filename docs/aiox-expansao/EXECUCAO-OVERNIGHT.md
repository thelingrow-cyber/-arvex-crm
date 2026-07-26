# Execução Overnight — Construção da Startup Team AIOX

> Início: 2026-07-19 (madrugada). Orquestrador: Orion (@aiox-master).
> Modo: autônomo (Vitor autorizou rodar sem intervenção enquanto dorme).
> Regra: subagentes em background criam; Orion consolida/valida; commit local; **sem git push** (é do @devops, e requer o Vitor acordado).

## Fontes de verdade
- `docs/aiox-expansao/PLANO-SQUADS-STARTUP.md` (6 squads, blueprints)
- `docs/aiox-expansao/MAPEAMENTO-SETUP-ALAN.md` (C-level, mecanismos, clones)
- Moldes: `squads/webdesign/` (squad) · `.claude/clones/hormozi/` + `.claude/commands/AIOX/clone/hormozi.md` (clone)

## Ondas

### ONDA 1 — disparada (background)
Squads: `security`, `marketing`, `comercial`, `research`
Clones: `michael-gerber`, `charlie-munger`, `naval-ravikant`, `eugene-schwartz`, `molly-pittman`

### ONDA 2 — após consolidar Onda 1
Squads: `financas`, `branding`, `c-level` (novo — camada executiva do MAPEAMENTO cat. B)
Clones: `al-ries`, `simon-sinek`, `dan-mall`, `reid-hoffman`, `thiago-finch`
Local (Orion): desmembrar `hormozi` → offers/copy/content (reusa fonte local)

### ONDA 3 — mecanismos + fechamento
- `roundtable` (deliberação multi-clone) · `wave-execute` (paralelização) · story-cmds slash
- Validação global (`*validate-squad` mental / consistência de padrão)
- Commit local por bloco
- Relatório final + lista de pendências que exigem o Vitor

## Pendências previstas (exigem o Vitor / @devops)
- `nano-banana-generator`: precisa de chave/acesso à API de imagem (Gemini) — só casca sem isso
- `media-buyer`: MCP de Google Ads (@devops) — nasce em modo co-piloto
- git push de tudo (@devops)
- Validação humana de cada squad/clone (rodar 1 tarefa real)

## Status (atualizado pelo Orion conforme notificações)
- [x] Onda 1 squads — ✅ security · ✅ research · ✅ marketing · ✅ comercial
- [~] Onda 1 clones — RETOMADO após reset de cota. Lote 1 (gerber, munger, naval) RE-DISPARADO com trava de orçamento (pesquisa enxuta + reservar cota p/ escrever). Lote 2 (schwartz, pittman) na fila. Falha anterior: morreram ao gravar por limite de sessão.
- [~] Onda 2 — ✅ financas · ⏳ branding (skills registrando) · ⏳ c-level (não iniciado) · clones Onda2 e desmembrar hormozi pendentes
- [ ] Onda 3 — não iniciada
- [ ] Commit local — não feito
- [ ] Relatório final

## PARADA POR LIMITE DE SESSÃO (reset 7:20am America/Sao_Paulo)
Entregue e salvo: 4 squads (security, research, marketing, comercial). NÃO validados/commitados ainda.
Para RETOMAR (após reset ou quando o Vitor mandar), em lotes MENORES (máx 3-4 subagentes por vez p/ não estourar cota):
1. Re-rodar os 5 clones da Onda 1 (pesquisa terá que ser refeita).
2. Validar consistência dos 4 squads (o padrão webdesign foi seguido; conferir arquivos).
3. Onda 2 e 3.
4. Commit local por bloco (push só @devops).

### Log
- munger ✅ (clone) — Charlie/🧠; latticework ~80 modelos, inversão, incentivos, 25 tendências + Lollapalooza; conselheiro racional do roundtable. Os 4 core-files da tentativa anterior tinham sido salvos — subagente validou e completou. FONTES REAIS (fs.blog, Poor Charlie's Almanack). Descoberta: falhas anteriores gravaram parcial → novos subagentes completam, não refazem.
- gerber ✅ (clone) — Michael/🏗️; E-Myth, 3 papéis, NO vs DENTRO, Franchise Prototype, Inovação/Quantificação/Orquestração. 5 de 7 arquivos já salvos da tentativa anterior; completou 2. Par do Hormozi (sistema vs oferta).
- naval ✅ (clone) — Naval/🧭; 4 leverages (código+mídia permissionless), specific knowledge, wealth vs status, produtizar-se. Fonte primária: thread How to Get Rich + Almanack.
- schwartz ✅ (clone) — Eugene/🧲; 5 níveis de consciência, 5 estágios de sofisticação, "channel desire", mecanismo. Alimenta copy-chief/marketing. Skills ativas: AIOX:clone:{munger,gerber,naval,eugene-schwartz}.

## ⚠️ DÍVIDA TÉCNICA — profundidade dos clones (Vitor perguntou 2026-07-19)
Estes clones NÃO foram feitos como Tay/Hormozi (fonte primária integral: vídeos baixados+transcritos, livro completo). Foram por WebSearch/WebFetch (resumos, análises, citações verbatim). Profundidade varia: Munger/Naval pegaram fonte primária que ESTÁ na web (discurso fs.blog, thread navalmanack); Gerber/Schwartz ficaram em resumos (declarado honestamente no briefing de cada um, Art. IV). Nível = CONSULTIVO (serve roundtable + squads), não nível-Tay.
UPGRADE Tay-style (quando valer): baixar 2-3 palestras YouTube → transcrever c/ Whisper local (grátis, motor do WhisperFlow) → re-destilar → guardar em sources/. Candidatos prioritários a upgrade: eugene-schwartz (copy=dinheiro) e o que o Vitor eleger. Decisão do Vitor pendente.
- security ✅ — appsec-auditor (lead) + opsec-guardian; /security-review como motor; verdict PASS/CONCERNS/FAIL; defensivo. Pendente: *validate-squad + *ids register + smoke test (audit-rls do arvex-crm).
- research ✅ — deep-researcher/Darwin (alias dr-orchestrator) + evidence-auditor/Pierce + competitive-intel/Sun; gate No Invention ([n] ou inferência); relatórios em docs/research/. 9 arquivos.
- marketing ✅ — Maya (lead) + Buck (media-buyer, modo co-piloto até MCP ads) + Halbert (copy-chief cross-canal) + Nina + Reva + Dot. 15 arquivos, 19 tasks. Pendente: MCP Google Ads (@devops).
- comercial ✅ — Blake (lead) + Grand (offer, fonte hormozi) + Wolf (closer-coach, Sales Coach/Meet) + Cady (dona do prompt Carol) + Quill (proposal, aviso jurídico). 13 arquivos, 15 tasks.
- NOTA: subagentes relataram "marketing/security incompletos" — eram snapshots durante execução concorrente; validar de verdade na consolidação final.
