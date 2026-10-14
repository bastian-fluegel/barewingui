"""
barewingui._api
~~~~~~~~~~~~~~~
Win32 bindings (ctypes). Importing this module never touches a DLL, so the
package imports on every platform; DLLs are loaded on first use and every
function must have a prototype declared below (no unprototyped calls, which
would truncate 64-bit handles).
"""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from typing import Any

from barewingui.errors import PlatformError

IS_WINDOWS = sys.platform == "win32"

# ---------------------------------------------------------------------------
# Pointer-sized types
# ---------------------------------------------------------------------------
LONG_PTR = ctypes.c_ssize_t
ULONG_PTR = ctypes.c_size_t
LRESULT = ctypes.c_ssize_t
WPARAM = wintypes.WPARAM
LPARAM = wintypes.LPARAM
HWND = wintypes.HWND

_FUNCTYPE = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
WNDPROC = _FUNCTYPE(LRESULT, HWND, wintypes.UINT, WPARAM, LPARAM)

# ---------------------------------------------------------------------------
# Window messages and styles used by the core
# ---------------------------------------------------------------------------
WM_DESTROY = 0x0002
WM_SIZE = 0x0005
WM_CLOSE = 0x0010
WM_GETMINMAXINFO = 0x0024
WM_NCCREATE = 0x0081
WM_NCDESTROY = 0x0082
WM_DPICHANGED = 0x02E0
WM_APP = 0x8000

SIZE_MINIMIZED = 1

WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_THICKFRAME = 0x00040000
WS_MAXIMIZEBOX = 0x00010000
WS_CLIPCHILDREN = 0x02000000
WS_EX_CONTROLPARENT = 0x00010000

SW_HIDE = 0
SW_SHOW = 5

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

CW_USEDEFAULT = -0x80000000
COLOR_BTNFACE = 15
IDC_ARROW = 32512
GA_ROOT = 2
ERROR_ACCESS_DENIED = 5
ERROR_CLASS_ALREADY_EXISTS = 1410

DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
HWND_MESSAGE = -3

# ---------------------------------------------------------------------------
# Child controls
# ---------------------------------------------------------------------------
WM_SETFONT = 0x0030
WM_COMMAND = 0x0111

WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
WS_CLIPSIBLINGS = 0x04000000
WS_TABSTOP = 0x00010000
WS_GROUP = 0x00020000
WS_VSCROLL = 0x00200000
WS_EX_CLIENTEDGE = 0x00000200

IDOK = 1

BS_PUSHBUTTON = 0x00
BS_DEFPUSHBUTTON = 0x01
BS_AUTO3STATE = 0x06
BS_AUTOCHECKBOX = 0x03
BS_GROUPBOX = 0x07
BS_AUTORADIOBUTTON = 0x09
BM_GETCHECK = 0x00F0
BM_SETCHECK = 0x00F1
BM_CLICK = 0x00F5
BST_UNCHECKED, BST_CHECKED, BST_INDETERMINATE = 0, 1, 2
BN_CLICKED = 0

SS_LEFT = 0x00
SS_NOPREFIX = 0x80

ES_MULTILINE = 0x0004
ES_PASSWORD = 0x0020
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL = 0x0080
ES_READONLY = 0x0800
ES_WANTRETURN = 0x1000
EN_CHANGE = 0x0300
EM_SETSEL = 0x00B1
EM_SETREADONLY = 0x00CF
EM_SETCUEBANNER = 0x1501

CBS_DROPDOWN = 0x0002
CBS_DROPDOWNLIST = 0x0003
CBS_AUTOHSCROLL = 0x0040
CB_ERR = -1
CB_GETCOUNT = 0x0146
CB_GETCURSEL = 0x0147
CB_GETLBTEXT = 0x0148
CB_GETLBTEXTLEN = 0x0149
CB_ADDSTRING = 0x0143
CB_DELETESTRING = 0x0144
CB_INSERTSTRING = 0x014A
CB_RESETCONTENT = 0x014B
CB_SETCURSEL = 0x014E
CB_SETMINVISIBLE = 0x1701
CBN_SELCHANGE = 1
CBN_EDITCHANGE = 5

