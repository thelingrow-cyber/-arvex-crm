"""overlay_layered.py — the voice orb with REAL per-pixel alpha.

Why this exists (and why overlay.py stays as the fallback): Tk's only
transparency on Windows is a color key -- one exact color is punched out,
everything else is fully opaque. So the halo could never actually fade
into the desktop; it ended at a hard edge, which reads as a dark smudge
around the orb over any light background, and any item painted in the key
color got cut clean out of the window (that bug sliced two transparent
gashes through the halo).

A layered window (WS_EX_LAYERED + UpdateLayeredWindow with ULW_ALPHA)
takes a 32-bit BGRA bitmap with a genuine alpha channel, composited by the
desktop compositor. The halo can then fall off to nothing, correctly, over
a white page or a dark terminal alike.

The frame is computed with numpy on a precomputed polar grid (radius and
angle per pixel never change, only the profile that maps them to color and
alpha), so a frame costs a handful of vectorized passes over ~100k pixels
instead of a per-pixel Python loop.

Same public API as overlay.Overlay -- start/show/thinking/done/hide/
set_level -- so main.py doesn't care which one it got.

WS_EX_TRANSPARENT is set: clicks pass straight through to whatever is
underneath, and WS_EX_NOACTIVATE keeps it from ever stealing focus from
the app you're dictating into.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import math
import queue
import random
import sys
import threading
import time
from typing import Optional

import numpy as np

BASE_SIZE = 190      # logical box at 96 DPI for the orb itself
CANVAS_PAD = 1.6     # window is bigger than the orb so the halo and the
                     # "done" bloom have room without being clipped

# Violet -> cyan, same language as the Tk version, now with an alpha ramp.
CORE_LIGHT = (234, 250, 255)
CORE_COLOR = (139, 125, 255)
CORE_HOT = (34, 211, 238)
GLOW_MID = (76, 63, 153)
GLOW_DEEP = (42, 34, 100)
ARC_COLOR = (159, 240, 255)

# Low integer frequencies: 2, 3 and 5 lobes beating against each other read
# as an amorphous living blob; higher ones look like a gear.
HARMONICS = (2, 3, 5)
HARM_WEIGHTS = (0.5, 0.32, 0.2)
HARM_SPEEDS = (1.05, -1.87, 0.58)
BASE_RADIUS = 22
LEVEL_GAIN = 9.0
FRAME_MS = 33        # ~30fps: with a real alpha ramp the motion reads smooth
                     # at 30 and leaves headroom on a 4-core laptop.
SUPERSAMPLE = 2      # compute the field at 1/N resolution and expand. The
                     # image is a soft glow, so the 2px blocks are invisible,
                     # and it cuts the per-frame pixel count by 4x. Set to 1
                     # for exact pixels on a machine with CPU to spare.
LUT_STEPS = 512      # color/alpha lookup resolution along the radial profile
RN_MAX = 2.05        # normalized radius covered by the LUT (past the halo)

ATTACK = 0.55
RELEASE = 0.09
FADE_IN_S = 0.18
DONE_S = 0.42

STATE_HIDDEN = "hidden"
STATE_LISTENING = "listening"
STATE_THINKING = "thinking"
STATE_DONE = "done"

# --- Win32 plumbing ---------------------------------------------------

WS_POPUP = 0x80000000
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
WS_EX_NOACTIVATE = 0x08000000
SW_SHOWNA = 8
SW_HIDE = 0
ULW_ALPHA = 0x00000002
AC_SRC_OVER = 0x00
AC_SRC_ALPHA = 0x01
BI_RGB = 0
DIB_RGB_COLORS = 0
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ("BlendOp", ctypes.c_byte),
        ("BlendFlags", ctypes.c_byte),
        ("SourceConstantAlpha", ctypes.c_byte),
        ("AlphaFormat", ctypes.c_byte),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
        ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
        ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wt.DWORD * 3)]


class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wt.UINT), ("lpfnWndProc", ctypes.c_void_p), ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int), ("hInstance", wt.HINSTANCE), ("hIcon", wt.HICON),
        ("hCursor", wt.HANDLE), ("hbrBackground", wt.HBRUSH),
        ("lpszMenuName", wt.LPCWSTR), ("lpszClassName", wt.LPCWSTR),
    ]


LRESULT = ctypes.c_ssize_t  # NOT c_long: on 64-bit, LRESULT/LPARAM are
                            # pointer-sized, and c_long overflows on the
                            # first message the window receives.
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

_user32 = ctypes.windll.user32
_user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
_user32.DefWindowProcW.restype = LRESULT
_user32.CreateWindowExW.argtypes = [
    wt.DWORD, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wt.HWND, wt.HMENU, wt.HINSTANCE, wt.LPVOID,
]
_user32.CreateWindowExW.restype = wt.HWND
_user32.RegisterClassW.argtypes = [ctypes.c_void_p]
_user32.RegisterClassW.restype = wt.ATOM
_kernel32 = ctypes.windll.kernel32
_kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
_kernel32.GetModuleHandleW.restype = wt.HMODULE
_user32.UpdateLayeredWindow.argtypes = [
    wt.HWND, wt.HDC, ctypes.POINTER(wt.POINT), ctypes.POINTER(wt.SIZE), wt.HDC,
    ctypes.POINTER(wt.POINT), wt.DWORD, ctypes.POINTER(BLENDFUNCTION), wt.DWORD,
]
_user32.UpdateLayeredWindow.restype = wt.BOOL
_user32.GetDC.restype = wt.HDC
_user32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
_user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
_user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, wt.UINT]

# Every handle-returning/handle-taking call needs explicit types: ctypes
# defaults to C int, and a 64-bit HDC/HBITMAP does not fit in one
# ("OverflowError: int too long to convert" at the first call).
_gdi32 = ctypes.windll.gdi32
_gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
_gdi32.CreateCompatibleDC.restype = wt.HDC
_gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
_gdi32.SelectObject.restype = wt.HGDIOBJ
_gdi32.CreateDIBSection.argtypes = [wt.HDC, ctypes.c_void_p, wt.UINT,
                                    ctypes.POINTER(ctypes.c_void_p), wt.HANDLE, wt.DWORD]
_gdi32.CreateDIBSection.restype = wt.HBITMAP
_gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
_gdi32.DeleteDC.argtypes = [wt.HDC]


def _enable_dpi_awareness() -> None:
    """Draw in real pixels. Must run before any window exists."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _work_area() -> Optional[tuple[int, int, int, int]]:
    """Desktop rect excluding the taskbar, in real pixels."""
    try:
        rect = wt.RECT()
        if not ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
            return None
        return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        return None


