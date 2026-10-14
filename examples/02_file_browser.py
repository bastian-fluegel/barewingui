"""File browser: Menu, TreeView (lazy), ListView and StatusBar."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from barewingui import (
    App, HBox, ListView, Menu, MenuBar, MenuItem, MenuSeparator, StatusBar,
    TreeView, VBox, Window, pick_folder,
)


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return str(size)


def list_dir(path: Path, show_hidden: bool) -> tuple[list[Path], list[Path]]:
    """(directories, files) of ``path``, sorted; unreadable folders give empty lists."""
    try:
        entries = [e for e in path.iterdir() if show_hidden or not e.name.startswith(".")]
    except OSError:
        return [], []
    key = lambda p: p.name.lower()
    return (
        sorted((e for e in entries if e.is_dir()), key=key),
        sorted((e for e in entries if e.is_file()), key=key),
    )


def build(start: Path | None = None) -> Window:
    root_path = start or Path.home()
    with Window("Files", size=(820, 520)) as win:
        with MenuBar():
            with Menu("&File"):
                open_item = MenuItem("&Open folder...", shortcut="Ctrl+O")
                MenuSeparator()
                quit_item = MenuItem("&Quit", shortcut="Ctrl+Q")
            with Menu("&View"):
                refresh_item = MenuItem("&Refresh", shortcut="F5")
                hidden_item = MenuItem("Show &hidden files", checkable=True)
        status = StatusBar(parts=[500, None])
        with VBox():
            with HBox(gap=6, padding=6, grow=1):
                tree = TreeView(width=250)
                table = ListView([("Name", 280), ("Size", 90), ("Modified", 150)], grow=1)

    def load_children() -> None:
        node = tree.event_node
        if node is None or node.children:
            return
        dirs, _ = list_dir(node.data, hidden_item.checked)
        for directory in dirs:
            node.add(directory.name, data=directory, has_children=True)

    def show_selected() -> None:
        node = tree.selected
        if node is None:
            return
        dirs, files = list_dir(node.data, hidden_item.checked)
        table.clear()
        for directory in dirs:
            table.add_row([directory.name + "\\", "", ""])
        for file in files:
            try:
                info = file.stat()
                table.add_row([file.name, human_size(info.st_size),
                               dt.datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M")])
            except OSError:
                table.add_row([file.name, "", ""])
        status.text = str(node.data)
        status[1] = f"{len(dirs)} folders, {len(files)} files"

    def set_root(path: Path) -> None:
        tree.clear()
        root = tree.add(str(path), data=path, has_children=True)
        root.expand()
        root.select()
        show_selected()

    def refresh() -> None:
        if tree.roots:
            set_root(tree.roots[0].data)

    def choose_folder() -> None:
        chosen = pick_folder("Open folder", parent=win)
        if chosen:
            set_root(Path(chosen))

    tree.on_expand(load_children)
    tree.on_select(show_selected)
    open_item.on_click(choose_folder)
    quit_item.on_click(win.close)
    refresh_item.on_click(refresh)
    hidden_item.on_click(refresh)
    set_root(root_path)
    return win


if __name__ == "__main__":
    app = App()
    build()
    app.run()
