"""
barewingui.layout
~~~~~~~~~~~~~~~~~
Flexbox-style stacks: :class:`VBox`, :class:`HBox` and :class:`Spacer`.

Layout is two-pass. Each child reports its natural size; the stack then
distributes the remaining space by ``grow`` (or takes back a deficit by
``shrink``). All options are in DIPs and scale with the monitor DPI.

Containers are context managers; anything created inside the ``with`` block
is added to the innermost open container::

    with VBox(padding=12, gap=8):
        name = TextBox()
        with HBox(justify="end"):
            Button("OK")
"""

from __future__ import annotations

import math
from typing import NamedTuple

from barewingui._layout_core import (
    ALIGNS,
    DIRECTIONS,
    JUSTIFIES,
    Align,
    Container,
    Direction,
    Flex,
    Insets,
    Justify,
    Node,
    Rect,
    Size,
    adopt,
    resolve_flex,
)
from barewingui.dpi import Scale
from barewingui.errors import LayoutError

__all__ = ["Stack", "VBox", "HBox", "Spacer", "Flex", "Size", "Rect"]


class _Spec(NamedTuple):
    base: int
    lo: int
    hi: float
    explicit: bool


def _spec(flex: Flex, natural: int, node_min: int, width_axis: bool, scale: Scale) -> _Spec:
    """Resolve one axis of one child: base size, bounds and whether it was set explicitly."""
    if width_axis:
        explicit, lo_f, hi_f = flex.width, flex.min_width, flex.max_width
    else:
        explicit, lo_f, hi_f = flex.height, flex.min_height, flex.max_height
    base = scale.px(explicit) if explicit is not None else natural
    lo = scale.px(lo_f) if lo_f is not None else min(node_min, base)
    hi: float = scale.px(hi_f) if hi_f is not None else math.inf
    hi = max(hi, lo)  # a minimum always wins over a maximum
    base = int(min(max(base, lo), hi))
    return _Spec(base, lo, hi, explicit is not None)


