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

DEFAULT_RESTORE_DELAY = 0.15  # AD-5: 150ms between Ctrl+V and clipboard restore


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


def paste_type_mode(text: str) -> None:
    """Fallback: type character-by-character (keyboard.write), no clipboard
    involved at all — nothing to save/restore."""
    keyboard.write(text)


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
