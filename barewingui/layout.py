"""
barewingui.layout
~~~~~~~~~~~~~~~~~
Lightweight box-sizer layout engine (VBox / HBox) for automatic,
resolution-independent control positioning and resizing without fixed coordinates.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self

from barewingui.types import user32

if TYPE_CHECKING:
    from barewingui.controls.base import Control
    from barewingui.window import Window


@dataclass
class _LayoutItem:
    target: Control | Box | None
    stretch: int = 0
    fixed_size: int | None = None


class Box:
    """
    Eindimensionaler Layout-Container für vertikale oder horizontale Anordnung.
    Unterstützt Verschachtelung, automatischen Dehnungsfaktor (Stretch), feste Abstände
    und Fenster-Resizing.
    """

    def __init__(
        self,
        orientation: Literal["vertical", "horizontal"] = "vertical",
        spacing: int = 8,
        padding: int | tuple[int, int] | tuple[int, int, int, int] = 10,
        fixed_size: int | None = None,
    ) -> None:
        self.orientation = orientation
        self.spacing = spacing
        self.fixed_size = fixed_size
        self._items: list[_LayoutItem] = []
        self._window: Window | None = None

        # Padding normalisieren auf (top, right, bottom, left)
        if isinstance(padding, int):
            self.pad_top = self.pad_right = self.pad_bottom = self.pad_left = padding
        elif len(padding) == 2:
            self.pad_left = self.pad_right = padding[0]
            self.pad_top = self.pad_bottom = padding[1]
        elif len(padding) == 4:
            self.pad_top, self.pad_right, self.pad_bottom, self.pad_left = padding
        else:
            raise ValueError("Padding muss ein int, 2er- oder 4er-Tupel sein.")

    def add(
        self,
        item: Control | Box,
        stretch: int = 0,
        fixed_size: int | None = None,
    ) -> Self:
        """
        Fügt ein Steuerelement oder eine untergeordnete Box hinzu.

        :param item: Ein Control oder eine verschachtelte Box.
        :param stretch: Dehnungsfaktor (> 0 nimmt verfügbaren Leerraum proportional ein).
        :param fixed_size: Feste Ausdehnung entlang der Hauptachse (ignoriert Control-Größe).
        """
        if stretch == 0 and fixed_size is None:
            if isinstance(item, Box) and item.fixed_size is not None:
                fixed_size = item.fixed_size
            elif hasattr(item, "size"):
                measured = item.size[1] if self.orientation == "vertical" else item.size[0]
                if measured > 0:
                    fixed_size = measured

        self._items.append(_LayoutItem(target=item, stretch=stretch, fixed_size=fixed_size))
        return self

    def add_spacing(self, pixels: int) -> Self:
        """Fügt einen starren Leerraum (Spacer) entlang der Hauptachse ein."""
        self._items.append(_LayoutItem(target=None, stretch=0, fixed_size=pixels))
        return self

    def add_stretch(self, factor: int = 1) -> Self:
        """Fügt eine elastische Feder ein, die den Leerraum dynamisch verdrängt."""
        self._items.append(_LayoutItem(target=None, stretch=factor, fixed_size=None))
        return self

    def apply(self, x: int, y: int, width: int, height: int) -> None:
        """Berechnet alle Abmessungen neu und aktualisiert die nativen HWND-Positionen."""
        if not self._items:
            return

        is_vertical = self.orientation == "vertical"

        avail_w = max(0, width - self.pad_left - self.pad_right)
        avail_h = max(0, height - self.pad_top - self.pad_bottom)
        main_avail = avail_h if is_vertical else avail_w
        cross_avail = avail_w if is_vertical else avail_h

        # Zwischenabstände zwischen den Elementen abziehen
        visible_gaps = max(0, len(self._items) - 1) * self.spacing
        main_remaining = max(0, main_avail - visible_gaps)

        total_stretch = 0
        allocated_sizes: list[int] = []

        # 1. Pass: Feste Größen ermitteln
        for item in self._items:
            if item.stretch > 0:
                total_stretch += item.stretch
                allocated_sizes.append(0)
            else:
                size = 24
                if item.fixed_size is not None:
                    size = item.fixed_size
                elif item.target is None:
                    size = 0
                elif isinstance(item.target, Box):
                    size = item.target.fixed_size or 24
                else:
                    # Control: Höhe bei VBox, Breite bei HBox übernehmen
                    size = item.target.size[1] if is_vertical else item.target.size[0]

                size = min(main_remaining, size)
                main_remaining -= size
                allocated_sizes.append(size)

        # 2. Pass: Verbleibenden Raum auf Stretch-Elemente verteilen
        if total_stretch > 0 and main_remaining > 0:
            for i, item in enumerate(self._items):
                if item.stretch > 0:
                    share = int(main_remaining * (item.stretch / total_stretch))
                    allocated_sizes[i] = share

        # 3. Pass: Positionierung durchführen
        curr_main = (y + self.pad_top) if is_vertical else (x + self.pad_left)

        for i, item in enumerate(self._items):
            item_size = allocated_sizes[i]

            if is_vertical:
                item_x = x + self.pad_left
                item_y = curr_main
                item_w = cross_avail
                item_h = item_size
            else:
                item_x = curr_main
                item_y = y + self.pad_top
                item_w = item_size
                item_h = cross_avail

            if item.target is not None:
                if isinstance(item.target, Box):
                    item.target.apply(item_x, item_y, item_w, item_h)
                else:
                    item.target.move(x=item_x, y=item_y, width=item_w, height=item_h)

            curr_main += item_size + self.spacing

    def attach(self, window: Window) -> None:
        """Verbindet das Layout mit einem Fenster und aktiviert automatisches Resize-Handling."""
        self._window = window

        def _on_window_resize(w: int, h: int) -> None:
            self.apply(0, 0, w, h)

        # Bestehenden Callback verketten
        prev_callback = window.on_resize

        def _resize_chain(w: int, h: int) -> None:
            if prev_callback:
                prev_callback(w, h)
            _on_window_resize(w, h)

        window.on_resize = _resize_chain

        # Initialen Layout-Durchlauf erzwingen
        if window.hwnd:
            rc = wintypes.RECT()
            user32.GetClientRect(window.hwnd, ctypes.byref(rc))
            self.apply(0, 0, rc.right - rc.left, rc.bottom - rc.top)


class VBox(Box):
    """Vertikaler Stapelcontainer (Ordnet Steuerelemente von oben nach unten an)."""

    def __init__(
        self,
        spacing: int = 8,
        padding: int | tuple[int, int] | tuple[int, int, int, int] = 10,
        fixed_size: int | None = None,
    ) -> None:
        super().__init__(
            orientation="vertical",
            spacing=spacing,
            padding=padding,
            fixed_size=fixed_size,
        )


class HBox(Box):
    """Horizontaler Stapelcontainer (Ordnet Steuerelemente von links nach rechts an)."""

    def __init__(
        self,
        spacing: int = 8,
        padding: int | tuple[int, int] | tuple[int, int, int, int] = 10,
        fixed_size: int | None = None,
    ) -> None:
        super().__init__(
            orientation="horizontal",
            spacing=spacing,
            padding=padding,
            fixed_size=fixed_size,
        )