"""DatePicker and TimePicker (native date/time picker control)."""

from __future__ import annotations

import ctypes
import datetime as dt
from typing import Callable

from barewingui import _api
from barewingui._layout_core import Size
from barewingui.controls._base import Control
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]


class _Picker(Control):
    on_change = event()

    def _setup(self, style: int, on_change: Handler | None) -> None:
        self._create("SysDateTimePick32", "", _api.WS_TABSTOP | style)
        if on_change is not None:
            self.on_change(on_change)

    def _get(self) -> "_api.SYSTEMTIME | None":
        st = _api.SYSTEMTIME()
        if self._send(_api.DTM_GETSYSTEMTIME, 0, ctypes.addressof(st)) != _api.GDT_VALID:
            return None
        return st

    def _set(self, st: "_api.SYSTEMTIME") -> None:
        was, self._muted = self._muted, True
        try:
            self._send(_api.DTM_SETSYSTEMTIME, _api.GDT_VALID, ctypes.addressof(st))
        finally:
            self._muted = was

    def min_size(self, scale: Scale) -> Size:
        return self.natural_size(scale)

    def _notify(self, code: int, lparam: int) -> int:
        if code == _api.DTN_DATETIMECHANGE and not self._muted:
            self.on_change.emit()
        return 0


class DatePicker(_Picker):
    """
    A date field with a drop-down calendar. ``value`` is a :class:`datetime.date`.

    :param value: initial date (default: today).
    :param long: use the long date format ("Monday, 5 May 2025").
    """

    def __init__(
        self,
        value: dt.date | None = None,
        *,
        long: bool = False,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._long = bool(long)
        self._setup(_api.DTS_LONGDATEFORMAT if long else _api.DTS_SHORTDATEFORMAT, on_change)
        self.value = value or dt.date.today()

    @property
    def value(self) -> dt.date:
        st = self._get()
        return dt.date(st.wYear, st.wMonth, st.wDay) if st else dt.date.today()

    @value.setter
    def value(self, value: dt.date) -> None:
        st = self._get() or _api.SYSTEMTIME()
        st.wYear, st.wMonth, st.wDay = value.year, value.month, value.day
        self._set(st)

    def natural_size(self, scale: Scale) -> Size:
        sample = "Wednesday, 30. September 2000" if self._long else "30.09.2000"
        w, h = self._measure(sample, scale)
        return Size(w + scale.px(40), h + scale.px(9))


class TimePicker(_Picker):
    """A time field. ``value`` is a :class:`datetime.time` (seconds resolution)."""

    def __init__(
        self,
        value: dt.time | None = None,
        *,
        on_change: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._setup(_api.DTS_TIMEFORMAT, on_change)
        self.value = value or dt.datetime.now().time().replace(microsecond=0)

    @property
    def value(self) -> dt.time:
        st = self._get()
        return dt.time(st.wHour, st.wMinute, st.wSecond) if st else dt.time(0, 0, 0)

    @value.setter
    def value(self, value: dt.time) -> None:
        st = self._get() or _api.SYSTEMTIME()
        st.wHour, st.wMinute, st.wSecond, st.wMilliseconds = (
            value.hour, value.minute, value.second, 0,
        )
        if not st.wYear:
            today = dt.date.today()
            st.wYear, st.wMonth, st.wDay = today.year, today.month, today.day
        self._set(st)

    def natural_size(self, scale: Scale) -> Size:
        w, h = self._measure("00:00:00", scale)
        return Size(w + scale.px(40), h + scale.px(9))
