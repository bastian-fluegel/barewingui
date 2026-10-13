"""
barewingui.events
~~~~~~~~~~~~~~~~~
Tiny event helper. Controls expose events such as ``on_click``; handlers are
called without arguments (read the state from the controls)::

    ok = Button("OK", on_click=save)      # as a constructor option
    ok.on_click(save)                     # register another handler
    @ok.on_click                          # as a decorator
    def save(): ...
    ok.on_click = save                    # assignment replaces all handlers
    ok.on_click = None                    # removes all handlers
"""

from __future__ import annotations

from typing import Any, Callable

Handler = Callable[[], Any]


class Event:
    """An ordered list of handlers."""

    __slots__ = ("_handlers",)

    def __init__(self) -> None:
        self._handlers: list[Handler] = []

    def __call__(self, handler: Handler) -> Handler:
        """Register ``handler`` (also usable as a decorator) and return it."""
        return self.connect(handler)

    def connect(self, handler: Handler) -> Handler:
        if not callable(handler):
            raise TypeError(f"an event handler must be callable, got {handler!r}")
        self._handlers.append(handler)
        return handler

    def disconnect(self, handler: Handler) -> None:
        self._handlers.remove(handler)

    def clear(self) -> None:
        self._handlers.clear()

    def emit(self) -> None:
        """Call all handlers in registration order. The first exception propagates."""
        for handler in list(self._handlers):
            handler()

    def __len__(self) -> int:
        return len(self._handlers)

    def __bool__(self) -> bool:
        return True  # an Event object is always truthy, even without handlers

    def __repr__(self) -> str:
        return f"Event({len(self._handlers)} handlers)"


class event:
    """Descriptor that gives every instance its own :class:`Event`."""

    def __set_name__(self, owner: type, name: str) -> None:
        self._key = "_event_" + name

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        if obj is None:
            return self
        ev = obj.__dict__.get(self._key)
        if ev is None:
            ev = obj.__dict__[self._key] = Event()
        return ev

    def __set__(self, obj: Any, value: Handler | None) -> None:
        ev = self.__get__(obj)
        ev.clear()
        if value is not None:
            ev.connect(value)
