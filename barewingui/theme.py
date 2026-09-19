"""
barewingui.theme
~~~~~~~~~~~~~~~~
Sysinternals-style Windows 11 light surfaces and uxtheme control styling.

Classic Win32 controls (BUTTON, COMBOBOX, scrollbars) have no native Dark Mode.
Painting a dark client while those controls stay light collapses into
High Contrast Black. BareWinGUI therefore uses a consistent light canvas
(#F3F3F3) with a forced light title bar.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from barewingui.types import gdi32, uxtheme, user32

# Win11 Settings / Explorer surfaces (COLORREF = 0x00BBGGRR)
_WINDOW_COLOR = 0x00F3F3F3  # RGB(243, 243, 243)
_CONTROL_COLOR = 0x00FFFFFF  # RGB(255, 255, 255)
_TEXT_COLOR = 0x00111111     # RGB(17, 17, 17)

_initialized = False
_window_brush: wintypes.HBRUSH | None = None
_control_brush: wintypes.HBRUSH | None = None


def uses_dark_mode() -> bool:
    """Win32 Dark Mode is not used. Always False (Sysinternals light canvas)."""
    return False


def window_brush() -> wintypes.HBRUSH | None:
    return _window_brush


def control_brush() -> wintypes.HBRUSH | None:
    return _control_brush


def text_color() -> int:
    return _TEXT_COLOR


def control_color() -> int:
    return _CONTROL_COLOR


def theme_name(class_name: str) -> str | None:
    """uxtheme class: Explorer for lists/buttons, CFD for edits."""
    mapping = {
        "BUTTON": "Explorer",
        "EDIT": "CFD",
        "COMBOBOX": "Explorer",
        "LISTBOX": "Explorer",
    }
    return mapping.get(class_name.upper())


def init_theme() -> None:
    global _initialized, _window_brush, _control_brush
    if _initialized:
        return

    _window_brush = gdi32.CreateSolidBrush(_WINDOW_COLOR)
    _control_brush = gdi32.CreateSolidBrush(_CONTROL_COLOR)
    _initialized = True


def cleanup_theme() -> None:
    global _window_brush, _control_brush, _initialized
    if _window_brush:
        gdi32.DeleteObject(_window_brush)
    if _control_brush:
        gdi32.DeleteObject(_control_brush)
    _window_brush = None
    _control_brush = None
    _initialized = False


def apply_control_theme(hwnd: wintypes.HWND, class_name: str) -> None:
    if not hwnd or uxtheme is None:
        return
    name = theme_name(class_name)
    if name:
        uxtheme.SetWindowTheme(hwnd, name, None)


def paint_static(hdc: wintypes.HDC) -> int:
    gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
    gdi32.SetTextColor(hdc, _TEXT_COLOR)
    return _brush_int(_window_brush)


def paint_edit(hdc: wintypes.HDC) -> int:
    gdi32.SetBkMode(hdc, 1)
    gdi32.SetTextColor(hdc, _TEXT_COLOR)
    gdi32.SetBkColor(hdc, _CONTROL_COLOR)
    return _brush_int(_control_brush)


def erase_background(hwnd: wintypes.HWND, hdc: wintypes.HDC) -> bool:
    if not _window_brush:
        return False
    rc = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rc))
    user32.FillRect(hdc, ctypes.byref(rc), _window_brush)
    return True


def _brush_int(brush: wintypes.HBRUSH | None) -> int:
    if not brush:
        return 0
    raw = getattr(brush, "value", brush)
    return 0 if raw is None else int(raw)
