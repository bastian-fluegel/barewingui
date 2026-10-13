"""Smoke tests for the Win32 layer. They only run on Windows (CI: windows-latest)."""

import ctypes
import sys
import threading
import unittest
from ctypes import wintypes

from barewingui import App, HBox, LayoutError, Rect, Size, VBox, Window
from barewingui._layout_core import Flex, adopt

WINDOWS = sys.platform == "win32"


class Probe:
    """A pure-Python layout node that records where it was placed."""

    def __init__(self, w, h, **flex):
        self.flex = Flex(**flex)
        self.visible = True
        self._size = Size(w, h)
        self.rect = None
        adopt(self)

    def natural_size(self, scale):
        return self._size

    def min_size(self, scale):
        return self._size

    def place(self, rect, scale):
        self.rect = rect


def later(app, seconds, fn, *args):
    """Run ``fn`` on the UI thread after ``seconds``, triggered from a timer thread."""
    timer = threading.Timer(seconds, lambda: app.invoke(fn, *args))
    timer.daemon = True
    timer.start()
    return timer


@unittest.skipUnless(WINDOWS, "needs Windows")
class WindowsTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def test_common_controls_v6_is_active(self):
        class DLLVERSIONINFO(ctypes.Structure):
            _fields_ = [(n, wintypes.DWORD) for n in
                        ("cbSize", "dwMajorVersion", "dwMinorVersion", "dwBuildNumber", "dwPlatformID")]

        info = DLLVERSIONINFO()
        info.cbSize = ctypes.sizeof(DLLVERSIONINFO)
        self.assertEqual(ctypes.WinDLL("comctl32").DllGetVersion(ctypes.byref(info)), 0)
        self.assertGreaterEqual(info.dwMajorVersion, 6)

    def test_run_ends_when_last_window_closes(self):
        win = Window("close me", size=(300, 200))
        later(self.app, 0.2, win.close)
        self.assertEqual(self.app.run(), 0)
        self.assertFalse(win.alive)

    def test_app_is_a_singleton_until_run_ends(self):
        self.assertIs(App(), self.app)
        win = Window("x")
        later(self.app, 0.1, win.close)
        self.app.run()
        with self.assertRaises(RuntimeError):
            self.app.invoke(print)
        self.assertIsNot(App(), self.app)

    def test_client_size_is_in_dips(self):
        win = Window("size", size=(300, 200))
        self.assertGreaterEqual(win.dpi, 96)
        scale = win.scale
        self.assertEqual(win._client_px(), (scale.px(300), scale.px(200)))
        self.assertEqual(win.size, (300, 200))

    def test_call_returns_the_result_from_the_ui_thread(self):
        win = Window("call")
        seen = {}

        def worker():
            seen["thread"] = self.app.call(threading.get_ident)
            self.app.call(win.close)

        thread = threading.Thread(target=worker)
        thread.start()
        self.app.run()
        thread.join(5)
        self.assertEqual(seen["thread"], threading.get_ident())

    def test_error_in_a_callback_is_raised_by_run(self):
        Window("boom")
        self.app.invoke(lambda: 1 / 0)
        with self.assertRaises(ZeroDivisionError):
            self.app.run()

    def test_error_handler_keeps_the_loop_running(self):
        seen = []
        self.app.on_error = seen.append
        win = Window("handled")
        self.app.invoke(lambda: 1 / 0)
        later(self.app, 0.3, win.close)
        self.assertEqual(self.app.run(), 0)
        self.assertEqual(len(seen), 1)
        self.assertIsInstance(seen[0], ZeroDivisionError)

    def test_on_close_can_veto(self):
        calls = []
        win = Window("veto")
        win.on_close = lambda: calls.append(1) or len(calls) > 1
        later(self.app, 0.2, win.close)
        later(self.app, 0.4, win.close)
        self.app.run()
        self.assertEqual(len(calls), 2)

    def test_layout_is_applied_when_shown_and_on_resize(self):
        with Window("layout", size=(300, 200)) as win:
            with VBox(padding=10, gap=8):
                a = Probe(50, 20)
                b = Probe(50, 20, grow=1)
        scale = win.scale
        pad, gap, h_a = scale.px(10), scale.px(8), scale.px(20)
        cw, ch = win._client_px()
        later(self.app, 0.2, setattr, win, "size", (400, 300))
        snapshot = {}
        later(self.app, 0.5, lambda: snapshot.update(a=a.rect, b=b.rect))
        later(self.app, 0.6, win.close)

        # first layout happens in run() -> show(); check it before the resize arrives
        first = {}
        later(self.app, 0.1, lambda: first.update(a=a.rect, b=b.rect))
        self.app.run()

        self.assertEqual(first["a"], Rect(pad, pad, cw - 2 * pad, h_a))
        self.assertEqual(first["b"], Rect(pad, pad + h_a + gap, cw - 2 * pad, ch - 2 * pad - h_a - gap))
        cw2, ch2 = scale.px(400), scale.px(300)
        self.assertEqual(snapshot["b"], Rect(pad, pad + h_a + gap, cw2 - 2 * pad, ch2 - 2 * pad - h_a - gap))

    def test_a_window_takes_one_root_container(self):
        with Window("root") as win:
            VBox()
            with self.assertRaises(LayoutError):
                HBox()
        self.assertIsNotNone(win._root)


if __name__ == "__main__":
    unittest.main()
