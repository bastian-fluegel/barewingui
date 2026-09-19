"""
barewingui.constants
~~~~~~~~~~~~~~~~~~~~
Type-safe Win32 constants, window styles, control flags, and messages
represented as modern Python IntEnum and IntFlag structures.
"""

from __future__ import annotations

from enum import IntEnum, IntFlag


# ---------------------------------------------------------------------------
# Fenster-Stile (Window Styles)
# ---------------------------------------------------------------------------
class WindowStyle(IntFlag):
    OVERLAPPED = 0x00000000
    POPUP = 0x80000000
    CHILD = 0x40000000
    MINIMIZE = 0x20000000
    VISIBLE = 0x10000000
    DISABLED = 0x08000000
    CLIPSIBLINGS = 0x04000000
    CLIPCHILDREN = 0x02000000
    MAXIMIZE = 0x01000000
    CAPTION = 0x00C00000      # BORDER | DLGFRAME
    BORDER = 0x00800000
    DLGFRAME = 0x00400000
    VSCROLL = 0x00200000
    HSCROLL = 0x00100000
    SYSMENU = 0x00080000
    THICKFRAME = 0x00040000
    GROUP = 0x00020000
    TABSTOP = 0x00010000

    MINIMIZEBOX = 0x00020000
    MAXIMIZEBOX = 0x00010000

    # Häufige Kombinationen
    TILED = OVERLAPPED
    ICONIC = MINIMIZE
    SIZEBOX = THICKFRAME
    OVERLAPPEDWINDOW = (
        OVERLAPPED | CAPTION | SYSMENU | THICKFRAME | MINIMIZEBOX | MAXIMIZEBOX
    )
    POPUPWINDOW = POPUP | BORDER | SYSMENU
    CHILDWINDOW = CHILD


class WindowStyleEx(IntFlag):
    DLGMODALFRAME = 0x00000001
    NOPARENTNOTIFY = 0x00000004
    TOPMOST = 0x00000008
    ACCEPTFILES = 0x00000010
    TRANSPARENT = 0x00000020
    MDICHILD = 0x00000040
    TOOLWINDOW = 0x00000080
    WINDOWEDGE = 0x00000100
    CLIENTEDGE = 0x00000200
    CONTEXTHELP = 0x00000400
    RIGHT = 0x00001000
    RTLREADING = 0x00002000
    LEFTSCROLLBAR = 0x00004000
    CONTROLPARENT = 0x00010000
    STATICEDGE = 0x00020000
    APPWINDOW = 0x00040000
    LAYERED = 0x00080000
    NOINHERITLAYOUT = 0x00100000
    NOREDIRECTIONBITMAP = 0x00200000
    LAYOUTRTL = 0x00400000
    COMPOSITED = 0x02000000
    NOACTIVATE = 0x08000000

    OVERLAPPEDWINDOW = WINDOWEDGE | CLIENTEDGE
    PALETTEWINDOW = WINDOWEDGE | TOOLWINDOW | TOPMOST


# ---------------------------------------------------------------------------
# Windows Messages (WM_*)
# ---------------------------------------------------------------------------
class WM(IntEnum):
    NULL = 0x0000
    CREATE = 0x0001
    DESTROY = 0x0002
    MOVE = 0x0003
    SIZE = 0x0005
    ACTIVATE = 0x0006
    SETFOCUS = 0x0007
    KILLFOCUS = 0x0008
    ENABLE = 0x000A
    SETREDRAW = 0x000B
    SETTEXT = 0x000C
    GETTEXT = 0x000D
    GETTEXTLENGTH = 0x000E
    PAINT = 0x000F
    CLOSE = 0x0010
    QUERYENDSESSION = 0x0011
    QUIT = 0x0012
    ERASEBKGND = 0x0014
    SYSCOLORCHANGE = 0x0015
    SHOWWINDOW = 0x0018
    SETFONT = 0x0030
    GETFONT = 0x0031
    NOTIFY = 0x004E
    COMMAND = 0x0111
    SYSCOMMAND = 0x0112
    TIMER = 0x0113
    HSCROLL = 0x0114
    VSCROLL = 0x0115
    CTLCOLORMSGBOX = 0x0132
    CTLCOLOREDIT = 0x0133
    CTLCOLORLISTBOX = 0x0134
    CTLCOLORBTN = 0x0135
    CTLCOLORDLG = 0x0136
    CTLCOLORSCROLLBAR = 0x0137
    CTLCOLORSTATIC = 0x0138
    KEYDOWN = 0x0100
    KEYUP = 0x0101
    CHAR = 0x0102
    MOUSEMOVE = 0x0200
    LBUTTONDOWN = 0x0201
    LBUTTONUP = 0x0202
    LBUTTONDBLCLK = 0x0203
    RBUTTONDOWN = 0x0204
    RBUTTONUP = 0x0205
    RBUTTONDBLCLK = 0x0206
    MBUTTONDOWN = 0x0207
    MBUTTONUP = 0x0208
    MBUTTONDBLCLK = 0x0209
    MOUSEWHEEL = 0x020A
    DPICHANGED = 0x02E0
    USER = 0x0400


# ---------------------------------------------------------------------------
# Control-spezifische Stile
# ---------------------------------------------------------------------------
class ButtonStyle(IntFlag):
    PUSHBUTTON = 0x00000000
    DEFPUSHBUTTON = 0x00000001
    CHECKBOX = 0x00000002
    AUTOCHECKBOX = 0x00000003
    RADIOBUTTON = 0x00000004
    AUTORADIOBUTTON = 0x00000009
    GROUPBOX = 0x00000007
    AUTOTHREE_STATE = 0x0000000B
    LEFTTEXT = 0x00000020
    ICON = 0x00000040
    BITMAP = 0x00000080
    LEFT = 0x00000100
    RIGHT = 0x00000200
    CENTER = 0x00000300
    TOP = 0x00000400
    BOTTOM = 0x00000800
    VCENTER = 0x00000C00
    PUSHLIKE = 0x00001000
    MULTILINE = 0x00002000
    NOTIFY = 0x00004000
    FLAT = 0x00008000


