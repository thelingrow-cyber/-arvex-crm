"""polish.py — optional post-transcription cleanup via an LLM (V2 roadmap item).

Off by default (config `polish_enabled: false`) so V1's "R$0, 100% local"
promise for anyone who doesn't opt in stays true. When enabled, this adds
exactly one network round-trip between transcription and paste, so it has
its own short timeout and NEVER raises -- a slow/down API must degrade to
the raw transcript, not break dictation (same AD-10 spirit as the rest of
the daemon).

Uses `urllib` (stdlib) instead of `requests` to avoid a new dependency --
this is a single small JSON POST, no need for a full HTTP client lib.

Provider: Groq (OpenAI-compatible chat completions endpoint), chosen for
its genuinely free tier (no credit card, no expiration -- rate-limited
only) and LPU hardware, which makes it the lowest-latency inference
option around, matching AD-1's "instant response" requirement. This was
already flagged as the intended low-latency fallback in the original
WhisperFlow architecture dossier -- not a new decision. The API key is
read from the GROQ_API_KEY environment variable -- never from config.json
or any file in the repo (AD-3.3: no secrets in chat or disk).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
TIMEOUT_SECONDS = 5.0

SYSTEM_PROMPT = (
    "Você limpa transcrições de ditado por voz em português do Brasil. "
    "Remova vícios de fala (é, tipo, então, aí, sabe) e falsos começos, "
    "corrija gramática e pontuação, mas preserve o sentido e o tom exatos "
    "do que foi dito -- não resuma, não reescreva o estilo, não adicione "
    "informação que não foi dita. "
    "Se o texto for uma instrução/comando dirigido a uma IA ou sistema "
    "(um pedido de tarefa, uma especificação técnica), organize-o como um "
    "prompt claro: objetivo em primeiro lugar, requisitos/contexto "
    "relevantes depois, sem ambiguidade -- mas só reorganizando o que foi "
    "dito, nunca inventando requisito novo. Se for uma mensagem comum "
    "(conversa, recado, pergunta), só limpe, sem reestruturar. "
    "Responda APENAS com o texto final, sem comentário nenhum."
)


class PolishUnavailable(RuntimeError):
    """Raised when polish can't run (no key, network error, bad response).
    Callers should catch this and fall back to the raw transcript."""


def _api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        raise PolishUnavailable("GROQ_API_KEY não está setada no ambiente")
    return key


def polish(text: str) -> str:
    """Send `text` through the cleanup model, return the polished version.

    Raises PolishUnavailable on any failure (missing key, timeout, network
    error, malformed response) -- callers must catch it and paste the raw
    transcript instead, never let a polish failure block dictation.
    """
    if not text.strip():
        return text

    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
            "stream": False,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            # Groq's edge rejects urllib's default "Python-urllib/x.y" UA as
            # bot traffic (403) -- any normal-looking UA clears it.
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise PolishUnavailable(f"erro de rede/timeout: {exc}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PolishUnavailable(f"resposta inválida da API: {exc}") from exc

    try:
        polished = body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise PolishUnavailable(f"formato de resposta inesperado: {exc}") from exc

    return polished if polished else text


if __name__ == "__main__":
    # Manual test: python polish.py -- requires GROQ_API_KEY set.
    # python polish.py "é, tipo, eu queria confirmar a reunião de amanhã né"
    import sys

    sample = " ".join(sys.argv[1:]) or "é, tipo, eu queria confirmar a reuniao de amanha, ne, umas quinze horas"
    print("original:", sample)
    try:
        print("polido:  ", polish(sample))
    except PolishUnavailable as exc:
        print("indisponível:", exc)
