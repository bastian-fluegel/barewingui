"""
barewingui.dialogs
~~~~~~~~~~~~~~~~~~
Native standard dialogs: message boxes, file/folder pickers, color and font
choosers, and a simple input box. Call them on the UI thread; each returns when
the dialog is closed (``None`` means "cancelled").
"""

from __future__ import annotations

import ctypes
import os
from typing import NamedTuple, Sequence

from barewingui import _api
from barewingui._api import comdlg32, ole32, shell32, user32
from barewingui.app import App

__all__ = [
    "message_box", "show_info", "show_warning", "show_error", "ask_yes_no", "ask_ok_cancel",
    "open_file", "save_file", "pick_folder", "choose_color", "choose_font", "input_box",
    "FontChoice",
]

_ICONS = {
    None: 0,
    "info": _api.MB_ICONINFORMATION,
    "warning": _api.MB_ICONWARNING,
    "error": _api.MB_ICONERROR,
    "question": _api.MB_ICONQUESTION,
}


def _owner(parent: object) -> int | None:
    """HWND of a Window (or ``None``)."""
    if parent is None:
        return None
    if not getattr(parent, "alive", False):
        return None
    return parent.hwnd  # type: ignore[attr-defined]


def _ready() -> App:
    app = App.current()
    assert app is not None
    app._check_thread()
    return app


# ---------------------------------------------------------------------------
# Message boxes
# ---------------------------------------------------------------------------
def message_box(
    text: str,
    title: str = "",
    *,
    icon: str | None = "info",
    buttons: str = "ok",
    parent: object = None,
) -> str:
    """
    Show a message box and return the pressed button as text:
    ``"ok"``, ``"cancel"``, ``"yes"``, ``"no"``, ``"retry"``, ``"abort"`` or ``"ignore"``.

    :param icon: ``"info"``, ``"warning"``, ``"error"``, ``"question"`` or ``None``.
    :param buttons: ``"ok"``, ``"ok_cancel"``, ``"yes_no"``, ``"yes_no_cancel"``,
        ``"retry_cancel"`` or ``"abort_retry_ignore"``.
    :param parent: a Window that is blocked while the box is open.
    """
    if icon not in _ICONS:
        raise ValueError(f"icon must be one of {[k for k in _ICONS if k]} or None, got {icon!r}")
    if buttons not in _api.MB_BUTTONS:
        raise ValueError(f"buttons must be one of {sorted(_api.MB_BUTTONS)}, got {buttons!r}")
    _ready()
    result = user32.MessageBoxW(
        _owner(parent), str(text), str(title), _api.MB_BUTTONS[buttons] | _ICONS[icon]
    )
    if result == 0:
        raise _api.last_error("MessageBoxW")
    return _api.MB_RESULTS.get(result, "cancel")


def show_info(text: str, title: str = "", *, parent: object = None) -> None:
    message_box(text, title, icon="info", parent=parent)


def show_warning(text: str, title: str = "", *, parent: object = None) -> None:
    message_box(text, title, icon="warning", parent=parent)


def show_error(text: str, title: str = "", *, parent: object = None) -> None:
    message_box(text, title, icon="error", parent=parent)


def ask_yes_no(text: str, title: str = "", *, icon: str | None = "question", parent: object = None) -> bool:
    """``True`` for Yes, ``False`` for No (or closing the box)."""
    return message_box(text, title, icon=icon, buttons="yes_no", parent=parent) == "yes"


def ask_ok_cancel(text: str, title: str = "", *, icon: str | None = "question", parent: object = None) -> bool:
    """``True`` for OK, ``False`` for Cancel."""
    return message_box(text, title, icon=icon, buttons="ok_cancel", parent=parent) == "ok"


# ---------------------------------------------------------------------------
# Files and folders
# ---------------------------------------------------------------------------
def _filter_chars(filters: Sequence[tuple[str, str | Sequence[str]]] | None) -> str:
    """The OPENFILENAME filter text: ``label\\0pattern\\0...\\0\\0``."""
    if not filters:
        filters = [("All files", "*.*")]
    parts: list[str] = []
    for label, pattern in filters:
        patterns = pattern if isinstance(pattern, str) else ";".join(pattern)
        parts.extend((f"{label} ({patterns})", patterns))
    return "\0".join(parts) + "\0\0"


