"""
barewingui.controls.choice
~~~~~~~~~~~~~~~~~~~~~~~~~~
Native Win32 selection controls: ComboBox (Dropdown) and ListBox.
Handles string populations, selection queries, and dropdown height corrections.
"""

from __future__ import annotations

import ctypes
import inspect
from typing import TYPE_CHECKING, Callable, ClassVar

from barewingui.constants import WindowStyle, WindowStyleEx
from barewingui.controls.base import Control
from barewingui.types import user32

if TYPE_CHECKING:
    from barewingui.window import Window

# ---------------------------------------------------------------------------
# ComboBox Messages & Styles
# ---------------------------------------------------------------------------
CBS_DROPDOWN = 0x0002
CBS_DROPDOWNLIST = 0x0003
CBS_HASSTRINGS = 0x0200
CBS_AUTOHSCROLL = 0x0040

CB_ADDSTRING = 0x0143
CB_DELETESTRING = 0x0144
CB_GETCOUNT = 0x0146
CB_GETCURSEL = 0x0147
CB_SETCURSEL = 0x014E
CB_GETLBTEXT = 0x0148
CB_GETLBTEXTLEN = 0x0149
CB_RESETCONTENT = 0x014B

CBN_SELCHANGE = 1

# ---------------------------------------------------------------------------
# ListBox Messages & Styles
# ---------------------------------------------------------------------------
LBS_NOTIFY = 0x0001
LBS_NOINTEGRALHEIGHT = 0x0100

LB_ADDSTRING = 0x0180
LB_DELETESTRING = 0x0182
LB_GETCURSEL = 0x0188
LB_SETCURSEL = 0x0186
LB_GETCOUNT = 0x018B
LB_GETTEXT = 0x0189
LB_GETTEXTLEN = 0x018A
LB_RESETCONTENT = 0x0184

LBN_SELCHANGE = 1
LBN_DBLCLK = 2


def _send_string(hwnd: object, message: int, text: str) -> None:
    """Sendet CB_ADDSTRING / LB_ADDSTRING mit einem gültigen LPCWSTR als LPARAM."""
    buf = ctypes.c_wchar_p(text)
    user32.SendMessageW(hwnd, message, 0, ctypes.cast(buf, ctypes.c_void_p).value or 0)


