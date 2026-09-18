"""
barewingui.constants
~~~~~~~~~~~~~~~~~~~~
Native Win32 window, extended, dialog, and control style flags,
sowie Windows Messages, MessageBox-, Common-Dialog- und Shell-Flags.
"""

from enum import IntEnum, IntFlag


# ---------------------------------------------------------------------------
# Windows Messages (WM_*) - Diskrete Nachrichten-IDs
# ---------------------------------------------------------------------------
class WindowsMessage(IntEnum):
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
    QUIT = 0x0012
    ERASEBKGND = 0x0014
    SHOWWINDOW = 0x0018
    ACTIVATEAPP = 0x001C

    # Tastatur
    KEYDOWN = 0x0100
    KEYUP = 0x0101
    CHAR = 0x0102

    # Steuerung & Benachrichtigungen
    COMMAND = 0x0111
    SYSCOMMAND = 0x0112
    TIMER = 0x0113
    HSCROLL = 0x0114
    VSCROLL = 0x0115
    NOTIFY = 0x004E

    # Maus
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


# ---------------------------------------------------------------------------
# MessageBox Flags (MB_*)
# ---------------------------------------------------------------------------
class MessageBoxStyle(IntFlag):
    # Schaltflächen
    OK = 0x00000000
    OKCANCEL = 0x00000001
    ABORTRETRYIGNORE = 0x00000002
    YESNOCANCEL = 0x00000003
    YESNO = 0x00000004
    RETRYCANCEL = 0x00000005
    CANCELTRYCONTINUE = 0x00000006

    # Symbole
    ICONHAND = 0x00000010
    ICONSTOP = 0x00000010
    ICONERROR = 0x00000010
    ICONQUESTION = 0x00000020
    ICONEXCLAMATION = 0x00000030
    ICONWARNING = 0x00000030
    ICONASTERISK = 0x00000040
    ICONINFORMATION = 0x00000040

    # Standard-Schaltfläche (Fokus)
    DEFBUTTON1 = 0x00000000
    DEFBUTTON2 = 0x00000100
    DEFBUTTON3 = 0x00000200
    DEFBUTTON4 = 0x00000300

    # Modalität
    APPLMODAL = 0x00000000
    SYSTEMMODAL = 0x00001000
    TASKMODAL = 0x00002000

    # Zusätzliche Optionen
    SETFOREGROUND = 0x00010000
    TOPMOST = 0x00040000


# ---------------------------------------------------------------------------
# MessageBox Rückgabewerte (ID*)
# ---------------------------------------------------------------------------
class MessageBoxResult(IntEnum):
    OK = 1
    CANCEL = 2
    ABORT = 3
    RETRY = 4
    IGNORE = 5
    YES = 6
    NO = 7
    TRYAGAIN = 10
    CONTINUE = 11


# ---------------------------------------------------------------------------
# Datei-Dialog Flags (OFN_* für GetOpenFileName / GetSaveFileName)
# ---------------------------------------------------------------------------
class OpenFileNameFlag(IntFlag):
    NONE = 0x00000000
    READONLY = 0x00000001
    OVERWRITEPROMPT = 0x00000002
    HIDEREADONLY = 0x00000004
    NOCHANGEDIR = 0x00000008
    SHOWHELP = 0x00000010
    NOVALIDATE = 0x00000100
    ALLOWMULTISELECT = 0x00000200
    EXTENSIONDIFFERENT = 0x00000400
    PATHMUSTEXIST = 0x00000800
    FILEMUSTEXIST = 0x00001000
    CREATEPROMPT = 0x00002000
    SHAREAWARE = 0x00004000
    NOREADONLYRETURN = 0x00008000
    NOTESTFILECREATE = 0x00010000
    NONETWORKBUTTON = 0x00020000
    NOLONGNAMES = 0x00040000
    EXPLORER = 0x00080000
    NODEREFERENCELINKS = 0x00100000
    LONGNAMES = 0x00200000
    ENABLESIZING = 0x00800000
    DONTADDTORECENT = 0x02000000
    FORCESHOWHIDDEN = 0x10000000