def _dpi_scale() -> float:
    try:
        dc = ctypes.windll.user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
        ctypes.windll.user32.ReleaseDC(0, dc)
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0


def _ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class Overlay:
    """Drop-in replacement for overlay.Overlay, drawn with real alpha."""

    def __init__(self, config: Optional[dict] = None) -> None:
        config = config or {}
        self._position = str(config.get("overlay_position", "bottom")).lower()
        self._margin = int(config.get("overlay_margin", 140))
        self._zoom = float(config.get("overlay_zoom", 1.0))

        self._cmd_q: "queue.Queue[str]" = queue.Queue()
        self._ready = threading.Event()
        self._failed = threading.Event()
        self._lock = threading.Lock()
        self._level = 0.0
        self._level_smooth = 0.0
        self._t0 = time.time()
        self._state = STATE_HIDDEN
        self._state_t0 = time.time()
        self._visible = False

        self._hwnd = None
        self._error = ""
        self._hdc_mem = None
        self._bits = None
        self._size = 0
        self._radius = float(BASE_RADIUS)
        self._thread = threading.Thread(target=self._run, daemon=True)

    # -- public API (any thread) --

    def start(self) -> None:
        if sys.platform != "win32":
            raise RuntimeError("janela em camadas e especifica do Windows")
        self._thread.start()
        self._ready.wait(timeout=4)
        if self._failed.is_set() or self._hwnd is None:
            raise RuntimeError(
                "janela em camadas indisponivel: "
                + getattr(self, "_error", "(sem detalhes)")
            )

    def show(self) -> None:
        self._cmd_q.put(STATE_LISTENING)

    def thinking(self) -> None:
        self._cmd_q.put(STATE_THINKING)

    def done(self) -> None:
        self._cmd_q.put(STATE_DONE)

    def hide(self) -> None:
        self._cmd_q.put(STATE_HIDDEN)

    def set_level(self, level: float) -> None:
        with self._lock:
            self._level = level

    def _get_level(self) -> float:
        with self._lock:
            return self._level

    # -- window thread --

    def _run(self) -> None:
        try:
            self._create_window()
        except Exception as exc:
            # Keep the reason: start() raises it so the caller can log why
            # the layered path was unavailable before falling back to Tk.
            import traceback
            self._error = traceback.format_exc()
            self._failed.set()
            self._ready.set()
            return
        self._ready.set()

        user32 = ctypes.windll.user32
        msg = wt.MSG()
        next_frame = time.time()
        while True:
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

            try:
                while True:
                    self._set_state(self._cmd_q.get_nowait())
            except queue.Empty:
                pass

            now = time.time()
            if now >= next_frame:
                next_frame = now + FRAME_MS / 1000.0
                if self._state != STATE_HIDDEN:
                    try:
                        self._draw()
                    except Exception:
                        pass  # cosmetic: never take the daemon down
            time.sleep(0.004)

    def _create_window(self) -> None:
        _enable_dpi_awareness()
        user32, gdi32 = _user32, _gdi32

        scale = _dpi_scale() * self._zoom
        self._radius = BASE_RADIUS * scale
        # MUST be a multiple of SUPERSAMPLE: the expanded buffer is
        # (size//S)*S wide, and if that differs from the DIB width by even
        # one pixel every row lands shifted and the orb comes out sheared.
        self._size = int(BASE_SIZE * scale * CANVAS_PAD) // SUPERSAMPLE * SUPERSAMPLE

        area = _work_area()
        if area is None:
            left, top = 0, 0
            right, bottom = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        else:
            left, top, right, bottom = area

        # The orb sits at the center of a padded canvas, so position by the
        # visual center and then back out the padding.
        margin = int(self._margin * scale)
        orb = int(BASE_SIZE * scale)
        pad = (self._size - orb) // 2
        x = left + (right - left - orb) // 2 - pad
        if self._position == "top":
            y = top + margin - pad
        elif self._position == "center":
            y = top + (bottom - top - orb) // 2 - pad
        else:
            y = bottom - orb - margin - pad
        x = max(left - pad, min(x, right - orb + pad))
        y = max(top - pad, min(y, bottom - orb + pad))
        self._pos = (x, y)

        # Kept on self: a garbage-collected callback would crash the window.
        self._wndproc = WNDPROC(lambda h, m, w, l: _user32.DefWindowProcW(h, m, w, l))
        cls = WNDCLASS()
        cls.lpfnWndProc = ctypes.cast(self._wndproc, ctypes.c_void_p)
        cls.lpszClassName = f"WhisperFlowOrb{id(self)}"
        cls.hInstance = _kernel32.GetModuleHandleW(None)
        self._cls = cls  # ditto
        if not user32.RegisterClassW(ctypes.byref(cls)):
            raise ctypes.WinError()

        self._hwnd = user32.CreateWindowExW(
            WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_NOACTIVATE,
            cls.lpszClassName, "WhisperFlow", WS_POPUP,
            x, y, self._size, self._size, None, None, cls.hInstance, None,
        )
        if not self._hwnd:
            raise ctypes.WinError()

        hdc_screen = user32.GetDC(0)
        self._hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = self._size
        bmi.bmiHeader.biHeight = -self._size  # negative: top-down rows
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB
        ppv = ctypes.c_void_p()
        self._hbitmap = gdi32.CreateDIBSection(
            hdc_screen, ctypes.cast(ctypes.byref(bmi), ctypes.c_void_p),
            DIB_RGB_COLORS, ctypes.byref(ppv), None, 0
        )
        user32.ReleaseDC(0, hdc_screen)
        if not self._hbitmap:
            raise ctypes.WinError()
        gdi32.SelectObject(self._hdc_mem, self._hbitmap)
        self._bits = ppv

        # Precompute the polar grid: radius and angle per pixel never change,
        # only the profile that maps them to color/alpha does.
        n = self._size // SUPERSAMPLE
        self._n = n
        c = (n - 1) / 2.0
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        xx -= c
        yy -= c
        # Radii are expressed in FULL-resolution pixels so every size in the
        # drawing code stays in real screen units regardless of SUPERSAMPLE.
        self._r = (np.sqrt(xx * xx + yy * yy) * SUPERSAMPLE).astype(np.float32)
        self._ang = np.mod(np.arctan2(yy, xx), 2 * math.pi)
        self._rn = np.empty_like(self._r)
        self._idx = np.empty(self._r.shape, dtype=np.int32)
        self._small = np.empty((n, n, 4), dtype=np.uint8)
        self._lut_x = np.linspace(0, RN_MAX, LUT_STEPS, dtype=np.float32)
        self._lut = np.empty((LUT_STEPS, 4), dtype=np.uint8)
        # Continuous angular harmonics instead of interpolating between N
        # control points: linear interp leaves a derivative kink at every
        # control point, and each kink propagates outward as a visible star
        # ray. sin(k*ang) and cos(k*ang) never change, so each frame only
        # needs a scalar phase rotation of these precomputed fields:
        #   sin(k*ang + p) = sin(k*ang)cos(p) + cos(k*ang)sin(p)
        self._harm = [
            (np.sin(k * self._ang).astype(np.float32),
             np.cos(k * self._ang).astype(np.float32))
            for k in HARMONICS
        ]
        self._harm_phase = [random.uniform(0, 2 * math.pi) for _ in HARMONICS]

    def _set_state(self, state: str) -> None:
        if state == self._state:
            return
        self._state = state
        self._state_t0 = time.time()
        if state == STATE_HIDDEN:
            self._level_smooth = 0.0
            if self._visible:
                _user32.ShowWindow(self._hwnd, SW_HIDE)
                self._visible = False
        elif state == STATE_LISTENING:
            self._t0 = time.time()
            self._level_smooth = 0.0

    def _draw(self) -> None:
        now = time.time()
        since = now - self._state_t0
        t = now - self._t0
        k = self._radius / BASE_RADIUS

        if self._state == STATE_LISTENING:
            raw = max(0.0, min(1.0, self._get_level() * LEVEL_GAIN))
            ease = ATTACK if raw > self._level_smooth else RELEASE
            self._level_smooth += (raw - self._level_smooth) * ease
            level = self._level_smooth
            fade = _ease_out(since / FADE_IN_S) if since < FADE_IN_S else 1.0
            grow = 0.72 + 0.28 * fade
        elif self._state == STATE_THINKING:
            self._level_smooth += (0.22 - self._level_smooth) * 0.08
            level = self._level_smooth
            grow = 0.80 + 0.05 * math.sin(t * 3.2)
            fade = 1.0
        else:  # done
            p = min(1.0, since / DONE_S)
            level = 1.0
            grow = 1.0 + 0.55 * _ease_out(p)
            fade = max(0.0, 1.0 - _ease_out(p))
            if p >= 1.0:
                self._set_state(STATE_HIDDEN)
                return

        breathing = 0.5 + 0.5 * math.sin(t * 1.4)
        energy = 0.15 + 0.85 * level
        core_r = (self._radius * (1 + 0.12 * breathing) + 14 * k * level) * grow
        # Gentler than the Tk version: with a soft alpha rim the same
        # amplitude read as a shapeless amoeba instead of a living orb.
        wobble = (2.0 + 5.5 * energy) * k

        # Normalized radius: 1.0 == the blob outline, so the profile below is
        # written in "core radii" and the wobble comes along for free.
        noise = None
        for (sk, ck), w, ph, sp in zip(self._harm, HARM_WEIGHTS, self._harm_phase, HARM_SPEEDS):
            a = ph + t * sp
            term = (sk * math.cos(a) + ck * math.sin(a)) * w
            noise = term if noise is None else noise + term
        edge_per_px = core_r + noise * wobble
        # Deform by OFFSET, not by scaling. Dividing r by the outline radius
        # makes every iso-line a shrunken copy of the wobbly outline, so the
        # ripples pile up at the center and shoot out as star rays. Offsetting
        # instead, with the deformation faded in as you move outward, leaves
        # the core perfectly round and only the rim organic.
        rn0 = self._r / core_r
        delta = (edge_per_px - core_r) / core_r
        rn = rn0 - delta * np.clip(rn0, 0.0, 1.0)

        hot = tuple(
            CORE_COLOR[i] + (CORE_HOT[i] - CORE_COLOR[i]) * level for i in range(3)
        )
        # rn -> (color, alpha). The tail reaching 0 alpha is the whole point:
        # the halo dissolves into the desktop instead of ending at an edge.
        # The bright heart used to sit inside rn<0.18 -- a pinprick. Widened
        # so the lit core is the thing you see and the halo frames it.
        stops = [
            (0.00, CORE_LIGHT, 1.00),
            (0.34, tuple((CORE_LIGHT[i] + hot[i]) / 2 for i in range(3)), 1.00),
            (0.66, hot, 1.00),
            (0.88, tuple((hot[i] + GLOW_MID[i]) / 2 for i in range(3)), 0.92),
            (1.10, GLOW_MID, 0.68),
            (1.40, tuple((GLOW_MID[i] + GLOW_DEEP[i]) / 2 for i in range(3)), 0.40),
            (1.70, GLOW_DEEP, 0.15),
            (2.05, GLOW_DEEP, 0.00),
        ]
        # Build the profile ONCE per frame as a 512-entry lookup table, then
        # index it per pixel. Running np.interp over every pixel instead cost
        # 47ms/frame here (measured) -- four float64 passes over 263k pixels.
        xs = np.array([s[0] for s in stops], dtype=np.float32)
        a_tab = np.array([s[2] for s in stops], dtype=np.float32)
        a_lut = np.interp(self._lut_x, xs, a_tab).astype(np.float32) * fade
        rgb_lut = [
            np.interp(self._lut_x, xs, np.array([s[1][ch] for s in stops], dtype=np.float32))
            for ch in range(3)
        ]

        # premultiplied BGRA, straight into the LUT (ULW_ALPHA wants premult)
        self._lut[:, 0] = np.clip(rgb_lut[2] * a_lut, 0, 255).astype(np.uint8)
        self._lut[:, 1] = np.clip(rgb_lut[1] * a_lut, 0, 255).astype(np.uint8)
        self._lut[:, 2] = np.clip(rgb_lut[0] * a_lut, 0, 255).astype(np.uint8)
        self._lut[:, 3] = np.clip(a_lut * 255.0, 0, 255).astype(np.uint8)

        np.multiply(rn, LUT_STEPS / RN_MAX, out=self._rn)
        np.clip(self._rn, 0, LUT_STEPS - 1, out=self._rn)
        idx = self._rn.astype(np.int32)
        small = self._lut[idx]

        # ---- thinking arcs, painted over the field ----
        if self._state == STATE_THINKING:
            arc_in = min(1.0, since / 0.2)
            for j, (orbit_f, width_f, span, speed, weight) in enumerate((
                (2.00, 0.13, 88.0, 150.0, 1.00),
                (2.34, 0.09, 52.0, -95.0, 0.55),
            )):
                orbit = core_r * orbit_f
                half = max(1.0, self._radius * width_f) / 2.0
                # soft radial edge so the ring isn't aliased
                band = np.clip(1.0 - np.abs(self._r - orbit) / (half + 1.0), 0.0, 1.0)
                start = math.radians((t * speed + (180 if j else 0)) % 360)
                delta = np.mod(self._ang - start, 2 * math.pi)
                span_r = math.radians(span)
                inside = delta <= span_r
                # taper the ends so the arc fades out instead of stopping dead
                taper = np.clip(np.minimum(delta, span_r - delta) / 0.25, 0.0, 1.0)
                m = (band * inside * taper * arc_in * weight).astype(np.float32)
                hit = m > 0.004
                if not hit.any():
                    continue
                mv = m[hit][:, None]
                col = np.array([ARC_COLOR[2], ARC_COLOR[1], ARC_COLOR[0], 255.0],
                               dtype=np.float32) * np.float32(fade)
                small[hit] = np.clip(
                    small[hit].astype(np.float32) * (1 - mv) + col * mv, 0, 255
                ).astype(np.uint8)

        if SUPERSAMPLE > 1:
            self._buf = np.repeat(np.repeat(small, SUPERSAMPLE, axis=0), SUPERSAMPLE, axis=1)
        else:
            self._buf = small
        buf = np.ascontiguousarray(self._buf)
        if buf.shape[0] != self._size or buf.shape[1] != self._size:
            raise RuntimeError(
                f"buffer {buf.shape[1]}x{buf.shape[0]} != janela {self._size}x{self._size}"
            )
        ctypes.memmove(self._bits, buf.ctypes.data, buf.nbytes)

        user32 = _user32
        if not self._visible:
            user32.ShowWindow(self._hwnd, SW_SHOWNA)
            user32.SetWindowPos(self._hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
            self._visible = True

        blend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
        pt_dst = wt.POINT(self._pos[0], self._pos[1])
        pt_src = wt.POINT(0, 0)
        size = wt.SIZE(self._size, self._size)
        user32.UpdateLayeredWindow(
            self._hwnd, None, ctypes.byref(pt_dst), ctypes.byref(size),
            self._hdc_mem, ctypes.byref(pt_src), 0, ctypes.byref(blend), ULW_ALPHA,
        )


if __name__ == "__main__":
    # Manual test: python overlay_layered.py — full arc, no mic involved.
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
        speaking = (t % 1.6) < 1.0
        ov.set_level(0.02 + (0.10 * (1 + math.sin(t * 9)) if speaking else 0.0))
        time.sleep(0.02)
    ov.thinking()
    time.sleep(1.6)
    ov.done()
    time.sleep(0.9)
