"""
barewingui._layout_core
~~~~~~~~~~~~~~~~~~~~~~~
Win32-free layout primitives: geometry, per-child flex options, the node
protocol, the ``with``-block build stack and the flex distribution algorithm.

Everything in here is plain Python and is unit-tested on every platform.
"""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from typing import Literal, Protocol, Sequence

from barewingui.dpi import Scale
from barewingui.errors import LayoutError

Align = Literal["start", "center", "end", "stretch"]
Justify = Literal["start", "center", "end", "space_between"]
Direction = Literal["vertical", "horizontal"]

ALIGNS = frozenset({"start", "center", "end", "stretch"})
JUSTIFIES = frozenset({"start", "center", "end", "space_between"})
DIRECTIONS = frozenset({"vertical", "horizontal"})

_EPS = 1e-9


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Size:
    """Width and height in physical pixels."""

    w: int = 0
    h: int = 0


@dataclass(frozen=True, slots=True)
class Rect:
    """Position and size in physical pixels, relative to the parent's client area."""

    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True, slots=True)
class Insets:
    """Padding in DIPs. Accepts CSS-like shorthands via :meth:`parse`."""

    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

    @classmethod
    def parse(cls, value: object) -> Insets:
        """``8`` -> all sides, ``(v, h)`` -> vertical/horizontal, ``(t, r, b, l)``."""
        if isinstance(value, Insets):
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return cls(value, value, value, value)
        if isinstance(value, tuple) and all(
            isinstance(v, (int, float)) and not isinstance(v, bool) for v in value
        ):
            if len(value) == 2:
                v, h = value
                return cls(v, h, v, h)
            if len(value) == 4:
                return cls(*value)
        raise LayoutError(
            "padding must be a number, a (vertical, horizontal) pair "
            f"or a (top, right, bottom, left) tuple, got {value!r}"
        )

    def __post_init__(self) -> None:
        if min(self.top, self.right, self.bottom, self.left) < 0:
            raise LayoutError("padding must not be negative")


@dataclass
class Flex:
    """
    Per-child layout options (sizes in DIPs).

    ``grow``/``shrink`` work like CSS ``flex-grow``/``flex-shrink``.
    ``width``/``height`` fix a size; ``min_*``/``max_*`` bound it. Without an
    explicit minimum a child never shrinks below its natural size.
    ``align_self`` overrides the container's cross-axis ``align`` for this child.
    """

    grow: float = 0.0
    shrink: float = 1.0
    width: float | None = None
    height: float | None = None
    min_width: float | None = None
    min_height: float | None = None
    max_width: float | None = None
    max_height: float | None = None
    align_self: Align | None = None

    def __post_init__(self) -> None:
        if self.grow < 0 or self.shrink < 0:
            raise LayoutError("grow and shrink must not be negative")
        for name in ("width", "height", "min_width", "min_height", "max_width", "max_height"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise LayoutError(f"{name} must not be negative")
        if self.align_self is not None and self.align_self not in ALIGNS:
            raise LayoutError(
                f"align_self must be one of {sorted(ALIGNS)}, got {self.align_self!r}"
            )


class Node(Protocol):
    """Anything a container can lay out (controls, nested containers, spacers)."""

    flex: Flex
    visible: bool

    def natural_size(self, scale: Scale) -> Size:
        """Preferred size in pixels."""
        ...

    def min_size(self, scale: Scale) -> Size:
        """Smallest size in pixels the node can reasonably be shown at."""
        ...

    def place(self, rect: Rect, scale: Scale) -> None:
        """Move/resize the node to ``rect`` (pixels, parent client coordinates)."""
        ...


# ---------------------------------------------------------------------------
# ``with``-block build stack
# ---------------------------------------------------------------------------
_state = threading.local()


def _stack() -> list[Container]:
    stack = getattr(_state, "stack", None)
    if stack is None:
        stack = []
        _state.stack = stack
    return stack


def current_container() -> Container | None:
    """Innermost container whose ``with`` block is currently open (this thread)."""
    stack = _stack()
    return stack[-1] if stack else None


def adopt(node: Node) -> None:
    """Add ``node`` to the innermost open container, if there is one."""
    container = current_container()
    if container is not None:
        container.add(node)


class Container:
    """Mixin: a node/window that collects children created inside its ``with`` block."""

    def add(self, node: Node) -> Node:  # pragma: no cover - interface
        raise NotImplementedError

    def __enter__(self):
        _stack().append(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        stack = _stack()
        if stack and stack[-1] is self:
            stack.pop()


# ---------------------------------------------------------------------------
# Flex distribution
# ---------------------------------------------------------------------------
def _grow(sizes: list[float], maxs: Sequence[float], grows: Sequence[float], free: float) -> None:
    active = [i for i, g in enumerate(grows) if g > 0 and sizes[i] < maxs[i] - _EPS]
    remaining = free
    while active and remaining > _EPS:
        total = sum(grows[i] for i in active)
        over = [
            i for i in active if sizes[i] + remaining * grows[i] / total > maxs[i] + _EPS
        ]
        if not over:
            for i in active:
                sizes[i] += remaining * grows[i] / total
            return
        for i in over:
            remaining -= maxs[i] - sizes[i]
            sizes[i] = maxs[i]
        active = [i for i in active if i not in over]


def _shrink(
    sizes: list[float],
    mins: Sequence[float],
    shrinks: Sequence[float],
    bases: Sequence[float],
    deficit: float,
) -> None:
    active = [i for i, s in enumerate(shrinks) if s > 0 and sizes[i] > mins[i] + _EPS]
    remaining = deficit
    while active and remaining > _EPS:
        weights = {i: shrinks[i] * bases[i] for i in active}
        total = sum(weights.values())
        if total <= _EPS:
            return
        under = [
            i for i in active if sizes[i] - remaining * weights[i] / total < mins[i] - _EPS
        ]
        if not under:
            for i in active:
                sizes[i] -= remaining * weights[i] / total
            return
        for i in under:
            remaining -= sizes[i] - mins[i]
            sizes[i] = mins[i]
        active = [i for i in active if i not in under]


def _round_preserving_sum(values: Sequence[float]) -> list[int]:
    """Round to ints so that the total equals the rounded total of ``values``."""
    floors = [math.floor(v + _EPS) for v in values]
    target = round(sum(values))
    leftover = target - sum(floors)
    if leftover > 0:
        order = sorted(range(len(values)), key=lambda i: (-(values[i] - floors[i]), i))
        for i in order[:leftover]:
            floors[i] += 1
    return floors


def resolve_flex(
    bases: Sequence[int],
    mins: Sequence[int],
    maxs: Sequence[float],
    grows: Sequence[float],
    shrinks: Sequence[float],
    space: int,
) -> list[int]:
    """
    Distribute ``space`` pixels among items along one axis.

    Items start at ``bases``. Free space is shared by ``grows`` (never beyond
    ``maxs``); a deficit is taken by ``shrinks * base`` (never below ``mins``).
    The result is integral. It may exceed ``space`` if the minimums do not fit.
    """
    n = len(bases)
    if not (len(mins) == len(maxs) == len(grows) == len(shrinks) == n):
        raise ValueError("all sequences must have the same length")
    sizes = [float(b) for b in bases]
    free = space - sum(bases)
    if free > 0:
        _grow(sizes, maxs, grows, free)
    elif free < 0:
        _shrink(sizes, mins, shrinks, bases, -free)
    return _round_preserving_sum(sizes)