# ---------------------------------------------------------------------------
# Ordnerauswahl Flags (BIF_* für SHBrowseForFolder)
# ---------------------------------------------------------------------------
class BrowseInfoFlag(IntFlag):
    NONE = 0x00000000
    RETURNONLYFSDIRS = 0x00000001
    DONTGOBELOWDOMAIN = 0x00000002
    STATUSTEXT = 0x00000004
    RETURNFSANCESTORS = 0x00000008
    EDITBOX = 0x00000010
    VALIDATE = 0x00000020
    NEWDIALOGSTYLE = 0x00000040
    USENEWUI = 0x00000040 | 0x00000010
    BROWSEINCLUDEURLS = 0x00000080
    UAHINT = 0x00000100
    NONEWFOLDERBUTTON = 0x00000200
    NOTRANSLATETARGETS = 0x00000400
    BROWSEFORCOMPUTER = 0x00001000
    BROWSEFORPRINTER = 0x00002000
    BROWSEINCLUDEFILES = 0x00004000
    SHAREABLE = 0x00008000
    BROWSEFILEJUNCTIONS = 0x00010000


# ---------------------------------------------------------------------------
# Window Styles (WS_*)
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
    CAPTION = 0x00C00000
    BORDER = 0x00800000
    DLGFRAME = 0x00400000
    VSCROLL = 0x00200000
    HSCROLL = 0x00100000
    SYSMENU = 0x00080000
    THICKFRAME = 0x00040000
    SIZEBOX = 0x00040000
    GROUP = 0x00020000
    TABSTOP = 0x00010000
    MINIMIZEBOX = 0x00020000
    MAXIMIZEBOX = 0x00010000
    TILED = 0x00000000

    # Zusammengesetzte Standardstile
    OVERLAPPEDWINDOW = 0x00CF0000
    TILEDWINDOW = 0x00CF0000
    POPUPWINDOW = 0x80880000


# ---------------------------------------------------------------------------
# Dialog Styles (DS_*)
# ---------------------------------------------------------------------------
class DialogStyle(IntFlag):
    MODALFRAME = 0x00000080
    SETFOREGROUND = 0x00000200
    CONTEXTHELP = 0x00002000


# ---------------------------------------------------------------------------
# Extended Window Styles (WS_EX_*)
# ---------------------------------------------------------------------------
class WindowExStyle(IntFlag):
    NONE = 0x00000000
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
    LEFT = 0x00000000
    RTLREADING = 0x00002000
    LTRREADING = 0x00000000
    LEFTSCROLLBAR = 0x00004000
    RIGHTSCROLLBAR = 0x00000000
    CONTROLPARENT = 0x00010000
    STATICEDGE = 0x00020000
    APPWINDOW = 0x00040000
    LAYERED = 0x00080000
    NOINHERITLAYOUT = 0x00100000
    NOREDIRECTIONBITMAP = 0x00200000
    LAYOUTRTL = 0x00400000
    COMPOSITED = 0x02000000
    NOACTIVATE = 0x08000000

    # Zusammengesetzte Extended Styles
    OVERLAPPEDWINDOW = 0x00000300
    PALETTEWINDOW = 0x00000188