LBS_NOTIFY = 0x0001
LBS_NOINTEGRALHEIGHT = 0x0100
LBS_EXTENDEDSEL = 0x0800
LB_ERR = -1
LB_ADDSTRING = 0x0180
LB_INSERTSTRING = 0x0181
LB_DELETESTRING = 0x0182
LB_RESETCONTENT = 0x0184
LB_SETSEL = 0x0185
LB_SETCURSEL = 0x0186
LB_GETSEL = 0x0187
LB_GETCURSEL = 0x0188
LB_GETTEXT = 0x0189
LB_GETTEXTLEN = 0x018A
LB_GETCOUNT = 0x018B
LB_GETSELCOUNT = 0x0190
LB_GETSELITEMS = 0x0191
LBN_SELCHANGE = 1
LBN_DBLCLK = 2

SPI_GETNONCLIENTMETRICS = 0x0029

# dialog-style child windows (tab pages)
DS_CONTROL = 0x0400
ETDT_ENABLETAB = 0x0006
DLGPROC = _FUNCTYPE(ctypes.c_ssize_t, HWND, wintypes.UINT, WPARAM, LPARAM)

# ---------------------------------------------------------------------------
# Common controls (comctl32)
# ---------------------------------------------------------------------------
WM_NOTIFY = 0x004E
WM_HSCROLL = 0x0114
WM_VSCROLL = 0x0115
WM_USER = 0x0400

# progress bar
PBS_SMOOTH = 0x01
PBS_MARQUEE = 0x08
PBM_SETPOS = WM_USER + 2
PBM_GETPOS = WM_USER + 8
PBM_SETRANGE32 = WM_USER + 6
PBM_SETMARQUEE = WM_USER + 10
PBM_SETSTATE = WM_USER + 16
PBST_NORMAL, PBST_ERROR, PBST_PAUSED = 1, 2, 3

# trackbar
TBS_AUTOTICKS = 0x0001
TBS_VERT = 0x0002
TBS_NOTICKS = 0x0010
TBM_GETPOS = WM_USER
TBM_SETPOS = WM_USER + 5
TBM_SETRANGEMIN = WM_USER + 7
TBM_SETRANGEMAX = WM_USER + 8
TBM_SETTICFREQ = WM_USER + 20
TBM_SETPAGESIZE = WM_USER + 21
TBM_SETLINESIZE = WM_USER + 23
TB_ENDTRACK = 8

# up-down (spin box)
UDM_SETBUDDY = WM_USER + 105
UDM_SETRANGE32 = WM_USER + 111
UDM_SETPOS32 = WM_USER + 113
UDS_SETBUDDYINT = 0x0002
UDS_ALIGNRIGHT = 0x0004
UDS_ARROWKEYS = 0x0020
UDS_NOTHOUSANDS = 0x0080
ES_NUMBER = 0x2000

# status bar
SBARS_SIZEGRIP = 0x0100
SB_SETPARTS = WM_USER + 4
SB_SETTEXTW = WM_USER + 11

# date/time picker
DTS_SHORTDATEFORMAT = 0x0000
DTS_LONGDATEFORMAT = 0x0004
DTS_TIMEFORMAT = 0x0009
DTM_GETSYSTEMTIME = 0x1001
DTM_SETSYSTEMTIME = 0x1002
DTN_DATETIMECHANGE = -759
GDT_VALID = 0

