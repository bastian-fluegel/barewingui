"""
barewingui.controls.base
~~~~~~~~~~~~~~~~~~~~~~~~
Abstract base class for all native Win32 controls.
Handles child window lifecycle, geometry management, default system font
assignment (WM_SETFONT), and notification message routing.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, ClassVar

from barewingui.constants import (
    ShowWindowCmd,
    WindowStyle,
    WindowStyleEx,
    WM,
)
from barewingui.types import (
    kernel32,
    user32,
)

if TYPE_CHECKING:
    from barewingui.window import Window

# ---------------------------------------------------------------------------
# Zusätzliche USER32-Signaturen für Text-Handling
# ---------------------------------------------------------------------------
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int


class Control:
    """
    Abstrakte Basisklasse für alle nativen Win32-Steuerelemente (Child Windows).
    """

    _WIN32_CLASS: ClassVar[str] = ""

    def __init__(
        self,
        parent: Window,
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (100, 30),
        text: str = "",
        style: int = 0,
        ex_style: int = 0,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        if not self._WIN32_CLASS:
            raise NotImplementedError(
                "Subklassen von Control müssen ein `_WIN32_CLASS`-Attribut definieren."
            )

        self._parent = parent
        self._x, self._y = pos
        self._width, self._height = size
        self._text = text
        self._visible = visible
        self._enabled = enabled

        self._control_id = self._parent.register_control(self)
        self._hwnd: wintypes.HWND | None = None

        # Basis-Stile für Win32-Kindfenster
        native_style = (
            int(WindowStyle.CHILD)
            | (int(WindowStyle.VISIBLE) if visible else 0)
            | (0 if enabled else int(WindowStyle.DISABLED))
            | style
        )

        self._create_native_control(native_style, ex_style)
        self._apply_default_font()
        self._apply_control_theme()

    @property
    def hwnd(self) -> wintypes.HWND:
        if self._hwnd is None:
            raise RuntimeError("Das Steuerelement wurde nicht initialisiert oder zerstört.")
        return self._hwnd

    @property
    def control_id(self) -> int:
        return self._control_id

    @property
    def parent(self) -> Window:
        return self._parent

    @property
    def text(self) -> str:
        if not self._hwnd:
            return self._text
        length = user32.GetWindowTextLengthW(self._hwnd)
        if length == 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(self._hwnd, buffer, length + 1)
        self._text = buffer.value
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        if self._hwnd:
            user32.SetWindowTextW(self._hwnd, value)

    @property
    def pos(self) -> tuple[int, int]:
        return (self._x, self._y)

    @pos.setter
    def pos(self, value: tuple[int, int]) -> None:
        self.move(x=value[0], y=value[1])

    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self.move(width=value[0], height=value[1])

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value
        if self._hwnd:
            cmd = ShowWindowCmd.SHOW if value else ShowWindowCmd.HIDE
            user32.ShowWindow(self._hwnd, int(cmd))

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        if self._hwnd:
            user32.EnableWindow(self._hwnd, value)

    def _create_native_control(self, style: int, ex_style: int) -> None:
        """Erzeugt das native Child-Fenster via CreateWindowExW."""
        h_instance = kernel32.GetModuleHandleW(None)

        hwnd = user32.CreateWindowExW(
            ex_style,
            self._WIN32_CLASS,
            self._text,
            style,
            self._x,
            self._y,
            self._width,
            self._height,
            self._parent.hwnd,
            wintypes.HMENU(self._control_id),
            h_instance,
            None,
        )

        if not hwnd:
            raise RuntimeError(
                f"Konnte Control '{self._WIN32_CLASS}' nicht erzeugen "
                f"(Fehler {kernel32.GetLastError()})"
            )

        self._hwnd = hwnd

    def _apply_control_theme(self) -> None:
        if not self._hwnd:
            return
        from barewingui.theme import apply_control_theme

        apply_control_theme(self._hwnd, self._WIN32_CLASS)

    def _apply_default_font(self) -> None:
        if not self._hwnd:
            return
        from barewingui.core import get_system_font
        h_font = get_system_font()
        if h_font:
            user32.SendMessageW(self._hwnd, int(WM.SETFONT), h_font, 1)

    def _handle_command(self, notification_code: int) -> None:
        """Wird von Window bei WM_COMMAND für dieses Control aufgerufen."""
        pass

    def move(
        self,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Passt Position und Abmessungen des Controls an."""
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height

        if self._hwnd:
            user32.MoveWindow(
                self._hwnd,
                self._x,
                self._y,
                self._width,
                self._height,
                True,
            )

    def focus(self) -> None:
        """Setzt den Eingabefokus auf dieses Control."""
        if self._hwnd:
            user32.SetFocus(self._hwnd)

    def destroy(self) -> None:
        """Zerstört das native Child-Handle."""
        if self._hwnd:
            hwnd_to_destroy = self._hwnd
            self._hwnd = None
            user32.DestroyWindow(hwnd_to_destroy)