"""overlay.py — floating "listening" indicator: an organic pulsing orb with
a soft glow halo, reacting live to mic RMS level.

Runs its own Tk root + mainloop on a dedicated thread (Tk is not meant to
share a thread with the hotkey polling loop). Cross-thread communication is
one-way (main loop -> overlay) via a thread-safe Queue for show/hide, and a
lock-guarded float for the live audio level (purely cosmetic, no
correctness requirement — last-write-wins is fine).

No rectangular card: the window background is color-keyed transparent
(Windows-only Tk feature, `-transparentcolor`) so only the orb/glow blobs
are visible, floating directly over the desktop. Borderless, always-on-top,
bottom-center of the primary screen. Never calls focus/deiconify tricks
beyond withdraw/deiconify, so it shouldn't steal keyboard focus from
whatever app the user is dictating into.
"""

from __future__ import annotations

import math
import queue
import random
import threading
import time
import tkinter as tk
from typing import Optional

SIZE = 190
CENTER = SIZE / 2
TRANSPARENT_KEY = "#050505"  # magic color-keyed as "invisible" (Windows only)

CORE_COLOR = "#8b7dff"       # violet, idle/quiet
CORE_COLOR_HOT = "#22d3ee"   # cyan, blended in as level rises
GLOW_MID = "#4c3f99"
GLOW_OUTER = "#241f4d"