def _parse_file_result(raw: str, multiple: bool) -> list[str]:
    """Paths from an OPENFILENAME result buffer (single path, or ``dir\\0name\\0name``)."""
    parts: list[str] = []
    for piece in raw.split("\0"):
        if not piece:
            break
        parts.append(piece)
    if not parts:
        return []
    if not multiple or len(parts) == 1:
        return [parts[0]]
    folder, names = parts[0], parts[1:]
    return [os.path.join(folder, name) for name in names]


def _file_dialog(
    save: bool,
    title: str,
    filters: Sequence[tuple[str, str | Sequence[str]]] | None,
    initial_dir: str | None,
    initial_name: str,
    default_ext: str | None,
    multiple: bool,
    parent: object,
) -> list[str]:
    _ready()
    filter_text = _filter_chars(filters)
    filter_buf = (ctypes.c_wchar * len(filter_text))(*filter_text)
    size = 32768 if multiple else 1024
    file_buf = ctypes.create_unicode_buffer(initial_name, size)
    ofn = _api.OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(_api.OPENFILENAMEW)
    ofn.hwndOwner = _owner(parent)
    ofn.lpstrFilter = ctypes.cast(filter_buf, ctypes.c_wchar_p)
    ofn.nFilterIndex = 1
    ofn.lpstrFile = ctypes.cast(file_buf, ctypes.c_wchar_p)
    ofn.nMaxFile = size
    ofn.lpstrInitialDir = initial_dir
    ofn.lpstrTitle = title or None
    ofn.lpstrDefExt = (default_ext or "").lstrip(".") or None
    flags = _api.OFN_EXPLORER | _api.OFN_NOCHANGEDIR | _api.OFN_PATHMUSTEXIST
    if save:
        flags |= _api.OFN_OVERWRITEPROMPT
    else:
        flags |= _api.OFN_FILEMUSTEXIST
        if multiple:
            flags |= _api.OFN_ALLOWMULTISELECT
    ofn.Flags = flags
    function = comdlg32.GetSaveFileNameW if save else comdlg32.GetOpenFileNameW
    if function(ctypes.byref(ofn)):
        return _parse_file_result(file_buf[:], multiple)
    error = comdlg32.CommDlgExtendedError()
    if error:
        raise OSError(f"the file dialog failed (CommDlgExtendedError 0x{error:04X})")
    return []


def open_file(
    title: str = "Open",
    *,
    filters: Sequence[tuple[str, str | Sequence[str]]] | None = None,
    initial_dir: str | None = None,
    multiple: bool = False,
    parent: object = None,
) -> str | list[str] | None:
    """
    Let the user choose an existing file. Returns the path, a list of paths
    (``multiple=True``), or ``None`` if cancelled.

    ``filters`` is a list like ``[("Text files", "*.txt"), ("Images", ["*.png", "*.jpg"])]``.
    """
    paths = _file_dialog(False, title, filters, initial_dir, "", None, multiple, parent)
    if not paths:
        return None
    return paths if multiple else paths[0]


def save_file(
    title: str = "Save as",
    *,
    filters: Sequence[tuple[str, str | Sequence[str]]] | None = None,
    initial_dir: str | None = None,
    initial_name: str = "",
    default_ext: str | None = None,
    parent: object = None,
) -> str | None:
    """Let the user choose where to save (asks before overwriting). Returns the path or ``None``."""
    paths = _file_dialog(True, title, filters, initial_dir, initial_name, default_ext, False, parent)
    return paths[0] if paths else None


