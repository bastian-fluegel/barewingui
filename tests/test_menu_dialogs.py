"""Menus, shortcuts, timers, modal windows and dialogs (Windows only)."""

import ctypes
import threading
import unittest
from ctypes import wintypes

from barewingui import (
    App,
    ContextMenu,
    Label,
    Menu,
    MenuBar,
    MenuItem,
    MenuSeparator,
    TextBox,
    Timer,
    VBox,
    Window,
    _api,
    input_box,
    message_box,
)
from winhelpers import WINDOWS, _user32

WM_COMMAND = 0x0111

if WINDOWS:
    _user32.GetMenu.argtypes = [wintypes.HWND]
    _user32.GetMenu.restype = ctypes.c_void_p
    _user32.GetMenuItemCount.argtypes = [ctypes.c_void_p]
    _user32.GetMenuItemCount.restype = ctypes.c_int
    _user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    _user32.FindWindowW.restype = wintypes.HWND
    _user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    _user32.TranslateAcceleratorW.argtypes = [wintypes.HWND, wintypes.HANDLE, ctypes.POINTER(wintypes.MSG)]
    _user32.TranslateAcceleratorW.restype = ctypes.c_int


def later(app, seconds, fn, *args):
    timer = threading.Timer(seconds, lambda: app.invoke(fn, *args))
    timer.daemon = True
    timer.start()
    return timer


@unittest.skipUnless(WINDOWS, "needs Windows")
class MenuTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def build(self, calls):
        with Window("menu", size=(300, 200)) as win:
            with MenuBar() as bar:
                with Menu("&File"):
                    self.open_item = MenuItem("&Open", shortcut="Ctrl+O", on_click=lambda: calls.append("open"))
                    MenuSeparator()
                    self.wrap = MenuItem("Wrap", checkable=True, checked=True, on_click=lambda: calls.append("wrap"))
                    self.gone = MenuItem("Disabled", enabled=False)
                with Menu("&Edit"):
                    with Menu("Sub"):
                        self.deep = MenuItem("deep", on_click=lambda: calls.append("deep"))
            with VBox():
                Label("content")
        return win, bar

    def test_menu_bar_structure_and_client_size(self):
        win, bar = self.build([])
        self.assertEqual(_user32.GetMenu(win.hwnd), bar._hmenu)
        self.assertEqual(_user32.GetMenuItemCount(bar._hmenu), 2)
        self.assertEqual(win.size, (300, 200))  # the menu bar does not eat client height

    def test_commands_reach_the_handlers(self):
        calls = []
        win, _ = self.build(calls)
        for item in (self.open_item, self.deep):
            _user32.SendMessageW(win.hwnd, WM_COMMAND, item._id, 0)
        self.assertEqual(calls, ["open", "deep"])

    def test_checkable_items_toggle(self):
        calls = []
        win, _ = self.build(calls)
        self.assertTrue(self.wrap.checked)
        _user32.SendMessageW(win.hwnd, WM_COMMAND, self.wrap._id, 0)
        self.assertFalse(self.wrap.checked)
        self.assertEqual(calls, ["wrap"])
        self.wrap.checked = True
        self.assertTrue(self.wrap.checked)

    def test_item_properties(self):
        win, _ = self.build([])
        self.open_item.text = "&Open file"
        self.assertEqual(self.open_item.text, "&Open file")
        self.gone.enabled = True
        self.assertTrue(self.gone.enabled)
        self.open_item.enabled = False
        self.assertFalse(self.open_item.enabled)

    def test_shortcuts_become_an_accelerator_table(self):
        calls = []
        win, _ = self.build(calls)
        self.assertTrue(win._haccel)
        win.add_shortcut("F5", lambda: calls.append("f5"))
        msg = wintypes.MSG()
        msg.hWnd, msg.message, msg.wParam, msg.lParam = win.hwnd, 0x0100, 0x74, 0  # WM_KEYDOWN F5
        self.assertTrue(_user32.TranslateAcceleratorW(win.hwnd, win._haccel, ctypes.byref(msg)))
        self.assertEqual(calls, ["f5"])
        with self.assertRaises(ValueError):
            win.add_shortcut("x", lambda: None)

    def test_misuse(self):
        from barewingui import LayoutError

        win, _ = self.build([])
        with self.assertRaises(LayoutError):
            with win:
                MenuBar()  # a second menu bar
        with Window("two") as other:
            with MenuBar():
                with self.assertRaises(LayoutError):
                    MenuItem("not in a menu")

    def test_context_menu_items_are_commands(self):
        calls = []
        with Window("ctx") as win:
            with ContextMenu() as menu:
                item = MenuItem("Copy", on_click=lambda: calls.append("copy"))
            with VBox():
                Label("x")
        win.context_menu = menu
        _user32.SendMessageW(win.hwnd, WM_COMMAND, item._id, 0)
        self.assertEqual(calls, ["copy"])


