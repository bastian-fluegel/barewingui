"""
barewingui.dpi
~~~~~~~~~~~~~~
Device-independent pixel (DIP) scaling. Pure Python, no Win32 calls.

All public sizes in BareWinGUI are DIPs: 1 DIP is one pixel at 96 DPI (100 %).
At 144 DPI (150 %) one DIP is 1.5 physical pixels.
"""

from __future__ import annotations

import math

BASE_DPI = 96


class Scale:
    """Converts between DIPs and physical pixels for one DPI value."""

    __slots__ = ("dpi",)

    def __init__(self, dpi: int = BASE_DPI) -> None:
        if dpi <= 0:
            raise ValueError(f"dpi must be positive, got {dpi!r}")
        self.dpi = int(dpi)

    @property
    def factor(self) -> float:
        """Scale factor relative to 96 DPI (1.0 = 100 %)."""
        return self.dpi / BASE_DPI

    def px(self, dip: float) -> int:
        """DIPs to physical pixels, rounded half up."""
        return math.floor(dip * self.dpi / BASE_DPI + 0.5)

    def dip(self, px: float) -> float:
        """Physical pixels to DIPs."""
        return px * BASE_DPI / self.dpi

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Scale) and other.dpi == self.dpi

    def __hash__(self) -> int:
        return hash(self.dpi)

    def __repr__(self) -> str:
        return f"Scale(dpi={self.dpi})"
