"""
barewingui.window
~~~~~~~~~~~~~~~~~
Top-level window: native HWND, DIP sizes, per-monitor DPI changes and the
connection to the layout engine.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Any, Callable

from barewingui import _api
from barewingui._api import kernel32, user32
from barewingui._layout_core import Container, Node, Rect
from barewingui.app import App
from barewingui.dpi import BASE_DPI, Scale
from barewingui.errors import LayoutError

_CLASS_NAME = "BareWinGUI.Window"
_window_proc_ptr = None  # keeps the C callback alive
_PTR_MASK = (1 << (8 * ctypes.sizeof(ctypes.c_void_p))) - 1


def _window_proc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    """Single native window procedure: finds the Python Window and forwards the message."""
    app = App._instance
    try:
        if app is not None:
            if msg == _api.WM_NCCREATE:
                _bind(app, hwnd, lparam)
            window = app._windows.get(hwnd)
            if window is not None:
                handled, result = window._dispatch(msg, wparam, lparam)
                if handled:
                    return result
    except BaseException as exc:  # noqa: BLE001 - must not escape into native code
        if app is not None:
            app.errors.capture(exc)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def _bind(app: App, hwnd: int, lparam: int) -> None:
    """Connect a freshly created HWND to the Window that asked for it (via lpCreateParams)."""
    create = ctypes.cast(lparam, ctypes.POINTER(_api.CREATESTRUCTW)).contents
    window = app._pending.pop(create.lpCreateParams or 0, None)
    if window is not None:
        window._hwnd = hwnd
        app._windows[hwnd] = window


class Window(Container):
    """
    A top-level window.

    Sizes are DIPs and describe the *client area*. Use it as a context manager
    to collect its content; it takes exactly one root container::

        with Window("Demo", size=(480, 240)) as win:
            with VBox(padding=12):
                ...
        App().run()

    :param title: caption text.
    :param size: client size ``(width, height)`` in DIPs.
    :param resizable: whether the user can resize the window.
    """

    def __init__(
        self,
        title: str = "",
        size: tuple[int, int] = (640, 480),
        *,
        resizable: bool = True,
    ) -> None:
        if len(size) != 2 or size[0] <= 0 or size[1] <= 0:
            raise ValueError(f"size must be (width, height) with positive values, got {size!r}")
        self._app = App.current()
        self._title = title
        self._hwnd: int | None = None
        self._dpi = BASE_DPI
        self._root: Node | None = None
        self._controls: dict[int, Any] = {}  # control HWND -> control
        self.default_button: Any = None
        self._last_control: Any = None
        self._status: Any = None
        self._menubar: Any = None
        self._commands: dict[int, Callable[[], object]] = {}
        self._next_command = 1000
        self._accels: list[tuple[Any, int]] = []
        self._haccel: Any = None
        self.context_menu: Any = None
        self.cancel_button: Any = None
        self._shown = False
        # No WS_CLIPCHILDREN: group boxes do not paint their interior, the window must erase it
        # (else moved or hidden controls leave stale pixels inside a group).
        self._style = _api.WS_OVERLAPPEDWINDOW
        if not resizable:
            self._style &= ~(_api.WS_THICKFRAME | _api.WS_MAXIMIZEBOX)
        self._ex_style = _api.WS_EX_CONTROLPARENT

        self.on_close: Callable[[], bool | None] | None = None
        self.on_destroy: Callable[[], None] | None = None
        self.on_resize: Callable[[int, int], None] | None = None

        self._create()
        self._set_client_size(size)

    # -- properties ----------------------------------------------------------
    @property
    def hwnd(self) -> int:
        if self._hwnd is None:
            raise RuntimeError("the window has been destroyed")
        return self._hwnd

    @property
    def alive(self) -> bool:
        return self._hwnd is not None

    @property
    def dpi(self) -> int:
        """DPI of the monitor the window is on (96 = 100 %)."""
        return self._dpi

    @property
    def scale(self) -> Scale:
        return Scale(self._dpi)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        if self._hwnd:
            user32.SetWindowTextW(self._hwnd, value)

    @property
    def size(self) -> tuple[int, int]:
        """Client size in DIPs."""
        w, h = self._client_px()
        scale = self.scale
        return round(scale.dip(w)), round(scale.dip(h))

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self._set_client_size(value)

    # -- content -------------------------------------------------------------
    def add(self, node: Node) -> Node:
        """Set the root container (called automatically for the first container in ``with``)."""
        if self._root is not None:
            raise LayoutError(
                "a Window takes exactly one root container; put further content into a VBox/HBox"
            )
        self._root = node
        try:
            node._parent = self  # type: ignore[attr-defined]
        except AttributeError:
            pass
        return node

    @property
    def status_bar(self) -> Any:
        """The window's :class:`StatusBar`, or ``None``."""
        return self._status

    # -- menus, shortcuts, commands --------------------------------------------
    def _register_command(self, handler: Callable[[], object]) -> int:
        """A command id for a menu item or shortcut (delivered as WM_COMMAND)."""
        ident = self._next_command
        self._next_command += 1
        self._commands[ident] = handler
        return ident

    def _attach_menubar(self, bar: Any) -> None:
        if self._menubar is not None:
            raise LayoutError("a Window has only one MenuBar")
        size = self.size  # the client size the program asked for
        self._menubar = bar
        if not user32.SetMenu(self.hwnd, bar._hmenu):
            raise _api.last_error("SetMenu")
        self._set_client_size(size)  # the bar takes room: grow the window to keep the client size

    def _add_accelerator(self, shortcut: Any, ident: int) -> None:
        self._accels.append((shortcut, ident))
        self._rebuild_accelerators()

    def _rebuild_accelerators(self) -> None:
        if self._haccel:
            user32.DestroyAcceleratorTable(self._haccel)
            self._haccel = None
        if not self._accels:
            return
        table = (_api.ACCEL * len(self._accels))()
        for slot, (shortcut, ident) in zip(table, self._accels):
            slot.fVirt = (
                _api.FVIRTKEY
                | (_api.FCONTROL if shortcut.ctrl else 0)
                | (_api.FSHIFT if shortcut.shift else 0)
                | (_api.FALT if shortcut.alt else 0)
            )
            slot.key = shortcut.vk
            slot.cmd = ident
        handle = user32.CreateAcceleratorTableW(table, len(table))
        if not handle:
            raise _api.last_error("CreateAcceleratorTableW")
        self._haccel = handle

    def add_shortcut(self, keys: str, handler: Callable[[], object]) -> None:
        """Run ``handler`` when ``keys`` (e.g. ``"Ctrl+K"``, ``"F5"``) is pressed in this window."""
        from barewingui.shortcuts import parse_shortcut

        self._add_accelerator(parse_shortcut(keys), self._register_command(handler))

    def show_modal(self, parent: "Window | None" = None) -> None:
        """
        Show the window and wait until it is closed. ``parent`` is blocked meanwhile
        and becomes the owner (the dialog stays on top of it).
        """
        app = self._app
        app._check_thread()
        owner = parent.hwnd if parent is not None and parent.alive else None
        if owner:
            user32.SetWindowLongPtrW(self.hwnd, _api.GWLP_HWNDPARENT, owner)
            user32.EnableWindow(owner, False)
        try:
            self.show()
            app._pump(until=lambda: not self.alive)
        finally:
            if owner and parent is not None and parent.alive:
                user32.EnableWindow(owner, True)
                user32.SetForegroundWindow(owner)

    def relayout(self) -> None:
        """Place the root container to fill the client area."""
        if self._hwnd is None or self._root is None:
            return
        w, h = self._client_px()
        status_h = self._status.reposition(self.scale) if self._status is not None else 0
        self._root.place(Rect(0, 0, w, max(0, h - status_h)), self.scale)

    # -- lifecycle -----------------------------------------------------------
    def show(self) -> None:
        if self._hwnd:
            self._shown = True
            self.relayout()
            user32.ShowWindow(self._hwnd, _api.SW_SHOW)
            user32.UpdateWindow(self._hwnd)

    def hide(self) -> None:
        if self._hwnd:
            user32.ShowWindow(self._hwnd, _api.SW_HIDE)

    def close(self) -> None:
        """Ask the window to close (like the X button; ``on_close`` may veto). Thread-safe."""
        if self._hwnd:
            user32.PostMessageW(self._hwnd, _api.WM_CLOSE, 0, 0)

    def destroy(self) -> None:
        """Destroy the native window immediately (UI thread only)."""
        if self._hwnd:
            user32.DestroyWindow(self._hwnd)

    # -- internals -----------------------------------------------------------
    def _show_if_unseen(self) -> None:
        if not self._shown:
            self.show()

    def _create(self) -> None:
        app = self._app
        key = app._next_key
        app._next_key += 1
        app._pending[key] = self
        try:
            global _window_proc_ptr
            if _window_proc_ptr is None:
                _window_proc_ptr = _api.WNDPROC(_window_proc)
            _api.register_window_class(
                _CLASS_NAME, _window_proc_ptr, background=_api.COLOR_BTNFACE + 1
            )
            hwnd = user32.CreateWindowExW(
                self._ex_style, _CLASS_NAME, self._title, self._style,
                _api.CW_USEDEFAULT, _api.CW_USEDEFAULT, _api.CW_USEDEFAULT, _api.CW_USEDEFAULT,
                None, None, kernel32.GetModuleHandleW(None), key,
            )
            if not hwnd:
                raise _api.last_error("CreateWindowExW")
        finally:
            app._pending.pop(key, None)
        if self._hwnd != hwnd:  # WM_NCCREATE normally did this already
            self._hwnd = hwnd
            app._windows[hwnd] = self
        dpi = user32.GetDpiForWindow(hwnd)
        self._dpi = dpi or BASE_DPI

    def _client_px(self) -> tuple[int, int]:
        rc = wintypes.RECT()
        if self._hwnd and user32.GetClientRect(self._hwnd, ctypes.byref(rc)):
            return rc.right - rc.left, rc.bottom - rc.top
        return 0, 0

    def _outer_px(self, client_w: int, client_h: int) -> tuple[int, int]:
        """Outer window size in pixels that yields the given client size at the current DPI."""
        rc = wintypes.RECT(0, 0, client_w, client_h)
        if not user32.AdjustWindowRectExForDpi(
            ctypes.byref(rc), self._style, self._menubar is not None, self._ex_style, self._dpi
        ):
            raise _api.last_error("AdjustWindowRectExForDpi")
        return rc.right - rc.left, rc.bottom - rc.top

    def _set_client_size(self, size_dip: tuple[int, int]) -> None:
        scale = self.scale
        outer_w, outer_h = self._outer_px(scale.px(size_dip[0]), scale.px(size_dip[1]))
        user32.SetWindowPos(
            self.hwnd, None, 0, 0, outer_w, outer_h,
            _api.SWP_NOMOVE | _api.SWP_NOZORDER | _api.SWP_NOACTIVATE,
        )

    def _dispatch(self, msg: int, wparam: int, lparam: int) -> tuple[bool, int]:
        """Handle one message. Returns ``(handled, result)``; unhandled goes to DefWindowProc."""
        if msg == _api.WM_SIZE:
            if wparam != _api.SIZE_MINIMIZED:
                self.relayout()
                if self.on_resize is not None:
                    self.on_resize(*self.size)
            return True, 0

        if msg == _api.WM_DPICHANGED:
            self._dpi = wparam & 0xFFFF
            suggested = ctypes.cast(lparam, ctypes.POINTER(wintypes.RECT)).contents
            user32.SetWindowPos(
                self.hwnd, None, suggested.left, suggested.top,
                suggested.right - suggested.left, suggested.bottom - suggested.top,
                _api.SWP_NOZORDER | _api.SWP_NOACTIVATE,
            )
            for control in list(self._controls.values()):
                control._dpi_changed(self._dpi)
            self.relayout()
            return True, 0

        if msg == _api.WM_COMMAND:
            if lparam:
                control = self._controls.get(lparam & _PTR_MASK)
                if control is not None:
                    control._command((wparam >> 16) & 0xFFFF)
                    return True, 0
            else:
                ident = wparam & 0xFFFF
                handler = self._commands.get(ident)
                if handler is not None:  # menu item or shortcut
                    handler()
                    return True, 0
                if ident == _api.IDOK and self.default_button is not None:
                    self.default_button.click()  # Enter pressed inside a text box
                    return True, 0
                if ident == _api.IDCANCEL and self.cancel_button is not None:
                    self.cancel_button.click()  # Esc
                    return True, 0
            return False, 0

        if msg == _api.WM_CONTEXTMENU:
            control = self._controls.get(wparam & _PTR_MASK)
            menu = getattr(control, "context_menu", None) or self.context_menu
            if menu is not None:
                x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                if lparam & 0xFFFFFFFF == 0xFFFFFFFF:  # opened with the keyboard: use the control's corner
                    rc = wintypes.RECT()
                    user32.GetWindowRect(wparam & _PTR_MASK or self.hwnd, ctypes.byref(rc))
                    x, y = rc.left + 8, rc.top + 8
                else:
                    x, y = x - 0x10000 if x & 0x8000 else x, y - 0x10000 if y & 0x8000 else y
                menu.popup(x, y)
                return True, 0
            return False, 0

        if msg in (_api.WM_HSCROLL, _api.WM_VSCROLL) and lparam:
            control = self._controls.get(lparam & _PTR_MASK)
            if control is not None:
                control._scroll(wparam & 0xFFFF)
                return True, 0
            return False, 0

        if msg == _api.WM_NOTIFY and lparam:
            header = ctypes.cast(lparam, ctypes.POINTER(_api.NMHDR)).contents
            control = self._controls.get(header.hwndFrom or 0)
            if control is not None:
                return True, control._notify(header.code, lparam)
            return False, 0

        if msg == _api.WM_GETMINMAXINFO:
            if self._root is not None:
                info = ctypes.cast(lparam, ctypes.POINTER(_api.MINMAXINFO)).contents
                need = self._root.min_size(self.scale)
                status_h = self._status.height_px() if self._status is not None else 0
                outer_w, outer_h = self._outer_px(need.w, need.h + status_h)
                info.ptMinTrackSize.x = outer_w
                info.ptMinTrackSize.y = outer_h
                return True, 0
            return False, 0

        if msg == _api.WM_CLOSE:
            if self.on_close is not None and self.on_close() is False:
                return True, 0
            self.destroy()
            return True, 0

        if msg == _api.WM_DESTROY:
            if self.on_destroy is not None:
                self.on_destroy()
            return False, 0

        if msg == _api.WM_NCDESTROY:
            hwnd, self._hwnd = self._hwnd, None
            self._controls.clear()
            if self._haccel:
                user32.DestroyAcceleratorTable(self._haccel)
                self._haccel = None
            self.default_button = None
            app = self._app
            if hwnd is not None:
                app._windows.pop(hwnd, None)
            if app._running and not app._windows:
                user32.PostQuitMessage(0)
            return False, 0

        return False, 0
