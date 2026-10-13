"""ComboBox and ListBox."""

from __future__ import annotations

import ctypes
from typing import Callable, Iterable

from barewingui import _api
from barewingui._layout_core import Size
from barewingui.controls._base import Control
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]


class _ItemControl(Control):
    """Shared item handling of ComboBox and ListBox (items are strings)."""

    # message numbers, set by the subclasses
    _ADD = _INSERT = _DELETE = _RESET = _GETCUR = _SETCUR = 0
    _ERR = -1

    def _init_items(self, items: Iterable[str]) -> None:
        self._items: list[str] = []
        self._muted = True
        try:
            for item in items:
                self.add(item)
        finally:
            self._muted = False

    # -- items -----------------------------------------------------------------
    @property
    def items(self) -> tuple[str, ...]:
        return tuple(self._items)

    @items.setter
    def items(self, values: Iterable[str]) -> None:
        was, self._muted = self._muted, True
        try:
            self.clear()
            for value in values:
                self.add(value)
        finally:
            self._muted = was

    def add(self, text: str) -> None:
        """Append an item."""
        text = str(text)
        buf = ctypes.create_unicode_buffer(text)
        self._send(self._ADD, 0, ctypes.addressof(buf))
        self._items.append(text)
        self._content_changed()

    def insert(self, index: int, text: str) -> None:
        text = str(text)
        index = max(0, min(index, len(self._items)))
        buf = ctypes.create_unicode_buffer(text)
        self._send(self._INSERT, index, ctypes.addressof(buf))
        self._items.insert(index, text)
        self._content_changed()

    def remove(self, index: int) -> None:
        """Remove the item at ``index``."""
        if not 0 <= index < len(self._items):
            raise IndexError(f"item index {index} out of range")
        self._send(self._DELETE, index)
        del self._items[index]
        self._content_changed()

    def clear(self) -> None:
        self._send(self._RESET)
        self._items.clear()
        self._content_changed()

    def __len__(self) -> int:
        return len(self._items)

    # -- selection -------------------------------------------------------------
    @property
    def selected_index(self) -> int | None:
        """Index of the selected item, or ``None``."""
        index = self._send(self._GETCUR)
        return None if index == self._ERR else index

    @selected_index.setter
    def selected_index(self, index: int | None) -> None:
        if index is not None and not 0 <= index < len(self._items):
            raise IndexError(f"item index {index} out of range")
        was, self._muted = self._muted, True
        try:
            self._send(self._SETCUR, -1 if index is None else index)
        finally:
            self._muted = was

    @property
    def selected(self) -> str | None:
        """Text of the selected item, or ``None``."""
        index = self.selected_index
        return None if index is None else self._items[index]

    @selected.setter
    def selected(self, text: str | None) -> None:
        self.selected_index = None if text is None else self._items.index(text)

    def _widest(self, scale: Scale) -> int:
        return max((self._measure(item, scale)[0] for item in self._items), default=0)


