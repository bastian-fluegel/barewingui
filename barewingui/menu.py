"""
barewingui.menu
~~~~~~~~~~~~~~~
Menu bar, drop-down menus, items and context menus (native Win32 menus).

::

    with Window("Editor") as win:
        with MenuBar():
            with Menu("&File"):
                MenuItem("&Open...", shortcut="Ctrl+O", on_click=open_file)
                MenuSeparator()
                MenuItem("E&xit", on_click=win.close)
            with Menu("&View"):
                MenuItem("&Word wrap", checkable=True, checked=True, on_click=toggle_wrap)
        with VBox():
            ...
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Any, Callable

from barewingui import _api
from barewingui._api import user32
from barewingui._layout_core import Container, Node, adopt
from barewingui.controls._base import owning_window
from barewingui.errors import LayoutError
from barewingui.events import event
from barewingui.shortcuts import Shortcut, parse_shortcut

Handler = Callable[[], object]
_PTR_MASK = (1 << (8 * ctypes.sizeof(ctypes.c_void_p))) - 1

__all__ = ["MenuBar", "Menu", "MenuItem", "MenuSeparator", "ContextMenu"]


class _MenuContainer(Container):
    """Shared code of everything that holds menu entries."""

    _hmenu: int | None
    _window: Any

    def _init_menu(self, *, bar: bool) -> None:
        self._window = owning_window()
        self._hmenu = (user32.CreateMenu if bar else user32.CreatePopupMenu)()
        if not self._hmenu:
            raise _api.last_error("CreateMenu")
        self._items: list[Any] = []
        self._parent: Any = None

    @property
    def items(self) -> tuple[Any, ...]:
        return tuple(self._items)

    def _redraw(self) -> None:
        if self._window.alive:
            user32.DrawMenuBar(self._window.hwnd)

    def add(self, node: Node) -> Node:
        if isinstance(node, Menu):
            ok = user32.AppendMenuW(
                self._hmenu, _api.MF_POPUP | _api.MF_STRING, node._hmenu & _PTR_MASK, node._text
            )
        elif isinstance(node, MenuItem):
            ok = node._append_to(self)
        elif isinstance(node, MenuSeparator):
            ok = user32.AppendMenuW(self._hmenu, _api.MF_SEPARATOR, 0, None)
        else:
            raise LayoutError(f"{type(node).__name__} cannot be placed in a menu")
        if not ok:
            raise _api.last_error("AppendMenuW")
        node._parent = self
        self._items.append(node)
        self._redraw()
        return node


class MenuBar(_MenuContainer):
    """The window's menu bar. Create it inside ``with Window(...)``; it takes :class:`Menu` entries."""

    def __init__(self) -> None:
        self._init_menu(bar=True)
        self._window._attach_menubar(self)

    def add(self, node: Node) -> Node:
        if not isinstance(node, Menu):
            raise LayoutError("a MenuBar only takes Menu entries (put items inside a Menu)")
        return super().add(node)


class Menu(_MenuContainer):
    """A drop-down menu (or a submenu inside another Menu) with a title like ``"&File"``."""

    def __init__(self, text: str) -> None:
        self._text = str(text)
        self._init_menu(bar=False)
        adopt(self)

    @property
    def text(self) -> str:
        return self._text


class MenuSeparator:
    """A dividing line between menu items."""

    def __init__(self) -> None:
        self._parent: Any = None
        adopt(self)


class MenuItem:
    """
    A menu entry.

    :param text: label; ``&`` marks the access key.
    :param shortcut: keyboard shortcut such as ``"Ctrl+O"`` (shown in the menu and active window-wide).
    :param on_click: handler.
    :param checkable: clicking toggles a check mark (:attr:`checked`).
    """

    on_click = event()

    def __init__(
        self,
        text: str,
        *,
        shortcut: str | None = None,
        on_click: Handler | None = None,
        checkable: bool = False,
        checked: bool = False,
        enabled: bool = True,
    ) -> None:
        self._text = str(text)
        self._shortcut: Shortcut | None = parse_shortcut(shortcut) if shortcut else None
        self._checkable = bool(checkable)
        self._checked = bool(checked)
        self._enabled = bool(enabled)
        self._id = 0
        self._parent: Any = None
        if on_click is not None:
            self.on_click(on_click)
        adopt(self)

    # -- native side -------------------------------------------------------------
    def _label(self) -> str:
        return self._text + (f"\t{self._shortcut.label}" if self._shortcut else "")

    def _flags(self) -> int:
        return (
            _api.MF_STRING
            | (_api.MF_CHECKED if self._checked else _api.MF_UNCHECKED)
            | (_api.MF_ENABLED if self._enabled else _api.MF_GRAYED)
        )

    def _append_to(self, container: _MenuContainer) -> bool:
        window = container._window
        self._window = window
        self._hmenu = container._hmenu
        self._id = window._register_command(self._activate)
        if self._shortcut:
            window._add_accelerator(self._shortcut, self._id)
        return bool(user32.AppendMenuW(self._hmenu, self._flags(), self._id, self._label()))

    def _activate(self) -> None:
        if self._checkable:
            self.checked = not self._checked
        self.on_click.emit()

    # -- properties --------------------------------------------------------------
    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = str(value)
        if self._id:
            user32.ModifyMenuW(self._hmenu, self._id, _api.MF_BYCOMMAND | self._flags(), self._id, self._label())
            self._parent._redraw()

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        self._checked = bool(value)
        if self._id:
            user32.CheckMenuItem(
                self._hmenu, self._id,
                _api.MF_BYCOMMAND | (_api.MF_CHECKED if self._checked else _api.MF_UNCHECKED),
            )

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)
        if self._id:
            user32.EnableMenuItem(
                self._hmenu, self._id,
                _api.MF_BYCOMMAND | (_api.MF_ENABLED if self._enabled else _api.MF_GRAYED),
            )

    def click(self) -> None:
        """Trigger the item like the user would (does nothing while disabled)."""
        if self._enabled:
            self._activate()


class ContextMenu(_MenuContainer):
    """
    A pop-up menu for the right mouse button. Assign it to a window or control::

        with ContextMenu() as menu:
            MenuItem("Copy path", on_click=copy_path)
        win.context_menu = menu           # or: table.context_menu = menu

    Text boxes and combo boxes keep their own native context menu.
    """

    def __init__(self) -> None:
        self._init_menu(bar=False)

    def popup(self, x: int | None = None, y: int | None = None) -> None:
        """Show the menu at screen position (x, y) in pixels, default: at the mouse."""
        if x is None or y is None:
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            x, y = point.x, point.y
        user32.SetForegroundWindow(self._window.hwnd)
        user32.TrackPopupMenu(self._hmenu, _api.TPM_RIGHTBUTTON, x, y, 0, self._window.hwnd, None)