class Stack(Container):
    """
    Lays children out in one direction.

    :param direction: ``"vertical"`` or ``"horizontal"``.
    :param gap: space between children (DIPs).
    :param padding: inner padding (DIPs): number, ``(vertical, horizontal)``
        or ``(top, right, bottom, left)``.
    :param justify: placement along the main axis when no child grows:
        ``start``, ``center``, ``end`` or ``space_between``.
    :param align: default placement across the main axis:
        ``start``, ``center``, ``end`` or ``stretch``.
    :param flex: options for this stack as a child of its parent
        (``grow``, ``shrink``, ``width``, ``height``, ``min_*``, ``max_*``, ``align_self``).
    """

    def __init__(
        self,
        direction: Direction = "vertical",
        *,
        gap: float = 8,
        padding: float | tuple[float, ...] = 0,
        justify: Justify = "start",
        align: Align = "stretch",
        **flex: object,
    ) -> None:
        if direction not in DIRECTIONS:
            raise LayoutError(f"direction must be one of {sorted(DIRECTIONS)}, got {direction!r}")
        if justify not in JUSTIFIES:
            raise LayoutError(f"justify must be one of {sorted(JUSTIFIES)}, got {justify!r}")
        if align not in ALIGNS:
            raise LayoutError(f"align must be one of {sorted(ALIGNS)}, got {align!r}")
        if gap < 0:
            raise LayoutError("gap must not be negative")
        self.direction: Direction = direction
        self.gap = gap
        self.padding = Insets.parse(padding)
        self.justify: Justify = justify
        self.align: Align = align
        self.flex = Flex(**flex)  # type: ignore[arg-type]
        self.visible = True
        self._children: list[Node] = []
        adopt(self)

    # -- children ------------------------------------------------------------
    @property
    def children(self) -> tuple[Node, ...]:
        return tuple(self._children)

    def add(self, node: Node) -> Node:
        """Append a child. Called automatically for nodes created inside ``with``."""
        if node is self or any(node is c for c in self._children):
            raise LayoutError("node is already part of this container")
        self._children.append(node)
        attached = getattr(node, "_attached", None)
        if attached is not None:
            attached(self)
        return node

    def remove(self, node: Node) -> None:
        for i, child in enumerate(self._children):
            if child is node:
                del self._children[i]
                return
        raise LayoutError("node is not part of this container")

    # -- measuring -----------------------------------------------------------
    def _horizontal(self) -> bool:
        return self.direction == "horizontal"

    def _padding_px(self, scale: Scale) -> tuple[int, int, int, int]:
        p = self.padding
        return scale.px(p.top), scale.px(p.right), scale.px(p.bottom), scale.px(p.left)

    def _measure(self, scale: Scale) -> tuple[list[Node], list[_Spec], list[_Spec]]:
        """Visible children with their main-axis and cross-axis specs."""
        horizontal = self._horizontal()
        kids = [c for c in self._children if c.visible]
        mains: list[_Spec] = []
        crosses: list[_Spec] = []
        for child in kids:
            nat = child.natural_size(scale)
            mn = child.min_size(scale)
            n_main, n_cross = (nat.w, nat.h) if horizontal else (nat.h, nat.w)
            m_main, m_cross = (mn.w, mn.h) if horizontal else (mn.h, mn.w)
            mains.append(_spec(child.flex, n_main, m_main, horizontal, scale))
            crosses.append(_spec(child.flex, n_cross, m_cross, not horizontal, scale))
        return kids, mains, crosses

    def _size(self, scale: Scale, use_min: bool) -> Size:
        top, right, bottom, left = self._padding_px(scale)
        pad_w, pad_h = left + right, top + bottom
        _, mains, crosses = self._measure(scale)
        if not mains:
            return Size(pad_w, pad_h)
        gaps = scale.px(self.gap) * (len(mains) - 1)
        main = sum((s.lo if use_min else s.base) for s in mains) + gaps
        cross = max((s.lo if use_min else s.base) for s in crosses)
        if self._horizontal():
            return Size(main + pad_w, cross + pad_h)
        return Size(cross + pad_w, main + pad_h)

    def natural_size(self, scale: Scale) -> Size:
        return self._size(scale, use_min=False)

    def min_size(self, scale: Scale) -> Size:
        return self._size(scale, use_min=True)

    # -- placing -------------------------------------------------------------
    def arrange(self, rect: Rect, scale: Scale) -> list[tuple[Node, Rect]]:
        """Compute the rectangle of every visible child inside ``rect`` (no side effects)."""
        top, right, bottom, left = self._padding_px(scale)
        inner_x, inner_y = rect.x + left, rect.y + top
        inner_w = max(0, rect.w - left - right)
        inner_h = max(0, rect.h - top - bottom)

        kids, mains, crosses = self._measure(scale)
        if not kids:
            return []

        horizontal = self._horizontal()
        main_inner, cross_inner = (inner_w, inner_h) if horizontal else (inner_h, inner_w)
        main_start, cross_start = (inner_x, inner_y) if horizontal else (inner_y, inner_x)

        n = len(kids)
        gap = scale.px(self.gap)
        sizes = resolve_flex(
            [s.base for s in mains],
            [s.lo for s in mains],
            [s.hi for s in mains],
            [k.flex.grow for k in kids],
            [k.flex.shrink for k in kids],
            main_inner - gap * (n - 1),
        )

        gaps = [gap] * (n - 1)
        cursor = main_start
        leftover = main_inner - (sum(sizes) + gap * (n - 1))
        if leftover > 0:
            if self.justify == "center":
                cursor += leftover // 2
            elif self.justify == "end":
                cursor += leftover
            elif self.justify == "space_between" and n > 1:
                per, rem = divmod(leftover, n - 1)
                gaps = [gap + per + (1 if i < rem else 0) for i in range(n - 1)]

        result: list[tuple[Node, Rect]] = []
        for i, child in enumerate(kids):
            cspec = crosses[i]
            align = child.flex.align_self or self.align
            if align == "stretch" and not cspec.explicit:
                csize = int(min(max(cross_inner, cspec.lo), cspec.hi))
            else:
                csize = cspec.base
            if align == "center":
                cpos = max(0, (cross_inner - csize) // 2)
            elif align == "end":
                cpos = max(0, cross_inner - csize)
            else:
                cpos = 0
            if horizontal:
                child_rect = Rect(cursor, cross_start + cpos, sizes[i], csize)
            else:
                child_rect = Rect(cross_start + cpos, cursor, csize, sizes[i])
            result.append((child, child_rect))
            cursor += sizes[i] + (gaps[i] if i < n - 1 else 0)
        return result

    def place(self, rect: Rect, scale: Scale) -> None:
        for child, child_rect in self.arrange(rect, scale):
            child.place(child_rect, scale)


class VBox(Stack):
    """Children from top to bottom."""

    def __init__(self, **options: object) -> None:
        super().__init__("vertical", **options)  # type: ignore[arg-type]


class HBox(Stack):
    """Children from left to right."""

    def __init__(self, **options: object) -> None:
        super().__init__("horizontal", **options)  # type: ignore[arg-type]


class Spacer:
    """
    Empty space inside a stack.

    ``Spacer()`` grows to fill all free space (pushes neighbours apart).
    ``Spacer(16)`` is a fixed gap of 16 DIPs along the stack's main axis.
    """

    def __init__(
        self, size: float | None = None, *, grow: float | None = None, **flex: object
    ) -> None:
        if size is not None and size < 0:
            raise LayoutError("spacer size must not be negative")
        if size is None and grow is None:
            grow = 1.0
        flex.setdefault("shrink", 0.0 if size is not None else 1.0)
        self._size = size
        self.flex = Flex(grow=grow or 0.0, **flex)  # type: ignore[arg-type]
        self.visible = True
        adopt(self)

    def _attached(self, parent: object) -> None:
        if self._size is not None:
            horizontal = getattr(parent, "direction", "vertical") == "horizontal"
            setattr(self.flex, "width" if horizontal else "height", self._size)

    def natural_size(self, scale: Scale) -> Size:
        return Size(0, 0)

    def min_size(self, scale: Scale) -> Size:
        return Size(0, 0)

    def place(self, rect: Rect, scale: Scale) -> None:
        return None
