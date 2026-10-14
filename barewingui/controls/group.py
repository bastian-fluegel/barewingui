"""GroupBox: a titled frame around other controls."""

from __future__ import annotations

from barewingui import _api
from barewingui._api import kernel32, user32
from barewingui._layout_core import Rect
from barewingui._font import font_for_dpi, text_size
from barewingui.controls._base import owning_window, parent_hwnd
from barewingui.dpi import Scale
from barewingui.layout import Stack


class GroupBox(Stack):
    """
    A titled frame that lays out its content like a :class:`VBox` (or an HBox
    with ``direction="horizontal"``)::

        with GroupBox("Options"):
            CheckBox("Remember me")
            CheckBox("Show hints")

    The frame is a native group box; the content are siblings placed inside it.
    Accepts the :class:`Stack` options.
    """

    def __init__(self, title: str = "", direction: str = "vertical", **options: object) -> None:
        window = owning_window()
        hwnd = user32.CreateWindowExW(
            0, "BUTTON", title,
            _api.WS_CHILD | _api.WS_VISIBLE | _api.WS_CLIPSIBLINGS | _api.BS_GROUPBOX,
            0, 0, 0, 0, parent_hwnd(), None, kernel32.GetModuleHandleW(None), None,
        )
        if not hwnd:
            raise _api.last_error("CreateWindowExW (group box)")
        self._hwnd: int | None = hwnd
        self._window = window
        self._title = title
        self._font_dpi = 0
        window._controls[hwnd] = self
        self._apply_font(window.dpi)
        super().__init__(direction, **options)  # type: ignore[arg-type]

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = str(value)
        if self._hwnd:
            user32.SetWindowTextW(self._hwnd, self._title)
            self._window.relayout()

    # -- layout: the frame adds room for its title and border --------------------
    def _padding_px(self, scale: Scale) -> tuple[int, int, int, int]:
        top, right, bottom, left = super()._padding_px(scale)
        _, title_h = text_size(self._title or "Ag", scale.dpi)
        return (
            top + title_h + scale.px(6),
            right + scale.px(9),
            bottom + scale.px(9),
            left + scale.px(9),
        )

    def place(self, rect: Rect, scale: Scale) -> None:
        if self._hwnd:
            self._apply_font(scale.dpi)
            # Always below its content: the frame fills its interior and would hide
            # the controls inside if it were above them.
            user32.SetWindowPos(
                self._hwnd, _api.HWND_BOTTOM, rect.x, rect.y, rect.w, rect.h, _api.SWP_NOACTIVATE,
            )
        super().place(rect, scale)

    def _apply_font(self, dpi: int) -> None:
        if self._hwnd and dpi != self._font_dpi:
            user32.SendMessageW(self._hwnd, _api.WM_SETFONT, font_for_dpi(dpi), 1)
            self._font_dpi = dpi

    def _dpi_changed(self, dpi: int) -> None:
        self._apply_font(dpi)

    # -- native frame events (none are needed) ------------------------------------
    def _command(self, code: int) -> None:
        pass

    def _scroll(self, code: int) -> None:
        pass

    def _notify(self, code: int, lparam: int) -> int:
        return 0
