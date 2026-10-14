"""TabControl and TabPage."""

from __future__ import annotations

import ctypes
import struct
from ctypes import wintypes
from typing import Callable

from barewingui import _api
from barewingui._api import kernel32, user32, uxtheme
from barewingui._layout_core import Container, Node, Rect, Size, current_container
from barewingui.controls._base import Control, owning_window
from barewingui.dpi import Scale
from barewingui.errors import LayoutError
from barewingui.events import event
from barewingui.layout import Stack

Handler = Callable[[], object]

_page_proc_ptr = None  # keeps the C callback alive


def _page_proc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    """Dialog procedure of a tab page: forwards control notifications to the Window."""
    from barewingui.app import App

    app = App._instance
    try:
        if app is not None and msg in (
            _api.WM_COMMAND, _api.WM_NOTIFY, _api.WM_HSCROLL, _api.WM_VSCROLL,
        ):
            top = user32.GetAncestor(hwnd, _api.GA_ROOT)
            if top:
                user32.SendMessageW(top, msg, wparam, lparam)
            return 1
    except BaseException as exc:  # noqa: BLE001 - must not escape into native code
        if app is not None:
            app.errors.capture(exc)
        return 1
    return 0  # everything else: the dialog manager's default handling


def _dialog_template() -> ctypes.Array:
    """An empty child-dialog template (DS_CONTROL: themed, tab-navigable tab page)."""
    style = _api.DS_CONTROL | _api.WS_CHILD | _api.WS_CLIPCHILDREN | _api.WS_CLIPSIBLINGS
    data = struct.pack("<IIHhhhhHHH", style, _api.WS_EX_CONTROLPARENT, 0, 0, 0, 0, 0, 0, 0, 0)
    return ctypes.create_string_buffer(data, len(data))


class TabPage(Stack):
    """
    The content of one tab. A vertical stack (like :class:`VBox`) that must be
    created inside a :class:`TabControl`::

        with TabControl() as tabs:
            with TabPage("General"):
                Label("...")
    """

    def __init__(self, title: str = "", *, padding: float | tuple[float, ...] = 10,
                 gap: float = 8, **options: object) -> None:
        tabs = current_container()
        if not isinstance(tabs, TabControl):
            raise LayoutError("a TabPage must be created inside the with-block of a TabControl")
        global _page_proc_ptr
        if _page_proc_ptr is None:
            _page_proc_ptr = _api.DLGPROC(_page_proc)
        template = _dialog_template()
        hwnd = user32.CreateDialogIndirectParamW(
            kernel32.GetModuleHandleW(None), ctypes.addressof(template),
            tabs._parent_hwnd, _page_proc_ptr, 0,
        )
        if not hwnd:
            raise _api.last_error("CreateDialogIndirectParamW")
        uxtheme.EnableThemeDialogTexture(hwnd, _api.ETDT_ENABLETAB)
        self._page_hwnd: int = hwnd
        self.title = str(title)
        super().__init__("vertical", padding=padding, gap=gap, **options)  # type: ignore[arg-type]

    def place(self, rect: Rect, scale: Scale) -> None:
        # No SWP_NOZORDER: the page must stay on top of its tab control (hWndInsertAfter
        # None is HWND_TOP), otherwise the tab control paints its body over the page.
        user32.SetWindowPos(
            self._page_hwnd, None, rect.x, rect.y, rect.w, rect.h, _api.SWP_NOACTIVATE,
        )
        super().place(Rect(0, 0, rect.w, rect.h), scale)  # children are relative to the page


class TabControl(Control, Container):
    """
    Tabs with one :class:`TabPage` each. Use it as a context manager and create
    the pages inside; give it ``grow=1`` to let it fill the space.

    :param on_change: called when the user switches tabs.
    """

    on_change = event()

    def __init__(self, *, on_change: Handler | None = None, **options: object) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._pages: list[TabPage] = []
        self._create("SysTabControl32", "", _api.WS_TABSTOP)
        if on_change is not None:
            self.on_change(on_change)

    # -- pages -------------------------------------------------------------------
    @property
    def children(self) -> tuple[TabPage, ...]:
        return tuple(self._pages)

    @property
    def pages(self) -> tuple[TabPage, ...]:
        return tuple(self._pages)

    def add(self, node: Node) -> Node:
        if not isinstance(node, TabPage):
            raise LayoutError("a TabControl only takes TabPage children")
        if any(node is p for p in self._pages):
            raise LayoutError("page is already part of this TabControl")
        item = _api.TCITEMW()
        item.mask = _api.TCIF_TEXT
        buf = ctypes.create_unicode_buffer(node.title)
        item.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
        index = len(self._pages)
        if self._send(_api.TCM_INSERTITEMW, index, ctypes.addressof(item)) == -1:
            raise _api.last_error("TCM_INSERTITEMW")
        self._pages.append(node)
        node._parent = self
        user32.ShowWindow(node._page_hwnd, _api.SW_SHOW if index == 0 and self._visible else _api.SW_HIDE)
        self._content_changed()
        return node

    @property
    def selected_index(self) -> int:
        return max(0, self._send(_api.TCM_GETCURSEL)) if self._pages else -1

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        if not 0 <= index < len(self._pages):
            raise IndexError(f"tab {index} out of range")
        self._send(_api.TCM_SETCURSEL, index)
        self._show_page(index)

    @property
    def selected_page(self) -> TabPage | None:
        return self._pages[self.selected_index] if self._pages else None

    def _show_page(self, index: int) -> None:
        for i, page in enumerate(self._pages):
            shown = i == index and self._visible
            user32.ShowWindow(page._page_hwnd, _api.SW_SHOW if shown else _api.SW_HIDE)

    def _sync_shown(self) -> None:
        super()._sync_shown()
        if self._pages:
            self._show_page(self.selected_index)

    # -- layout ------------------------------------------------------------------
    def _chrome(self, content: Size, to_window: bool) -> Size:
        rc = wintypes.RECT(0, 0, content.w, content.h)
        self._send(_api.TCM_ADJUSTRECT, 1 if to_window else 0, ctypes.addressof(rc))
        return Size(rc.right - rc.left, rc.bottom - rc.top)

    def natural_size(self, scale: Scale) -> Size:
        if not self._pages:
            return Size(scale.px(120), scale.px(80))
        sizes = [p.natural_size(scale) for p in self._pages]
        return self._chrome(Size(max(s.w for s in sizes), max(s.h for s in sizes)), True)

    def min_size(self, scale: Scale) -> Size:
        if not self._pages:
            return Size(scale.px(60), scale.px(40))
        sizes = [p.min_size(scale) for p in self._pages]
        return self._chrome(Size(max(s.w for s in sizes), max(s.h for s in sizes)), True)

    def place(self, rect: Rect, scale: Scale) -> None:
        super().place(rect, scale)
        if not self._hwnd:
            return
        rc = wintypes.RECT(0, 0, rect.w, rect.h)
        self._send(_api.TCM_ADJUSTRECT, 0, ctypes.addressof(rc))  # display area, tab-client coordinates
        area = Rect(rect.x + rc.left, rect.y + rc.top, max(0, rc.right - rc.left), max(0, rc.bottom - rc.top))
        for page in self._pages:
            page.place(area, scale)

    def _notify(self, code: int, lparam: int) -> int:
        if code == _api.TCN_SELCHANGE:
            self._show_page(self.selected_index)
            if not self._muted:
                self.on_change.emit()
        return 0
