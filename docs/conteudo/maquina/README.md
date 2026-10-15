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
| 8 | Corte (escolhe o take bom) | `tools/video-recut/limpar.cjs` (fica a última tentativa) | bruto | vídeo limpo + `RELATORIO.md` | ✅ já existia |
| 9 | Legendas + animações | `tools/video-recut/videos/2026-10-rei-do-gelo/montar.py` | vídeo limpo | vídeo final | 🟡 é preciso adaptar o script a cada vídeo |
| 10 | Capa + materiais (legenda do post, código do comentário, material do direct) | `_paginas/capa.md` | roteiro aprovado | `legenda.txt` + `capa.md` | 🟡 falta decidir o que vai no direct |
| 11 | Arquivar | `tools/maquina/maquina.py arquivar` | pasta do rascunho | move para `03-Publicados/` | ✅ |

## Como rodar

```powershell
python tools\maquina\coletar.py                          # 1 + 3 · a cada 2 dias
python tools\maquina\maquina.py temas                    # 2
python tools\maquina\maquina.py roteiro 12               # 4 + 5 · o tema nº 12 da lista
python tools\maquina\maquina.py reescrever <pasta> "nota"  # 6 · quando o Vitor não curtir
python tools\maquina\maquina.py legenda <pasta>          # 10
python tools\maquina\maquina.py arquivar <pasta>         # 11
```

Os agentes rodam com `claude -p`: cada chamada é uma sessão nova, que só enxerga a página dela e os arquivos de entrada.

## As regras que todas as páginas leem

- `squads/conteudo/voz.md`: como o Vitor fala ("leia minhas regras de tom de voz primeiro").
- `_regras/proibido.md`: o que nunca entra, montado a partir de cada reprovação dele.
- `_regras/nao-fale-assim.md`: frases que ele reprovou, com o motivo.
- `_regras/checklists/roteiro.md`: a lista de verificação do roteiro.

**Regra de manutenção (como o Fabiano faz com a `capa.md`):** reprovação nova vira linha nova na página da etapa que errou, no mesmo dia. A máquina aprende pela página, não pela conversa.
