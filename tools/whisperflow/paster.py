"""paster.py — clipboard save/set/paste/restore + type-mode fallback (AD-5, AD-7).

paste_mode "clipboard" (default): save the user's current clipboard, put
the transcribed text on it, simulate Ctrl+V, wait for the paste to land,
then restore whatever was on the clipboard before — the user never loses
what they had copied.

paste_mode "type": types the text character-by-character via
keyboard.write() instead of Ctrl+V — a fallback for apps/terminals that
reject a simulated paste. Slower, off by default (AD-5).

Empty text (AD-7: silence/no speech) pastes nothing, in either mode.
"""

from __future__ import annotations

import time
from typing import Optional

import keyboard
import pyperclip

# AD-5 specified 150ms; raised to 400ms after real-world testing on Vitor's
# machine (2026-07-10) showed 150-300ms intermittently too short under
# normal system load: the restore step can fire before the target app has
# actually read the clipboard, so the paste silently does nothing (or the
# already-restored old clipboard gets pasted instead). Measured reliability
# against real Notepad, accented PT-BR text: 150-300ms flaky (0-2/3 pass),
# 400ms 2/2 clean passes. Still not a formal guarantee (no cross-process
# signal exists for "the target has finished reading the clipboard"), but
# a large practical safety margin over the spec value at negligible added
# latency (400ms is not perceptible as lag after an 8s dictation).
DEFAULT_RESTORE_DELAY = 0.4

# keyboard.write()'s own default (delay=0) sends keystrokes as fast as
# possible; verified for real that this drops/garbles characters against
# Windows 11's async WinUI3 text control (RichEditD2DPT) -- it can't keep
# up with unthrottled synthetic input. This delay smooths that out for
# mid-string characters (including PT-BR accents -- é/ê/á/ã/ç all verified
# to type correctly once past the first character, see KNOWN ISSUE below).
DEFAULT_TYPE_DELAY = 0.02

# KNOWN ISSUE (open, not resolved by delay tuning): in real-machine testing
# the FIRST word of a type-mode paste was intermittently dropped (e.g.
# "Nao sei..." arrived as "sei..."), independent of the delay value tried
# (12ms through 300ms) and independent of a longer settle pause inserted
# after confirming the target window has OS focus (tried up to 1000ms,
# which made results *worse*, not better -- inconsistent with a simple
# "window not ready yet" race). Root cause not isolated: could be a
# `keyboard` library quirk on the first keystroke, or could be an artifact
# of the test harness programmatically stealing OS foreground focus
# immediately before typing -- something the real product never does,
# since in actual use the user's cursor is already sitting in the target
# field for as long as they were recording before paste() is ever called.
# type_mode is off by default (AD-5); if Vitor enables it, this should be
# re-verified under normal (non-automated-focus-switch) conditions before
# relying on it for anything where a dropped leading word matters.


def paste_clipboard_mode(text: str, restore_delay: float = DEFAULT_RESTORE_DELAY) -> None:
    """AD-5 flow: save clipboard -> set text -> Ctrl+V -> wait -> restore."""
    previous: Optional[str] = None
    try:
        previous = pyperclip.paste()
    except Exception:
        # Clipboard held non-text content (image, files, ...) or was
        # otherwise unreadable — nothing safe to restore later, so skip
        # the restore step rather than clobber it with an empty string.
        previous = None

    pyperclip.copy(text)
    keyboard.send("ctrl+v")
    time.sleep(restore_delay)

    if previous is not None:
        try:
            pyperclip.copy(previous)
        except Exception:
            pass


def paste_type_mode(text: str, delay: float = DEFAULT_TYPE_DELAY) -> None:
    """Fallback: type character-by-character (keyboard.write), no clipboard
    involved at all -- nothing to save/restore.

    delay=DEFAULT_TYPE_DELAY (not keyboard.write()'s own default of 0):
    verified for real against Notepad on this machine that delay=0 drops/
    garbles characters against Windows 11's async text control -- see
    DEFAULT_TYPE_DELAY comment above.

    HYPOTHESIS FIX for the first-word-dropped KNOWN ISSUE above: prime the
    injection path with a harmless press+release (shift alone, produces no
    character) before the real text. This is a known workaround for
    `keyboard.write()`'s first-keystroke drop on Windows (the first
    SendInput after the hook re-arms can be lost). NOT verified live yet --
    the known-issue note above already logged that a settle-delay approach
    made things worse, so this is a different mechanism, not a longer wait.
    Re-test with real dictation before trusting type mode for anything
    where a dropped leading word matters."""
    keyboard.press_and_release("shift")
    time.sleep(0.03)
    keyboard.write(text, delay=delay)


def paste(text: str, mode: str = "clipboard", restore_delay: float = DEFAULT_RESTORE_DELAY) -> None:
    """Entry point used by main.py. AD-7: empty transcription pastes nothing
    (silence/no speech is a neutral no-op, not an error)."""
    if not text:
        return
    if mode == "type":
        paste_type_mode(text)
    else:
        paste_clipboard_mode(text, restore_delay)


if __name__ == "__main__":
    # Manual test: focus some text field, then run:
    #   python paster.py "texto de teste" [clipboard|type]
    import sys

    text = sys.argv[1] if len(sys.argv) > 1 else "teste whisperflow"
    mode = sys.argv[2] if len(sys.argv) > 2 else "clipboard"
    print(f"colando '{text}' (mode={mode}) em 3s — foque o campo de destino...")
    time.sleep(3)
    paste(text, mode=mode)
    print("feito")
