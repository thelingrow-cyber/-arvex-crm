# BENCH.md — S2 benchmark decisório (AD-3)

> Data: 2026-07-10 · Máquina: a máquina de trabalho do Vitor (Windows 11, CPU-only,
> sem GPU NVIDIA — confirmado em `ARCHITECTURE.md` seção 0), 8 cores lógicos.
> Motor: `faster-whisper` (CTranslate2), quantização `int8`, `vad_filter=True`,
> `initial_prompt` PT-BR conforme AD-2. `cpu_threads` explícito = `os.cpu_count()` (8).

## Metodologia

Regra (AD-3): **o maior modelo com latência média ≤ 3s vira default**; o outro
fica disponível via `config.json → model`.

**Áudio de teste:** `bench/frase-padrao.wav`, 16kHz mono PCM, a frase-padrão
exata do plano:

> "Bom dia, tudo bem? Quero confirmar nossa reunião de amanhã às quinze horas,
> e aproveitar pra te mandar a proposta atualizada com os dois planos que a
> gente conversou."

**Caveat sobre a fonte do áudio (leia antes de interpretar os números):** não
havia microfone humano disponível neste ambiente de execução (agente
autônomo, sem Vitor presente). O WAV foi gerado via SAPI/System.Speech do
Windows, voz `Microsoft Maria Desktop` (pt-BR), 16kHz mono — não é a voz do
Vitor. **As latências medidas são reais e confiáveis** (não dependem de quem
fala, só da duração/conteúdo do áudio processado pela CPU) — é exatamente
essa a medição que decide o modelo por AD-3. **A qualidade/precisão em cima
da voz real do Vitor ainda precisa ser confirmada por ele** (sotaque, ruído
de ambiente, velocidade de fala real são variáveis que este teste não cobre).

Nota de duração: a síntese de voz da Maria falou a frase em **14.40s**, mais
lenta que os "~8s" estimados no plano para uma fala humana natural. Isso não
invalida a decisão — ambos os modelos foram medidos no MESMO áudio, então a
comparação relativa é justa — mas os números absolutos de latência aqui são
para 14.4s de áudio, não 8s. Reportado abaixo também o fator tempo-real
(latência / duração do áudio) para dar uma leitura mais transferível.

Cada modelo: instância `Transcriber` carregada 1x, depois `transcribe()`
chamado 3x seguidas no MESMO áudio (mede só a inferência, não o load —
consistente com o daemon real, que carrega o modelo 1x no boot).

## Resultado

| Modelo | Load (s) | Run 1 (s) | Run 2 (s) | Run 3 (s) | Média (s) | Fator tempo-real (média/14.4s) |
|---|---|---|---|---|---|---|
| `base` int8 | 11.79 (1ª vez, baixa do HF) | 2.47 | 2.39 | 2.27 | **2.38** | 0.17x |
| `small` int8 | 2.53 (já em cache) | 7.88 | 7.85 | 7.98 | **7.90** | 0.55x |

**Texto produzido (idêntico nos dois modelos, nas 3 rodadas):**

> "Bom dia, tudo bem. Quero confirmar nossa reunião de amanhã às 15 horas, e
> aproveitar pra te mandar a proposta atualizada com os dois planos que a
> gente conversou."

Diferenças frente ao texto-fonte: `?` → `.` em "tudo bem" e "quinze horas" →
"15 horas" (Whisper normaliza número falado para dígito). Nenhuma muda o
sentido — dentro do critério CS3 ("sem erro que mude o sentido; pontuação
presente") para os dois modelos.

## Decisão (AD-3)

**`base` é o maior modelo com média ≤ 3s → vira default.** `small` ficou a
**7.90s em média — mais de 2.6x o teto de 3s (CS1)** mesmo já usando todos os
8 threads lógicos da CPU; não é viável como default nesta máquina.

Aplicado em `config.default.json` (`"model": "base"`) e no fallback
hardcoded de `config.py` (`DEFAULT_CONFIG["model"]`). `small` continua
disponível para quem quiser trocar via `config.json` (ex.: máquina com CPU
mais forte), mas não é mais o default do V1.

Extrapolando para um áudio de ~8s real (proporção linear aproximada, fator
tempo-real de `base` ≈ 0.17x): **~1.4s esperado** — bem dentro da meta CS1 de
≤3s, com folga. Isso é o resultado mais importante da S2: o risco de produto
#1 do PRD ("latência CPU decepcionar") está mitigado com o modelo `base`.

## Reprodução

```
cd tools/whisperflow
.venv/Scripts/python.exe bench_transcriber.py
```

## O que ainda precisa do Vitor

- Qualidade de transcrição na voz real dele (sotaque, ritmo, ruído de fundo,
  jargão/gírias) — este benchmark só provou a mecânica de latência, que é
  independente de quem fala; não provou a qualidade PT-BR na voz dele.
- Confirmar se ≤3s (ou os ~1.4s extrapolados para 8s reais) realmente
  "não incomoda" no uso do dia a dia — extrapolação linear é uma
  aproximação, não uma medição direta em áudio de 8s real.
