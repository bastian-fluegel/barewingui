"""
barewingui._dispatch
~~~~~~~~~~~~~~~~~~~~
Thread-safe call queue and error routing for the UI thread. Win32-free.

Win32 callbacks cannot raise into Python (ctypes prints and swallows the
exception). :class:`ErrorPolicy` catches them, stops the message loop and lets
``App.run()`` re-raise the first error afterwards.
"""

from __future__ import annotations

import queue
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class _Job:
    future: Future
    fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    report: bool


class ErrorPolicy:
    """
    Collects exceptions raised inside callbacks.

    Without a ``handler`` the first exception stops the loop (via ``stop``) and
    is re-raised by :meth:`raise_pending`. With a ``handler`` the loop keeps
    running; if the handler itself fails, that failure is treated as unhandled.
    """

    def __init__(self, stop: Callable[[], None]) -> None:
        self._stop = stop
        self._pending: BaseException | None = None
        self.handler: Callable[[BaseException], None] | None = None

    def capture(self, exc: BaseException) -> None:
        if self.handler is not None:
            try:
                self.handler(exc)
                return
            except BaseException as handler_exc:  # noqa: BLE001 - must never escape a callback
                exc = handler_exc
        if self._pending is None:
            self._pending = exc
            self._stop()
        else:
            self._pending.add_note(f"Further error while stopping: {exc!r}")

    @property
    def pending(self) -> BaseException | None:
        return self._pending

    def raise_pending(self) -> None:
        if self._pending is not None:
            exc, self._pending = self._pending, None
            raise exc


class InvokeQueue:
    """
    Runs callables on the UI thread on behalf of other threads.

    ``wake`` must make the UI thread call :meth:`drain` soon (it is called from
    the submitting thread). Errors of jobs submitted with ``report=True`` are
    forwarded to ``on_error``; they are always stored on the returned future.
    """

    def __init__(
        self, wake: Callable[[], None], on_error: Callable[[BaseException], None]
    ) -> None:
        self._wake = wake
        self._on_error = on_error
        self._queue: queue.SimpleQueue[_Job] = queue.SimpleQueue()
        self._lock = threading.Lock()
        self._closed = False

    def submit(
        self, fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any], *, report: bool
    ) -> Future:
        future: Future = Future()
        with self._lock:
            if self._closed:
                raise RuntimeError("the application is not running (anymore)")
            self._queue.put(_Job(future, fn, args, kwargs, report))
        self._wake()
        return future

    def drain(self) -> None:
        """Run all queued jobs. Must be called on the UI thread."""
        while True:
            try:
                job = self._queue.get_nowait()
            except queue.Empty:
                return
            if not job.future.set_running_or_notify_cancel():
                continue
            try:
                result = job.fn(*job.args, **job.kwargs)
            except BaseException as exc:  # noqa: BLE001
                job.future.set_exception(exc)
                if job.report:
                    self._on_error(exc)
            else:
                job.future.set_result(result)

    def close(self) -> None:
        """Refuse new jobs and cancel everything still queued."""
        with self._lock:
            self._closed = True
            while True:
                try:
                    job = self._queue.get_nowait()
                except queue.Empty:
                    break
                job.future.cancel()
