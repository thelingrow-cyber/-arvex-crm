# Máquina de conteúdo

> Montada em 15/10/2026 copiando o fluxo que o Fabiano Carvalho mostra no reel `DeSN2nhFZr3` (quadros conferidos um a um).
> Princípio dele, tirado do texto da Anthropic "Building effective agents" (*prompt chaining*): **um Claude, uma página por trabalho.** As etapas não conversam entre si. Cada uma lê a sua página e os arquivos da etapa anterior, e deixa um arquivo para a próxima. Quando um agente faz tudo, ele se confunde.

## O fluxo (11 etapas)

| # | Etapa | Página / ferramenta | Entra | Sai | Status |
|---|---|---|---|---|---|
| 1 | Reels dos concorrentes, a cada 2 dias | `tools/maquina/coletar.py` | `05-Concorrentes/concorrentes.json` | `05-Concorrentes/coletas/<dia>/` + `painel.html` | ✅ |
| 2 | Temas que eu não cobri | `_paginas/temas.md` | coleta + `03-Publicados/` + `02-Rascunhos/` | `01-Ideias/TEMAS-NAO-COBERTOS.md` (numerado) | ✅ |
| 3 | Ganchos → banco | `tools/maquina/coletar.py` (parte 2) | coletas | `06-Ganchos/ganchos.md`, ordenado por views | ✅ |
| 4 | Roteiro pela lista de verificação | `_paginas/roteiro.md` + `_regras/checklists/roteiro.md` | um tema numerado | `02-Rascunhos/<dia>-<slug>/roteiro.md` | ✅ |
| 5 | Checagem de voz + revisor novo | `tools/maquina/checar_voz.py` + `_paginas/revisor.md` | o roteiro (o revisor nunca viu como foi escrito) | `revisao.md`: APROVADO ou REFAZER COM CORREÇÕES, com até 2 voltas automáticas | ✅ |
| 6 | **Vitor lê** | — | `roteiro.md` | aprova, ou "não curti, reescreve" + a nota dele | ✅ |
| 7 | **Vitor filma** | — | — | `bruto/` na pasta do rascunho | — |
| 8 | Corte (escolhe os melhores takes, corta cada pausa, renderiza) | `maquina.py corte` → `limpar.cjs` (fica a última tentativa de cada frase) | `bruto/` | vídeo limpo + `RELATORIO.md` | ✅ |
| 9 | Legendas + animações | `_paginas/animacoes.md` (`maquina.py edicao`) → `montar.py` | roteiro + transcrição com tempos | `edicao.md` (pintura do topo, título, inserções com licença) + `CREDITOS.txt` | 🟡 o plano sai automático, mas a montagem ainda é por vídeo |
| 10 | Opções de capa + materiais | `_paginas/capa.md` (`maquina.py legenda`) | roteiro aprovado | 3 capas + código + **`guia.md`** (o material do direct) + `legenda.txt` | 🟡 o formato do guia precisa da aprovação do Vitor; capa só em texto |
| 10b | Guia em PDF (o arquivo que vai no direct) | `tools/maquina/guia_pdf.py` (roda dentro do `legenda`) | `guia.md` | `guia.pdf`, no molde do PDF do Fabiano | ✅ |
| ciclo | Corrigir a página, não o caso (prompt 3 do guia dele) | `_paginas/corrigir.md` (`maquina.py corrigir`) | roteiro + nota do Vitor | `correcao-de-pagina.md`: a etapa que errou e a edição no formato antes → depois | ✅ |
| 10c | **Agenda no Instagram** (desde 23/10) | `tools/maquina/insta.py` (Zernio, API oficial da Meta), chamado pelo maestro no "pode" | `final.mp4` + `legenda.txt` + créditos | post na fila no próximo horário livre (12h, 19h ou 21h); "cancela" tira; quando sai, arquiva e manda o link | ✅ |
| 11 | Arquiva tudo e limpa as gravações | `maquina.py arquivar <pasta> --limpar` | pasta do rascunho | `03-Publicados/`, com o bruto apagado | ✅ |

