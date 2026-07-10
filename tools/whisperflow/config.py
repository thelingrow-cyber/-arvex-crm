"""config.py — paths, config.json load/create, and logging setup for WhisperFlow.

Everything lives under %LOCALAPPDATA%\\WhisperFlow\\ (AD-8):
    config.json
    models\\           (faster-whisper HF cache)
    logs\\whisperflow.log   (rotating 1MB x 3)
    debug\\            (only when debug_save_wav: true)
    history.jsonl      (V2, not written by V1)
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
from pathlib import Path

APP_NAME = "WhisperFlow"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+windows",
    "model": "small",
    "language": "pt",
    "max_seconds": 120,
    "paste_mode": "clipboard",
    "beeps": True,
    "debug_save_wav": False,
}

_THIS_DIR = Path(__file__).resolve().parent
_DEFAULT_CONFIG_FILE = _THIS_DIR / "config.default.json"


def get_data_dir() -> Path:
    """Root data dir: %LOCALAPPDATA%\\WhisperFlow (falls back to ~/.whisperflow off-Windows)."""
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        base = Path(local_appdata)
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_models_dir() -> Path:
    d = get_data_dir() / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_logs_dir() -> Path:
    d = get_data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_debug_dir() -> Path:
    d = get_data_dir() / "debug"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_config_path() -> Path:
    return get_data_dir() / "config.json"


def _load_bundled_defaults() -> dict:
    if _DEFAULT_CONFIG_FILE.exists():
        try:
            with open(_DEFAULT_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return dict(DEFAULT_CONFIG)


def load_config() -> dict:
    """Load config.json, creating it with defaults on first run.

    Missing keys (e.g. after an upgrade added a new option) are backfilled
    from defaults without clobbering the user's existing customizations.
    """
    defaults = _load_bundled_defaults()
    config_path = get_config_path()

    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)
        return dict(defaults)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (OSError, json.JSONDecodeError):
        # Corrupted config.json: back it up and recreate from defaults (AD-10
        # style — never let a bad file take the daemon down).
        try:
            config_path.rename(config_path.with_suffix(".json.bak"))
        except OSError:
            pass
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)
        return dict(defaults)

    merged = dict(defaults)
    merged.update(user_config)
    if merged != user_config:
        # Backfilled a new key — persist it so the file stays authoritative.
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
    return merged


def setup_logging(console: bool = True) -> logging.Logger:
    """Rotating file logger (1MB x 3) + optional console handler.

    console=False is used when running under pythonw.exe (no console to
    write to — S5).
    """
    logger = logging.getLogger("whisperflow")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_file = get_logs_dir() / "whisperflow.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(fmt)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    # Manual test: python config.py
    cfg = load_config()
    log = setup_logging()
    log.info("config carregado de %s: %s", get_config_path(), cfg)
    log.info("models dir: %s", get_models_dir())
    log.info("logs dir: %s", get_logs_dir())