# list view
LVS_REPORT = 0x0001
LVS_SINGLESEL = 0x0004
LVS_SHOWSELALWAYS = 0x0008
LVS_EX_GRIDLINES = 0x00000001
LVS_EX_FULLROWSELECT = 0x00000020
LVS_EX_DOUBLEBUFFER = 0x00010000
LVM_GETITEMCOUNT = 0x1004
LVM_GETNEXTITEM = 0x100C
LVM_DELETEITEM = 0x1008
LVM_DELETEALLITEMS = 0x1009
LVM_ENSUREVISIBLE = 0x1013
LVM_SETCOLUMNWIDTH = 0x101E
LVM_SETITEMSTATE = 0x102B
LVM_GETSELECTEDCOUNT = 0x1032
LVM_SETEXTENDEDLISTVIEWSTYLE = 0x1036
LVM_GETITEMTEXTW = 0x1073
LVM_SETITEMTEXTW = 0x1074
LVM_INSERTITEMW = 0x104D
LVM_INSERTCOLUMNW = 0x1061
LVNI_SELECTED = 0x0002
LVIF_TEXT, LVIF_STATE = 0x0001, 0x0008
LVIS_FOCUSED, LVIS_SELECTED = 0x0001, 0x0002
LVCF_FMT, LVCF_WIDTH, LVCF_TEXT, LVCF_SUBITEM = 0x0001, 0x0002, 0x0004, 0x0008
LVCFMT_LEFT, LVCFMT_RIGHT = 0, 1
LVN_ITEMCHANGED = -101
LVN_COLUMNCLICK = -108
LVN_ITEMACTIVATE = -114
NM_DBLCLK = -3

# tree view
TVS_HASBUTTONS = 0x0001
TVS_HASLINES = 0x0002
TVS_LINESATROOT = 0x0004
TVS_SHOWSELALWAYS = 0x0020
TVM_INSERTITEMW = 0x1132
TVM_DELETEITEM = 0x1101
TVM_EXPAND = 0x1102
TVM_GETNEXTITEM = 0x110A
TVM_SELECTITEM = 0x110B
TVM_ENSUREVISIBLE = 0x1114
TVM_GETITEMW = 0x113E
TVM_SETITEMW = 0x113F
TVGN_CARET = 9
TVI_LAST = -0x0FFFE
TVI_ROOT = -0x10000
TVIF_TEXT, TVIF_CHILDREN = 0x0001, 0x0040
TVE_COLLAPSE, TVE_EXPAND = 1, 2
TVN_SELCHANGEDW = -451
TVN_ITEMEXPANDINGW = -454

# tab control
TCM_GETCURSEL = 0x130B
TCM_SETCURSEL = 0x130C
TCM_ADJUSTRECT = 0x1328
TCM_SETITEMW = 0x133D
TCM_INSERTITEMW = 0x133E
TCIF_TEXT = 0x0001
TCN_SELCHANGE = -551

# ---------------------------------------------------------------------------
# Menus, accelerators, timers, dialogs
# ---------------------------------------------------------------------------
WM_TIMER = 0x0113
WM_CONTEXTMENU = 0x007B
IDCANCEL = 2

MF_STRING = 0x0000
MF_SEPARATOR = 0x0800
MF_POPUP = 0x0010
MF_BYCOMMAND = 0x0000
MF_GRAYED = 0x0001
MF_ENABLED = 0x0000
MF_CHECKED = 0x0008
MF_UNCHECKED = 0x0000
TPM_RIGHTBUTTON = 0x0002

FVIRTKEY, FSHIFT, FCONTROL, FALT = 0x01, 0x04, 0x08, 0x10
GWLP_HWNDPARENT = -8

MB_ICONERROR, MB_ICONQUESTION, MB_ICONWARNING, MB_ICONINFORMATION = 0x10, 0x20, 0x30, 0x40
MB_BUTTONS = {
    "ok": 0x0, "ok_cancel": 0x1, "abort_retry_ignore": 0x2, "yes_no_cancel": 0x3,
    "yes_no": 0x4, "retry_cancel": 0x5,
}
MB_RESULTS = {1: "ok", 2: "cancel", 3: "abort", 4: "retry", 5: "ignore", 6: "yes", 7: "no"}

OFN_OVERWRITEPROMPT = 0x00000002
OFN_NOCHANGEDIR = 0x00000008
OFN_ALLOWMULTISELECT = 0x00000200
OFN_PATHMUSTEXIST = 0x00000800
OFN_FILEMUSTEXIST = 0x00001000
OFN_EXPLORER = 0x00080000
CC_RGBINIT, CC_FULLOPEN = 0x0001, 0x0002
CF_SCREENFONTS, CF_INITTOLOGFONTSTRUCT, CF_EFFECTS = 0x0001, 0x0040, 0x0100
BIF_RETURNONLYFSDIRS, BIF_NEWDIALOGSTYLE = 0x0001, 0x0040
COINIT_APARTMENTTHREADED = 0x2


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------
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
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON),
    ]


