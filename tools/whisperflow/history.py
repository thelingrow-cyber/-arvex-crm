"""history.py — last-50 transcription history (V1.1 backlog item, AD-8).

Purpose: recover text pasted in the wrong place. Same trust level as
whisperflow.log, which already logs every transcription in plaintext at
INFO level -- this adds no new class of exposure, just a structured,
bounded, easy-to-grep version of what's already logged.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import config as cfg

MAX_ENTRIES = 50


def get_history_path() -> Path:
    return cfg.get_data_dir() / "history.jsonl"


def append_entry(text: str, polished: bool, logger=None) -> None:
    """Append one entry, keeping only the last MAX_ENTRIES. Never raises --
    history is a convenience feature, not core functionality (AD-10
    spirit): a disk/permission error here must not block dictation."""
    if not text:
        return
    path = get_history_path()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "text": text,
        "polished": polished,
    }
    try:
        entries: list[dict] = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # skip a corrupted line, don't fail the whole read
        entries.append(entry)
        entries = entries[-MAX_ENTRIES:]
        with open(path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
    except OSError:
        if logger is not None:
            logger.exception("erro ao gravar history.jsonl")


if __name__ == "__main__":
    # Manual test: python history.py -- appends a test entry, prints the file
    append_entry("teste de history", polished=False)
    print("gravado em", get_history_path())
    print(get_history_path().read_text(encoding="utf-8"))
