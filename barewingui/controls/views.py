"""ListView (report view with columns) and TreeView."""

from __future__ import annotations

import ctypes
from typing import Callable, Iterable, Sequence

from barewingui import _api
from barewingui._layout_core import Size
from barewingui.controls._base import Control, wparam
from barewingui.dpi import Scale
from barewingui.events import event

Handler = Callable[[], object]
_PTR_MASK = (1 << (8 * ctypes.sizeof(ctypes.c_void_p))) - 1


# ---------------------------------------------------------------------------
# ListView
# ---------------------------------------------------------------------------
class ListView(Control):
    """
    A table: columns and rows of text.

    :param columns: column titles; a title may be a ``(title, width)`` pair
        with the width in DIPs (default 120).
    :param rows: initial rows (sequences of strings).
    :param multi: allow selecting several rows.
    :param grid: draw grid lines.
    :param on_select: called when the selection changes (once per changed row
        when several rows are (de)selected at once).
    :param on_activate: called on double click or Enter.
    :param on_column_click: called when a column header is clicked
        (:attr:`clicked_column` has its index) - sort the rows yourself.
    """

    on_select = event()
    on_activate = event()
    on_column_click = event()

    def __init__(
        self,
        columns: Sequence[str | tuple[str, float]],
        rows: Iterable[Sequence[object]] = (),
        *,
        multi: bool = False,
        grid: bool = False,
        on_select: Handler | None = None,
        on_activate: Handler | None = None,
        on_column_click: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        if not columns:
            raise ValueError("a ListView needs at least one column")
        self._columns: list[tuple[str, float]] = [
            (c, 120.0) if isinstance(c, str) else (str(c[0]), float(c[1])) for c in columns
        ]
        self._rows: list[tuple[str, ...]] = []
        self.clicked_column = -1
        self._multi = bool(multi)
        style = _api.WS_TABSTOP | _api.LVS_REPORT | _api.LVS_SHOWSELALWAYS
        if not multi:
            style |= _api.LVS_SINGLESEL
        self._create("SysListView32", "", style, _api.WS_EX_CLIENTEDGE)
        extended = _api.LVS_EX_FULLROWSELECT | _api.LVS_EX_DOUBLEBUFFER
        if grid:
            extended |= _api.LVS_EX_GRIDLINES
        self._send(_api.LVM_SETEXTENDEDLISTVIEWSTYLE, 0, extended)
        scale = self._window.scale
        for index, (title, width) in enumerate(self._columns):
            col = _api.LVCOLUMNW()
            col.mask = _api.LVCF_TEXT | _api.LVCF_WIDTH | _api.LVCF_SUBITEM | _api.LVCF_FMT
            col.fmt = _api.LVCFMT_LEFT
            col.cx = scale.px(width)
            buf = ctypes.create_unicode_buffer(title)
            col.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
            col.iSubItem = index
            if self._send(_api.LVM_INSERTCOLUMNW, index, ctypes.addressof(col)) == -1:
                raise _api.last_error("LVM_INSERTCOLUMNW")
        self._muted = True
        try:
            for row in rows:
                self.add_row(row)
        finally:
            self._muted = False
        for ev, handler in (
            (self.on_select, on_select),
            (self.on_activate, on_activate),
            (self.on_column_click, on_column_click),
        ):
            if handler is not None:
                ev(handler)

    # -- rows --------------------------------------------------------------------
    def _normalize(self, values: Sequence[object]) -> tuple[str, ...]:
        cells = tuple("" if v is None else str(v) for v in values)
        if len(cells) > len(self._columns):
            raise ValueError(f"a row has {len(cells)} cells but there are {len(self._columns)} columns")
        return cells + ("",) * (len(self._columns) - len(cells))

    def _write_cell(self, row: int, column: int, text: str) -> None:
        item = _api.LVITEMW()
        item.iSubItem = column
        buf = ctypes.create_unicode_buffer(text)
        item.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
        self._send(_api.LVM_SETITEMTEXTW, row, ctypes.addressof(item))

    def insert_row(self, index: int, values: Sequence[object]) -> int:
        """Insert a row before ``index`` (``len(self)`` appends). Returns the index."""
        cells = self._normalize(values)
        index = max(0, min(index, len(self._rows)))
        item = _api.LVITEMW()
        item.mask = _api.LVIF_TEXT
        item.iItem = index
        buf = ctypes.create_unicode_buffer(cells[0])
        item.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
        was, self._muted = self._muted, True
        try:
            result = self._send(_api.LVM_INSERTITEMW, 0, ctypes.addressof(item))
            if result == -1:
                raise _api.last_error("LVM_INSERTITEMW")
            for column, text in enumerate(cells[1:], start=1):
                if text:
                    self._write_cell(result, column, text)
        finally:
            self._muted = was
        self._rows.insert(result, cells)
        return result

    def add_row(self, values: Sequence[object]) -> int:
        """Append a row. Returns its index."""
        return self.insert_row(len(self._rows), values)

    def remove_row(self, index: int) -> None:
        if not 0 <= index < len(self._rows):
            raise IndexError(f"row {index} out of range")
        was, self._muted = self._muted, True
        try:
            self._send(_api.LVM_DELETEITEM, index)
        finally:
            self._muted = was
        del self._rows[index]

    def clear(self) -> None:
        was, self._muted = self._muted, True
        try:
            self._send(_api.LVM_DELETEALLITEMS)
        finally:
            self._muted = was
        self._rows.clear()

    def set_cell(self, row: int, column: int, text: object) -> None:
        if not 0 <= row < len(self._rows):
            raise IndexError(f"row {row} out of range")
        if not 0 <= column < len(self._columns):
            raise IndexError(f"column {column} out of range")
        cells = list(self._rows[row])
        cells[column] = "" if text is None else str(text)
        self._rows[row] = tuple(cells)
        self._write_cell(row, column, cells[column])

    @property
    def rows(self) -> tuple[tuple[str, ...], ...]:
        return tuple(self._rows)

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(title for title, _ in self._columns)

    def __len__(self) -> int:
        return len(self._rows)

    # -- selection ---------------------------------------------------------------
    @property
    def selected_indices(self) -> tuple[int, ...]:
        found: list[int] = []
        index = -1
        while True:
            index = self._send(_api.LVM_GETNEXTITEM, index, _api.LVNI_SELECTED)
            if index == -1:
                return tuple(found)
            found.append(index)

    @selected_indices.setter
    def selected_indices(self, indices: Iterable[int]) -> None:
        wanted = list(indices)
        if len(wanted) > 1 and not self._multi:
            raise ValueError("this ListView allows only one selected row (multi=False)")
        for i in wanted:
            if not 0 <= i < len(self._rows):
                raise IndexError(f"row {i} out of range")
        was, self._muted = self._muted, True
        try:
            self._set_state(-1, 0, _api.LVIS_SELECTED)
            for i in wanted:
                self._set_state(i, _api.LVIS_SELECTED | _api.LVIS_FOCUSED,
                                _api.LVIS_SELECTED | _api.LVIS_FOCUSED)
            if wanted:
                self._send(_api.LVM_ENSUREVISIBLE, wanted[0], 0)
        finally:
            self._muted = was

    def _set_state(self, index: int, state: int, mask: int) -> None:
        item = _api.LVITEMW()
        item.state, item.stateMask = state, mask
        self._send(_api.LVM_SETITEMSTATE, index, ctypes.addressof(item))

    @property
    def selected_index(self) -> int | None:
        found = self.selected_indices
        return found[0] if found else None

    @selected_index.setter
    def selected_index(self, index: int | None) -> None:
        self.selected_indices = () if index is None else (index,)

    @property
    def selected_row(self) -> tuple[str, ...] | None:
        index = self.selected_index
        return None if index is None else self._rows[index]

    # -- layout and notifications ------------------------------------------------
    def natural_size(self, scale: Scale) -> Size:
        return Size(scale.px(320), scale.px(160))

    def min_size(self, scale: Scale) -> Size:
        return Size(scale.px(80), scale.px(60))

    def _dpi_changed(self, dpi: int) -> None:
        super()._dpi_changed(dpi)
        scale = Scale(dpi)
        for index, (_, width) in enumerate(self._columns):
            self._send(_api.LVM_SETCOLUMNWIDTH, index, scale.px(width))

    def _notify(self, code: int, lparam: int) -> int:
        if self._muted:
            return 0
        info = ctypes.cast(lparam, ctypes.POINTER(_api.NMLISTVIEW)).contents
        if code == _api.LVN_ITEMCHANGED:
            if info.uChanged & _api.LVIF_STATE and (info.uOldState ^ info.uNewState) & _api.LVIS_SELECTED:
                self.on_select.emit()
        elif code == _api.LVN_ITEMACTIVATE:
            self.on_activate.emit()
        elif code == _api.LVN_COLUMNCLICK:
            self.clicked_column = info.iSubItem
            self.on_column_click.emit()
        return 0


# ---------------------------------------------------------------------------
# TreeView
# ---------------------------------------------------------------------------
class TreeNode:
    """One entry of a :class:`TreeView`. Create nodes with ``tree.add(...)`` / ``node.add(...)``."""

    def __init__(self, tree: "TreeView", handle: int, text: str, data: object, parent: "TreeNode | None") -> None:
        self.tree = tree
        self._handle = handle
        self._text = text
        self.data = data
        self.parent = parent
        self._children: list[TreeNode] = []

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = str(value)
        item = _api.TVITEMW()
        item.mask = _api.TVIF_TEXT
        item.hItem = self._handle
        buf = ctypes.create_unicode_buffer(self._text)
        item.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
        self.tree._send(_api.TVM_SETITEMW, 0, ctypes.addressof(item))

    @property
    def children(self) -> tuple["TreeNode", ...]:
        return tuple(self._children)

    def add(self, text: str, data: object = None, *, has_children: bool = False) -> "TreeNode":
        """Add a child node. ``has_children=True`` shows an expander before real children exist."""
        return self.tree._insert(self, str(text), data, has_children)

    def expand(self) -> None:
        self.tree._send(_api.TVM_EXPAND, _api.TVE_EXPAND, self._handle)

    def collapse(self) -> None:
        self.tree._send(_api.TVM_EXPAND, _api.TVE_COLLAPSE, self._handle)

    def select(self) -> None:
        was, self.tree._muted = self.tree._muted, True
        try:
            self.tree._send(_api.TVM_SELECTITEM, _api.TVGN_CARET, self._handle)
        finally:
            self.tree._muted = was

    def remove(self) -> None:
        self.tree._remove(self)

    def __repr__(self) -> str:
        return f"TreeNode({self._text!r})"


class TreeView(Control):
    """
    A tree of text nodes.

    Events do not get arguments; read :attr:`selected` (selection changed) or
    :attr:`event_node` (the node an ``on_expand`` / ``on_activate`` is about).

    ``on_expand`` fires *before* a node opens, so you can add its children lazily::

        tree = TreeView(on_expand=load_children)
        root = tree.add("C:\\\\", data="C:\\\\", has_children=True)
        def load_children():
            node = tree.event_node
            if not node.children:
                for name in os.listdir(node.data): node.add(name, ...)
    """

    on_select = event()
    on_expand = event()
    on_activate = event()

    def __init__(
        self,
        *,
        on_select: Handler | None = None,
        on_expand: Handler | None = None,
        on_activate: Handler | None = None,
        **options: object,
    ) -> None:
        super().__init__(**options)  # type: ignore[arg-type]
        self._nodes: dict[int, TreeNode] = {}
        self._roots: list[TreeNode] = []
        self.event_node: TreeNode | None = None
        style = (
            _api.WS_TABSTOP | _api.TVS_HASBUTTONS | _api.TVS_HASLINES
            | _api.TVS_LINESATROOT | _api.TVS_SHOWSELALWAYS
        )
        self._create("SysTreeView32", "", style, _api.WS_EX_CLIENTEDGE)
        for ev, handler in (
            (self.on_select, on_select),
            (self.on_expand, on_expand),
            (self.on_activate, on_activate),
        ):
            if handler is not None:
                ev(handler)

    # -- nodes -------------------------------------------------------------------
    def add(self, text: str, data: object = None, *, has_children: bool = False) -> TreeNode:
        """Add a top-level node."""
        return self._insert(None, str(text), data, has_children)

    def _insert(self, parent: TreeNode | None, text: str, data: object, has_children: bool) -> TreeNode:
        insert = _api.TVINSERTSTRUCTW()
        insert.hParent = parent._handle if parent else None
        insert.hInsertAfter = wparam(_api.TVI_LAST)
        insert.item.mask = _api.TVIF_TEXT | _api.TVIF_CHILDREN
        buf = ctypes.create_unicode_buffer(text)
        insert.item.pszText = ctypes.cast(buf, ctypes.c_wchar_p)
        insert.item.cChildren = 1 if has_children else 0
        was, self._muted = self._muted, True
        try:
            handle = self._send(_api.TVM_INSERTITEMW, 0, ctypes.addressof(insert)) & _PTR_MASK
        finally:
            self._muted = was
        if not handle:
            raise _api.last_error("TVM_INSERTITEMW")
        node = TreeNode(self, handle, text, data, parent)
        self._nodes[handle] = node
        (parent._children if parent else self._roots).append(node)
        return node

    def _remove(self, node: TreeNode) -> None:
        was, self._muted = self._muted, True
        try:
            self._send(_api.TVM_DELETEITEM, 0, node._handle)
        finally:
            self._muted = was
        siblings = node.parent._children if node.parent else self._roots
        siblings.remove(node)
        stack = [node]
        while stack:
            current = stack.pop()
            self._nodes.pop(current._handle, None)
            stack.extend(current._children)

    def clear(self) -> None:
        for node in list(self._roots):
            self._remove(node)

    @property
    def roots(self) -> tuple[TreeNode, ...]:
        return tuple(self._roots)

    @property
    def selected(self) -> TreeNode | None:
        handle = self._send(_api.TVM_GETNEXTITEM, _api.TVGN_CARET, 0) & _PTR_MASK
        return self._nodes.get(handle)

    # -- layout and notifications ------------------------------------------------
    def natural_size(self, scale: Scale) -> Size:
        return Size(scale.px(220), scale.px(220))

    def min_size(self, scale: Scale) -> Size:
        return Size(scale.px(60), scale.px(60))

    def _notify(self, code: int, lparam: int) -> int:
        if self._muted:
            return 0
        if code in (_api.TVN_SELCHANGEDW, _api.TVN_ITEMEXPANDINGW):
            info = ctypes.cast(lparam, ctypes.POINTER(_api.NMTREEVIEWW)).contents
            node = self._nodes.get((info.itemNew.hItem or 0) & _PTR_MASK)
            if node is None:
                return 0
            self.event_node = node
            if code == _api.TVN_SELCHANGEDW:
                self.on_select.emit()
            elif info.action == _api.TVE_EXPAND:
                self.on_expand.emit()
        elif code == _api.NM_DBLCLK:
            self.event_node = self.selected
            if self.event_node is not None:
                self.on_activate.emit()
        return 0
