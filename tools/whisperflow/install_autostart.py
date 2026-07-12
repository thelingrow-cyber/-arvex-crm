# -*- coding: utf-8 -*-
"""install_autostart.py — S5 (AD-9, V1 stage): source-run autostart.

Creates (or removes, with --uninstall) a Windows shortcut in the current
user's Startup folder that launches WhisperFlow silently on login:

    pythonw.exe  main.py     (working dir: this folder)

pythonw.exe (not python.exe) has no console window attached — the daemon
runs fully invisible from boot, per AD-9/PRD CS4 ("sem terminal visivel").

Deliberately dependency-free: shortcut (.lnk) creation uses the built-in
Windows Script Host (cscript.exe + WScript.Shell COM object) via a small
throwaway .vbs file, so this script needs nothing beyond the Python
standard library — no new entry in requirements.txt, no pywin32 required
just to install an icon in Startup.

V1 stage only (AD-9): runs from source (this checkout's own .venv). The
PyInstaller --onefile --noconsole packaging is V1.1/later, not built here.

Usage:
    python install_autostart.py              # install (idempotent)
    python install_autostart.py --uninstall  # remove
    python install_autostart.py --status     # just report current state
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

APP_NAME = "WhisperFlow"
THIS_DIR = Path(__file__).resolve().parent
MAIN_PY = THIS_DIR / "main.py"
VENV_PYTHONW = THIS_DIR / ".venv" / "Scripts" / "pythonw.exe"


def get_startup_dir() -> Path:
    """Current user's Startup folder (== what `shell:startup` opens)."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA nao definido -- ambiente nao parece Windows")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_shortcut_path() -> Path:
    return get_startup_dir() / f"{APP_NAME}.lnk"


def _run_vbscript_shortcut_creator(
    shortcut_path: Path, target: Path, arguments: str, working_dir: Path
) -> None:
    """Writes a tiny .vbs that creates/overwrites the .lnk via WScript.Shell,
    runs it with cscript.exe, then deletes the throwaway script."""
    vbs = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{target}"
oLink.Arguments = "{arguments}"
oLink.WorkingDirectory = "{working_dir}"
oLink.WindowStyle = 7
oLink.Description = "WhisperFlow -- ditado por voz global (Ctrl+Win para gravar)"
oLink.Save
'''.strip()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".vbs", delete=False, encoding="utf-8"
    ) as f:
        f.write(vbs)
        vbs_path = Path(f.name)

    try:
        result = subprocess.run(
            ["cscript.exe", "//nologo", str(vbs_path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"cscript falhou (code {result.returncode}): "
                f"stdout={result.stdout!r} stderr={result.stderr!r}"
            )
    finally:
        try:
            vbs_path.unlink()
        except OSError:
            pass


def install() -> None:
    if not VENV_PYTHONW.exists():
        print(f"ERRO: pythonw.exe nao encontrado em {VENV_PYTHONW}")
        print("Rode a partir do venv correto (tools/whisperflow/.venv) antes de instalar.")
        sys.exit(1)
    if not MAIN_PY.exists():
        print(f"ERRO: main.py nao encontrado em {MAIN_PY}")
        sys.exit(1)

    startup_dir = get_startup_dir()
    if not startup_dir.is_dir():
        print(f"ERRO: pasta Startup nao existe: {startup_dir}")
        sys.exit(1)

    shortcut_path = get_shortcut_path()
    _run_vbscript_shortcut_creator(
        shortcut_path=shortcut_path,
        target=VENV_PYTHONW,
        # No manual quotes here -- the .vbs template already wraps
        # {arguments} in double quotes; adding our own produced a
        # double-quoted literal ("") that VBScript's compiler rejected.
        arguments=str(MAIN_PY),
        working_dir=THIS_DIR,
    )

    if shortcut_path.exists():
        print(f"OK: atalho de autostart criado em {shortcut_path}")
        print(f"  target:  {VENV_PYTHONW}")
        print(f"  args:    \"{MAIN_PY}\"")
        print(f"  workdir: {THIS_DIR}")
        print("WhisperFlow vai iniciar automaticamente no proximo login do Windows.")
    else:
        print("ERRO: cscript rodou mas o atalho nao apareceu -- verifique permissoes da pasta Startup.")
        sys.exit(1)


def uninstall() -> None:
    shortcut_path = get_shortcut_path()
    if shortcut_path.exists():
        shortcut_path.unlink()
        print(f"OK: atalho removido ({shortcut_path}). Autostart desativado.")
    else:
        print("Nada para remover -- atalho de autostart nao existe.")


def status() -> None:
    shortcut_path = get_shortcut_path()
    print(f"atalho: {shortcut_path}")
    print(f"instalado: {shortcut_path.exists()}")
    print(f"pythonw.exe: {VENV_PYTHONW} (existe: {VENV_PYTHONW.exists()})")
    print(f"main.py:     {MAIN_PY} (existe: {MAIN_PY.exists()})")


def main() -> int:
    if "--uninstall" in sys.argv:
        uninstall()
    elif "--status" in sys.argv:
        status()
    else:
        install()
    return 0


if __name__ == "__main__":
    sys.exit(main())