class EditStyle(IntFlag):
    LEFT = 0x0000
    CENTER = 0x0001
    RIGHT = 0x0002
    MULTILINE = 0x0004
    UPPERCASE = 0x0008
    LOWERCASE = 0x0010
    PASSWORD = 0x0020
    AUTOVSCROLL = 0x0040
    AUTOHSCROLL = 0x0080
    NOHIDESEL = 0x0100
    OEMCONVERT = 0x0400
    READONLY = 0x0800
    WANTRETURN = 0x1000
    NUMBER = 0x2000


class StaticStyle(IntFlag):
    LEFT = 0x00000000
    CENTER = 0x00000001
    RIGHT = 0x00000002
    ICON = 0x00000003
    BLACKRECT = 0x00000004
    GRAYRECT = 0x00000005
    WHITERECT = 0x00000006
    BLACKFRAME = 0x00000007
    GRAYFRAME = 0x00000008
    WHITEFRAME = 0x00000009
    SIMPLE = 0x0000000B
    LEFTNOWORDWRAP = 0x0000000C
    OWNERDRAW = 0x0000000D
    BITMAP = 0x0000000E
    ENHMETAFILE = 0x0000000F
    ETCHEDHORZ = 0x00000010
    ETCHEDVERT = 0x00000011
    ETCHEDFRAME = 0x00000012
    NOPREFIX = 0x00000080
    NOTIFY = 0x00000100
    CENTERIMAGE = 0x00000200
    RIGHTJUST = 0x00000400
    SUNKEN = 0x00001000


# ---------------------------------------------------------------------------
# Edit Messages & Control Notifications
# ---------------------------------------------------------------------------
class EditMessage(IntEnum):
    SETSEL = 0x00B1
    GETSEL = 0x00B0
    GETLINE = 0x00C4
    LIMITTEXT = 0x00C5
    CANUNDO = 0x00C6
    UNDO = 0x00C7
    SETREADONLY = 0x00CF
    SETMARGINS = 0x00D3


EC_LEFTMARGIN = 0x0001
EC_RIGHTMARGIN = 0x0002


class ButtonNotification(IntEnum):
    CLICKED = 0
    PAINT = 1
    HILITE = 2
    UNHILITE = 3
    DISABLE = 4
    DOUBLECLICKED = 5
    SETFOCUS = 6
    KILLFOCUS = 7


class EditNotification(IntEnum):
    SETFOCUS = 0x0100
    KILLFOCUS = 0x0200
    CHANGE = 0x0300
    UPDATE = 0x0400
    ERRSPACE = 0x0500
    MAXTEXT = 0x0501
    HSCROLL = 0x0601
    VSCROLL = 0x0602


# ---------------------------------------------------------------------------
# Fenster-Operationen & Anzeige-Modi
# ---------------------------------------------------------------------------
class ShowWindowCmd(IntEnum):
    HIDE = 0
    SHOWNORMAL = 1
    SHOWMINIMIZED = 2
    SHOWMAXIMIZED = 3
    SHOWNOACTIVATE = 4
    SHOW = 5
    MINIMIZE = 6
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    RESTORE = 9
    SHOWDEFAULT = 10
    FORCEMINIMIZE = 11


class WindowLong(IntEnum):
    WNDPROC = -4
    HINSTANCE = -6
    HWNDPARENT = -8
    STYLE = -16
    EXSTYLE = -20
    USERDATA = -21
    ID = -12


class SysColor(IntEnum):
    SCROLLBAR = 0
    BACKGROUND = 1
    ACTIVECAPTION = 2
    INACTIVECAPTION = 3
    MENU = 4
    WINDOW = 5
    WINDOWFRAME = 6
    MENUTEXT = 7
    WINDOWTEXT = 8
    CAPTIONTEXT = 9
    ACTIVEBORDER = 10
    INACTIVEBORDER = 11
    APPWORKSPACE = 12
    HIGHLIGHT = 13
    HIGHLIGHTTEXT = 14
    BTNFACE = 15
    BTNSHADOW = 16
    GRAYTEXT = 17
    BTNTEXT = 18
    INACTIVECAPTIONTEXT = 19
    BTNHIGHLIGHT = 20


class StockObject(IntEnum):
    WHITE_BRUSH = 0
    LTGRAY_BRUSH = 1
    GRAY_BRUSH = 2
    DKGRAY_BRUSH = 3
    BLACK_BRUSH = 4
    NULL_BRUSH = 5
    HOLLOW_BRUSH = 5
    WHITE_PEN = 6
    BLACK_PEN = 7
    NULL_PEN = 8
    OEM_FIXED_FONT = 10
    ANSI_FIXED_FONT = 11
    ANSI_VAR_FONT = 12
    SYSTEM_FONT = 13
    DEVICE_DEFAULT_FONT = 14
    DEFAULT_PALETTE = 15
    SYSTEM_FIXED_FONT = 16
    DEFAULT_GUI_FONT = 17
    DC_BRUSH = 18
    DC_PEN = 19


class StandardID(IntEnum):
    OK = 1
    CANCEL = 2
    ABORT = 3
    RETRY = 4
    IGNORE = 5
    YES = 6
    NO = 7
    CLOSE = 8
    HELP = 9
    TRYAGAIN = 10
    CONTINUE = 11
    USER_FIRST = 1000