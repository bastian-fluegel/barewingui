"""
barewingui._font
~~~~~~~~~~~~~~~~
The system message font (what native dialogs use) per DPI, and text measuring.
Nothing is drawn here; controls draw themselves with this font.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from barewingui import _api
from barewingui._api import gdi32, user32

_fonts: dict[int, int] = {}


def font_for_dpi(dpi: int) -> int:
    """HFONT of the system message font at ``dpi`` (cached for the process lifetime)."""
    handle = _fonts.get(dpi)
    if handle is None:
        ncm = _api.NONCLIENTMETRICSW()
        ncm.cbSize = ctypes.sizeof(_api.NONCLIENTMETRICSW)
        if not user32.SystemParametersInfoForDpi(
            _api.SPI_GETNONCLIENTMETRICS, ncm.cbSize, ctypes.byref(ncm), 0, dpi
        ):
            raise _api.last_error("SystemParametersInfoForDpi")
        handle = gdi32.CreateFontIndirectW(ctypes.byref(ncm.lfMessageFont))
        if not handle:
            raise _api.last_error("CreateFontIndirectW")
        _fonts[dpi] = handle
    return handle


def text_size(text: str, dpi: int) -> tuple[int, int]:
    """Pixel size of ``text`` (may contain newlines) in the system font at ``dpi``."""
    lines = text.replace("\r\n", "\n").split("\n")
    hdc = user32.GetDC(None)
    if not hdc:
        raise _api.last_error("GetDC")
    old = gdi32.SelectObject(hdc, font_for_dpi(dpi))
    try:
        width = 0
        height = 0
        for line in lines:
            size = wintypes.SIZE()
            sample = line if line else "Ag"
            if not gdi32.GetTextExtentPoint32W(hdc, sample, len(sample), ctypes.byref(size)):
                raise _api.last_error("GetTextExtentPoint32W")
            width = max(width, size.cx if line else 0)
            height = size.cy
        return width, height * len(lines)
    finally:
        gdi32.SelectObject(hdc, old)
        user32.ReleaseDC(None, hdc)
