"""
barewingui.controls.button
~~~~~~~~~~~~~~~~~~~~~~~~~~
Native Win32 button controls: Button, CheckBox, and RadioButton.
Handles BM_* message communication, checked states, and click callbacks.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Callable, ClassVar

from barewingui.constants import ButtonNotification, ButtonStyle, WindowStyle
from barewingui.controls.base import Control
from barewingui.types import user32

if TYPE_CHECKING:
    from barewingui.window import Window

# ---------------------------------------------------------------------------
# Win32 Button Control Messages & State Constants
# ---------------------------------------------------------------------------
BM_GETCHECK: int = 0x00F0
BM_SETCHECK: int = 0x00F1

BST_UNCHECKED: int = 0x0000
BST_CHECKED: int = 0x0001
BST_INDETERMINATE: int = 0x0002


class Button(Control):
    """
    Nativer Win32 PushButton (BS_PUSHBUTTON / BS_DEFPUSHBUTTON).
    """

    _WIN32_CLASS: ClassVar[str] = "BUTTON"

    def __init__(
        self,
        parent: Window,
        text: str = "Button",
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (120, 32),
        on_click: Callable[[], None] | None = None,
        default: bool = False,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_click = on_click
        btn_style = (
            int(ButtonStyle.DEFPUSHBUTTON if default else ButtonStyle.PUSHBUTTON)
            | int(WindowStyle.TABSTOP)
        )
        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            text=text,
            style=btn_style,
            visible=visible,
            enabled=enabled,
        )

    def _handle_command(self, notification_code: int) -> None:
        if notification_code == int(ButtonNotification.CLICKED):
            if self.on_click is not None:
                self.on_click()


class CheckBox(Control):
    """
    Natives Win32 CheckBox-Steuerelement mit automatischem Statuswechsel (BS_AUTOCHECKBOX).
    Unterstützt Callbacks sowohl ohne Parameter als auch mit dem aktuellen Boolean-Zustand.
    """

    _WIN32_CLASS: ClassVar[str] = "BUTTON"

    def __init__(
        self,
        parent: Window,
        text: str = "CheckBox",
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (160, 24),
        checked: bool = False,
        on_click: Callable[[bool], None] | Callable[[], None] | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_click = on_click
        chk_style = int(ButtonStyle.AUTOCHECKBOX) | int(WindowStyle.TABSTOP)

        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            text=text,
            style=chk_style,
            visible=visible,
            enabled=enabled,
        )

        if checked:
            self.checked = True

    @property
    def checked(self) -> bool:
        """Gibt True zurück, wenn die Checkbox angewählt ist."""
        if not self._hwnd:
            return False
        state = user32.SendMessageW(self._hwnd, BM_GETCHECK, 0, 0)
        return state == BST_CHECKED

    @checked.setter
    def checked(self, value: bool) -> None:
        """Setzt den Auswahlstatus der Checkbox über BM_SETCHECK."""
        if self._hwnd:
            state = BST_CHECKED if value else BST_UNCHECKED
            user32.SendMessageW(self._hwnd, BM_SETCHECK, state, 0)

    def _handle_command(self, notification_code: int) -> None:
        if notification_code == int(ButtonNotification.CLICKED):
            if self.on_click is None:
                return

            # Automatische Parameter-Erkennung für flexibles Callback-Binding
            try:
                sig = inspect.signature(self.on_click)
                if len(sig.parameters) > 0:
                    self.on_click(self.checked)  # type: ignore[call-arg]
                else:
                    self.on_click()  # type: ignore[call-arg]
            except (ValueError, TypeError):
                self.on_click()  # type: ignore[call-arg]


class RadioButton(Control):
    """
    Nativer Win32 RadioButton (BS_AUTORADIOBUTTON).
    Das Setzen von `group_start=True` markiert den Beginn einer logischen Optionsgruppe (WS_GROUP).
    """

    _WIN32_CLASS: ClassVar[str] = "BUTTON"

    def __init__(
        self,
        parent: Window,
        text: str = "RadioButton",
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (160, 24),
        checked: bool = False,
        group_start: bool = False,
        on_click: Callable[[], None] | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_click = on_click
        radio_style = int(ButtonStyle.AUTORADIOBUTTON) | int(WindowStyle.TABSTOP)
        if group_start:
            radio_style |= int(WindowStyle.GROUP)

        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            text=text,
            style=radio_style,
            visible=visible,
            enabled=enabled,
        )

        if checked:
            self.checked = True

    @property
    def checked(self) -> bool:
        """Gibt True zurück, wenn dieser RadioButton aktuell aktiv ist."""
        if not self._hwnd:
            return False
        state = user32.SendMessageW(self._hwnd, BM_GETCHECK, 0, 0)
        return state == BST_CHECKED

    @checked.setter
    def checked(self, value: bool) -> None:
        """Setzt den Auswahlstatus des RadioButtons."""
        if self._hwnd:
            state = BST_CHECKED if value else BST_UNCHECKED
            user32.SendMessageW(self._hwnd, BM_SETCHECK, state, 0)

    def _handle_command(self, notification_code: int) -> None:
        if notification_code == int(ButtonNotification.CLICKED):
            if self.on_click is not None:
                self.on_click()