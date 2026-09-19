"""
barewingui.dialogs
~~~~~~~~~~~~~~~~~~
Deterministic, zero-dependency Win32 system dialogs and modal pickers.
Wraps user32, comdlg32, and shell32 APIs with native Segoe UI rendering.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, Literal

from barewingui.constants import (
    ShowWindowCmd,
    StandardID,
    StockObject,
    SysColor,
    WindowStyle,
    WindowStyleEx,
    WM,
)
from barewingui.core import Application, apply_window_chrome, get_system_font
from barewingui.types import (
    COLORREF,
    HFONT,
    LPARAM,
    LRESULT,
    WPARAM,
    WNDCLASSEXW,
    WNDPROC,
    gdi32,
    kernel32,
    user32,
)

if TYPE_CHECKING:
    from barewingui.window import Window

# ---------------------------------------------------------------------------
# DLL-Instanzen für Dialoge
# ---------------------------------------------------------------------------
comdlg32 = ctypes.windll.comdlg32
shell32 = ctypes.windll.shell32
ole32 = ctypes.windll.ole32

# ---------------------------------------------------------------------------
# MessageBox Konstanten & Typen
# ---------------------------------------------------------------------------
MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
MB_ABORTRETRYIGNORE = 0x00000002
MB_YESNOCANCEL = 0x00000003
MB_YESNO = 0x00000004
MB_RETRYCANCEL = 0x00000005

MB_ICONERROR = 0x00000010
MB_ICONQUESTION = 0x00000020
MB_ICONWARNING = 0x00000030
MB_ICONINFORMATION = 0x00000040

user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int

user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int

# ---------------------------------------------------------------------------
# Common Dialog C-Strukturen & Flags
# ---------------------------------------------------------------------------
OFN_OVERWRITEPROMPT = 0x00000002
OFN_FILEMUSTEXIST = 0x00001000
OFN_PATHMUSTEXIST = 0x00000800
OFN_EXPLORER = 0x00080000
OFN_ENABLESIZING = 0x00800000

CC_RGBINIT = 0x00000001
CC_FULLOPEN = 0x00000002

CF_SCREENFONTS = 0x00000001
CF_EFFECTS = 0x00000100
CF_INITTOLOGFONTSTRUCT = 0x00000040

BIF_RETURNONLYFSDIRS = 0x00000001
BIF_NEWDIALOGSTYLE = 0x00000040


class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]


class CHOOSECOLORW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HWND),
        ("rgbResult", COLORREF),
        ("lpCustColors", ctypes.POINTER(COLORREF)),
        ("Flags", wintypes.DWORD),
        ("lCustData", LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
    ]


class LOGFONTW(ctypes.Structure):
    _fields_ = [
        ("lfHeight", wintypes.LONG),
        ("lfWidth", wintypes.LONG),
        ("lfEscapement", wintypes.LONG),
        ("lfOrientation", wintypes.LONG),
        ("lfWeight", wintypes.LONG),
        ("lfItalic", wintypes.BYTE),
        ("lfUnderline", wintypes.BYTE),
        ("lfStrikeOut", wintypes.BYTE),
        ("lfCharSet", wintypes.BYTE),
        ("lfOutPrecision", wintypes.BYTE),
        ("lfClipPrecision", wintypes.BYTE),
        ("lfQuality", wintypes.BYTE),
        ("lfPitchAndFamily", wintypes.BYTE),
        ("lfFaceName", wintypes.WCHAR * 32),
    ]


class CHOOSEFONTW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hDC", wintypes.HDC),
        ("lpLogFont", ctypes.POINTER(LOGFONTW)),
        ("iPointSize", ctypes.c_int),
        ("Flags", wintypes.DWORD),
        ("rgbColors", COLORREF),
        ("lCustData", LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("hInstance", wintypes.HINSTANCE),
        ("lpszStyle", wintypes.LPWSTR),
        ("nFontType", wintypes.WORD),
        ("wReserved", wintypes.WORD),
        ("nSizeMin", ctypes.c_int),
        ("nSizeMax", ctypes.c_int),
    ]


class BROWSEINFOW(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", wintypes.HWND),
        ("pidlRoot", ctypes.c_void_p),
        ("pszDisplayName", wintypes.LPWSTR),
        ("lpszTitle", wintypes.LPCWSTR),
        ("ulFlags", wintypes.UINT),
        ("lpfn", ctypes.c_void_p),
        ("lParam", LPARAM),
        ("iImage", ctypes.c_int),
    ]


# Signaturen verankern
comdlg32.GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
comdlg32.GetOpenFileNameW.restype = wintypes.BOOL

comdlg32.GetSaveFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
comdlg32.GetSaveFileNameW.restype = wintypes.BOOL

comdlg32.ChooseColorW.argtypes = [ctypes.POINTER(CHOOSECOLORW)]
comdlg32.ChooseColorW.restype = wintypes.BOOL

comdlg32.ChooseFontW.argtypes = [ctypes.POINTER(CHOOSEFONTW)]
comdlg32.ChooseFontW.restype = wintypes.BOOL

shell32.SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFOW)]
shell32.SHBrowseForFolderW.restype = ctypes.c_void_p

shell32.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, wintypes.LPWSTR]
shell32.SHGetPathFromIDListW.restype = wintypes.BOOL

ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
ole32.CoTaskMemFree.restype = None

# Globale Farb-Palette für den Farbdialog (16 benutzerdefinierte Farben)
_CUSTOM_COLORS = (COLORREF * 16)()


def _to_lresult(value: object) -> int:
    """ctypes-WNDPROC darf nur einen Python-int zurückgeben."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    raw = getattr(value, "value", value)
    if raw is None:
        return 0
    return raw if isinstance(raw, int) else int(raw)