class CREATESTRUCTW(ctypes.Structure):
    _fields_ = [
        ("lpCreateParams", wintypes.LPVOID),
        ("hInstance", wintypes.HINSTANCE),
        ("hMenu", wintypes.HMENU),
        ("hwndParent", HWND),
        ("cy", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x", ctypes.c_int),
        ("style", wintypes.LONG),
        ("lpszName", wintypes.LPCWSTR),
        ("lpszClass", wintypes.LPCWSTR),
        ("dwExStyle", wintypes.DWORD),
    ]


class MINMAXINFO(ctypes.Structure):
    _fields_ = [
        ("ptReserved", wintypes.POINT),
        ("ptMaxSize", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("ptMinTrackSize", wintypes.POINT),
        ("ptMaxTrackSize", wintypes.POINT),
    ]


class INITCOMMONCONTROLSEX(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("dwICC", wintypes.DWORD)]


class ACTCTXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.ULONG),
        ("dwFlags", wintypes.DWORD),
        ("lpSource", wintypes.LPCWSTR),
        ("wProcessorArchitecture", wintypes.WORD),
        ("wLangId", wintypes.LANGID),
        ("lpAssemblyDirectory", wintypes.LPCWSTR),
        ("lpResourceName", wintypes.LPCWSTR),
        ("lpApplicationName", wintypes.LPCWSTR),
        ("hModule", wintypes.HMODULE),
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


class NONCLIENTMETRICSW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("iBorderWidth", ctypes.c_int),
        ("iScrollWidth", ctypes.c_int),
        ("iScrollHeight", ctypes.c_int),
        ("iCaptionWidth", ctypes.c_int),
        ("iCaptionHeight", ctypes.c_int),
        ("lfCaptionFont", LOGFONTW),
        ("iSmCaptionWidth", ctypes.c_int),
        ("iSmCaptionHeight", ctypes.c_int),
        ("lfSmCaptionFont", LOGFONTW),
        ("iMenuWidth", ctypes.c_int),
        ("iMenuHeight", ctypes.c_int),
        ("lfMenuFont", LOGFONTW),
        ("lfStatusFont", LOGFONTW),
        ("lfMessageFont", LOGFONTW),
        ("iPaddedBorderWidth", ctypes.c_int),
    ]


class NMHDR(ctypes.Structure):
    _fields_ = [("hwndFrom", HWND), ("idFrom", ULONG_PTR), ("code", ctypes.c_int)]


class SYSTEMTIME(ctypes.Structure):
    _fields_ = [
        (name, wintypes.WORD)
        for name in (
            "wYear", "wMonth", "wDayOfWeek", "wDay",
            "wHour", "wMinute", "wSecond", "wMilliseconds",
        )
    ]


class LVCOLUMNW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("fmt", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("pszText", wintypes.LPWSTR),
        ("cchTextMax", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("iOrder", ctypes.c_int),
    ]


class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("iItem", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("state", wintypes.UINT),
        ("stateMask", wintypes.UINT),
        ("pszText", wintypes.LPWSTR),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", LPARAM),
        ("iIndent", ctypes.c_int),
    ]


class NMLISTVIEW(ctypes.Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("iItem", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("uNewState", wintypes.UINT),
        ("uOldState", wintypes.UINT),
        ("uChanged", wintypes.UINT),
        ("ptAction", wintypes.POINT),
        ("lParam", LPARAM),
    ]


class TVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("hItem", ctypes.c_void_p),
        ("state", wintypes.UINT),
        ("stateMask", wintypes.UINT),
        ("pszText", wintypes.LPWSTR),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("iSelectedImage", ctypes.c_int),
        ("cChildren", ctypes.c_int),
        ("lParam", LPARAM),
    ]


class TVINSERTSTRUCTW(ctypes.Structure):
    _fields_ = [
        ("hParent", ctypes.c_void_p),
        ("hInsertAfter", ctypes.c_void_p),
        ("item", TVITEMW),
    ]


class NMTREEVIEWW(ctypes.Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("action", wintypes.UINT),
        ("itemOld", TVITEMW),
        ("itemNew", TVITEMW),
        ("ptDrag", wintypes.POINT),
    ]


class TCITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("pszText", wintypes.LPWSTR),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", LPARAM),
    ]