class ComboBox(_ItemControl):
    """
    A drop-down list.

    :param items: the entries.
    :param selected: index of the entry to select first (default: none).
    :param editable: the user may type free text (read it with :attr:`text`).
    :param on_change: called when the selection changes (or, if editable, the text).
    """

    on_change = event()
    _ADD, _INSERT, _DELETE, _RESET = (
        _api.CB_ADDSTRING, _api.CB_INSERTSTRING, _api.CB_DELETESTRING, _api.CB_RESETCONTENT,
    )
    _GETCUR, _SETCUR, _ERR = _api.CB_GETCURSEL, _api.CB_SETCURSEL, _api.CB_ERR

    def __init__(
        self,
        items: Iterable[str] = (),
        *,
        selected: int | None = None,
        editable: bool = False,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._editable = bool(editable)
        style = _api.WS_TABSTOP | _api.WS_VSCROLL
        style |= (_api.CBS_DROPDOWN | _api.CBS_AUTOHSCROLL) if editable else _api.CBS_DROPDOWNLIST
        self._create("COMBOBOX", "", style)
        self._send(_api.CB_SETMINVISIBLE, 10)
        self._init_items(items)
        if selected is not None:
            self.selected_index = selected
        if on_change is not None:
            self.on_change(on_change)

    @property
    def text(self) -> str:
        """Selected text; for an editable combo box the text in its edit field."""
        if self._editable:
            return super().text
        return self.selected or ""

    @text.setter
    def text(self, value: str) -> None:
        if not self._editable:
            raise AttributeError("only an editable ComboBox has settable text; use selected")
        self._set_text(str(value))

    def natural_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        return Size(max(scale.px(120), self._widest(scale) + scale.px(34)), h + scale.px(9))

    def min_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        return Size(scale.px(60), h + scale.px(9))

    def _command(self, code: int) -> None:
        if self._muted:
            return
        if code == _api.CBN_SELCHANGE or (self._editable and code == _api.CBN_EDITCHANGE):
            self.on_change.emit()


class ListBox(_ItemControl):
    """
    A scrolling list of strings.

    :param items: the entries.
    :param multi: allow selecting several entries (:attr:`selected_indices`).
    :param on_change: called when the selection changes.
    :param on_activate: called on double click (open/accept the entry).
    """

    on_change = event()
    on_activate = event()
    _ADD, _INSERT, _DELETE, _RESET = (
        _api.LB_ADDSTRING, _api.LB_INSERTSTRING, _api.LB_DELETESTRING, _api.LB_RESETCONTENT,
    )
    _GETCUR, _SETCUR, _ERR = _api.LB_GETCURSEL, _api.LB_SETCURSEL, _api.LB_ERR

    def __init__(
        self,
        items: Iterable[str] = (),
        *,
        multi: bool = False,
        selected: int | None = None,
        on_change: Handler | None = None,
        on_activate: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._multi = bool(multi)
        style = _api.WS_TABSTOP | _api.WS_VSCROLL | _api.LBS_NOTIFY | _api.LBS_NOINTEGRALHEIGHT
        if multi:
            style |= _api.LBS_EXTENDEDSEL
        self._create("LISTBOX", "", style, _api.WS_EX_CLIENTEDGE)
        self._init_items(items)
        if selected is not None:
            self.selected_index = selected
        if on_change is not None:
            self.on_change(on_change)
        if on_activate is not None:
            self.on_activate(on_activate)

    @property
    def selected_indices(self) -> tuple[int, ...]:
        """All selected indices (works for single and multi selection)."""
        if not self._multi:
            index = self.selected_index
            return () if index is None else (index,)
        count = self._send(_api.LB_GETSELCOUNT)
        if count <= 0:
            return ()
        buf = (ctypes.c_int * count)()
        got = self._send(_api.LB_GETSELITEMS, count, ctypes.addressof(buf))
        return tuple(buf[:got]) if got > 0 else ()

    @selected_indices.setter
    def selected_indices(self, indices: Iterable[int]) -> None:
        wanted = set(indices)
        if not self._multi:
            if len(wanted) > 1:
                raise ValueError("this ListBox allows only one selected item (multi=False)")
            self.selected_index = next(iter(wanted), None)
            return
        was, self._muted = self._muted, True
        try:
            for i in range(len(self._items)):
                self._send(_api.LB_SETSEL, 1 if i in wanted else 0, i)
        finally:
            self._muted = was

    @property
    def selected_items(self) -> tuple[str, ...]:
        return tuple(self._items[i] for i in self.selected_indices)

    def natural_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        return Size(max(scale.px(120), self._widest(scale) + scale.px(28)), h * 6 + scale.px(4))

    def min_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        return Size(scale.px(40), h * 2 + scale.px(4))

    def _command(self, code: int) -> None:
        if self._muted:
            return
        if code == _api.LBN_SELCHANGE:
            self.on_change.emit()
        elif code == _api.LBN_DBLCLK:
            self.on_activate.emit()