N_POINTS = 28
BASE_RADIUS = 22
LEVEL_GAIN = 9.0  # heuristic RMS -> [0,1] scaling for typical mic input


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lerp_color(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class Overlay:
    """Call start() once at boot, then show()/hide()/set_level() freely from
    the hotkey loop's thread. No-op safe to call before start() finishes."""

    def __init__(self) -> None:
        self._cmd_q: "queue.Queue[str]" = queue.Queue()
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._level = 0.0
        self._level_smooth = 0.0  # eased copy of _level, so motion breathes instead of jittering per mic frame
        self._t0 = time.time()
        self._root: Optional[tk.Tk] = None
        self._canvas: Optional[tk.Canvas] = None
        self._outer_id: Optional[int] = None
        self._mid_id: Optional[int] = None
        self._core_id: Optional[int] = None
        # per-point random phase offsets (one array per layer) so the wobble
        # isn't a perfectly symmetric function of point index -- set in
        # _setup_blobs(), on the Tk thread, once per show() lifecycle isn't
        # needed since these don't depend on size/level, just randomness.
        self._phase_core: list[float] = []
        self._phase_mid: list[float] = []
        self._phase_outer: list[float] = []
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()
        self._ready.wait(timeout=3)

    def show(self) -> None:
        self._cmd_q.put("show")

    def hide(self) -> None:
        self._cmd_q.put("hide")

    def set_level(self, level: float) -> None:
        with self._lock:
            self._level = level

    def _get_level(self) -> float:
        with self._lock:
            return self._level

    # -- Tk thread from here down --

    def _run(self) -> None:
        root = tk.Tk()
        self._root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try:
            root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass  # non-Windows dev fallback: window just stays opaque
        try:
            root.wm_attributes("-toolwindow", True)
        except tk.TclError:
            pass

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - SIZE) // 2
        y = sh - SIZE - 90
        root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")
        root.configure(bg=TRANSPARENT_KEY)

        canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg=TRANSPARENT_KEY, highlightthickness=0)
        canvas.pack()
        self._canvas = canvas
        self._setup_blobs()

        root.withdraw()
        self._ready.set()
        self._poll()
        root.mainloop()

    def _blob_points(
        self,
        t: float,
        radius: float,
        wobble_amp: float,
        phases: list[float],
        cx: float = CENTER,
        cy: float = CENTER,
    ) -> list[float]:
        """3 sine harmonics per point, each point's phase drawn once from a
        fixed random offset (not a function of i) -- breaks the radial
        symmetry a pure i*const phase step would produce, so the outline
        reads as an amorphous blob instead of a spinning gear/flower."""
        pts: list[float] = []
        for i in range(N_POINTS):
            ang = 2 * math.pi * i / N_POINTS
            p = phases[i]
            noise = (
                math.sin(t * 1.05 + p) * 0.5
                + math.sin(t * 1.87 + p * 1.6 + i * 0.35) * 0.3
                + math.sin(t * 0.58 - p * 2.2) * 0.2
            )
            r = radius + noise * wobble_amp
            pts.append(cx + r * math.cos(ang))
            pts.append(cy + r * math.sin(ang))
        return pts

    def _setup_blobs(self) -> None:
        c = self._canvas
        assert c is not None
        self._phase_core = [random.uniform(0, 2 * math.pi) for _ in range(N_POINTS)]
        self._phase_mid = [random.uniform(0, 2 * math.pi) for _ in range(N_POINTS)]
        self._phase_outer = [random.uniform(0, 2 * math.pi) for _ in range(N_POINTS)]
        outer_pts = self._blob_points(0.0, BASE_RADIUS * 2.1, 4, self._phase_outer)
        mid_pts = self._blob_points(0.0, BASE_RADIUS * 1.55, 4, self._phase_mid)
        core_pts = self._blob_points(0.0, BASE_RADIUS, 4, self._phase_core)
        self._outer_id = c.create_polygon(*outer_pts, fill=GLOW_OUTER, outline="", smooth=True, splinesteps=24)
        self._mid_id = c.create_polygon(*mid_pts, fill=GLOW_MID, outline="", smooth=True, splinesteps=24)
        self._core_id = c.create_polygon(*core_pts, fill=CORE_COLOR, outline="", smooth=True, splinesteps=24)

    def _poll(self) -> None:
        root = self._root
        assert root is not None
        try:
            while True:
                cmd = self._cmd_q.get_nowait()
                if cmd == "show":
                    self._t0 = time.time()  # restart the idle-breathing phase each time it appears
                    root.deiconify()
                elif cmd == "hide":
                    root.withdraw()
        except queue.Empty:
            pass
        self._animate()
        root.after(33, self._poll)

    def _animate(self) -> None:
        root, c = self._root, self._canvas
        assert root is not None and c is not None
        if root.state() == "withdrawn":
            return

        raw_level = max(0.0, min(1.0, self._get_level() * LEVEL_GAIN))
        self._level_smooth += (raw_level - self._level_smooth) * 0.2  # eases out raw mic-frame jitter
        level = self._level_smooth

        t = time.time() - self._t0
        breathing = 0.5 + 0.5 * math.sin(t * 1.4)  # idle life even at level=0
        energy = 0.15 + 0.85 * level

        # gentle overall drift so the blob feels afloat rather than pinned dead-center
        cx = CENTER + 3 * math.sin(t * 0.27)
        cy = CENTER + 2.5 * math.cos(t * 0.19)

        core_r = BASE_RADIUS * (1 + 0.12 * breathing) + 14 * level
        core_wobble = 3 + 10 * energy
        c.coords(self._core_id, *self._blob_points(t * 1.6, core_r, core_wobble, self._phase_core, cx, cy))

        mid_r = core_r * 1.55
        c.coords(self._mid_id, *self._blob_points(t * 1.1, mid_r, core_wobble * 0.8, self._phase_mid, cx, cy))

        outer_r = core_r * 2.1
        c.coords(self._outer_id, *self._blob_points(t * 0.8, outer_r, core_wobble * 0.6, self._phase_outer, cx, cy))

        c.itemconfig(self._core_id, fill=_lerp_color(CORE_COLOR, CORE_COLOR_HOT, level))
        c.itemconfig(self._mid_id, fill=_lerp_color(GLOW_MID, CORE_COLOR_HOT, level * 0.5))


if __name__ == "__main__":
    # Manual test: python overlay.py — shows the orb with a simulated
    # rising/falling level for ~8s, no mic/hotkey involved.
    ov = Overlay()
    ov.start()
    ov.show()
    t0 = time.time()
    while time.time() - t0 < 8:
        t = time.time() - t0
        ov.set_level(0.04 + 0.05 * (1 + math.sin(t * 2)))
        time.sleep(0.03)
    ov.hide()
    time.sleep(0.5)
