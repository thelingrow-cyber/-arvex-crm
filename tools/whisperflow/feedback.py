"""feedback.py — audio feedback beeps (AD-7, AD-10, PRD 5).

winsound is stdlib — zero extra dependency (AD-4). All functions are
no-ops when `enabled=False` (config.beeps toggle) so the daemon can run
silent (e.g. in a call).
"""

from __future__ import annotations

import time

try:
    import winsound
except ImportError:  # pragma: no cover - non-Windows dev fallback
    winsound = None


def _beep(freq: int, duration_ms: int) -> None:
    if winsound is None:
        return
    try:
        winsound.Beep(freq, duration_ms)
    except RuntimeError:
        # Some environments (RDP sessions without audio, etc.) reject Beep.
        pass


def beep_start(enabled: bool = True) -> None:
    """Short beep: recording started (key pressed)."""
    if not enabled:
        return
    _beep(880, 90)


def beep_stop(enabled: bool = True) -> None:
    """Short beep: recording stopped (key released, normal flow)."""
    if not enabled:
        return
    _beep(660, 90)


def beep_error(enabled: bool = True) -> None:
    """Triple beep: error (mic unavailable, exception caught by AD-10 handler)."""
    if not enabled:
        return
    for _ in range(3):
        _beep(330, 100)
        time.sleep(0.05)


def beep_cap(enabled: bool = True) -> None:
    """Double beep: max recording duration reached (AD-7 stuck-key protection)."""
    if not enabled:
        return
    for _ in range(2):
        _beep(500, 130)
        time.sleep(0.05)


if __name__ == "__main__":
    # Manual test: python feedback.py — should hear start, stop, cap(2x), error(3x)
    print("beep_start")
    beep_start()
    time.sleep(0.3)
    print("beep_stop")
    beep_stop()
    time.sleep(0.3)
    print("beep_cap")
    beep_cap()
    time.sleep(0.3)
    print("beep_error")
    beep_error()
