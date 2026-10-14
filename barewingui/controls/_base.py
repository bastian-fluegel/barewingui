"""
barewingui.controls._base
~~~~~~~~~~~~~~~~~~~~~~~~~
Base class of all native controls: creation, text, enabled/visible state,
system font handling and the connection to the layout engine.

Controls are created inside a ``with Window(...)`` block (usually inside a
VBox/HBox) and are collected by the innermost open container.
"""

from __future__ import annotations

import ctypes
from typing import Any

from barewingui import _api
from barewingui._api import kernel32, user32
from barewingui._font import font_for_dpi, text_size
from barewingui._layout_core import Flex, Rect, Size, adopt, current_container
from barewingui.dpi import BASE_DPI, Scale
from barewingui.errors import LayoutError

_WPARAM_MASK = (1 << (8 * ctypes.sizeof(ctypes.c_void_p))) - 1


def wparam(value: int) -> int:
    """Two's-complement wrap so that -1 can be passed as WPARAM."""
    return value & _WPARAM_MASK


def find_window(node: Any) -> Any:
    """The Window that (transitively) contains ``node``, or None."""
    from barewingui.window import Window

    while node is not None:
        if isinstance(node, Window):
            return node
        node = getattr(node, "_parent", None)
    return None


def owning_window() -> Any:
    """The Window whose ``with`` block is currently being built."""
    window = find_window(current_container())
    if window is None:
        raise LayoutError(
            "controls must be created inside the with-block of a Window "
            "(with Window(...): with VBox(): Button(...))"
        )
    return window


def parent_hwnd() -> int:
    """HWND that new controls get as parent: the enclosing tab page, else the window."""
    node = current_container()
    while node is not None:
        page = getattr(node, "_page_hwnd", None)
        if page:
            return page
        node = getattr(node, "_parent", None)
    return owning_window().hwnd


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n")


class Control:
    """
    Base class. Subclasses call :meth:`_create` at the end of their ``__init__``.

    Class attribute ``_in_layout = False`` marks controls that manage their own
    position (the status bar) and are not part of a layout container.

    :param enabled: ``False`` greys the control out.
    :param visible: ``False`` hides it and removes it from the layout.
    :param flex: layout options (``grow``, ``shrink``, ``width``, ``height``,
        ``min_*``, ``max_*``, ``align_self``), sizes in DIPs.
    """

    _in_layout = True
    context_menu: Any = None  # a ContextMenu shown on right click (see ContextMenu)

    def __init__(self, *, enabled: bool = True, visible: bool = True, **flex: object) -> None:
        self._window = owning_window()
        self._parent_hwnd = parent_hwnd()
        self._hwnd: int | None = None
        self._font_dpi = 0
        self._visible = bool(visible)
        self._enabled = bool(enabled)
        self.flex = Flex(**flex)  # type: ignore[arg-type]
        self._muted = False  # True while the program (not the user) changes the control

    # -- creation --------------------------------------------------------------
    def _create(
        self,
        win_class: str,
        text: str,
        style: int,
        ex_style: int = 0,
    ) -> None:
        window = self._window
        style |= _api.WS_CHILD | _api.WS_CLIPSIBLINGS
        if self._visible:
            style |= _api.WS_VISIBLE
        hwnd = user32.CreateWindowExW(
            ex_style, win_class, text, style, 0, 0, 0, 0,
            self._parent_hwnd, None, kernel32.GetModuleHandleW(None), None,
        )
        if not hwnd:
            raise _api.last_error(f"CreateWindowExW ({win_class})")
        self._hwnd = hwnd
        window._controls[hwnd] = self
        self._apply_font(window.dpi)
        if not self._enabled:
            user32.EnableWindow(hwnd, False)
        if self._in_layout:
            adopt(self)
            window._last_control = self
        self._after_create()
        if window._shown:
            window.relayout()

    def _after_create(self) -> None:
        """Hook for subclasses (runs after the control joined its container)."""

    # -- properties ------------------------------------------------------------
    @property
    def hwnd(self) -> int:
        if self._hwnd is None:
            raise RuntimeError("the control has been destroyed")
        return self._hwnd

    @property
    def window(self) -> Any:
        return self._window

    @property
    def text(self) -> str:
        """The control's text."""
        length = user32.GetWindowTextLengthW(self.hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(self.hwnd, buf, length + 1)
        return buf.value

    @text.setter
    def text(self, value: str) -> None:
        self._set_text(str(value))

    def _set_text(self, value: str) -> None:
        was, self._muted = self._muted, True
        try:
            user32.SetWindowTextW(self.hwnd, value)
        finally:
            self._muted = was
        self._content_changed()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)
        if self._hwnd:
            self._sync_enabled()

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        value = bool(value)
        if value == self._visible:
            return
        self._visible = value
        if self._hwnd:
            self._sync_shown()
            self._window.relayout()

    def _sync_shown(self) -> None:
        user32.ShowWindow(self.hwnd, _api.SW_SHOW if self._visible else _api.SW_HIDE)

    def _sync_enabled(self) -> None:
        user32.EnableWindow(self.hwnd, self._enabled)

    def focus(self) -> None:
        """Move the keyboard focus to this control."""
        user32.SetFocus(self.hwnd)

    # -- layout node protocol --------------------------------------------------
    def natural_size(self, scale: Scale) -> Size:  # pragma: no cover - interface
        raise NotImplementedError

    def min_size(self, scale: Scale) -> Size:
        return self.natural_size(scale)

    def place(self, rect: Rect, scale: Scale) -> None:
        if self._hwnd is None:
            return
        self._apply_font(scale.dpi)
        user32.SetWindowPos(
            self._hwnd, None, rect.x, rect.y, rect.w, rect.h,
            _api.SWP_NOZORDER | _api.SWP_NOACTIVATE,
        )

    # -- internals -------------------------------------------------------------
    def _content_changed(self) -> None:
        """Natural size depends on the content: lay out again."""
        if self._hwnd and self._window._shown:
            self._window.relayout()

    def _apply_font(self, dpi: int) -> None:
        if self._hwnd and dpi != self._font_dpi:
            user32.SendMessageW(self._hwnd, _api.WM_SETFONT, font_for_dpi(dpi), 1)
            self._font_dpi = dpi

    def _dpi_changed(self, dpi: int) -> None:
        self._apply_font(dpi)

    def _command(self, code: int) -> None:
        """A notification (WM_COMMAND) from the native control."""

    def _scroll(self, code: int) -> None:
        """A WM_HSCROLL/WM_VSCROLL notification (trackbars)."""

    def _notify(self, code: int, lparam: int) -> int:
        """A WM_NOTIFY notification (common controls). Returns the message result."""
        return 0

    def _send(self, msg: int, w: int = 0, l: int = 0) -> int:
        return user32.SendMessageW(self.hwnd, msg, wparam(w), l)

    def _measure(self, text: str, scale: Scale) -> tuple[int, int]:
        return text_size(text, scale.dpi if scale.dpi else BASE_DPI)