# ---------------------------------------------------------------------------
# Button / Checkbox / Radio Styles (BS_*)
# ---------------------------------------------------------------------------
class ButtonStyle(IntFlag):
    PUSHBUTTON = 0x00000000
    DEFPUSHBUTTON = 0x00000001
    CHECKBOX = 0x00000002
    AUTOCHECKBOX = 0x00000003
    RADIOBUTTON = 0x00000004
    THREE_STATE = 0x00000005
    AUTO3STATE = 0x00000006
    GROUPBOX = 0x00000007
    AUTORADIOBUTTON = 0x00000009
    RIGHTBUTTON = 0x00000020
    ICON = 0x00000040
    BITMAP = 0x00000080
    LEFT = 0x00000100
    RIGHT = 0x00000200
    CENTER = 0x00000300
    TOP = 0x00000400
    BOTTOM = 0x00000800
    PUSHLIKE = 0x00001000
    MULTILINE = 0x00002000
    NOTIFY = 0x00004000
    FLAT = 0x00008000
    VCENTER = 0x00000C00


# ---------------------------------------------------------------------------
# Combo Box Styles (CBS_*)
# ---------------------------------------------------------------------------
class ComboStyle(IntFlag):
    SIMPLE = 0x0001
    DROPDOWN = 0x0002
    DROPDOWNLIST = 0x0003
    AUTOHSCROLL = 0x0040
    OEMCONVERT = 0x0080
    SORT = 0x0100
    NOINTEGRALHEIGHT = 0x0400
    DISABLENOSCROLL = 0x0800
    UPPERCASE = 0x2000
    LOWERCASE = 0x4000


# ---------------------------------------------------------------------------
# List Box Styles (LBS_*)
# ---------------------------------------------------------------------------
class ListBoxStyle(IntFlag):
    NOTIFY = 0x0001
    SORT = 0x0002
    USETABSTOPS = 0x0080
    NOINTEGRALHEIGHT = 0x0100
    DISABLENOSCROLL = 0x1000
    NOSEL = 0x4000
    STANDARD = 0x00A00003


# ---------------------------------------------------------------------------
# Edit / Input Styles (ES_*)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Progress Bar Styles (PBS_*)
# ---------------------------------------------------------------------------
class ProgressStyle(IntFlag):
    SMOOTH = 0x01
    VERTICAL = 0x04
    MARQUEE = 0x08
    SMOOTHREVERSE = 0x10


# ---------------------------------------------------------------------------
# Up-Down / Spin Control Styles (UDS_*)
# ---------------------------------------------------------------------------
class UpDownStyle(IntFlag):
    WRAP = 0x01
    ALIGNRIGHT = 0x04
    ALIGNLEFT = 0x08
    ARROWKEYS = 0x20
    HORZ = 0x40
    NOTHOUSANDS = 0x80


# ---------------------------------------------------------------------------
# Static / Label / Icon Styles (SS_*)
# ---------------------------------------------------------------------------
class StaticStyle(IntFlag):
    LEFT = 0x0000
    CENTER = 0x0001
    RIGHT = 0x0002
    BLACKRECT = 0x04
    GRAYRECT = 0x05
    WHITERECT = 0x06
    BLACKFRAME = 0x07
    GRAYFRAME = 0x08
    WHITEFRAME = 0x09
    SIMPLE = 0x000B
    LEFTNOWORDWRAP = 0x000C
    ETCHEDHORZ = 0x10
    ETCHEDVERT = 0x11
    ETCHEDFRAME = 0x12
    NOPREFIX = 0x0080
    NOTIFY = 0x0100
    CENTERIMAGE = 0x0200
    RIGHTJUST = 0x0400
    SUNKEN = 0x1000


# ---------------------------------------------------------------------------
# Tab Control Styles (TCS_*)
# ---------------------------------------------------------------------------
class TabStyle(IntFlag):
    TABS = 0x0000
    SINGLELINE = 0x0000
    RIGHTJUSTIFY = 0x0000
    RAGGEDRIGHT = 0x0800
    SCROLLOPPOSITE = 0x0001
    BOTTOM = 0x0002
    RIGHT = 0x0002
    MULTISELECT = 0x0004
    FLATBUTTONS = 0x0008
    FORCEICONLEFT = 0x0010
    FORCELABELLEFT = 0x0020
    HOTTRACK = 0x0040
    VERTICAL = 0x0080
    BUTTONS = 0x0100
    MULTILINE = 0x0200
    FIXEDWIDTH = 0x0400
    FOCUSONBUTTONDOWN = 0x1000
    OWNERDRAWFIXED = 0x2000
    TOOLTIPS = 0x4000
    FOCUSNEVER = 0x8000


