"""
barewingui.types
~~~~~~~~~~~~~~~~
Pointer-adaptive Win32 ABI bindings, C-structures, and DLL prototypes.
Guarantees full 32-bit and 64-bit compatibility without external dependencies.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

# ---------------------------------------------------------------------------
# DLL-Instanzen
# ---------------------------------------------------------------------------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

try:
    comctl32 = ctypes.windll.comctl32
except OSError:
    comctl32 = None

# ---------------------------------------------------------------------------
# Pointer-adaptive Basis-Typen (32-Bit: 4 Bytes, 64-Bit: 8 Bytes)
# ---------------------------------------------------------------------------
LONG_PTR = ctypes.c_ssize_t
UINT_PTR = ctypes.c_size_t
LRESULT = ctypes.c_ssize_t
WPARAM = wintypes.WPARAM
LPARAM = wintypes.LPARAM

COLORREF = wintypes.DWORD
HGDIOBJ = wintypes.HANDLE
HBRUSH = wintypes.HBRUSH
HFONT = wintypes.HANDLE

# ---------------------------------------------------------------------------
# Callback-Definitionen
# ---------------------------------------------------------------------------
WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT,
    wintypes.HWND,
    wintypes.UINT,
    WPARAM,
    LPARAM,
)

# ---------------------------------------------------------------------------
# Win32 C-Strukturen
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

class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", wintypes.BYTE * 32),
    ]

class CREATESTRUCTW(ctypes.Structure):
    _fields_ = [
        ("lpCreateParams", wintypes.LPVOID),
        ("hInstance", wintypes.HINSTANCE),
        ("hMenu", wintypes.HMENU),
        ("hwndParent", wintypes.HWND),
        ("cy", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("y", ctypes.c_int),
        ("x", ctypes.c_int),
        ("style", wintypes.LONG),
        ("lpszName", wintypes.LPCWSTR),
        ("lpszClass", wintypes.LPCWSTR),
        ("dwExStyle", wintypes.DWORD),
    ]

class INITCOMMONCONTROLSEX(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("dwICC", wintypes.DWORD),
    ]

# ---------------------------------------------------------------------------
# 32-Bit / 64-Bit Kompatibilitätsweiche für WindowLongPtr
# Unter 32-Bit exportiert user32.dll nur GetWindowLongW/SetWindowLongW.
# ---------------------------------------------------------------------------
if hasattr(user32, "SetWindowLongPtrW"):
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
    SetWindowLongPtrW.restype = LONG_PTR

    GetWindowLongPtrW = user32.GetWindowLongPtrW
    GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    GetWindowLongPtrW.restype = LONG_PTR
else:
    SetWindowLongPtrW = user32.SetWindowLongW
    SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
    SetWindowLongPtrW.restype = LONG_PTR

    GetWindowLongPtrW = user32.GetWindowLongW
    GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    GetWindowLongPtrW.restype = LONG_PTR

# ---------------------------------------------------------------------------
# USER32 Funktions-Signaturen
# ---------------------------------------------------------------------------
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT

user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype = wintypes.ATOM

user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND

user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL

user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL

user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.UpdateWindow.restype = wintypes.BOOL

user32.MoveWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.BOOL,
]
user32.MoveWindow.restype = wintypes.BOOL

user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT

user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.PostMessageW.restype = wintypes.BOOL

user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.SendMessageW.restype = LRESULT

user32.BeginPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
user32.BeginPaint.restype = wintypes.HDC

user32.EndPaint.argtypes = [wintypes.HWND, ctypes.POINTER(PAINTSTRUCT)]
user32.EndPaint.restype = wintypes.BOOL

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL

user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL

user32.InvalidateRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT), wintypes.BOOL]
user32.InvalidateRect.restype = wintypes.BOOL

user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadCursorW.restype = wintypes.HANDLE

user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int

user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND

user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
user32.EnableWindow.restype = wintypes.BOOL

user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL

user32.GetSysColorBrush.argtypes = [ctypes.c_int]
user32.GetSysColorBrush.restype = wintypes.HBRUSH

# High-DPI Awareness ab Windows 10 (Version 1703+)
if hasattr(user32, "SetProcessDpiAwarenessContext"):
    user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
    user32.SetProcessDpiAwarenessContext.restype = wintypes.BOOL

# ---------------------------------------------------------------------------
# KERNEL32 Funktions-Signaturen
# ---------------------------------------------------------------------------
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

kernel32.GetLastError.argtypes = []
kernel32.GetLastError.restype = wintypes.DWORD

# ---------------------------------------------------------------------------
# GDI32 Funktions-Signaturen
# ---------------------------------------------------------------------------
gdi32.GetStockObject.argtypes = [ctypes.c_int]
gdi32.GetStockObject.restype = HGDIOBJ

gdi32.DeleteObject.argtypes = [HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL

gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.SetBkMode.restype = ctypes.c_int

gdi32.CreateSolidBrush.argtypes = [COLORREF]
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH

gdi32.CreateFontW.argtypes = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
    wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
    wintypes.DWORD, wintypes.LPCWSTR
]
gdi32.CreateFontW.restype = HFONT

# ---------------------------------------------------------------------------
# COMCTL32 Funktions-Signaturen (Windows Common Controls v6)
# ---------------------------------------------------------------------------
if comctl32 and hasattr(comctl32, "InitCommonControlsEx"):
    comctl32.InitCommonControlsEx.argtypes = [ctypes.POINTER(INITCOMMONCONTROLSEX)]
    comctl32.InitCommonControlsEx.restype = wintypes.BOOL