## Quem executa cada etapa (desde 19/10)

A máquina chamava um Claude genérico com uma página curta; os especialistas do squad e os bancos de estudo ficavam
de fora, e os roteiros saíam com cara de IA. Agora `maquina.py` (`AGENTES` + `quem()`) injeta em toda chamada a
persona do agente da etapa e a lista de bases que ele abre antes de trabalhar. A página continua dizendo o que fazer
e o formato de saída; em conflito, vale `voz.md` e `_regras/`.

| Etapa | Página | Agente | Bases que ele abre |
|---|---|---|---|
| Curadoria das notícias (7h) | `curadoria.md` | ☕ Caio (pauteiro) | `noticias.py` do dia + web; confere cada número na fonte primária; estudo @beprecht |
| Temas | `temas.md` | 🔬 Bia (analista) + ☕ Caio | ESTUDO-GANCHOS, CATALOGO-MOLDES, banco de pautas |
| Roteiro | `roteiro.md` | ✍️ Téo (roteirista) + 🖊️ Halbert (copy-chief) | voz + pares, ESTUDO-GANCHOS, GANCHOS-PRONTOS, ganchos dos concorrentes, moldes, proibido, não-fale-assim |
| Revisão | `revisor.md` | 🖊️ Halbert (copy-chief), sessão nova | voz + pares, ESTUDO-GANCHOS, proibido, não-fale-assim |
| Correção de página | `corrigir.md` | ✍️ Téo | voz, proibido |
| Edição (plano) | `animacoes.md` → `montar.py` | 🎞️ Rui (editor) | README do video-recut, `montar.py`, linha editorial |
| Capa, legenda e guia | `capa.md` | 🖊️ Halbert + ✍️ Téo | ESTUDO-GANCHOS, voz |

## Rodando sozinha (desde 19/10)

O Vitor só conversa pelo WhatsApp (conversa "Você") e sobe a gravação no Drive. O resto é de duas tarefas do Windows:

| Tarefa | Quando | O que faz |
|---|---|---|
| `ARVEX Maquina - roteiro da manha` | todo dia 04:00, envia às 07:00 | `maquina.py dia 4 5 --as 07:00`: **primeiro 4 notícias de mercado** (Caio cura e confere → Téo + Halbert escrevem → revisor), códigos `N1`…`N4`; **depois a grade** pela cota **2 Regra + 2 Identidade + 1 Tendência** (+1 reserva por molde), `R1`…`R5`. Gera tudo em sequência (2 em paralelo; 4 estourou a memória em 19/10) e manda N antes de R |
| `ARVEX Maquina - maestro` | ao entrar no Windows, sempre ligado | `maestro.py`: a cada 30 s lê as respostas; a cada 2 min olha a raiz da pasta do Drive |

**O que ele responde (em cima da mensagem, ou começando com o código):**

| No roteiro | No vídeo editado |
|---|---|
| `ok` → aprovado · `troca` → outro tema do mesmo molde · qualquer outra coisa (texto ou áudio) → nota: reescreve e manda a v2 | `pode` → sobe em `Prontos/`, manda a legenda e **agenda no Instagram** (avisa dia e hora) · `cancela` → tira da fila · publicado → arquiva sozinho e manda o link · `postei` → arquiva · outra coisa → vai para `ajustes-do-vitor.md` (ajuste de edição ainda é feito numa sessão com o Claude) |

O vídeo novo no Drive é reconhecido pela fala do primeiro minuto (o roteiro enviado mais parecido); depois roda corte → edicao → `montar.py` e a prévia vai para o WhatsApp. O que a máquina mandou fica em `tools/maquina/.estado.json` (id da mensagem → roteiro/vídeo) e tudo o que ele escreve, inclusive recado solto, fica em `tools/maquina/maestro.log` (os dois fora do git). Depende do PC ligado.

## Conferência com a fala do Fabiano (15/10)

