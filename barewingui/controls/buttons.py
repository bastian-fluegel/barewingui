"""Label, Button, CheckBox and RadioButton."""

from __future__ import annotations

from typing import Callable

from barewingui import _api
from barewingui._layout_core import Size
from barewingui.controls._base import Control
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]


def _visible_text(text: str) -> str:
    """Text as shown: ``&x`` loses the marker, ``&&`` becomes ``&``."""
    return text.replace("&&", "\0").replace("&", "").replace("\0", "&")


class Label(Control):
    """
    Static text. A ``&`` in the text marks an access key like in native dialogs
    (write ``&&`` for a literal ampersand).
    """

    def __init__(self, text: str = "", **options: object) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._create("STATIC", text, _api.SS_LEFT)

    def natural_size(self, scale: Scale) -> Size:
        w, h = self._measure(_visible_text(self.text), scale)
        return Size(w, h)


class Button(Control):
    """
    A push button.

    :param default: the default button: highlighted, and Enter in a text box clicks it.
    :param on_click: handler called when the button is clicked (mouse, Space or access key).
    """

    on_click = event()

    def __init__(
        self,
        text: str = "",
        *,
        default: bool = False,
        on_click: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._default = bool(default)
        if on_click is not None:
            self.on_click(on_click)
        style = _api.WS_TABSTOP | (_api.BS_DEFPUSHBUTTON if default else _api.BS_PUSHBUTTON)
        self._create("BUTTON", text, style)

    def _after_create(self) -> None:
        if self._default:
            self._window.default_button = self

    def click(self) -> None:
        """Click the button programmatically (like the user would)."""
        if self.enabled:
            self.on_click.emit()

    def natural_size(self, scale: Scale) -> Size:
        w, h = self._measure(_visible_text(self.text), scale)
        return Size(max(w + scale.px(24), scale.px(75)), max(h + scale.px(10), scale.px(23)))

    def _command(self, code: int) -> None:
        if code == _api.BN_CLICKED:
            self.on_click.emit()


class _Checkable(Control):
    """Shared code of CheckBox and RadioButton."""

    on_change = event()

    def natural_size(self, scale: Scale) -> Size:
        w, h = self._measure(_visible_text(self.text), scale)
        return Size(w + scale.px(22), max(h + scale.px(4), scale.px(17)))

    def _command(self, code: int) -> None:
        if code == _api.BN_CLICKED:
            self.on_change.emit()


class CheckBox(_Checkable):
    """
    A check box.

    :param checked: initial state.
    :param tristate: allow an in-between state (``checked`` is then ``None``).
    """

    def __init__(
        self,
        text: str = "",
        *,
        checked: bool | None = False,
        tristate: bool = False,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if on_change is not None:
            self.on_change(on_change)
        style = _api.WS_TABSTOP | (_api.BS_AUTO3STATE if tristate else _api.BS_AUTOCHECKBOX)
        self._create("BUTTON", text, style)
        self.checked = checked

    @property
    def checked(self) -> bool | None:
        state = self._send(_api.BM_GETCHECK)
        return None if state == _api.BST_INDETERMINATE else state == _api.BST_CHECKED

    @checked.setter
    def checked(self, value: bool | None) -> None:
        state = _api.BST_INDETERMINATE if value is None else (
            _api.BST_CHECKED if value else _api.BST_UNCHECKED
        )
        self._send(_api.BM_SETCHECK, state)


class RadioButton(_Checkable):
    """
    A radio button. Radio buttons created one after another form a group
    (only one can be checked); any other control in between, or
    ``new_group=True``, starts a new group.
    """

    def __init__(
        self,
        text: str = "",
        *,
        checked: bool = False,
        new_group: bool = False,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if on_change is not None:
            self.on_change(on_change)
        window = self._window
        previous = getattr(window, "_last_control", None)
        starts_group = new_group or not isinstance(previous, RadioButton)
        style = _api.BS_AUTORADIOBUTTON | (_api.WS_GROUP | _api.WS_TABSTOP if starts_group else 0)
        self._create("BUTTON", text, style)
        if checked:
            self.checked = True

    @property
    def checked(self) -> bool:
        return self._send(_api.BM_GETCHECK) == _api.BST_CHECKED

    @checked.setter
    def checked(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("RadioButton.checked must be True or False")
        self._send(_api.BM_SETCHECK, _api.BST_CHECKED if value else _api.BST_UNCHECKED)
