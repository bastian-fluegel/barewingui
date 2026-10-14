"""Common controls (comctl32): progress bar, slider, spin box, status bar, pickers."""

import ctypes
import datetime as dt
import unittest

from barewingui import (
    App,
    DatePicker,
    Label,
    ProgressBar,
    Slider,
    SpinBox,
    StatusBar,
    TextBox,
    TimePicker,
    VBox,
    Window,
    _api,
)
from winhelpers import WINDOWS, _user32, rect_of

WM_USER = 0x0400
UDM_GETBUDDY = WM_USER + 106
UDM_GETPOS32 = WM_USER + 114
EM_REPLACESEL = 0x00C2
TB_LINEDOWN = 1


def send_notify(window, control, code):
    """Deliver a WM_NOTIFY from ``control`` to its window the way comctl32 does."""
    header = _api.NMHDR()
    header.hwndFrom = control.hwnd
    header.idFrom = 100
    header.code = code
    return _user32.SendMessageW(window.hwnd, _api.WM_NOTIFY, 100, ctypes.addressof(header))


@unittest.skipUnless(WINDOWS, "needs Windows")
class CommonControlTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def test_progress_bar(self):
        with Window("t"):
            with VBox():
                bar = ProgressBar(25, maximum=200)
                busy = ProgressBar(indeterminate=True)
        self.assertEqual(bar.value, 25)
        bar.value = 500  # clamped
        self.assertEqual(bar.value, 200)
        bar.set_range(0, 10)
        bar.value = 7
        self.assertEqual((bar.value, bar.minimum, bar.maximum), (7, 0, 10))
        bar.state = "error"
        with self.assertRaises(ValueError):
            bar.state = "weird"
        self.assertTrue(busy.hwnd)
        with self.assertRaises(ValueError):
            ProgressBar(minimum=5, maximum=5)

    def test_slider(self):
        calls = []
        with Window("t") as win:
            with VBox():
                slider = Slider(30, minimum=10, maximum=60, on_change=lambda: calls.append(slider.value))
                vertical = Slider(vertical=True)
        self.assertEqual(slider.value, 30)
        slider.value = 100
        self.assertEqual(slider.value, 60)
        slider.value = 40
        self.assertEqual(calls, [])  # by program: silent
        _user32.SendMessageW(win.hwnd, _api.WM_HSCROLL, TB_LINEDOWN, slider.hwnd)
        self.assertEqual(calls, [40])
        _user32.SendMessageW(win.hwnd, _api.WM_HSCROLL, _api.TB_ENDTRACK, slider.hwnd)
        self.assertEqual(calls, [40])  # the closing notification is not an extra change
        horizontal_size = slider.natural_size(win.scale)
        vertical_size = vertical.natural_size(win.scale)
        self.assertEqual((horizontal_size.w, horizontal_size.h), (vertical_size.h, vertical_size.w))

    def test_spin_box(self):
        calls = []
        with Window("t", size=(300, 200)) as win:
            with VBox(padding=10):
                spin = SpinBox(5, minimum=0, maximum=20, on_change=lambda: calls.append(spin.value))
                negative = SpinBox(-3, minimum=-10, maximum=10)
        win.show()
        self.assertEqual(spin.value, 5)
        self.assertEqual(negative.value, -3)
        self.assertEqual(_user32.SendMessageW(spin._updown, UDM_GETBUDDY, 0, 0), spin.hwnd)
        self.assertEqual(_user32.SendMessageW(spin._updown, UDM_GETPOS32, 0, 0), 5)
        spin.value = 99  # clamped
        self.assertEqual(spin.value, 20)
        self.assertEqual(calls, [])
        buf = ctypes.create_unicode_buffer("1")
        _user32.SendMessageW(spin.hwnd, EM_REPLACESEL, 1, ctypes.addressof(buf))
        self.assertEqual(len(calls), 1)  # typed by the user
        rc = rect_of(spin)
        self.assertGreater(rc.right - rc.left, 0)

    def test_spin_box_rejects_empty_range(self):
        with Window("t"):
            with VBox():
                with self.assertRaises(ValueError):
                    SpinBox(minimum=3, maximum=3)

    def test_status_bar_takes_the_bottom_strip(self):
        with Window("t", size=(400, 300)) as win:
            status = StatusBar(parts=[150, None])
            with VBox(padding=0):
                Label("top")
                body = TextBox(multiline=True, grow=1)
        win.show()
        status.text = "Ready"
        status[1] = "3 items"
        self.assertEqual((status.text, status[1], len(status)), ("Ready", "3 items", 2))
        self.assertIs(win.status_bar, status)
        s, b = rect_of(status), rect_of(body)
        self.assertGreater(s.bottom - s.top, 0)
        self.assertLessEqual(b.bottom, s.top)  # the content ends where the status bar starts
        with self.assertRaises(IndexError):
            status[5] = "x"

    def test_status_bar_parts_validation(self):
        with Window("t"):
            with self.assertRaises(ValueError):
                StatusBar(parts=[None, 100])

    def test_date_picker(self):
        calls = []
        with Window("t") as win:
            with VBox():
                picker = DatePicker(dt.date(2024, 2, 29), on_change=lambda: calls.append(1))
        self.assertEqual(picker.value, dt.date(2024, 2, 29))
        picker.value = dt.date(2030, 12, 31)
        self.assertEqual(picker.value, dt.date(2030, 12, 31))
        self.assertEqual(calls, [])
        send_notify(win, picker, _api.DTN_DATETIMECHANGE)
        self.assertEqual(calls, [1])

    def test_time_picker(self):
        with Window("t"):
            with VBox():
                picker = TimePicker(dt.time(13, 45, 10))
        self.assertEqual(picker.value, dt.time(13, 45, 10))
        picker.value = dt.time(6, 5, 4)
        self.assertEqual(picker.value, dt.time(6, 5, 4))


if __name__ == "__main__":
    unittest.main()
