# -*- coding: utf-8 -*-
"""install_autostart.py — S5 (AD-9, V1 stage): source-run autostart.

Creates (or removes, with --uninstall) a Windows shortcut in the current
user's Startup folder that launches WhisperFlow silently on login:

    pythonw.exe  main.py     (working dir: this folder)

pythonw.exe (not python.exe) has no console window attached — the daemon
runs fully invisible from boot, per AD-9/PRD CS4 ("sem terminal visivel").

S7 fix (REFACTOR-PLAN.md): shortcut (.lnk) creation is a PowerShell
one-liner that drives the same `WScript.Shell.CreateShortcut` COM object
as before, invoked directly via `subprocess` — NOT through an intermediate
.vbs file anymore. Root cause of the old bug: cscript.exe reads a .vbs
script using the system ANSI codepage, which corrupted any non-ASCII path
segment baked into the script text (this machine's own username,
"Simões", is exactly such a segment) — a script whose OWN content depended
on the broken path could never render its accented characters correctly.
The PowerShell command is instead passed via `-EncodedCommand`
(base64 of UTF-16LE), which PowerShell decodes explicitly as UTF-16 — no
ANSI round-trip, no corruption, regardless of what's in the path. This is
the same mechanism as the manual workaround that has been running this
machine's production autostart since 2026-07-17.

Still dependency-free: `powershell.exe` and its WScript.Shell COM access
are both part of every Windows install — no new entry in requirements.txt,
no pywin32.

V1 stage only (AD-9): runs from source (this checkout's own .venv). The
PyInstaller --onefile --noconsole packaging is V1.1/later, not built here.

Usage:
    python install_autostart.py              # install (idempotent)
    python install_autostart.py --uninstall  # remove
    python install_autostart.py --status     # just report current state
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
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


def _create_shortcut_via_powershell(
    shortcut_path: Path, target: Path, arguments: str, working_dir: Path
) -> None:
    """Creates/overwrites the .lnk via WScript.Shell.CreateShortcut, driven
    straight from a PowerShell one-liner over subprocess -- no .vbs file on
    disk at any point (see module docstring for why that mattered:
    cscript's ANSI reading of the old .vbs corrupted accented paths).

    The script text is passed via `-EncodedCommand` (base64 of its
    UTF-16LE bytes) instead of as a quoted `-Command` string: this sidesteps
    BOTH remaining risk classes at once -- PowerShell's own command-line
    quoting rules (paths with spaces/quotes/special chars) and any codepage
    translation between Python's subprocess call and the process launch --
    since the payload is decoded explicitly as UTF-16 text, never
    reinterpreted through a locale-dependent ANSI codepage.
    """
    description = "WhisperFlow -- ditado por voz global (Ctrl+Win para gravar)"
    ps_script = (
        f'$ws = New-Object -ComObject WScript.Shell\n'
        f'$s = $ws.CreateShortcut("{shortcut_path}")\n'
        f'$s.TargetPath = "{target}"\n'
        f'$s.Arguments = "{arguments}"\n'
        f'$s.WorkingDirectory = "{working_dir}"\n'
        f'$s.WindowStyle = 7\n'
        f'$s.Description = "{description}"\n'
        f'$s.Save()\n'
    )
    encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-NoLogo",
            "-EncodedCommand",
            encoded,
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"powershell falhou (code {result.returncode}): "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )


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
    _create_shortcut_via_powershell(
        shortcut_path=shortcut_path,
        target=VENV_PYTHONW,
        # No manual quotes here -- the PowerShell template already wraps
        # {arguments} in double quotes.
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