| Fala dele (reel `DeSN2nhFZr3`) | Nosso agente | Material que precisa ter dentro | Temos? |
|---|---|---|---|
| "a cada dois dias os reels mais recentes dos concorrentes são puxados" | `coletar.py` | lista de concorrentes | ✅ 8 perfis (o do Speltz voltou vazio: conferir o @) |
| "um agente passa em cada um e escreve os temas que eu ainda não cobri" | `temas.md` | coleta + **o que já foi coberto** | ✅ lê `03-Publicados`, `02-Rascunhos`, `banco-pautas` e as adaptações |
| "os ganchos vão pra um banco ordenado por views" | `ganchos.md` (dentro do `coletar.py`) | aberturas transcritas | ✅ 42 aberturas |
| "escreve o roteiro a partir da minha lista de verificação: leia minhas regras de tom de voz, daqui vêm os ganchos, isso é proibido, não fale assim" | `roteiro.md` + `checklists/roteiro.md` | **voz**, **ganchos**, **proibido**, **não fale assim** | ✅ os quatro, mas o `voz.md` foi tirado de só ~4 min de fala (é preciso refazer com os takes de outubro) |
| "uma checagem de voz passa por cima" | `checar_voz.py` | regras mecânicas da voz | ✅ |
| "um Claude novo que nunca viu aquilo destrói o roteiro antes de eu ler" | `revisor.md` | proibido + não fale assim + voz | ✅ sessão nova, até 2 voltas |
| "eu leio, se eu não curtir ele reescreve" | `maquina.py reescrever` | a nota do Vitor | ✅ a nota fica em `notas-do-vitor.md` |
| "outro corta: escolhe os melhores takes, corta cada pausa e renderiza" | `corte` → `limpar.cjs` | bruto | ✅ |
| "outro faz as legendas, as animações" | `animacoes.md` → `montar.py` | molde visual aprovado + regras de edição | 🟡 falta um `montar.py` genérico que leia o `edicao.md` |
| "se precisar ele dá opções de capa e ainda cria os materiais" | `capa.md` | regras de capa + **formato do material** | 🟡 o `guia.md` sai por vídeo; falta o Vitor aprovar o formato e gerar a capa em imagem |
| "o último arquiva tudo e limpa as gravações" | `arquivar --limpar` | — | ✅ |
| "quando algo sai errado, eu não discuto no chat: arrumo a página daquele trabalho" | regra de manutenção (abaixo) | — | ✅ |
| (no quadro) "Painel dos concorrentes: reels puxados, views somadas, conta top, gancho top" | `05-Concorrentes/painel.html` | — | ✅ |

## Como rodar

```powershell
python tools\maquina\coletar.py                          # 1 + 3 · a cada 2 dias
python tools\maquina\maquina.py temas                    # 2
python tools\maquina\maquina.py roteiro 12               # 4 + 5 · o tema nº 12 da lista
python tools\maquina\maquina.py reescrever <pasta> "nota"  # 6 · quando o Vitor não curtir
python tools\maquina\maquina.py corte <pasta>            # 8 · depois de pôr a gravação em <pasta>\bruto\
python tools\maquina\maquina.py edicao <pasta>           # 9
python tools\maquina\maquina.py legenda <pasta>          # 10
python tools\maquina\maquina.py arquivar <pasta> --limpar  # 11 · depois de postado
```

Os agentes rodam com `claude -p`: cada chamada é uma sessão nova, que só enxerga a página dela e os arquivos de entrada.

## As regras que todas as páginas leem

- `squads/conteudo/voz.md`: como o Vitor fala ("leia minhas regras de tom de voz primeiro").
- `_regras/proibido.md`: o que nunca entra, montado a partir de cada reprovação dele.
- `_regras/nao-fale-assim.md`: frases que ele reprovou, com o motivo.
- `_regras/checklists/roteiro.md`: a lista de verificação do roteiro.

**Regra de manutenção (como o Fabiano faz com a `capa.md`):** reprovação nova vira linha nova na página da etapa que errou, no mesmo dia. A máquina aprende pela página, não pela conversa.
