"""ProgressBar, Slider and SpinBox: controls that hold a number."""

from __future__ import annotations

import ctypes
from typing import Callable

from barewingui import _api
from barewingui._api import kernel32, user32
from barewingui._layout_core import Rect, Size
from barewingui.controls._base import Control
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]


class ProgressBar(Control):
    """
    A progress bar.

    :param value: current position.
    :param minimum: / :param maximum: the range.
    :param indeterminate: endless "busy" animation instead of a position.
    """

    def __init__(
        self,
        value: int = 0,
        *,
        minimum: int = 0,
        maximum: int = 100,
        indeterminate: bool = False,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if minimum >= maximum:
            raise ValueError("minimum must be smaller than maximum")
        self._indeterminate = bool(indeterminate)
        self._min, self._max = minimum, maximum
        self._create(
            "msctls_progress32", "", _api.PBS_MARQUEE if indeterminate else 0
        )
        self._send(_api.PBM_SETRANGE32, minimum, maximum)
        if indeterminate:
            self._send(_api.PBM_SETMARQUEE, 1, 30)
        else:
            self.value = value

    @property
    def value(self) -> int:
        return self._send(_api.PBM_GETPOS)

    @value.setter
    def value(self, value: int) -> None:
        self._send(_api.PBM_SETPOS, max(self._min, min(self._max, int(value))))

    @property
    def minimum(self) -> int:
        return self._min

    @property
    def maximum(self) -> int:
        return self._max

    def set_range(self, minimum: int, maximum: int) -> None:
        if minimum >= maximum:
            raise ValueError("minimum must be smaller than maximum")
        self._min, self._max = minimum, maximum
        self._send(_api.PBM_SETRANGE32, minimum, maximum)

    @property
    def state(self) -> str:
        return getattr(self, "_state", "normal")

    @state.setter
    def state(self, value: str) -> None:
        codes = {"normal": _api.PBST_NORMAL, "error": _api.PBST_ERROR, "paused": _api.PBST_PAUSED}
        if value not in codes:
            raise ValueError(f"state must be one of {sorted(codes)}, got {value!r}")
        self._state = value
        self._send(_api.PBM_SETSTATE, codes[value])

    def natural_size(self, scale: Scale) -> Size:
        return Size(scale.px(150), scale.px(15))

    def min_size(self, scale: Scale) -> Size:
        return Size(scale.px(40), scale.px(15))


class Slider(Control):
    """
    A slider (track bar).

    :param value: initial position.
    :param minimum: / :param maximum: the range.
    :param vertical: vertical orientation.
    :param ticks: show tick marks.
    :param on_change: called while the user moves the slider.
    """

    on_change = event()

    def __init__(
        self,
        value: int = 0,
        *,
        minimum: int = 0,
        maximum: int = 100,
        vertical: bool = False,
        ticks: bool = True,
        tick_frequency: int | None = None,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if minimum >= maximum:
            raise ValueError("minimum must be smaller than maximum")
        self._min, self._max = minimum, maximum
        self._vertical = bool(vertical)
        self._ticks = bool(ticks)
        style = _api.WS_TABSTOP | (_api.TBS_AUTOTICKS if ticks else _api.TBS_NOTICKS)
        if vertical:
            style |= _api.TBS_VERT
        self._create("msctls_trackbar32", "", style)
        self._send(_api.TBM_SETRANGEMIN, 0, minimum)
        self._send(_api.TBM_SETRANGEMAX, 1, maximum)
        if tick_frequency:
            self._send(_api.TBM_SETTICFREQ, tick_frequency)
        self.value = value
        if on_change is not None:
            self.on_change(on_change)

    @property
    def value(self) -> int:
        return self._send(_api.TBM_GETPOS)

    @value.setter
    def value(self, value: int) -> None:
        self._send(_api.TBM_SETPOS, 1, max(self._min, min(self._max, int(value))))

    @property
    def minimum(self) -> int:
        return self._min

    @property
    def maximum(self) -> int:
        return self._max

    def natural_size(self, scale: Scale) -> Size:
        long_side, short_side = scale.px(150), scale.px(32 if self._ticks else 26)
        return Size(short_side, long_side) if self._vertical else Size(long_side, short_side)

    def min_size(self, scale: Scale) -> Size:
        long_side, short_side = scale.px(50), scale.px(32 if self._ticks else 26)
        return Size(short_side, long_side) if self._vertical else Size(long_side, short_side)

    def _scroll(self, code: int) -> None:
        if code != _api.TB_ENDTRACK and not self._muted:
            self.on_change.emit()


class SpinBox(Control):
    """
    A number field with up/down arrows.

    :param value: initial number.
    :param minimum: / :param maximum: allowed range (the arrows stop there).
    :param on_change: called when the number changes.
    """

    on_change = event()

    def __init__(
        self,
        value: int = 0,
        *,
        minimum: int = 0,
        maximum: int = 100,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if minimum >= maximum:
            raise ValueError("minimum must be smaller than maximum")
        self._min, self._max = minimum, maximum
        self._updown: int | None = None
        self._value_on_create = value
        style = _api.WS_TABSTOP | _api.ES_AUTOHSCROLL
        if minimum >= 0:
            style |= _api.ES_NUMBER
        self._create("EDIT", "", style, _api.WS_EX_CLIENTEDGE)
        if on_change is not None:
            self.on_change(on_change)

    def _after_create(self) -> None:
        hwnd = user32.CreateWindowExW(
            0, "msctls_updown32", "",
            _api.WS_CHILD | _api.WS_VISIBLE | _api.WS_CLIPSIBLINGS | _api.UDS_SETBUDDYINT
            | _api.UDS_ALIGNRIGHT | _api.UDS_ARROWKEYS | _api.UDS_NOTHOUSANDS,
            0, 0, 0, 0, self._window.hwnd, None, kernel32.GetModuleHandleW(None), None,
        )
        if not hwnd:
            raise _api.last_error("CreateWindowExW (up-down)")
        self._updown = hwnd
        self._updown_send(_api.UDM_SETRANGE32, self._min, self._max)
        self._updown_send(_api.UDM_SETBUDDY, self.hwnd, 0)
        self.value = self._value_on_create
        if not self._visible or self._suppressed:
            user32.ShowWindow(hwnd, _api.SW_HIDE)
        if not self._enabled:
            user32.EnableWindow(hwnd, False)

    def _updown_send(self, msg: int, w: int = 0, l: int = 0) -> int:
        return user32.SendMessageW(self._updown, msg, w & ((1 << (8 * ctypes.sizeof(ctypes.c_void_p))) - 1), l)

    @property
    def value(self) -> int:
        try:
            number = int(self.text.strip())
        except ValueError:
            return self._min
        return max(self._min, min(self._max, number))

    @value.setter
    def value(self, value: int) -> None:
        value = max(self._min, min(self._max, int(value)))
        was, self._muted = self._muted, True
        try:
            self._updown_send(_api.UDM_SETPOS32, 0, value)
        finally:
            self._muted = was

    @property
    def minimum(self) -> int:
        return self._min

    @property
    def maximum(self) -> int:
        return self._max

    def natural_size(self, scale: Scale) -> Size:
        _, h = self._measure("Ag", scale)
        digits = len(str(self._max))
        width, _ = self._measure("0" * max(digits, 2), scale)
        return Size(width + scale.px(34), h + scale.px(8))

    def place(self, rect: Rect, scale: Scale) -> None:
        super().place(rect, scale)
        if self._updown:
            self._updown_send(_api.UDM_SETBUDDY, self.hwnd, 0)  # re-attach after moving

    def _sync_shown(self) -> None:
        super()._sync_shown()
        if self._updown:
            shown = self._visible and not self._suppressed
            user32.ShowWindow(self._updown, _api.SW_SHOW if shown else _api.SW_HIDE)

    def _sync_enabled(self) -> None:
        super()._sync_enabled()
        if self._updown:
            user32.EnableWindow(self._updown, self._enabled)

    def _command(self, code: int) -> None:
        if code == _api.EN_CHANGE and not self._muted:
            self.on_change.emit()