@unittest.skipUnless(WINDOWS, "needs Windows")
class TimerTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def test_repeating_timer(self):
        ticks = []
        win = Window("timer")
        clock = Timer(0.02, lambda: ticks.append(1))
        later(self.app, 0.5, win.close)
        self.app.run()
        self.assertGreaterEqual(len(ticks), 3)

    def test_one_shot_and_stop(self):
        ticks = []
        win = Window("timer")
        once = Timer(0.02, lambda: ticks.append("once"), repeat=False)
        stopped = Timer(0.02, lambda: ticks.append("never"), start=False)
        later(self.app, 0.4, win.close)
        self.app.run()
        self.assertEqual(ticks, ["once"])
        self.assertFalse(once.running)
        self.assertFalse(stopped.running)

    def test_stop_prevents_ticks(self):
        ticks = []
        win = Window("timer")
        clock = Timer(0.02, lambda: ticks.append(1))
        later(self.app, 0.15, clock.stop)
        later(self.app, 0.6, win.close)
        self.app.run()
        seen = len(ticks)
        self.assertGreater(seen, 0)
        self.assertLess(seen, 20)  # it stopped well before the window closed

    def test_error_in_a_tick_is_raised_by_run(self):
        Window("timer")
        Timer(0.02, lambda: 1 / 0)
        with self.assertRaises(ZeroDivisionError):
            self.app.run()

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            Timer(0)


@unittest.skipUnless(WINDOWS, "needs Windows")
class DialogTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def test_message_box_returns_the_pressed_button(self):
        title = "bwg-message-box-test"

        def close_it():
            hwnd = _user32.FindWindowW("#32770", title)
            if hwnd:
                _user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

        timer = threading.Timer(0.6, close_it)
        timer.start()
        try:
            self.assertEqual(message_box("hello", title), "ok")
        finally:
            timer.cancel()

    def test_message_box_validates_options(self):
        with self.assertRaises(ValueError):
            message_box("x", icon="smiley")
        with self.assertRaises(ValueError):
            message_box("x", buttons="maybe")

    def _dialog(self, title):
        return next(w for w in self.app._windows.values() if w.title == title)

    def test_input_box_returns_the_text(self):
        def drive():
            dialog = self._dialog("bwg-input")
            box = next(c for c in dialog._controls.values() if isinstance(c, TextBox))
            self.assertEqual(box.text, "preset")
            box.text = "typed"
            dialog.default_button.click()

        later(self.app, 0.4, drive)
        self.assertEqual(input_box("Name?", "bwg-input", "preset"), "typed")

    def test_input_box_cancel(self):
        later(self.app, 0.4, lambda: self._dialog("bwg-input").cancel_button.click())
        self.assertIsNone(input_box("Name?", "bwg-input"))

    def test_modal_dialog_blocks_the_parent(self):
        states = []
        with Window("parent") as parent:
            with VBox():
                Label("x")
        parent.show()

        def check():
            states.append(bool(_user32.IsWindowEnabled(parent.hwnd)))
            self._dialog("bwg-input").cancel_button.click()

        later(self.app, 0.4, check)
        self.assertIsNone(input_box("?", "bwg-input", parent=parent))
        self.assertEqual(states, [False])  # blocked while the dialog was open
        self.assertTrue(_user32.IsWindowEnabled(parent.hwnd))  # and free again afterwards


if __name__ == "__main__":
    unittest.main()
