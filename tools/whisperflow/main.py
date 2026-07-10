"""main.py — WhisperFlow daemon entrypoint.

S0: instance lock (AD-6) + config load + logging + idle loop.
S1+ extends this with hotkey registration and the record/transcribe/paste
pipeline; kept as a thin orchestrator so each concern stays in its own
module (recorder.py, transcriber.py, paster.py, feedback.py).
"""

from __future__ import annotations

import socket
import sys
import time
from typing import Optional

import config as cfg

INSTANCE_LOCK_PORT = 52700


def acquire_instance_lock() -> Optional[socket.socket]:
    """AD-6 — exclusive bind on 127.0.0.1:52700.

    Returns the bound+listening socket (caller must keep a reference alive
    for the whole process lifetime — closing/GC'ing it releases the lock),
    or None if the port is already taken by another WhisperFlow instance.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", INSTANCE_LOCK_PORT))
        sock.listen(1)
    except OSError:
        sock.close()
        return None
    return sock


def main() -> int:
    config = cfg.load_config()
    logger = cfg.setup_logging(console=True)

    lock = acquire_instance_lock()
    if lock is None:
        logger.info("instância já ativa — encerrando em silêncio")
        return 0

    logger.info(
        "daemon iniciado (hotkey=%s, model=%s, language=%s, paste_mode=%s, "
        "max_seconds=%s, beeps=%s)",
        config["hotkey"],
        config["model"],
        config["language"],
        config["paste_mode"],
        config["max_seconds"],
        config["beeps"],
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("daemon encerrado (Ctrl+C)")
    finally:
        lock.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
