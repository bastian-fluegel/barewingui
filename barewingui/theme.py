"""
barewingui.theme
~~~~~~~~~~~~~~~~
Sysinternals-style Windows 11 light surfaces and Explorer theming.

Win32 has no native Dark Mode. BareWinGUI therefore uses a consistent
light canvas (#F3F3F3), white control surfaces, and SetWindowTheme("Explorer").
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from barewingui.types import gdi32, uxtheme, user32

# COLORREF = 0x00BBGGRR
COLOR_CANVAS = 0x00F3F3F3    # #F3F3F3
COLOR_SURFACE = 0x00FFFFFF   # #FFFFFF
COLOR_TEXT = 0x00111111      # #111111

_BKMODE_TRANSPARENT = 1
_BKMODE_OPAQUE = 2

_initialized = False
_brush_canvas: wintypes.HBRUSH | None = None
_brush_surface: wintypes.HBRUSH | None = None


def window_brush() -> wintypes.HBRUSH | None:
    return _brush_canvas


def control_brush() -> wintypes.HBRUSH | None:
    return _brush_surface


def init_theme() -> None:
    global _initialized, _brush_canvas, _brush_surface
    if _initialized:
        return
    _brush_canvas = gdi32.CreateSolidBrush(COLOR_CANVAS)
    _brush_surface = gdi32.CreateSolidBrush(COLOR_SURFACE)
    _initialized = True


def cleanup_theme() -> None:
    global _brush_canvas, _brush_surface, _initialized
    if _brush_canvas:
        gdi32.DeleteObject(_brush_canvas)
    if _brush_surface:
        gdi32.DeleteObject(_brush_surface)
    _brush_canvas = None
    _brush_surface = None
    _initialized = False


def apply_control_theme(hwnd: wintypes.HWND, class_name: str = "") -> None:
    if not hwnd or uxtheme is None:
        return
    uxtheme.SetWindowTheme(hwnd, "Explorer", None)


def paint_static(hdc: wintypes.HDC, hwnd_ctl: wintypes.HWND | None = None) -> int:
    # Read-only Edits senden WM_CTLCOLORSTATIC statt WM_CTLCOLOREDIT.
    if hwnd_ctl and _is_edit_class(hwnd_ctl):
        return paint_edit(hdc)
    gdi32.SetBkMode(hdc, _BKMODE_TRANSPARENT)
    gdi32.SetTextColor(hdc, COLOR_TEXT)
    return _brush_int(_brush_canvas)


def paint_edit(hdc: wintypes.HDC) -> int:
    gdi32.SetBkMode(hdc, _BKMODE_OPAQUE)
    gdi32.SetBkColor(hdc, COLOR_SURFACE)
    gdi32.SetTextColor(hdc, COLOR_TEXT)
    return _brush_int(_brush_surface)


def paint_button(hdc: wintypes.HDC) -> int:
    gdi32.SetBkMode(hdc, _BKMODE_TRANSPARENT)
    gdi32.SetTextColor(hdc, COLOR_TEXT)
    return _brush_int(_brush_canvas)


def erase_background(hwnd: wintypes.HWND, hdc: wintypes.HDC) -> bool:
    if not _brush_canvas:
        return False
    rc = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rc))
    user32.FillRect(hdc, ctypes.byref(rc), _brush_canvas)
    return True


def _is_edit_class(hwnd: wintypes.HWND) -> bool:
    buf = ctypes.create_unicode_buffer(32)
    user32.GetClassNameW(hwnd, buf, 32)
    return buf.value.upper() == "EDIT"


def _brush_int(brush: wintypes.HBRUSH | None) -> int:
    if not brush:
        return 0
    raw = getattr(brush, "value", brush)
    return 0 if raw is None else int(raw)