def _hwnd_key(hwnd: object) -> int:
    if hwnd is None:
        return 0
    if isinstance(hwnd, int):
        return hwnd
    raw = getattr(hwnd, "value", hwnd)
    return 0 if raw is None else int(raw)


def _resolve_hwnd(parent: Window | wintypes.HWND | int | None) -> wintypes.HWND | None:
    if parent is None:
        return None
    if hasattr(parent, "hwnd"):
        return parent.hwnd
    return wintypes.HWND(int(parent))


def _build_filter_string(filters: list[tuple[str, str]] | None) -> str:
    if not filters:
        return "Alle Dateien (*.*)\0*.*\0\0"
    parts: list[str] = []
    for desc, pat in filters:
        parts.append(f"{desc}\0{pat}")
    parts.append("Alle Dateien (*.*)\0*.*")
    return "\0".join(parts) + "\0\0"


def _double_null_buffer(text: str) -> ctypes.Array[ctypes.c_wchar]:
    """Kopiert einen Filterstring inklusive eingebetteter Nullzeichen nach LPCWSTR."""
    buf = (ctypes.c_wchar * (len(text) + 1))()
    for i, ch in enumerate(text):
        buf[i] = ch
    return buf


# ---------------------------------------------------------------------------
# 1. Universelle MessageBox & Hilfsdialoge (2–5)
# ---------------------------------------------------------------------------
def message_box(
    message: str,
    title: str = "Hinweis",
    icon: Literal["info", "warning", "error", "question", "none"] = "info",
    buttons: Literal["ok", "ok_cancel", "yes_no", "yes_no_cancel", "retry_cancel"] = "ok",
    parent: Window | wintypes.HWND | int | None = None,
) -> str:
    """Zeigt eine native Win32-MessageBox an."""
    Application.initialize()
    u_type = 0

    if buttons == "ok":
        u_type |= MB_OK
    elif buttons == "ok_cancel":
        u_type |= MB_OKCANCEL
    elif buttons == "yes_no":
        u_type |= MB_YESNO
    elif buttons == "yes_no_cancel":
        u_type |= MB_YESNOCANCEL
    elif buttons == "retry_cancel":
        u_type |= MB_RETRYCANCEL

    if icon == "info":
        u_type |= MB_ICONINFORMATION
    elif icon == "warning":
        u_type |= MB_ICONWARNING
    elif icon == "error":
        u_type |= MB_ICONERROR
    elif icon == "question":
        u_type |= MB_ICONQUESTION

    hwnd_owner = _resolve_hwnd(parent)
    result = user32.MessageBoxW(hwnd_owner, message, title, u_type)

    mapping = {
        int(StandardID.OK): "ok",
        int(StandardID.CANCEL): "cancel",
        int(StandardID.YES): "yes",
        int(StandardID.NO): "no",
        int(StandardID.RETRY): "retry",
    }
    return mapping.get(result, "cancel")


