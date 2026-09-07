"""overlay.py — floating voice indicator: a layered, breathing orb that
reacts live to mic RMS and narrates the whole dictation, not just the
recording part.

Three states, driven from the hotkey loop:

    listening -> the orb reacts to your voice (attack fast, release slow)
    thinking  -> you stopped talking; two counter-rotating arcs orbit a
                 calm, contracted core while the transcription lands
    done      -> a brief bloom: the core flares near-white, expands, and
                 the whole window fades out

The "thinking" state earns its keep: the transcription round-trip is ~1s
of dead air where the old overlay simply vanished, leaving no sign the
tool was still working.

Rendering notes (Tk has neither blur nor per-item alpha):
- The glow is faked with N concentric polygons interpolated from the outer
  halo color to the core color. Measured on the target machine: 14 layers
  x 28 points redraw at ~426fps, so 60fps costs a fraction of one core.
- Per-item "opacity" is a color lerp toward the background key color.
  Window-wide fades DO use real alpha -- `-alpha` and `-transparentcolor`
  coexist fine on Windows (verified 2026-09-07).
- The window background is color-keyed transparent, so only the blobs are
  visible, floating directly over the desktop. Borderless, always-on-top,
  never steals keyboard focus from whatever you're dictating into.

Runs its own Tk root + mainloop on a dedicated thread. Cross-thread
communication is one-way (main loop -> overlay) via a thread-safe Queue
for state changes, and a lock-guarded float for the live audio level
(purely cosmetic — last-write-wins is fine).
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import math
import queue
import random
import sys
import threading
import time
import tkinter as tk
from typing import Optional

BASE_SIZE = 190  # logical size at 96 DPI; multiplied by the real DPI scale at runtime
TRANSPARENT_KEY = "#050505"  # magic color-keyed as "invisible" (Windows only)

# Same violet -> cyan language as before, extended with a deep halo for the
# outer falloff and a near-white specular for the core's hot peak.
GLOW_EDGE = "#161230"       # outermost, nearly background
GLOW_MID = "#4c3f99"
CORE_COLOR = "#8b7dff"      # violet, idle/quiet
CORE_COLOR_HOT = "#22d3ee"  # cyan, blended in as level rises
CORE_LIGHT = "#eafaff"      # near-white heart: what keeps the core from
                            # reading as one flat plastic disc
ARC_COLOR = "#9ff0ff"

N_POINTS = 28
N_LAYERS = 30               # concentric polygons faking a radial gradient
BASE_RADIUS = 22
LEVEL_GAIN = 9.0            # heuristic RMS -> [0,1] scaling for typical mic input
FRAME_MS = 16               # ~60fps

# Asymmetric smoothing: snap up on speech, ease down on silence. This is
# what makes the orb feel alive rather than laggy -- a symmetric filter
# either dulls the onset or jitters on the tail.
ATTACK = 0.55
RELEASE = 0.09

FADE_IN_S = 0.18
DONE_S = 0.42

STATE_HIDDEN = "hidden"
STATE_LISTENING = "listening"
STATE_THINKING = "thinking"
STATE_DONE = "done"


def _enable_dpi_awareness() -> None:
    """Tell Windows this process draws in real pixels.

    Without it a scaled display (this machine runs 125%) hands Tk logical
    coordinates while the compositor multiplies the window's position back
    up -- the orb drifted right and off the bottom edge of the screen.
    Must run before the first Tk window exists. No-op off Windows.
    """
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # pre-8.1 fallback
        except Exception:
            pass


def _work_area() -> Optional[tuple[int, int, int, int]]:
    """Desktop rect excluding the taskbar, in real pixels: (l, t, r, b)."""
    if sys.platform != "win32":
        return None
    try:
        rect = ctypes.wintypes.RECT()
        # SPI_GETWORKAREA = 0x0030
        if not ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
            return None
        return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        return None


def _dpi_scale() -> float:
    if sys.platform != "win32":
        return 1.0
    try:
        dc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, dc)
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0


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


def _ease_out(t: float) -> float:
    """Cubic ease-out: fast start, gentle settle."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class Overlay:
    """Call start() once at boot, then show()/set_level()/thinking()/done()
    /hide() freely from the hotkey loop's thread. No-op safe to call before
    start() finishes."""

    def __init__(self, config: Optional[dict] = None) -> None:
        config = config or {}
        # "bottom" (default), "top" or "center" of the work area.
        self._position = str(config.get("overlay_position", "bottom")).lower()
        # Gap from the work-area edge, in logical px (scaled with the display).
        self._margin = int(config.get("overlay_margin", 140))
        # Extra size multiplier on top of the DPI scale, if the orb still
        # reads too small/large for the user's screen.
        self._zoom = float(config.get("overlay_zoom", 1.0))
        self._size = BASE_SIZE
        self._center = BASE_SIZE / 2
        self._radius = BASE_RADIUS
        self._cmd_q: "queue.Queue[str]" = queue.Queue()
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._level = 0.0
        self._level_smooth = 0.0
        self._t0 = time.time()
        self._state = STATE_HIDDEN
        self._state_t0 = time.time()
        self._root: Optional[tk.Tk] = None
        self._canvas: Optional[tk.Canvas] = None
        self._layer_ids: list[int] = []
        self._arc_ids: list[int] = []
        # Per-point random phase offsets, one array per layer, so the wobble
        # isn't a symmetric function of point index -- that's what makes the
        # outline read as an amorphous blob instead of a spinning gear.
        self._phases: list[list[float]] = []
        self._thread = threading.Thread(target=self._run, daemon=True)

    # -- public API (any thread) --

    def start(self) -> None:
        self._thread.start()
        self._ready.wait(timeout=3)

    def show(self) -> None:
        self._cmd_q.put(STATE_LISTENING)

    def thinking(self) -> None:
        """Recording stopped; transcription is in flight."""
        self._cmd_q.put(STATE_THINKING)

    def done(self) -> None:
        """Text is on its way to the cursor -- bloom, then fade out."""
        self._cmd_q.put(STATE_DONE)

    def hide(self) -> None:
        self._cmd_q.put(STATE_HIDDEN)

    def set_level(self, level: float) -> None:
        with self._lock:
            self._level = level

    def _get_level(self) -> float:
        with self._lock:
            return self._level

    # -- Tk thread from here down --

    def _run(self) -> None:
        _enable_dpi_awareness()
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

        scale = _dpi_scale() * self._zoom
        self._size = int(BASE_SIZE * scale)
        self._center = self._size / 2
        self._radius = BASE_RADIUS * scale

        # Work area (taskbar excluded) when Windows gives it to us; the raw
        # screen otherwise. Both are real pixels now that we're DPI-aware.
        area = _work_area()
        if area is None:
            left, top = 0, 0
            right, bottom = root.winfo_screenwidth(), root.winfo_screenheight()
        else:
            left, top, right, bottom = area

        margin = int(self._margin * scale)
        x = left + (right - left - self._size) // 2
        if self._position == "top":
            y = top + margin
        elif self._position == "center":
            y = top + (bottom - top - self._size) // 2
        else:  # "bottom"
            y = bottom - self._size - margin
        # Never let it hang off an edge, however odd the margin/screen combo.
        x = max(left, min(x, right - self._size))
        y = max(top, min(y, bottom - self._size))

        root.geometry(f"{self._size}x{self._size}+{x}+{y}")
        root.configure(bg=TRANSPARENT_KEY)

        canvas = tk.Canvas(root, width=self._size, height=self._size, bg=TRANSPARENT_KEY, highlightthickness=0)
        canvas.pack()
        self._canvas = canvas
        self._setup_items()

        root.withdraw()
        self._ready.set()
        self._poll()
        root.mainloop()

    def _setup_items(self) -> None:
        c = self._canvas
        assert c is not None
        # One shared phase field, nudged slightly per layer. Independent
        # phases per layer made each shell ripple its own way, which is what
        # separates them visually and reads as banding; near-concentric
        # shells let the color ramp read as a gradient instead.
        base = [random.uniform(0, 2 * math.pi) for _ in range(N_POINTS)]
        drift = [random.uniform(-0.18, 0.18) for _ in range(N_POINTS)]
        self._phases = [
            [base[i] + drift[i] * (layer / (N_LAYERS - 1)) for i in range(N_POINTS)]
            for layer in range(N_LAYERS)
        ]
        # Outermost first so the core paints on top.
        self._layer_ids = []
        for _ in range(N_LAYERS):
            self._layer_ids.append(
                c.create_polygon(
                    *([self._center, self._center] * N_POINTS),
                    fill=GLOW_EDGE, outline="", smooth=True, splinesteps=20,
                )
            )
        # Two thin arcs, only visible while thinking.
        self._arc_ids = [
            c.create_arc(0, 0, 1, 1, start=0, extent=88, style=tk.ARC,
                         outline=TRANSPARENT_KEY, width=max(2, int(self._radius * 0.13))),
            c.create_arc(0, 0, 1, 1, start=180, extent=52, style=tk.ARC,
                         outline=TRANSPARENT_KEY, width=max(2, int(self._radius * 0.09))),
        ]

    def _blob_points(
        self,
        t: float,
        radius: float,
        wobble_amp: float,
        phases: list[float],
        cx: Optional[float] = None,
        cy: Optional[float] = None,
    ) -> list[float]:
        """3 sine harmonics per point, each point's phase drawn once from a
        fixed random offset (not a function of i) -- breaks the radial
        symmetry a pure i*const phase step would produce, so the outline
        reads as an amorphous blob instead of a spinning gear/flower."""
        if cx is None:
            cx = self._center
        if cy is None:
            cy = self._center
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

    def _set_state(self, state: str) -> None:
        root = self._root
        assert root is not None
        if state == self._state:
            return
        self._state = state
        self._state_t0 = time.time()
        if state == STATE_HIDDEN:
            root.withdraw()
            self._level_smooth = 0.0
            return
        if state == STATE_LISTENING:
            self._t0 = time.time()  # restart idle breathing each appearance
            self._level_smooth = 0.0
            try:
                root.wm_attributes("-alpha", 0.0)
            except tk.TclError:
                pass
            root.deiconify()

    def _poll(self) -> None:
        root = self._root
        assert root is not None
        try:
            while True:
                self._set_state(self._cmd_q.get_nowait())
        except queue.Empty:
            pass
        self._animate()
        root.after(FRAME_MS, self._poll)

    def _animate(self) -> None:
        root, c = self._root, self._canvas
        assert root is not None and c is not None
        if self._state == STATE_HIDDEN:
            return

        now = time.time()
        since_state = now - self._state_t0
        t = now - self._t0
        k = self._radius / BASE_RADIUS  # DPI/zoom factor, so motion scales with size

        # ---- per-state envelope: level, size, alpha ----
        if self._state == STATE_LISTENING:
            raw = max(0.0, min(1.0, self._get_level() * LEVEL_GAIN))
            ease = ATTACK if raw > self._level_smooth else RELEASE
            self._level_smooth += (raw - self._level_smooth) * ease
            level = self._level_smooth
            alpha = _ease_out(since_state / FADE_IN_S) if since_state < FADE_IN_S else 1.0
            # Entry pop: 0.72 -> 1.0 on the same easing as the fade.
            grow = 0.72 + 0.28 * alpha

        elif self._state == STATE_THINKING:
            # Calm down: contract, drop the audio reactivity, breathe slowly.
            self._level_smooth += (0.22 - self._level_smooth) * 0.08
            level = self._level_smooth
            grow = 0.80 + 0.05 * math.sin(t * 3.2)
            alpha = 1.0

        else:  # STATE_DONE -- bloom outward and fade
            p = min(1.0, since_state / DONE_S)
            level = 1.0
            grow = 1.0 + 0.55 * _ease_out(p)
            alpha = max(0.0, 1.0 - _ease_out(p))
            if p >= 1.0:
                self._set_state(STATE_HIDDEN)
                return

        try:
            root.wm_attributes("-alpha", alpha)
        except tk.TclError:
            pass

        breathing = 0.5 + 0.5 * math.sin(t * 1.4)  # idle life even at level=0
        energy = 0.15 + 0.85 * level

        # Gentle drift so the blob feels afloat rather than pinned dead-center.
        cx = self._center + 3 * k * math.sin(t * 0.27)
        cy = self._center + 2.5 * k * math.cos(t * 0.19)

        core_r = (self._radius * (1 + 0.12 * breathing) + 14 * k * level) * grow
        wobble = (3 + 10 * energy) * k

        # ---- layered glow: outermost (dim, wide) to core (bright, tight) ----
        # Radius falls off faster than color so the halo reads as light
        # spreading, not as a stack of concentric rings.
        hot = _lerp_color(CORE_COLOR, CORE_COLOR_HOT, level)
        for i, pid in enumerate(self._layer_ids):
            f = i / (N_LAYERS - 1)          # 0 = outermost, 1 = innermost
            # Every shell is a FILLED blob, not a ring, so the innermost one
            # paints the whole middle -- which is why the color has to be
            # keyed to the shell's radius, not to its index. Radii run from
            # the halo edge down to a small bright heart, in tight eased
            # steps so neighbouring shells overlap and fake the blur.
            rr = 2.05 - 1.95 * (f ** 0.85)   # 2.05 -> 0.10, in core radii
            layer_r = core_r * rr
            if rr > 1.0:                      # outer halo
                fill = _lerp_color(GLOW_EDGE, GLOW_MID, (2.05 - rr) / 1.05)
            elif rr > 0.45:                   # body: violet -> hot
                fill = _lerp_color(GLOW_MID, hot, (1.0 - rr) / 0.55)
            else:                             # heart: a small bright point
                fill = _lerp_color(hot, CORE_LIGHT, 0.78 * (1.0 - rr / 0.45) ** 1.2)
            # The innermost shells drift up-left a touch: an off-center
            # highlight reads as volume, where a centered disc read as an eye.
            lift = core_r * 0.13 * max(0.0, 0.9 - rr) / 0.8
            speed = 0.9 + 0.25 * f
            # Amplitude has to scale with the shell's own radius. A fixed
            # wobble is a small ripple on the wide halo but a huge deformation
            # on the tiny inner shells -- their peaks then poke through each
            # other and the orb reads as a star burst instead of a soft core.
            amp = wobble * min(1.0, rr) * 0.85
            c.coords(pid, *self._blob_points(t * speed, layer_r, amp,
                                             self._phases[i], cx - lift * 0.9, cy - lift))
            c.itemconfig(pid, fill=fill)

        # ---- orbiting arcs: the "working on it" signature ----
        if self._state == STATE_THINKING:
            for j, aid in enumerate(self._arc_ids):
                # Outside the halo (which stops at ~2.05 * core_r), otherwise
                # the arcs drown in it.
                orbit = core_r * (2.02 + 0.34 * j)
                spin = t * (150 if j == 0 else -95)
                c.coords(aid, cx - orbit, cy - orbit, cx + orbit, cy + orbit)
                # Fade in over the first 200ms so the arcs don't pop.
                strength = min(1.0, since_state / 0.2) * (1.0 if j == 0 else 0.55)
                c.itemconfig(aid, start=spin % 360,
                             outline=_lerp_color(TRANSPARENT_KEY, ARC_COLOR, strength))
        else:
            for aid in self._arc_ids:
                c.itemconfig(aid, outline=TRANSPARENT_KEY)


if __name__ == "__main__":
    # Manual test: python overlay.py — plays the full arc (listening with a
    # simulated voice, thinking, done) with no mic/hotkey involved.
    try:
        from config import load_config
        cfg = load_config()
    except Exception:
        cfg = {}
    ov = Overlay(cfg)
    ov.start()
    ov.show()
    t0 = time.time()
    while time.time() - t0 < 5:
        t = time.time() - t0
        speaking = (t % 1.6) < 1.0   # bursts of "speech" with pauses between
        ov.set_level(0.02 + (0.10 * (1 + math.sin(t * 9)) if speaking else 0.0))
        time.sleep(0.02)
    ov.thinking()
    time.sleep(1.4)
    ov.done()
    time.sleep(0.8)
