"""
barewingui.controls.text
~~~~~~~~~~~~~~~~~~~~~~~~
Native Win32 text controls: Label (STATIC) and TextInput (EDIT).
Supports single-line, multi-line, password masking, read-only states,
and real-time text change notifications.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Callable, ClassVar, Literal

from barewingui.constants import (
    EC_LEFTMARGIN,
    EC_RIGHTMARGIN,
    EditMessage,
    EditNotification,
    EditStyle,
    StaticStyle,
    WindowStyle,
)
from barewingui.controls.base import Control
from barewingui.types import user32

if TYPE_CHECKING:
    from barewingui.window import Window

TextAlign = Literal["left", "center", "right"]


class Label(Control):
    """
    Natives Win32 Text-Label auf Basis der Fensterklasse 'STATIC'.
    Dient zur Anzeige von statischen Beschriftungen und Informationstexten.
    """

    _WIN32_CLASS: ClassVar[str] = "STATIC"

    def __init__(
        self,
        parent: Window,
        text: str = "",
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (120, 20),
        align: TextAlign = "left",
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        align_style = StaticStyle.LEFT
        if align == "center":
            align_style = StaticStyle.CENTER
        elif align == "right":
            align_style = StaticStyle.RIGHT

        # SS_NOPREFIX verhindert, dass ein kaufmännisches Und (&) als Unterstrich gerendert wird
        static_style = int(align_style) | int(StaticStyle.NOPREFIX)

        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            text=text,
            style=static_style,
            visible=visible,
            enabled=enabled,
        )


class TextInput(Control):
    """
    Natives Win32 Eingabefeld auf Basis der Fensterklasse 'EDIT'.
    Unterstützt Einzeilen- und Mehrzeilenbetrieb, Passwortmaskierung,
    Schreibschutz (Read-Only) und Ereignis-Callbacks bei Textänderungen.
    """

    _WIN32_CLASS: ClassVar[str] = "EDIT"

    def __init__(
        self,
        parent: Window,
        text: str = "",
        pos: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (160, 32),
        password: bool = False,
        multiline: bool = False,
        readonly: bool = False,
        on_change: Callable[[str], None] | Callable[[], None] | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        self.on_change = on_change
        self._readonly = readonly
        self._multiline = multiline
        self._password = password

        # Standard-Styling für Win32 Edit-Controls
        edit_style = int(WindowStyle.TABSTOP)

        if multiline:
            edit_style |= (
                int(EditStyle.MULTILINE)
                | int(EditStyle.AUTOVSCROLL)
                | int(EditStyle.WANTRETURN)
                | int(WindowStyle.VSCROLL)
            )
        else:
            edit_style |= int(EditStyle.AUTOHSCROLL)

        if password and not multiline:
            edit_style |= int(EditStyle.PASSWORD)

        if readonly:
            edit_style |= int(EditStyle.READONLY)

        # Kein WS_BORDER: pechschwarze 1px-Linie. Den Rahmen zeichnet das CFD-Theme.
        super().__init__(
            parent=parent,
            pos=pos,
            size=size,
            text=text,
            style=edit_style,
            ex_style=0,
            visible=visible,
            enabled=enabled,
        )
        self._apply_text_margins()

    def _apply_text_margins(self) -> None:
        """8px Innenabstand, damit der Text nicht am Rahmen klebt."""
        if not self._hwnd:
            return
        user32.SendMessageW(
            self._hwnd,
            int(EditMessage.SETMARGINS),
            EC_LEFTMARGIN | EC_RIGHTMARGIN,
            (8 << 16) | 8,
        )

    @property
    def readonly(self) -> bool:
        """Gibt zurück, ob das Eingabefeld schreibgeschützt ist."""
        return self._readonly

    @readonly.setter
    def readonly(self, value: bool) -> None:
        """Aktiviert oder deaktiviert den Schreibschutz über EM_SETREADONLY."""
        self._readonly = bool(value)
        if self._hwnd:
            user32.SendMessageW(
                self._hwnd,
                int(EditMessage.SETREADONLY),
                1 if self._readonly else 0,
                0,
            )

    def select_all(self) -> None:
        """Markiert den gesamten Text im Eingabefeld."""
        if self._hwnd:
            # EM_SETSEL: wParam=0, lParam=-1 wählt den gesamten Bereich aus
            user32.SendMessageW(self._hwnd, int(EditMessage.SETSEL), 0, -1)

    def clear(self) -> None:
        """Leert das Eingabefeld."""
        self.text = ""

    def _handle_command(self, notification_code: int) -> None:
        """Verarbeitet Benachrichtigungscodes von Windows für das Edit-Control."""
        if notification_code == int(EditNotification.CHANGE):
            if self.on_change is None:
                return

            try:
                sig = inspect.signature(self.on_change)
                if len(sig.parameters) > 0:
                    self.on_change(self.text)  # type: ignore[call-arg]
                else:
                    self.on_change()  # type: ignore[call-arg]
            except (ValueError, TypeError):
                self.on_change()  # type: ignore[call-arg]