"""TextBox: single-line, password and multi-line text input."""

from __future__ import annotations

import ctypes
from typing import Callable

from barewingui import _api
from barewingui._layout_core import Size
from barewingui.controls._base import Control, normalize_newlines
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]


class TextBox(Control):
    """
    An edit control.

    :param text: initial text.
    :param multiline: several lines, vertical scroll bar.
    :param password: show dots instead of the characters (single-line only).
    :param readonly: the user cannot change the text.
    :param placeholder: grey hint shown while empty (single-line only).
    :param on_change: handler called whenever the text changes.
    """

    on_change = event()

    def __init__(
        self,
        text: str = "",
        *,
        multiline: bool = False,
        password: bool = False,
        readonly: bool = False,
        placeholder: str = "",
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if multiline and (password or placeholder):
            raise ValueError("password and placeholder are only available for single-line text boxes")
        self._multiline = bool(multiline)
        self._readonly = bool(readonly)
        self._placeholder = ""
        style = _api.WS_TABSTOP
        if multiline:
            style |= (
                _api.ES_MULTILINE | _api.ES_AUTOVSCROLL | _api.ES_WANTRETURN | _api.WS_VSCROLL
            )
        else:
            style |= _api.ES_AUTOHSCROLL
            if password:
                style |= _api.ES_PASSWORD
        if readonly:
            style |= _api.ES_READONLY
        self._create("EDIT", "", style, _api.WS_EX_CLIENTEDGE)
        if text:
            self.text = text
        if placeholder:
            self.placeholder = placeholder
        if on_change is not None:
            self.on_change(on_change)

    # -- text ------------------------------------------------------------------
    @property
    def text(self) -> str:
        return normalize_newlines(super().text)

    @text.setter
    def text(self, value: str) -> None:
        value = normalize_newlines(str(value))
        self._set_text(value.replace("\n", "\r\n") if self._multiline else value)

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        if self._multiline:
            raise ValueError("a multi-line text box has no placeholder")
        self._placeholder = value
        buf = ctypes.create_unicode_buffer(value)
        self._send(_api.EM_SETCUEBANNER, 1, ctypes.addressof(buf))

    @property
    def readonly(self) -> bool:
        return self._readonly

    @readonly.setter
    def readonly(self, value: bool) -> None:
        self._readonly = bool(value)
        self._send(_api.EM_SETREADONLY, 1 if self._readonly else 0)

    def select_all(self) -> None:
        self._send(_api.EM_SETSEL, 0, -1)

    # -- layout ----------------------------------------------------------------
    def natural_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        if self._multiline:
            return Size(scale.px(200), h * 5 + scale.px(8))
        return Size(scale.px(150), h + scale.px(8))

    def min_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        if self._multiline:
            return Size(scale.px(40), h * 2 + scale.px(8))
        return Size(scale.px(40), h + scale.px(8))

    def _command(self, code: int) -> None:
        if code == _api.EN_CHANGE and not self._muted:
            self.on_change.emit()


TextInput = TextBox