def info_box(message: str, title: str = "Information", parent: Window | wintypes.HWND | int | None = None) -> None:
    """Zeigt eine native Informations-Meldung (OK) an."""
    message_box(message, title=title, icon="info", buttons="ok", parent=parent)


def warning_box(message: str, title: str = "Warnung", parent: Window | wintypes.HWND | int | None = None) -> None:
    """Zeigt eine Warnungsmeldung (OK) an."""
    message_box(message, title=title, icon="warning", buttons="ok", parent=parent)


def error_box(message: str, title: str = "Fehler", parent: Window | wintypes.HWND | int | None = None) -> None:
    """Zeigt eine Fehlermeldung (OK) an."""
    message_box(message, title=title, icon="error", buttons="ok", parent=parent)


def confirm_box(message: str, title: str = "Bestätigung", parent: Window | wintypes.HWND | int | None = None) -> bool:
    """Zeigt einen Ja/Nein-Bestätigungsdialog an. Gibt True bei 'Ja' zurück."""
    return message_box(message, title=title, icon="question", buttons="yes_no", parent=parent) == "yes"


ask_yes_no = confirm_box


# ---------------------------------------------------------------------------
# 6. Modal InputBox (Eigenständiges leichtgewichtiges Win32-Fenster)
# ---------------------------------------------------------------------------
_INPUT_BOX_CLASS = "BareWinGUI_InputBox"
_input_class_registered = False
_input_sessions: dict[int, dict[str, Any]] = {}


def _input_proc(hwnd: wintypes.HWND, msg: int, wparam: WPARAM, lparam: LPARAM) -> int:
    session = _input_sessions.get(_hwnd_key(hwnd))

    if msg == int(WM.ERASEBKGND):
        from barewingui.theme import erase_background

        if erase_background(hwnd, wintypes.HDC(wparam)):
            return 1

    if msg == int(WM.CTLCOLORSTATIC):
        from barewingui.theme import paint_static

        return _to_lresult(paint_static(wintypes.HDC(wparam)))

    if msg == int(WM.CTLCOLOREDIT):
        from barewingui.theme import paint_edit

        return _to_lresult(paint_edit(wintypes.HDC(wparam)))

    if session is None:
        return _to_lresult(user32.DefWindowProcW(hwnd, msg, wparam, lparam))

    controls: dict[str, wintypes.HWND] = session["controls"]
    result_text: list[str | None] = session["result"]

    if msg == int(WM.COMMAND):
        ctrl_id = int(wparam) & 0xFFFF
        if ctrl_id == int(StandardID.OK):
            edit_h = controls.get("edit")
            if edit_h:
                length = user32.GetWindowTextLengthW(edit_h)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(edit_h, buf, length + 1)
                result_text[0] = buf.value
            user32.DestroyWindow(hwnd)
            return 0
        if ctrl_id == int(StandardID.CANCEL):
            result_text[0] = None
            user32.DestroyWindow(hwnd)
            return 0

    elif msg == int(WM.CLOSE):
        result_text[0] = None
        user32.DestroyWindow(hwnd)
        return 0

    return _to_lresult(user32.DefWindowProcW(hwnd, msg, wparam, lparam))


# Dauerhafte Referenz hält den C-Funktionszeiger gegen GC-Löschung
_input_wndproc_anchor: WNDPROC = WNDPROC(_input_proc)