# ---------------------------------------------------------------------------
# AVI Clip Styles (ACS_*)
# ---------------------------------------------------------------------------
class AviStyle(IntFlag):
    CENTER = 0x01
    TRANSPARENT = 0x02
    AUTOPLAY = 0x04
    NONTRANSPARENT = 0x10


# ---------------------------------------------------------------------------
# DateTimePicker Styles (DTS_*)
# ---------------------------------------------------------------------------
class DateTimeStyle(IntFlag):
    SHORTDATEFORMAT = 0x00
    UPDOWN = 0x01
    SHOWNONE = 0x02
    LONGDATEFORMAT = 0x04
    TIMEFORMAT = 0x09
    RIGHTALIGN = 0x20


# ---------------------------------------------------------------------------
# Month Calendar Styles (MCS_*)
# ---------------------------------------------------------------------------
class MonthCalStyle(IntFlag):
    WEEKNUMBERS = 0x04
    NOTODAYCIRCLE = 0x08
    NOTODAY = 0x10


# ---------------------------------------------------------------------------
# TreeView Styles (TVS_*)
# ---------------------------------------------------------------------------
class TreeViewStyle(IntFlag):
    HASBUTTONS = 0x0001
    HASLINES = 0x0002
    LINESATROOT = 0x0004
    DISABLEDRAGDROP = 0x0010
    SHOWSELALWAYS = 0x0020
    RTLREADING = 0x0040
    NOTOOLTIPS = 0x0080
    CHECKBOXES = 0x0100
    TRACKSELECT = 0x0200
    SINGLEEXPAND = 0x0400
    FULLROWSELECT = 0x1000
    NOSCROLL = 0x2000
    NONEVENHEIGHT = 0x4000


# ---------------------------------------------------------------------------
# Slider / Trackbar Styles (TBS_*)
# ---------------------------------------------------------------------------
class SliderStyle(IntFlag):
    HORZ = 0x0000
    BOTTOM = 0x0000
    RIGHT = 0x0000
    AUTOTICKS = 0x0001
    VERT = 0x0002
    TOP = 0x0004
    LEFT = 0x0004
    BOTH = 0x0008
    NOTICKS = 0x0010
    NOTHUMB = 0x0080


# ---------------------------------------------------------------------------
# ListView Styles (LVS_*)
# ---------------------------------------------------------------------------
class ListViewStyle(IntFlag):
    ICON = 0x0000
    REPORT = 0x0001
    SMALLICON = 0x0002
    LIST = 0x0003
    SINGLESEL = 0x0004
    SHOWSELALWAYS = 0x0008
    SORTASCENDING = 0x0010
    SORTDESCENDING = 0x0020
    NOLABELWRAP = 0x0080
    EDITLABELS = 0x0200
    NOCOLUMNHEADER = 0x4000
    NOSORTHEADER = 0x8000


# ---------------------------------------------------------------------------
# ListView Extended Styles (LVS_EX_*)
# ---------------------------------------------------------------------------
class ListViewExStyle(IntFlag):
    GRIDLINES = 0x00000001
    SUBITEMIMAGES = 0x00000002
    CHECKBOXES = 0x00000004
    TRACKSELECT = 0x00000008
    HEADERDRAGDROP = 0x00000010
    FULLROWSELECT = 0x00000020
    FLATSB = 0x00000100
    INFOTIP = 0x00000400
    MULTIWORKAREAS = 0x00002000
    BORDERSELECT = 0x00008000
    DOUBLEBUFFER = 0x00010000
    SNAPTOGRID = 0x00080000