"""
barewingui.dialogs
~~~~~~~~~~~~~~~~~~
Complete, zero-dependency Win32 system dialog wrappers.
Covers all native modal dialogs without third-party dependencies.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Sequence

# ---------------------------------------------------------------------------
# DLL-Initialisierung & Basis-Typen
# ---------------------------------------------------------------------------
user32 = ctypes.windll.user32
comdlg32 = ctypes.windll.comdlg32
shell32 = ctypes.windll.shell32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

MAX_PATH = 260
LF_FACESIZE = 32
COLORREF = wintypes.DWORD
LRESULT = ctypes.c_int64
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

# ---------------------------------------------------------------------------
# Win32 C-Strukturen (64-Bit ABI Alignment)
# ---------------------------------------------------------------------------
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
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", wintypes.LPVOID),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]

class BROWSEINFOW(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", wintypes.HWND),
        ("pidlRoot", wintypes.LPVOID),
        ("pszDisplayName", wintypes.LPWSTR),
        ("lpszTitle", wintypes.LPCWSTR),
        ("ulFlags", wintypes.UINT),
        ("lpfn", wintypes.LPVOID),
        ("lParam", wintypes.LPARAM),
        ("iImage", ctypes.c_int),
    ]

class CHOOSECOLORW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HWND),
        ("rgbResult", COLORREF),
        ("lpCustColors", ctypes.POINTER(COLORREF)),
        ("Flags", wintypes.DWORD),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID),
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
        ("lfFaceName", wintypes.WCHAR * LF_FACESIZE),
    ]

class CHOOSEFONTW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hDC", wintypes.HDC),
        ("lpLogFont", ctypes.POINTER(LOGFONTW)),
        ("iPointSize", wintypes.INT),
        ("Flags", wintypes.DWORD),
        ("rgbColors", COLORREF),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("hInstance", wintypes.HINSTANCE),
        ("lpszStyle", wintypes.LPWSTR),
        ("nFontType", wintypes.WORD),
        ("___MISSING_ALIGNMENT", wintypes.WORD),
        ("nSizeMin", wintypes.INT),
        ("nSizeMax", wintypes.INT),
    ]

class PRINTDLGW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hDevMode", wintypes.HGLOBAL),
        ("hDevNames", wintypes.HGLOBAL),
        ("hDC", wintypes.HDC),
        ("Flags", wintypes.DWORD),
        ("nFromPage", wintypes.WORD),
        ("nToPage", wintypes.WORD),
        ("nMinPage", wintypes.WORD),
        ("nMaxPage", wintypes.WORD),
        ("nCopies", wintypes.WORD),
        ("hInstance", wintypes.HINSTANCE),
        ("lCustData", wintypes.LPARAM),
        ("lpfnPrintHook", wintypes.LPVOID),
        ("lpfnSetupHook", wintypes.LPVOID),
        ("lpPrintTemplateName", wintypes.LPCWSTR),
        ("lpSetupTemplateName", wintypes.LPCWSTR),
        ("hPrintTemplate", wintypes.HGLOBAL),
        ("hSetupTemplate", wintypes.HGLOBAL),
    ]

class PAGESETUPDLGW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hDevMode", wintypes.HGLOBAL),
        ("hDevNames", wintypes.HGLOBAL),
        ("Flags", wintypes.DWORD),
        ("ptPaperSize", wintypes.POINT),
        ("rtMinMargin", wintypes.RECT),
        ("rtMargin", wintypes.RECT),
        ("hInstance", wintypes.HINSTANCE),
        ("lCustData", wintypes.LPARAM),
        ("lpfnPageSetupHook", wintypes.LPVOID),
        ("lpfnPagePaintHook", wintypes.LPVOID),
        ("lpPageSetupTemplateName", wintypes.LPCWSTR),
        ("hPageSetupTemplate", wintypes.HGLOBAL),
    ]

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON),
    ]

# ---------------------------------------------------------------------------
# C-Signaturen deklarieren (Explizite 64-Bit-Typensicherheit)
# ---------------------------------------------------------------------------
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND

user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = LRESULT

user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL

user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None

user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
user32.EnableWindow.restype = wintypes.BOOL

user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL

user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype = wintypes.ATOM

user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL

user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadCursorW.restype = wintypes.HANDLE

user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int

user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT

comdlg32.GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
comdlg32.GetOpenFileNameW.restype = wintypes.BOOL

comdlg32.GetSaveFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
comdlg32.GetSaveFileNameW.restype = wintypes.BOOL

comdlg32.ChooseColorW.argtypes = [ctypes.POINTER(CHOOSECOLORW)]
comdlg32.ChooseColorW.restype = wintypes.BOOL

comdlg32.ChooseFontW.argtypes = [ctypes.POINTER(CHOOSEFONTW)]
comdlg32.ChooseFontW.restype = wintypes.BOOL

comdlg32.PrintDlgW.argtypes = [ctypes.POINTER(PRINTDLGW)]
comdlg32.PrintDlgW.restype = wintypes.BOOL

comdlg32.PageSetupDlgW.argtypes = [ctypes.POINTER(PAGESETUPDLGW)]
comdlg32.PageSetupDlgW.restype = wintypes.BOOL

shell32.SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFOW)]
shell32.SHBrowseForFolderW.restype = wintypes.LPVOID

shell32.SHGetPathFromIDListW.argtypes = [wintypes.LPVOID, wintypes.LPWSTR]
shell32.SHGetPathFromIDListW.restype = wintypes.BOOL

shell32.ShellAboutW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.HICON]
shell32.ShellAboutW.restype = ctypes.c_int

gdi32.GetStockObject.argtypes = [ctypes.c_int]
gdi32.GetStockObject.restype = wintypes.HGDIOBJ

gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteDC.restype = wintypes.BOOL

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

ole32.CoTaskMemFree.argtypes = [wintypes.LPVOID]
ole32.CoTaskMemFree.restype = None

kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL

_CUSTOM_COLORS = (COLORREF * 16)()

# ---------------------------------------------------------------------------
# Datenklassen für Rückgabewerte
# ---------------------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class FontSelection:
    name: str
    size_pt: float
    weight: int
    italic: bool
    underline: bool
    strikeout: bool
    color: tuple[int, int, int]

@dataclass(slots=True, frozen=True)
class PrintSelection:
    copies: int
    from_page: int
    to_page: int
    all_pages: bool
    selection_only: bool

@dataclass(slots=True, frozen=True)
class PageSetupSelection:
    width_mm: float
    height_mm: float
    margin_left_mm: float
    margin_top_mm: float
    margin_right_mm: float
    margin_bottom_mm: float

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _format_filters(filters: Sequence[tuple[str, str]]) -> str:
    parts = []
    for label, pattern in filters:
        parts.append(label)
        parts.append(pattern)
    return "\0".join(parts) + "\0\0"

def _colorref_to_rgb(raw: int) -> tuple[int, int, int]:
    return (raw & 0xFF, (raw >> 8) & 0xFF, (raw >> 16) & 0xFF)

def _rgb_to_colorref(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    return (b << 16) | (g << 8) | r

# ---------------------------------------------------------------------------
# Die 10 nativen Systemdialoge
# ---------------------------------------------------------------------------
def message_box(
    text: str,
    title: str = "Hinweis",
    style: int = 0x00000000,  # MB_OK
    owner_hwnd: int | None = None
) -> int:
    """Zeigt eine native Windows MessageBox an."""
    return user32.MessageBoxW(owner_hwnd, text, title, style)


def open_file(
    title: str = "Datei öffnen",
    initial_dir: str | None = None,
    filters: Sequence[tuple[str, str]] = (("Alle Dateien (*.*)", "*.*"),),
    allow_multi: bool = False,
    owner_hwnd: int | None = None
) -> str | list[str] | None:
    """Öffnet den nativen Dateiauswahl-Dialog (GetOpenFileNameW)."""
    buf_size = 65536 if allow_multi else MAX_PATH
    buffer = ctypes.create_unicode_buffer(buf_size)

    flags = 0x00001000 | 0x00000800 | 0x00080000  # OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_EXPLORER
    if allow_multi:
        flags |= 0x00000200  # OFN_ALLOWMULTISELECT

    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    ofn.hwndOwner = owner_hwnd
    ofn.lpstrFilter = _format_filters(filters)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = buf_size
    ofn.lpstrInitialDir = initial_dir
    ofn.lpstrTitle = title
    ofn.Flags = flags

    if comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        if allow_multi:
            raw = buffer.raw.decode("utf-16le")
            parts = [p for p in raw.split("\0") if p]
            if len(parts) == 1:
                return parts[0]
            folder = parts[0]
            return [f"{folder}\\{name}" for name in parts[1:]]
        return buffer.value
    return None


def save_file(
    title: str = "Datei speichern",
    default_name: str = "",
    default_ext: str = "",
    initial_dir: str | None = None,
    filters: Sequence[tuple[str, str]] = (("Alle Dateien (*.*)", "*.*"),),
    overwrite_prompt: bool = True,
    owner_hwnd: int | None = None
) -> str | None:
    """Öffnet den nativen Speicherndialog (GetSaveFileNameW)."""
    buffer = ctypes.create_unicode_buffer(MAX_PATH)
    if default_name:
        buffer.value = default_name

    flags = 0x00000800 | 0x00080000  # OFN_PATHMUSTEXIST | OFN_EXPLORER
    if overwrite_prompt:
        flags |= 0x00000002  # OFN_OVERWRITEPROMPT

    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    ofn.hwndOwner = owner_hwnd
    ofn.lpstrFilter = _format_filters(filters)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrDefExt = default_ext if default_ext else None
    ofn.lpstrInitialDir = initial_dir
    ofn.lpstrTitle = title
    ofn.Flags = flags

    if comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None


def select_folder(
    title: str = "Ordner auswählen",
    owner_hwnd: int | None = None
) -> str | None:
    """Öffnet die native Ordnerauswahl (SHBrowseForFolderW)."""
    display_name = ctypes.create_unicode_buffer(MAX_PATH)
    path_buffer = ctypes.create_unicode_buffer(MAX_PATH)

    bi = BROWSEINFOW()
    bi.hwndOwner = owner_hwnd
    bi.pszDisplayName = ctypes.cast(display_name, wintypes.LPWSTR)
    bi.lpszTitle = title
    bi.ulFlags = 0x00000001 | 0x00000040  # BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE

    pidl = shell32.SHBrowseForFolderW(ctypes.byref(bi))
    if pidl:
        shell32.SHGetPathFromIDListW(pidl, path_buffer)
        ole32.CoTaskMemFree(pidl)
        return path_buffer.value
    return None


def choose_color(
    initial_color: tuple[int, int, int] = (0, 0, 0),
    full_open: bool = True,
    owner_hwnd: int | None = None
) -> tuple[int, int, int] | None:
    """Öffnet den nativen Farbwähler (ChooseColorW)."""
    flags = 0x00000001  # CC_RGBINIT
    if full_open:
        flags |= 0x00000002  # CC_FULLOPEN

    cc = CHOOSECOLORW()
    cc.lStructSize = ctypes.sizeof(CHOOSECOLORW)
    cc.hwndOwner = owner_hwnd
    cc.rgbResult = _rgb_to_colorref(initial_color)
    cc.lpCustColors = _CUSTOM_COLORS
    cc.Flags = flags

    if comdlg32.ChooseColorW(ctypes.byref(cc)):
        return _colorref_to_rgb(cc.rgbResult)
    return None


def choose_font(
    initial_font: str = "Segoe UI",
    point_size: int = 10,
    owner_hwnd: int | None = None
) -> FontSelection | None:
    """Öffnet den nativen Schriftart-Dialog (ChooseFontW)."""
    log_font = LOGFONTW()
    log_font.lfFaceName = initial_font
    log_font.lfHeight = -int(point_size * 96 / 72)

    cf = CHOOSEFONTW()
    cf.lStructSize = ctypes.sizeof(CHOOSEFONTW)
    cf.hwndOwner = owner_hwnd
    cf.lpLogFont = ctypes.pointer(log_font)
    cf.Flags = 0x00000001 | 0x00000100 | 0x00000040  # CF_SCREENFONTS | CF_EFFECTS | CF_INITTOLOGFONTSTRUCT

    if comdlg32.ChooseFontW(ctypes.byref(cf)):
        return FontSelection(
            name=log_font.lfFaceName,
            size_pt=cf.iPointSize / 10.0,
            weight=log_font.lfWeight,
            italic=bool(log_font.lfItalic),
            underline=bool(log_font.lfUnderline),
            strikeout=bool(log_font.lfStrikeOut),
            color=_colorref_to_rgb(cf.rgbColors),
        )
    return None


def print_dialog(
    min_page: int = 1,
    max_page: int = 1,
    owner_hwnd: int | None = None
) -> PrintSelection | None:
    """Öffnet den nativen Druckerauswahl-Dialog (PrintDlgW)."""
    pd = PRINTDLGW()
    pd.lStructSize = ctypes.sizeof(PRINTDLGW)
    pd.hwndOwner = owner_hwnd
    pd.nMinPage = min_page
    pd.nMaxPage = max_page
    pd.nCopies = 1
    pd.Flags = 0x00000100 | 0x00000004  # PD_RETURNDC | PD_NOSELECTION

    if comdlg32.PrintDlgW(ctypes.byref(pd)):
        sel = PrintSelection(
            copies=pd.nCopies,
            from_page=pd.nFromPage,
            to_page=pd.nToPage,
            all_pages=not bool(pd.Flags & 0x00000002),
            selection_only=bool(pd.Flags & 0x00000001),
        )
        if pd.hDevMode:
            kernel32.GlobalFree(pd.hDevMode)
        if pd.hDevNames:
            kernel32.GlobalFree(pd.hDevNames)
        if pd.hDC:
            gdi32.DeleteDC(pd.hDC)
        return sel
    return None


def page_setup(owner_hwnd: int | None = None) -> PageSetupSelection | None:
    """Öffnet den nativen Seiteneinrichtungs-Dialog (PageSetupDlgW)."""
    psd = PAGESETUPDLGW()
    psd.lStructSize = ctypes.sizeof(PAGESETUPDLGW)
    psd.hwndOwner = owner_hwnd
    psd.Flags = 0x00000008  # PSD_DEFAULTMINMARGINS

    if comdlg32.PageSetupDlgW(ctypes.byref(psd)):
        sel = PageSetupSelection(
            width_mm=psd.ptPaperSize.x / 100.0,
            height_mm=psd.ptPaperSize.y / 100.0,
            margin_left_mm=psd.rtMargin.left / 100.0,
            margin_top_mm=psd.rtMargin.top / 100.0,
            margin_right_mm=psd.rtMargin.right / 100.0,
            margin_bottom_mm=psd.rtMargin.bottom / 100.0,
        )
        if psd.hDevMode:
            kernel32.GlobalFree(psd.hDevMode)
        if psd.hDevNames:
            kernel32.GlobalFree(psd.hDevNames)
        return sel
    return None


def about_dialog(
    app_name: str,
    other_info: str = "BareWinGUI // Zero-Dependency Architecture",
    icon_handle: int | None = None,
    owner_hwnd: int | None = None
) -> None:
    """Ruft die native Shell-Info-/About-Box auf (ShellAboutW)."""
    shell32.ShellAboutW(owner_hwnd, app_name, other_info, icon_handle)


def input_box(
    prompt: str,
    title: str = "Eingabe",
    default_value: str = "",
    owner_hwnd: int | None = None
) -> str | None:
    """
    Erzeugt eine rein native modale Eingabebox (InputBox) ohne Dritt-Frameworks
    via CreateWindowExW und einer modalen Message-Loop.
    """
    result_text: str | None = None
    h_instance = kernel32.GetModuleHandleW(None)
    class_name = f"BareWinInputBox_{abs(id(prompt))}"

    # Win32 Stile & IDs
    WS_POPUPWINDOW = 0x80880000
    WS_CAPTION = 0x00C00000
    WS_VISIBLE = 0x10000000
    WS_CHILD = 0x40000000
    WS_BORDER = 0x00800000
    ES_AUTOHSCROLL = 0x0080
    BS_DEFPUSHBUTTON = 0x0001
    WM_SETFONT = 0x0030
    DEFAULT_GUI_FONT = 17
    ID_OK, ID_CANCEL, ID_EDIT = 1001, 1002, 1003

    hwnd_dlg = None
    hwnd_edit = None

    def wnd_proc(hwnd, msg, wparam, lparam):
        nonlocal result_text, hwnd_dlg, hwnd_edit
        if msg == 0x0111:  # WM_COMMAND
            cmd_id = wparam & 0xFFFF
            if cmd_id == ID_OK:
                buf = ctypes.create_unicode_buffer(1024)
                user32.SendMessageW(hwnd_edit, 0x000D, 1024, ctypes.addressof(buf))  # WM_GETTEXT
                result_text = buf.value
                user32.DestroyWindow(hwnd)
                return 0
            elif cmd_id == ID_CANCEL:
                result_text = None
                user32.DestroyWindow(hwnd)
                return 0
        elif msg == 0x0010:  # WM_CLOSE
            result_text = None
            user32.DestroyWindow(hwnd)
            return 0
        elif msg == 0x0002:  # WM_DESTROY
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    proc_ptr = WNDPROC(wnd_proc)

    wcex = WNDCLASSEXW()
    wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
    wcex.lpfnWndProc = proc_ptr
    wcex.hInstance = h_instance
    wcex.hCursor = user32.LoadCursorW(None, wintypes.LPCWSTR(32512))
    wcex.hbrBackground = wintypes.HANDLE(5 + 1)  # COLOR_WINDOW + 1
    wcex.lpszClassName = class_name
    user32.RegisterClassExW(ctypes.byref(wcex))

    if owner_hwnd:
        user32.EnableWindow(owner_hwnd, False)

    # Automatische Zentrierung auf dem Bildschirm
    dlg_w, dlg_h = 440, 185
    pos_x = max(0, (user32.GetSystemMetrics(0) - dlg_w) // 2)
    pos_y = max(0, (user32.GetSystemMetrics(1) - dlg_h) // 2)

    hwnd_dlg = user32.CreateWindowExW(
        0x00010000,  # WS_EX_CONTROLPARENT
        class_name,
        title,
        WS_POPUPWINDOW | WS_CAPTION | WS_VISIBLE,
        pos_x, pos_y, dlg_w, dlg_h,
        owner_hwnd, None, h_instance, None
    )

    # Moderne Standard-Schriftart abrufen
    h_font = gdi32.GetStockObject(DEFAULT_GUI_FONT)

    # Prompt-Label
    hwnd_lbl = user32.CreateWindowExW(
        0, "STATIC", prompt,
        WS_CHILD | WS_VISIBLE,
        20, 16, 385, 36,
        hwnd_dlg, None, h_instance, None
    )
    user32.SendMessageW(hwnd_lbl, WM_SETFONT, h_font, 1)

    # Eingabefeld (Edit)
    hwnd_edit = user32.CreateWindowExW(
        0x00000200,  # WS_EX_CLIENTEDGE
        "EDIT", default_value,
        WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
        20, 56, 385, 26,
        hwnd_dlg, wintypes.HMENU(ID_EDIT), h_instance, None
    )
    user32.SendMessageW(hwnd_edit, WM_SETFONT, h_font, 1)

    # Buttons
    hwnd_btn_ok = user32.CreateWindowExW(
        0, "BUTTON", "OK",
        WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
        205, 98, 95, 28,
        hwnd_dlg, wintypes.HMENU(ID_OK), h_instance, None
    )
    user32.SendMessageW(hwnd_btn_ok, WM_SETFONT, h_font, 1)

    hwnd_btn_cancel = user32.CreateWindowExW(
        0, "BUTTON", "Abbrechen",
        WS_CHILD | WS_VISIBLE,
        310, 98, 95, 28,
        hwnd_dlg, wintypes.HMENU(ID_CANCEL), h_instance, None
    )
    user32.SendMessageW(hwnd_btn_cancel, WM_SETFONT, h_font, 1)

    # Modale Message-Loop
    msg = wintypes.MSG()
    p_msg = ctypes.byref(msg)
    while user32.GetMessageW(p_msg, None, 0, 0) > 0:
        user32.TranslateMessage(p_msg)
        user32.DispatchMessageW(p_msg)

    # Ressourcen freigeben & Parent reaktivieren
    if owner_hwnd:
        user32.EnableWindow(owner_hwnd, True)
        user32.SetForegroundWindow(owner_hwnd)

    user32.UnregisterClassW(class_name, h_instance)
    return result_text