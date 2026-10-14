"""barewingui.timer: repeating or one-shot timers that call back on the UI thread."""

from __future__ import annotations

from typing import Callable

from barewingui import _api
from barewingui._api import user32
from barewingui.app import App
from barewingui.events import event

Handler = Callable[[], object]

__all__ = ["Timer"]


class Timer:
    """
    Calls ``on_tick`` on the UI thread every ``interval`` seconds.

    ::

        clock = Timer(1.0, update_clock)          # starts immediately
        once = Timer(3, hide_hint, repeat=False)
        clock.stop(); clock.start()

    :param interval: seconds (the system resolution is about 15 ms).
    :param repeat: ``False`` for a single shot.
    :param start: ``False`` to create it stopped.
    """

    on_tick = event()

    def __init__(
        self, interval: float, handler: Handler | None = None, *, repeat: bool = True, start: bool = True
    ) -> None:
        if not interval > 0:
            raise ValueError("interval must be positive (seconds)")
        self._app = App.current()
        self._app._check_thread()
        self._interval = float(interval)
        self.repeat = bool(repeat)
        self._id = 0
        if handler is not None:
            self.on_tick(handler)
        if start:
            self.start()

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, seconds: float) -> None:
        if not seconds > 0:
            raise ValueError("interval must be positive (seconds)")
        self._interval = float(seconds)
        if self.running:
            self.start()  # restart with the new interval

    @property
    def running(self) -> bool:
        return bool(self._id)

    def start(self) -> None:
        """(Re)start the timer."""
        self.stop()
        app = self._app
        app._check_thread()
        if not app._msg_hwnd:
            raise RuntimeError("the application has been shut down")
        app._next_timer += 1
        timer_id = app._next_timer
        if not user32.SetTimer(app._msg_hwnd, timer_id, max(1, round(self._interval * 1000)), None):
            raise _api.last_error("SetTimer")
        app._timers[timer_id] = self
        self._id = timer_id

    def stop(self) -> None:
        if self._id:
            app = self._app
            app._timers.pop(self._id, None)
            if app._msg_hwnd:
                user32.KillTimer(app._msg_hwnd, self._id)
            self._id = 0

    def _fire(self) -> None:
        if not self.repeat:
            self.stop()
        self.on_tick.emit()