def pick_folder(title: str = "", *, parent: object = None) -> str | None:
    """Let the user choose a folder. Returns its path or ``None``."""
    _ready()
    display = ctypes.create_unicode_buffer(260)
    info = _api.BROWSEINFOW()
    info.hwndOwner = _owner(parent)
    info.pszDisplayName = ctypes.cast(display, ctypes.c_wchar_p)
    info.lpszTitle = title or None
    info.ulFlags = _api.BIF_RETURNONLYFSDIRS | _api.BIF_NEWDIALOGSTYLE
    pidl = shell32.SHBrowseForFolderW(ctypes.byref(info))
    if not pidl:
        return None
    try:
        path = ctypes.create_unicode_buffer(1024)
        if shell32.SHGetPathFromIDListW(pidl, path):
            return path.value
        return None
    finally:
        ole32.CoTaskMemFree(pidl)


# ---------------------------------------------------------------------------
# Color and font
# ---------------------------------------------------------------------------
def choose_color(
    initial: tuple[int, int, int] = (255, 255, 255), *, parent: object = None
) -> tuple[int, int, int] | None:
    """Color chooser. Takes and returns ``(red, green, blue)`` (0-255), ``None`` if cancelled."""
    _ready()
    custom = (ctypes.c_uint32 * 16)(*([0x00FFFFFF] * 16))
    cc = _api.CHOOSECOLORW()
    cc.lStructSize = ctypes.sizeof(_api.CHOOSECOLORW)
    cc.hwndOwner = _owner(parent)
    r, g, b = initial
    cc.rgbResult = (r & 255) | (g & 255) << 8 | (b & 255) << 16
    cc.lpCustColors = ctypes.cast(custom, ctypes.POINTER(ctypes.c_uint32))
    cc.Flags = _api.CC_RGBINIT | _api.CC_FULLOPEN
    if not comdlg32.ChooseColorW(ctypes.byref(cc)):
        return None
    value = cc.rgbResult
    return value & 255, (value >> 8) & 255, (value >> 16) & 255


class FontChoice(NamedTuple):
    name: str
    size: float  # points
    bold: bool
    italic: bool


def choose_font(initial: FontChoice | None = None, *, parent: object = None) -> FontChoice | None:
    """Font chooser. Returns a :class:`FontChoice`, or ``None`` if cancelled."""
    _ready()
    face = initial or FontChoice("Segoe UI", 9.0, False, False)
    lf = _api.LOGFONTW()
    lf.lfFaceName = face.name[:31]
    lf.lfHeight = -round(face.size * 96 / 72)
    lf.lfWeight = 700 if face.bold else 400
    lf.lfItalic = 1 if face.italic else 0
    cf = _api.CHOOSEFONTW()
    cf.lStructSize = ctypes.sizeof(_api.CHOOSEFONTW)
    cf.hwndOwner = _owner(parent)
    cf.lpLogFont = ctypes.pointer(lf)
    cf.Flags = _api.CF_SCREENFONTS | _api.CF_INITTOLOGFONTSTRUCT
    if not comdlg32.ChooseFontW(ctypes.byref(cf)):
        return None
    return FontChoice(lf.lfFaceName, cf.iPointSize / 10, lf.lfWeight >= 600, bool(lf.lfItalic))


# ---------------------------------------------------------------------------
# Input box (built from BareWinGUI's own controls)
# ---------------------------------------------------------------------------
def input_box(
    prompt: str,
    title: str = "",
    default: str = "",
    *,
    password: bool = False,
    parent: object = None,
) -> str | None:
    """Ask for one line of text. Returns the text, or ``None`` if cancelled."""
    from barewingui.controls import Button, Label, TextBox
    from barewingui.layout import HBox, VBox
    from barewingui.window import Window

    _ready()
    answer: list[str] = []
    with Window(title, size=(380, 140), resizable=False) as dialog:
        with VBox(padding=14, gap=10):
            Label(prompt)
            box = TextBox(default, password=password)
            with HBox(justify="end", gap=8):
                def accept() -> None:
                    answer.append(box.text)
                    dialog.destroy()

                Button("OK", default=True, on_click=accept)
                cancel = Button("Cancel", on_click=dialog.destroy)
    dialog.cancel_button = cancel
    app = _ready()
    app.invoke(lambda: (box.focus(), box.select_all()))  # runs once the dialog is on screen
    dialog.show_modal(parent if getattr(parent, "alive", False) else None)  # type: ignore[arg-type]
    return answer[0] if answer else None