def input_box(
    prompt: str,
    title: str = "Eingabe",
    default: str = "",
    password: bool = False,
    parent: Window | wintypes.HWND | int | None = None,
) -> str | None:
    """
    Öffnet einen modalen Eingabedialog mit Segoe UI Typografie.
    Gibt den eingegebenen String zurück oder None bei Abbruch/Schließen.
    """
    Application.initialize()
    global _input_class_registered

    h_instance = kernel32.GetModuleHandleW(None)
    owner_hwnd = _resolve_hwnd(parent)

    result_text: list[str | None] = [None]
    controls: dict[str, wintypes.HWND] = {}

    # Einmalige Registrierung der Fensterklasse für InputBoxes
    if not _input_class_registered:
        wcex = WNDCLASSEXW()
        wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wcex.style = 0
        wcex.lpfnWndProc = _input_wndproc_anchor
        wcex.hInstance = h_instance
        wcex.hCursor = user32.LoadCursorW(None, ctypes.c_wchar_p(32512))
        from barewingui.theme import window_brush

        wcex.hbrBackground = window_brush() or user32.GetSysColorBrush(int(SysColor.WINDOW))
        wcex.lpszClassName = _INPUT_BOX_CLASS
        atom = user32.RegisterClassExW(ctypes.byref(wcex))
        if not atom:
            err = kernel32.GetLastError()
            # 1410 = ERROR_CLASS_ALREADY_EXISTS
            if err != 1410:
                raise RuntimeError(f"Konnte InputBox-Klasse nicht registrieren (Fehler {err})")
        _input_class_registered = True

    # Maße und Zentrierung
    dlg_w, dlg_h = 420, 180
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    x = max(0, (screen_w - dlg_w) // 2)
    y = max(0, (screen_h - dlg_h) // 2)

    if owner_hwnd:
        user32.EnableWindow(owner_hwnd, False)

    dlg_style = int(WindowStyle.POPUPWINDOW | WindowStyle.CAPTION | WindowStyle.VISIBLE)
    dlg_ex_style = int(WindowStyleEx.DLGMODALFRAME | WindowStyleEx.TOPMOST)

    hwnd_dlg = user32.CreateWindowExW(
        dlg_ex_style,
        _INPUT_BOX_CLASS,
        title,
        dlg_style,
        x,
        y,
        dlg_w,
        dlg_h,
        owner_hwnd,
        None,
        h_instance,
        None,
    )

    if not hwnd_dlg:
        if owner_hwnd:
            user32.EnableWindow(owner_hwnd, True)
        raise RuntimeError(
            f"Konnte InputBox nicht erzeugen (Fehler {kernel32.GetLastError()})"
        )

    session_key = _hwnd_key(hwnd_dlg)
    _input_sessions[session_key] = {"controls": controls, "result": result_text}
    apply_window_chrome(hwnd_dlg)

    try:
        sys_font = get_system_font()

        # Prompt Label
        lbl_hwnd = user32.CreateWindowExW(
            0,
            "STATIC",
            prompt,
            int(WindowStyle.CHILD | WindowStyle.VISIBLE),
            20,
            18,
            365,
            38,
            hwnd_dlg,
            None,
            h_instance,
            None,
        )
        user32.SendMessageW(lbl_hwnd, int(WM.SETFONT), sys_font, 1)

        edit_style = (
            int(WindowStyle.CHILD | WindowStyle.VISIBLE | WindowStyle.TABSTOP)
            | 0x0080  # ES_AUTOHSCROLL
        )
        if password:
            edit_style |= 0x0020  # ES_PASSWORD

        edit_hwnd = user32.CreateWindowExW(
            0,
            "EDIT",
            default,
            edit_style,
            20,
            62,
            365,
            32,
            hwnd_dlg,
            None,
            h_instance,
            None,
        )
        controls["edit"] = edit_hwnd
        user32.SendMessageW(edit_hwnd, int(WM.SETFONT), sys_font, 1)
        user32.SendMessageW(edit_hwnd, 0x00D3, 0x0001 | 0x0002, (8 << 16) | 8)  # EM_SETMARGINS
        from barewingui.theme import apply_control_theme

        apply_control_theme(edit_hwnd, "EDIT")

        # OK Button
        ok_hwnd = user32.CreateWindowExW(
            0,
            "BUTTON",
            "OK",
            int(WindowStyle.CHILD | WindowStyle.VISIBLE | WindowStyle.TABSTOP) | 0x0001,  # BS_DEFPUSHBUTTON
            205,
            102,
            85,
            32,
            hwnd_dlg,
            wintypes.HMENU(int(StandardID.OK)),
            h_instance,
            None,
        )
        user32.SendMessageW(ok_hwnd, int(WM.SETFONT), sys_font, 1)
        apply_control_theme(ok_hwnd, "BUTTON")

        # Abbrechen Button
        cancel_hwnd = user32.CreateWindowExW(
            0,
            "BUTTON",
            "Abbrechen",
            int(WindowStyle.CHILD | WindowStyle.VISIBLE | WindowStyle.TABSTOP),
            298,
            102,
            87,
            32,
            hwnd_dlg,
            wintypes.HMENU(int(StandardID.CANCEL)),
            h_instance,
            None,
        )
        user32.SendMessageW(cancel_hwnd, int(WM.SETFONT), sys_font, 1)
        apply_control_theme(cancel_hwnd, "BUTTON")

        user32.SetFocus(edit_hwnd)
        user32.SendMessageW(edit_hwnd, 0x00B1, 0, -1)  # EM_SETSEL: Alles markieren

        # Modale Message-Schleife
        msg = wintypes.MSG()
        p_msg = ctypes.byref(msg)

        while user32.IsWindow(hwnd_dlg) and user32.GetMessageW(p_msg, None, 0, 0) > 0:
            # Enter- und Escape-Taste abfangen
            if msg.message == int(WM.KEYDOWN):
                if msg.wParam == 0x0D:  # VK_RETURN
                    user32.SendMessageW(hwnd_dlg, int(WM.COMMAND), int(StandardID.OK), ok_hwnd)
                    continue
                if msg.wParam == 0x1B:  # VK_ESCAPE
                    user32.SendMessageW(hwnd_dlg, int(WM.COMMAND), int(StandardID.CANCEL), cancel_hwnd)
                    continue

            user32.TranslateMessage(p_msg)
            user32.DispatchMessageW(p_msg)
    finally:
        _input_sessions.pop(session_key, None)
        if owner_hwnd:
            user32.EnableWindow(owner_hwnd, True)
            user32.SetForegroundWindow(owner_hwnd)

    return result_text[0]


# ---------------------------------------------------------------------------
# 7. Datei öffnen (GetOpenFileNameW)
# ---------------------------------------------------------------------------
def open_file(
    title: str = "Datei öffnen",
    default_dir: str = "",
    filters: list[tuple[str, str]] | None = None,
    parent: Window | wintypes.HWND | int | None = None,
) -> str | None:
    """Öffnet den Explorer-Dateiauswahldialog."""
    Application.initialize()
    buffer = ctypes.create_unicode_buffer(65536)
    filter_buf = _double_null_buffer(_build_filter_string(filters))

    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    owner = _resolve_hwnd(parent)
    if owner:
        ofn.hwndOwner = owner
    ofn.lpstrFilter = ctypes.cast(filter_buf, wintypes.LPCWSTR)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 65536
    ofn.lpstrInitialDir = default_dir or None
    ofn.lpstrTitle = title
    ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_ENABLESIZING

    if comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None


# ---------------------------------------------------------------------------
# 8. Datei speichern (GetSaveFileNameW)
# ---------------------------------------------------------------------------
def save_file(
    title: str = "Datei speichern",
    default_dir: str = "",
    default_name: str = "",
    default_ext: str = "",
    filters: list[tuple[str, str]] | None = None,
    parent: Window | wintypes.HWND | int | None = None,
) -> str | None:
    """Öffnet den Explorer-Speicherdialog mit Überschreibwarnung."""
    Application.initialize()
    buffer = ctypes.create_unicode_buffer(65536)
    if default_name:
        buffer.value = default_name

    filter_buf = _double_null_buffer(_build_filter_string(filters))

    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    owner = _resolve_hwnd(parent)
    if owner:
        ofn.hwndOwner = owner
    ofn.lpstrFilter = ctypes.cast(filter_buf, wintypes.LPCWSTR)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 65536
    ofn.lpstrInitialDir = default_dir or None
    ofn.lpstrTitle = title
    ofn.lpstrDefExt = default_ext or None
    ofn.Flags = OFN_EXPLORER | OFN_OVERWRITEPROMPT | OFN_PATHMUSTEXIST | OFN_ENABLESIZING

    if comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None


# ---------------------------------------------------------------------------
# 9. Ordner auswählen (SHBrowseForFolderW)
# ---------------------------------------------------------------------------
def pick_folder(
    title: str = "Ordner auswählen",
    parent: Window | wintypes.HWND | int | None = None,
) -> str | None:
    """Öffnet den nativen Windows-Ordnerauswahldialog."""
    Application.initialize()
    display_buf = ctypes.create_unicode_buffer(260)

    bi = BROWSEINFOW()
    owner = _resolve_hwnd(parent)
    if owner:
        bi.hwndOwner = owner
    bi.pszDisplayName = ctypes.cast(display_buf, wintypes.LPWSTR)
    bi.lpszTitle = title
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE

    pidl = shell32.SHBrowseForFolderW(ctypes.byref(bi))
    if not pidl:
        return None

    path_buf = ctypes.create_unicode_buffer(260)
    success = shell32.SHGetPathFromIDListW(pidl, path_buf)
    ole32.CoTaskMemFree(pidl)

    return path_buf.value if success else None


select_folder = pick_folder


# ---------------------------------------------------------------------------
# 10. Farb- und Schriftart-Dialoge (ChooseColorW / ChooseFontW)
# ---------------------------------------------------------------------------
def choose_color(
    initial_color: tuple[int, int, int] | None = None,
    parent: Window | wintypes.HWND | int | None = None,
) -> tuple[int, int, int] | None:
    """
    Öffnet die Win32-Farbpalette.
    Gibt ein (Rot, Grün, Blau) Tupel von 0–255 zurück oder None bei Abbruch.
    """
    Application.initialize()
    rgb_init = 0
    if initial_color:
        r, g, b = initial_color
        rgb_init = (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)

    cc = CHOOSECOLORW()
    cc.lStructSize = ctypes.sizeof(CHOOSECOLORW)
    owner = _resolve_hwnd(parent)
    if owner:
        cc.hwndOwner = owner
    cc.rgbResult = rgb_init
    cc.lpCustColors = ctypes.cast(_CUSTOM_COLORS, ctypes.POINTER(COLORREF))
    cc.Flags = CC_RGBINIT | CC_FULLOPEN

    if comdlg32.ChooseColorW(ctypes.byref(cc)):
        val = int(cc.rgbResult)
        r = val & 0xFF
        g = (val >> 8) & 0xFF
        b = (val >> 16) & 0xFF
        return (r, g, b)

    return None


def choose_font(
    parent: Window | wintypes.HWND | int | None = None,
) -> dict[str, Any] | None:
    """
    Öffnet den Windows-Schriftartendialog.
    Gibt ein Dict mit Name, Größe (pt), Bold, Italic und Farbe zurück.
    """
    Application.initialize()
    lf = LOGFONTW()

    cf = CHOOSEFONTW()
    cf.lStructSize = ctypes.sizeof(CHOOSEFONTW)
    owner = _resolve_hwnd(parent)
    if owner:
        cf.hwndOwner = owner
    cf.lpLogFont = ctypes.pointer(lf)
    cf.Flags = CF_SCREENFONTS | CF_EFFECTS

    if comdlg32.ChooseFontW(ctypes.byref(cf)):
        val = int(cf.rgbColors)
        r = val & 0xFF
        g = (val >> 8) & 0xFF
        b = (val >> 16) & 0xFF

        return {
            "name": lf.lfFaceName,
            "size": cf.iPointSize // 10,
            "bold": lf.lfWeight >= 700,
            "italic": bool(lf.lfItalic),
            "underline": bool(lf.lfUnderline),
            "strikeout": bool(lf.lfStrikeOut),
            "color": (r, g, b),
        }

    return None