class ACCEL(ctypes.Structure):
    _fields_ = [("fVirt", wintypes.BYTE), ("key", wintypes.WORD), ("cmd", wintypes.WORD)]


class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", HWND),
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
        ("hwndOwner", HWND),
        ("hInstance", wintypes.HWND),
        ("rgbResult", wintypes.DWORD),
        ("lpCustColors", ctypes.POINTER(wintypes.DWORD)),
        ("Flags", wintypes.DWORD),
        ("lCustData", LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
    ]


class CHOOSEFONTW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", HWND),
        ("hDC", wintypes.HDC),
        ("lpLogFont", ctypes.POINTER(LOGFONTW)),
        ("iPointSize", ctypes.c_int),
        ("Flags", wintypes.DWORD),
        ("rgbColors", wintypes.DWORD),
        ("lCustData", LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("hInstance", wintypes.HINSTANCE),
        ("lpszStyle", wintypes.LPWSTR),
        ("nFontType", wintypes.WORD),
        ("missingAlignment", wintypes.WORD),
        ("nSizeMin", ctypes.c_int),
        ("nSizeMax", ctypes.c_int),
    ]


class BROWSEINFOW(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", HWND),
        ("pidlRoot", ctypes.c_void_p),
        ("pszDisplayName", wintypes.LPWSTR),
        ("lpszTitle", wintypes.LPCWSTR),
        ("ulFlags", wintypes.UINT),
        ("lpfn", ctypes.c_void_p),
        ("lParam", LPARAM),
        ("iImage", ctypes.c_int),
    ]


# ---------------------------------------------------------------------------
# Lazy libraries with mandatory prototypes
# ---------------------------------------------------------------------------
def require_windows() -> None:
    if not IS_WINDOWS:
        raise PlatformError("BareWinGUI needs Windows (it binds directly to the Win32 DLLs).")


class _Library:
    """A DLL that is loaded on first use; functions get their prototype on first access."""

    def __init__(
        self,
        name: str,
        prototypes: dict[str, tuple[Any, list[Any]]],
        aliases: dict[str, str] | None = None,
    ) -> None:
        self._name = name
        self._prototypes = prototypes
        self._aliases = aliases or {}
        self._cdll: Any = None

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            restype, argtypes = self._prototypes[name]
        except KeyError:
            raise AttributeError(
                f"{self._name}.{name} has no prototype declared in barewingui._api"
            ) from None
        if self._cdll is None:
            require_windows()
            self._cdll = ctypes.WinDLL(self._name, use_last_error=True)  # type: ignore[attr-defined]
        target = name
        if not hasattr(self._cdll, target):
            target = self._aliases.get(name, name)
        func = getattr(self._cdll, target)
        func.restype = restype
        func.argtypes = argtypes
        self.__dict__[name] = func
        return func


_P = ctypes.POINTER
_BOOL, _UINT, _DWORD, _INT = wintypes.BOOL, wintypes.UINT, wintypes.DWORD, ctypes.c_int