class ComboBox(Control):
    """
    Natives Win32 Dropdown-Auswahlfeld (COMBOBOX).
    Löst das Win32-Höhenproblem (Dropdown-Aufklapphöhe) automatisch auf.
    """

    _WIN32_CLASS: ClassVar[str] = "COMBOBOX"

    def __init__(
        self,
        parent: Window,
        items: list[str] | None = None,
        selected_index: int = 0,
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (160, 26),
        dropdown_height: int = 220,
        on_change: Callable[[int, str], None] | Callable[[str], None] | Callable[[], None] | None = None,
        editable: bool = False,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_change = on_change
        self.dropdown_height = dropdown_height
        self._items: list[str] = []

        combo_style = (
            int(WindowStyle.TABSTOP)
            | int(WindowStyle.VSCROLL)
            | (CBS_DROPDOWN if editable else CBS_DROPDOWNLIST)
            | CBS_HASSTRINGS
            | CBS_AUTOHSCROLL
        )

        # Win32-Besonderheit: In CreateWindowExW muss für ComboBoxen die Höhe
        # des aufgeklappten Menüs übergeben werden, sonst klappt die Liste nicht auf.
        create_size = (size[0], dropdown_height)

        super().__init__(
            parent=parent,
            pos=pos,
            size=create_size,
            style=combo_style,
            visible=visible,
            enabled=enabled,
        )

        # Gespeicherte Höhe für Layout-Manager auf tatsächliche Control-Höhe setzen
        self._height = size[1]

        if items:
            for item in items:
                self.add(item)
            if 0 <= selected_index < len(items):
                self.selected_index = selected_index

    def move(
        self,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Sichert zu, dass die Dropdown-Liste beim Resize durch Layouts nicht kollabiert."""
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height

        if self._hwnd:
            # Dropdown-Höhe für Windows beibehalten
            user32.MoveWindow(
                self._hwnd,
                self._x,
                self._y,
                self._width,
                max(self._height, self.dropdown_height),
                True,
            )

    def add(self, item: str) -> None:
        """Fügt einen Eintrag hinzu."""
        self._items.append(item)
        if self._hwnd:
            _send_string(self._hwnd, CB_ADDSTRING, item)

    def clear(self) -> None:
        """Leert alle Einträge."""
        self._items.clear()
        if self._hwnd:
            user32.SendMessageW(self._hwnd, CB_RESETCONTENT, 0, 0)

    @property
    def selected_index(self) -> int:
        if not self._hwnd:
            return -1
        return int(user32.SendMessageW(self._hwnd, CB_GETCURSEL, 0, 0))

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        if self._hwnd:
            user32.SendMessageW(self._hwnd, CB_SETCURSEL, index, 0)

    @property
    def selected_text(self) -> str | None:
        idx = self.selected_index
        if idx < 0 or idx >= len(self._items):
            return None
        return self._items[idx]

    def _handle_command(self, notification_code: int) -> None:
        if notification_code == CBN_SELCHANGE:
            if self.on_change is None:
                return
            idx = self.selected_index
            text = self.selected_text or ""
            try:
                sig = inspect.signature(self.on_change)
                param_count = len(sig.parameters)
                if param_count == 2:
                    self.on_change(idx, text)  # type: ignore[call-arg]
                elif param_count == 1:
                    self.on_change(text)  # type: ignore[call-arg]
                else:
                    self.on_change()  # type: ignore[call-arg]
            except (ValueError, TypeError):
                self.on_change()  # type: ignore[call-arg]


class ListBox(Control):
    """
    Natives Win32 Listenfeld (LISTBOX).
    Unterstützt Scrollbars, Einzelklick- und Doppelklick-Events.
    """

    _WIN32_CLASS: ClassVar[str] = "LISTBOX"

    def __init__(
        self,
        parent: Window,
        items: list[str] | None = None,
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (180, 120),
        on_change: Callable[[int, str], None] | Callable[[str], None] | Callable[[], None] | None = None,
        on_double_click: Callable[[int, str], None] | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_change = on_change
        self.on_double_click = on_double_click
        self._items: list[str] = []

        lb_style = (
            int(WindowStyle.TABSTOP)
            | int(WindowStyle.VSCROLL)
            | LBS_NOTIFY
            | LBS_NOINTEGRALHEIGHT
        )
        ex_style = int(WindowStyleEx.CLIENTEDGE)

        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            style=lb_style,
            ex_style=ex_style,
            visible=visible,
            enabled=enabled,
        )

        if items:
            for item in items:
                self.add(item)

    def add(self, item: str) -> None:
        """Fügt einen Eintrag an das Ende der Liste an."""
        self._items.append(item)
        if self._hwnd:
            _send_string(self._hwnd, LB_ADDSTRING, item)

    def clear(self) -> None:
        """Leert die Liste."""
        self._items.clear()
        if self._hwnd:
            user32.SendMessageW(self._hwnd, LB_RESETCONTENT, 0, 0)

    @property
    def selected_index(self) -> int:
        if not self._hwnd:
            return -1
        return int(user32.SendMessageW(self._hwnd, LB_GETCURSEL, 0, 0))

    @selected_index.setter
    def selected_index(self, index: int) -> None:
        if self._hwnd:
            user32.SendMessageW(self._hwnd, LB_SETCURSEL, index, 0)

    @property
    def selected_text(self) -> str | None:
        idx = self.selected_index
        if idx < 0 or idx >= len(self._items):
            return None
        return self._items[idx]

    def _handle_command(self, notification_code: int) -> None:
        idx = self.selected_index
        text = self.selected_text or ""

        if notification_code == LBN_SELCHANGE and self.on_change:
            try:
                sig = inspect.signature(self.on_change)
                param_count = len(sig.parameters)
                if param_count == 2:
                    self.on_change(idx, text)  # type: ignore[call-arg]
                elif param_count == 1:
                    self.on_change(text)  # type: ignore[call-arg]
                else:
                    self.on_change()  # type: ignore[call-arg]
            except (ValueError, TypeError):
                self.on_change()  # type: ignore[call-arg]

        elif notification_code == LBN_DBLCLK and self.on_double_click:
            self.on_double_click(idx, text)
