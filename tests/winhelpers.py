"""Helpers shared by the Windows-only tests (importable on every platform)."""

import ctypes
import sys
from ctypes import wintypes

WINDOWS = sys.platform == "win32"
_user32 = None

if WINDOWS:
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    _user32.GetWindowRect.restype = wintypes.BOOL
    _user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    _user32.SendMessageW.restype = ctypes.c_ssize_t
    _user32.IsWindowEnabled.argtypes = [wintypes.HWND]
    _user32.IsWindowVisible.argtypes = [wintypes.HWND]


def rect_of(control_or_hwnd):
    """Screen rectangle of a control (or HWND)."""
    hwnd = getattr(control_or_hwnd, "hwnd", control_or_hwnd)
    rc = wintypes.RECT()
    assert _user32.GetWindowRect(hwnd, ctypes.byref(rc))
    return rc