user32 = _Library(
    "user32",
    {
        "RegisterClassExW": (wintypes.ATOM, [_P(WNDCLASSEXW)]),
        "CreateWindowExW": (
            HWND,
            [
                _DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, _DWORD,
                _INT, _INT, _INT, _INT,
                HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID,
            ],
        ),
        "DestroyWindow": (_BOOL, [HWND]),
        "DefWindowProcW": (LRESULT, [HWND, _UINT, WPARAM, LPARAM]),
        "ShowWindow": (_BOOL, [HWND, _INT]),
        "UpdateWindow": (_BOOL, [HWND]),
        "SetWindowTextW": (_BOOL, [HWND, wintypes.LPCWSTR]),
        "SetWindowPos": (_BOOL, [HWND, HWND, _INT, _INT, _INT, _INT, _UINT]),
        "GetClientRect": (_BOOL, [HWND, _P(wintypes.RECT)]),
        "GetWindowRect": (_BOOL, [HWND, _P(wintypes.RECT)]),
        "AdjustWindowRectExForDpi": (_BOOL, [_P(wintypes.RECT), _DWORD, _BOOL, _DWORD, _UINT]),
        "GetDpiForWindow": (_UINT, [HWND]),
        "SetProcessDpiAwarenessContext": (_BOOL, [ctypes.c_void_p]),
        "LoadCursorW": (wintypes.HANDLE, [wintypes.HINSTANCE, ctypes.c_void_p]),
        "GetMessageW": (_BOOL, [_P(wintypes.MSG), HWND, _UINT, _UINT]),
        "TranslateMessage": (_BOOL, [_P(wintypes.MSG)]),
        "DispatchMessageW": (LRESULT, [_P(wintypes.MSG)]),
        "IsDialogMessageW": (_BOOL, [HWND, _P(wintypes.MSG)]),
        "PostMessageW": (_BOOL, [HWND, _UINT, WPARAM, LPARAM]),
        "PostQuitMessage": (None, [_INT]),
        "GetAncestor": (HWND, [HWND, _UINT]),
        "CreateDialogIndirectParamW": (
            HWND, [wintypes.HINSTANCE, ctypes.c_void_p, HWND, DLGPROC, LPARAM],
        ),
        "SendMessageW": (LRESULT, [HWND, _UINT, WPARAM, LPARAM]),
        "CreateMenu": (wintypes.HMENU, []),
        "CreatePopupMenu": (wintypes.HMENU, []),
        "DestroyMenu": (_BOOL, [wintypes.HMENU]),
        "AppendMenuW": (_BOOL, [wintypes.HMENU, _UINT, ULONG_PTR, wintypes.LPCWSTR]),
        "ModifyMenuW": (_BOOL, [wintypes.HMENU, _UINT, _UINT, ULONG_PTR, wintypes.LPCWSTR]),
        "CheckMenuItem": (_DWORD, [wintypes.HMENU, _UINT, _UINT]),
        "EnableMenuItem": (_BOOL, [wintypes.HMENU, _UINT, _UINT]),
        "SetMenu": (_BOOL, [HWND, wintypes.HMENU]),
        "DrawMenuBar": (_BOOL, [HWND]),
        "TrackPopupMenu": (_BOOL, [wintypes.HMENU, _UINT, _INT, _INT, _INT, HWND, ctypes.c_void_p]),
        "GetCursorPos": (_BOOL, [_P(wintypes.POINT)]),
        "SetForegroundWindow": (_BOOL, [HWND]),
        "CreateAcceleratorTableW": (wintypes.HANDLE, [_P(ACCEL), _INT]),
        "DestroyAcceleratorTable": (_BOOL, [wintypes.HANDLE]),
        "TranslateAcceleratorW": (_INT, [HWND, wintypes.HANDLE, _P(wintypes.MSG)]),
        "SetTimer": (ULONG_PTR, [HWND, ULONG_PTR, _UINT, ctypes.c_void_p]),
        "KillTimer": (_BOOL, [HWND, ULONG_PTR]),
        "MessageBoxW": (_INT, [HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, _UINT]),
        "SetWindowLongPtrW": (LONG_PTR, [HWND, _INT, LONG_PTR]),
        "GetWindowTextLengthW": (_INT, [HWND]),
        "GetWindowTextW": (_INT, [HWND, wintypes.LPWSTR, _INT]),
        "EnableWindow": (_BOOL, [HWND, _BOOL]),
        "IsWindowEnabled": (_BOOL, [HWND]),
        "SetFocus": (HWND, [HWND]),
        "GetDC": (wintypes.HDC, [HWND]),
        "ReleaseDC": (_INT, [HWND, wintypes.HDC]),
        "SystemParametersInfoForDpi": (
            _BOOL, [_UINT, _UINT, ctypes.c_void_p, _UINT, _UINT],
        ),
    },
    aliases={"SetWindowLongPtrW": "SetWindowLongW"},  # 32-bit Windows has no *Ptr export
)

