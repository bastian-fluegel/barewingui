"""A small text editor: MenuBar, shortcuts, multi-line TextBox, file dialogs, StatusBar."""

from __future__ import annotations

from pathlib import Path

from barewingui import (
    App, Menu, MenuBar, MenuItem, MenuSeparator, StatusBar, TextBox, VBox, Window,
    ask_yes_no, open_file, save_file, show_error,
)

FILTERS = [("Text files", "*.txt"), ("All files", "*.*")]


def build(path: str | None = None) -> Window:
    state = {"path": None, "dirty": False}
    with Window("Untitled - Editor", size=(720, 520)) as win:
        with MenuBar():
            with Menu("&File"):
                new_item = MenuItem("&New", shortcut="Ctrl+N")
                open_item = MenuItem("&Open...", shortcut="Ctrl+O")
                save_item = MenuItem("&Save", shortcut="Ctrl+S")
                save_as_item = MenuItem("Save &as...", shortcut="Ctrl+Shift+S")
                MenuSeparator()
                quit_item = MenuItem("&Quit", shortcut="Ctrl+Q")
            with Menu("&Edit"):
                select_all_item = MenuItem("Select &all", shortcut="Ctrl+A")
        status = StatusBar(parts=[500, None])
        with VBox():
            editor = TextBox(multiline=True, grow=1)

    def refresh_title() -> None:
        name = Path(state["path"]).name if state["path"] else "Untitled"
        win.title = f"{'*' if state['dirty'] else ''}{name} - Editor"
        status.text = str(state["path"] or "")
        status[1] = f"{len(editor.text)} characters"

    def changed() -> None:
        state["dirty"] = True
        refresh_title()

    def confirm_discard() -> bool:
        if not state["dirty"]:
            return True
        return ask_yes_no("Discard the unsaved changes?", "Editor", parent=win)

    def load(target: str) -> None:
        try:
            editor.text = Path(target).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            show_error(f"Cannot open the file:\n{exc}", "Editor", parent=win)
            return
        state.update(path=target, dirty=False)
        refresh_title()

    def new() -> None:
        if confirm_discard():
            editor.text = ""
            state.update(path=None, dirty=False)
            refresh_title()

    def open_() -> None:
        if not confirm_discard():
            return
        target = open_file("Open", filters=FILTERS, parent=win)
        if target:
            load(target)

    def save_as() -> bool:
        target = save_file("Save as", filters=FILTERS, default_ext="txt", parent=win)
        if not target:
            return False
        state["path"] = target
        return save()

    def save() -> bool:
        if not state["path"]:
            return save_as()
        try:
            Path(state["path"]).write_text(editor.text, encoding="utf-8")
        except OSError as exc:
            show_error(f"Cannot save the file:\n{exc}", "Editor", parent=win)
            return False
        state["dirty"] = False
        refresh_title()
        return True

    editor.on_change(changed)
    new_item.on_click(new)
    open_item.on_click(open_)
    save_item.on_click(save)
    save_as_item.on_click(save_as)
    quit_item.on_click(win.close)
    select_all_item.on_click(editor.select_all)
    win.on_close = lambda: None if confirm_discard() else False
    refresh_title()
    if path:
        load(path)
    return win


if __name__ == "__main__":
    import sys

    app = App()
    build(sys.argv[1] if len(sys.argv) > 1 else None)
    app.run()
