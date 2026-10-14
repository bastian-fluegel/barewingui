"""StatusBar: the strip at the bottom of a window."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Sequence

from barewingui import _api
from barewingui._api import user32
from barewingui._layout_core import Size
from barewingui.controls._base import Control
from barewingui.dpi import Scale


class StatusBar(Control):
    """
    The window's status bar. It is not part of the layout: it always sits at the
    bottom edge and the window's content fills the space above it. Create it
    inside the ``with Window(...)`` block, outside of any box::

        with Window("Files") as win:
            status = StatusBar(parts=[200, None])   # widths in DIPs, None = the rest
            with VBox():
                ...
        status.text = "Ready"       # first part
        status[1] = "3 items"

    :param parts: widths of the parts in DIPs; the last may be ``None`` (fills the rest).
    """

    _in_layout = False

    def __init__(self, parts: Sequence[float | None] = (None,), **options: object) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        parts = tuple(parts) or (None,)
        if any(p is None for p in parts[:-1]):
            raise ValueError("only the last status bar part may have no width (None)")
        self._parts = parts
        self._texts = [""] * len(parts)
        self._create("msctls_statusbar32", "", _api.SBARS_SIZEGRIP | 0x0003)  # CCS_BOTTOM
        self._window._status = self

    def _after_create(self) -> None:
        self._apply_parts(self._window.scale)

    # -- texts -------------------------------------------------------------------
    @property
    def text(self) -> str:
        return self._texts[0]

    @text.setter
    def text(self, value: str) -> None:
        self[0] = value

    def __len__(self) -> int:
        return len(self._parts)

    def __getitem__(self, index: int) -> str:
        return self._texts[index]

    def __setitem__(self, index: int, value: str) -> None:
        if not -len(self._parts) <= index < len(self._parts):
            raise IndexError(f"status bar part {index} out of range")
        index %= len(self._parts)
        self._texts[index] = str(value)
        buf = ctypes.create_unicode_buffer(self._texts[index])
        self._send(_api.SB_SETTEXTW, index, ctypes.addressof(buf))

    # -- layout (called by the Window) ---------------------------------------------
    def _apply_parts(self, scale: Scale) -> None:
        edges: list[int] = []
        total = 0
        for width in self._parts:
            if width is None:
                edges.append(-1)
            else:
                total += scale.px(width)
                edges.append(total)
        array = (ctypes.c_int * len(edges))(*edges)
        self._send(_api.SB_SETPARTS, len(edges), ctypes.addressof(array))
        for index, text in enumerate(self._texts):
            if text:
                buf = ctypes.create_unicode_buffer(text)
                self._send(_api.SB_SETTEXTW, index, ctypes.addressof(buf))

    def reposition(self, scale: Scale) -> int:
        """Let the bar snap to the bottom of the window; returns its height in pixels."""
        self._apply_font(scale.dpi)
        if scale.dpi != getattr(self, "_parts_dpi", 0):
            self._apply_parts(scale)
            self._parts_dpi = scale.dpi
        self._send(_api.WM_SIZE, 0, 0)
        return self.height_px()

    def height_px(self) -> int:
        if not self._hwnd or not self._visible:
            return 0
        rc = wintypes.RECT()
        user32.GetWindowRect(self._hwnd, ctypes.byref(rc))
        return rc.bottom - rc.top

    def natural_size(self, scale: Scale) -> Size:
        return Size(0, self.height_px())

    def _dpi_changed(self, dpi: int) -> None:
        super()._dpi_changed(dpi)
        self._apply_parts(Scale(dpi))
        self._parts_dpi = dpi