kernel32 = _Library(
    "kernel32",
    {
        "GetModuleHandleW": (wintypes.HINSTANCE, [wintypes.LPCWSTR]),
        "CreateActCtxW": (wintypes.HANDLE, [_P(ACTCTXW)]),
        "ActivateActCtx": (_BOOL, [wintypes.HANDLE, _P(ULONG_PTR)]),
        "DeactivateActCtx": (_BOOL, [_DWORD, ULONG_PTR]),
        "ReleaseActCtx": (None, [wintypes.HANDLE]),
    },
)

gdi32 = _Library(
    "gdi32",
    {
        "CreateFontIndirectW": (wintypes.HFONT, [_P(LOGFONTW)]),
        "DeleteObject": (_BOOL, [wintypes.HGDIOBJ]),
        "SelectObject": (wintypes.HGDIOBJ, [wintypes.HDC, wintypes.HGDIOBJ]),
        "GetTextExtentPoint32W": (_BOOL, [wintypes.HDC, wintypes.LPCWSTR, _INT, _P(wintypes.SIZE)]),
    },
)

comdlg32 = _Library(
    "comdlg32",
    {
        "GetOpenFileNameW": (_BOOL, [_P(OPENFILENAMEW)]),
        "GetSaveFileNameW": (_BOOL, [_P(OPENFILENAMEW)]),
        "ChooseColorW": (_BOOL, [_P(CHOOSECOLORW)]),
        "ChooseFontW": (_BOOL, [_P(CHOOSEFONTW)]),
        "CommDlgExtendedError": (_DWORD, []),
    },
)

shell32 = _Library(
    "shell32",
    {
        "SHBrowseForFolderW": (ctypes.c_void_p, [_P(BROWSEINFOW)]),
        "SHGetPathFromIDListW": (_BOOL, [ctypes.c_void_p, wintypes.LPWSTR]),
    },
)

ole32 = _Library(
    "ole32",
    {
        "CoInitializeEx": (ctypes.c_long, [ctypes.c_void_p, _DWORD]),
        "CoTaskMemFree": (None, [ctypes.c_void_p]),
    },
)

uxtheme = _Library(
    "uxtheme",
    {"EnableThemeDialogTexture": (ctypes.c_long, [HWND, _DWORD])},
)

# comctl32 must only be touched after the activation context is active,
# otherwise Windows binds version 5 for the whole process.
comctl32 = _Library(
    "comctl32",
    {"InitCommonControlsEx": (_BOOL, [_P(INITCOMMONCONTROLSEX)])},
)


def last_error(what: str) -> OSError:
    """OSError for the last Win32 error of a failed call, with the call name attached."""
    error = ctypes.WinError(ctypes.get_last_error())  # type: ignore[attr-defined]
    error.add_note(f"while calling {what}")
    return error


def register_window_class(
    name: str, wndproc: Any, *, background: int | None = None, cursor: bool = True
) -> None:
    """Register a window class once; an already registered class is not an error."""
    wcex = WNDCLASSEXW()
    wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
    wcex.style = 0x0002 | 0x0001  # CS_HREDRAW | CS_VREDRAW
    wcex.lpfnWndProc = wndproc
    wcex.hInstance = kernel32.GetModuleHandleW(None)
    if cursor:
        wcex.hCursor = user32.LoadCursorW(None, IDC_ARROW)
    if background is not None:
        wcex.hbrBackground = background
    wcex.lpszClassName = name
    if not user32.RegisterClassExW(ctypes.byref(wcex)):
        if ctypes.get_last_error() != ERROR_CLASS_ALREADY_EXISTS:  # type: ignore[attr-defined]
            raise last_error("RegisterClassExW")
