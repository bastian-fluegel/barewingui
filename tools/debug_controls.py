"""Prints where every control of an example window really is (Windows only).

    python tools/debug_controls.py examples/03_settings.py
"""

import ctypes
import importlib.util
import sys
import threading
from ctypes import wintypes
from pathlib import Path

from barewingui import App

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]


def describe(win):
    print(f"window dpi={win.dpi} size={win.size}")
    items = [(c.hwnd, type(c).__name__) for c in win._controls.values()]
    for page in (getattr(c, "pages", ()) for c in win._controls.values()):
        items += [(p._page_hwnd, "TabPage:" + p.title) for p in page]
    for hwnd, name in items:
        rc = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rc))
        parent = user32.GetParent(hwnd)
        print(f"{name:18} hwnd={hwnd:#x} parent={parent or 0:#x} visible={bool(user32.IsWindowVisible(hwnd))} "
              f"rect=({rc.left},{rc.top},{rc.right - rc.left}x{rc.bottom - rc.top})")


def main(path):
    app = App()
    spec = importlib.util.spec_from_file_location("example", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    win = module.build()

    def report():
        describe(win)
        win.close()

    timer = threading.Timer(1.5, lambda: app.invoke(report))
    timer.daemon = True
    timer.start()
    app.run()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
