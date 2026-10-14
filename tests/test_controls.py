"""Native control tests. They only run on Windows (CI: windows-latest)."""

import ctypes
import unittest

from barewingui import (
    App,
    Button,
    CheckBox,
    ComboBox,
    GroupBox,
    HBox,
    Label,
    ListBox,
    RadioButton,
    TextBox,
    VBox,
    Window,
)

from winhelpers import WINDOWS, _user32, rect_of

WM_COMMAND = 0x0111
WM_GETFONT = 0x0031
BM_CLICK = 0x00F5
EM_REPLACESEL = 0x00C2


def notify(window, control, code):
    """Deliver a notification to ``control`` the way its native parent would."""
    _user32.SendMessageW(window.hwnd, WM_COMMAND, (code << 16) | 100, control.hwnd)


@unittest.skipUnless(WINDOWS, "needs Windows")
class ControlTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    # -- buttons -------------------------------------------------------------
    def test_button_click_calls_handler(self):
        calls = []
        with Window("t") as win:
            with VBox():
                ok = Button("OK", on_click=lambda: calls.append("ctor"))
                ok.on_click(lambda: calls.append("second"))
        win.show()  # BM_CLICK is ignored while the window was never shown
        _user32.SendMessageW(ok.hwnd, BM_CLICK, 0, 0)
        self.assertEqual(calls, ["ctor", "second"])
        self.assertEqual(ok.text, "OK")
        ok.text = "Save"
        self.assertEqual(ok.text, "Save")

    def test_disabled_button_does_not_click(self):
        calls = []
        with Window("t"):
            with VBox():
                btn = Button("x", on_click=lambda: calls.append(1), enabled=False)
        self.assertFalse(_user32.IsWindowEnabled(btn.hwnd))
        btn.click()
        self.assertEqual(calls, [])
        btn.enabled = True
        self.assertTrue(_user32.IsWindowEnabled(btn.hwnd))

    def test_enter_in_a_text_box_clicks_the_default_button(self):
        calls = []
        with Window("t") as win:
            with VBox():
                TextBox()
                Button("Go", default=True, on_click=lambda: calls.append(1))
        _user32.SendMessageW(win.hwnd, WM_COMMAND, 1, 0)  # IDOK, as IsDialogMessage sends it
        self.assertEqual(calls, [1])

    def test_handler_error_is_raised_by_run(self):
        with Window("t") as win:
            with VBox():
                btn = Button("x", on_click=lambda: 1 / 0)
        self.app.invoke(lambda: _user32.SendMessageW(btn.hwnd, BM_CLICK, 0, 0))
        self.app.invoke(win.close)
        with self.assertRaises(ZeroDivisionError):
            self.app.run()

    # -- check boxes and radio buttons ---------------------------------------
    def test_checkbox_state_and_event(self):
        calls = []
        with Window("t") as win:
            with VBox():
                box = CheckBox("Remember", checked=True, on_change=lambda: calls.append(1))
        win.show()
        self.assertIs(box.checked, True)
        _user32.SendMessageW(box.hwnd, BM_CLICK, 0, 0)
        self.assertIs(box.checked, False)
        self.assertEqual(calls, [1])
        box.checked = True  # set by the program: no event
        self.assertEqual(calls, [1])

    def test_tristate_checkbox(self):
        with Window("t"):
            with VBox():
                box = CheckBox("Some", tristate=True, checked=None)
        self.assertIsNone(box.checked)
        box.checked = True
        self.assertIs(box.checked, True)

    def test_radio_groups(self):
        with Window("t") as win:
            with VBox():
                a = RadioButton("A", checked=True)
                b = RadioButton("B")
                Label("separator starts a new group")
                c = RadioButton("C", checked=True)
                d = RadioButton("D")
        win.show()
        self.assertTrue(a.checked and not b.checked and c.checked and not d.checked)
        _user32.SendMessageW(b.hwnd, BM_CLICK, 0, 0)
        self.assertTrue(b.checked)
        self.assertFalse(a.checked)
        self.assertTrue(c.checked)  # the other group is untouched
        _user32.SendMessageW(d.hwnd, BM_CLICK, 0, 0)
        self.assertTrue(d.checked and not c.checked)
        self.assertTrue(b.checked)

    # -- text ----------------------------------------------------------------
    def test_textbox_text_and_events(self):
        calls = []
        with Window("t"):
            with VBox():
                box = TextBox("hello", on_change=lambda: calls.append(box.text))
        self.assertEqual(box.text, "hello")
        box.text = "set by program"
        self.assertEqual(calls, [])  # programmatic changes are silent
        buf = ctypes.create_unicode_buffer("!")
        _user32.SendMessageW(box.hwnd, EM_REPLACESEL, 1, ctypes.addressof(buf))
        self.assertEqual(len(calls), 1)  # typed text: exactly one event
        self.assertIn("!", calls[0])

    def test_multiline_text_uses_plain_newlines(self):
        with Window("t"):
            with VBox():
                box = TextBox("a\nb", multiline=True)
        self.assertEqual(box.text, "a\nb")
        box.text = "x\r\ny\nz"
        self.assertEqual(box.text, "x\ny\nz")

    def test_password_and_placeholder_options(self):
        with Window("t"):
            with VBox():
                secret = TextBox(password=True)
                hint = TextBox(placeholder="name")
        self.assertEqual(hint.placeholder, "name")
        secret.text = "pw"
        self.assertEqual(secret.text, "pw")
        with Window("t2"):
            with VBox():
                with self.assertRaises(ValueError):
                    TextBox(multiline=True, password=True)

    # -- lists ---------------------------------------------------------------
    def test_combobox_items_and_selection(self):
        calls = []
        with Window("t") as win:
            with VBox():
                combo = ComboBox(["one", "two", "three"], selected=1, on_change=lambda: calls.append(combo.selected))
        self.assertEqual(combo.items, ("one", "two", "three"))
        self.assertEqual((combo.selected_index, combo.selected, combo.text), (1, "two", "two"))
        combo.selected = "three"
        self.assertEqual(combo.selected_index, 2)
        self.assertEqual(calls, [])  # by program: silent
        notify(win, combo, 1)  # CBN_SELCHANGE from the native control
        self.assertEqual(calls, ["three"])
        combo.selected_index = None
        self.assertIsNone(combo.selected)
        combo.add("four")
        combo.insert(0, "zero")
        self.assertEqual(combo.items[0], "zero")
        combo.remove(0)
        combo.clear()
        self.assertEqual(len(combo), 0)

    def test_editable_combobox_text(self):
        with Window("t"):
            with VBox():
                combo = ComboBox(["a"], editable=True)
        combo.text = "free text"
        self.assertEqual(combo.text, "free text")

    def test_listbox_single_and_multi_selection(self):
        calls = []
        with Window("t") as win:
            with VBox():
                single = ListBox(["a", "b", "c"], on_activate=lambda: calls.append("open"))
                multi = ListBox(["a", "b", "c", "d"], multi=True)
        single.selected_index = 2
        self.assertEqual((single.selected, single.selected_indices), ("c", (2,)))
        notify(win, single, 2)  # LBN_DBLCLK
        self.assertEqual(calls, ["open"])
        multi.selected_indices = [0, 3]
        self.assertEqual(multi.selected_indices, (0, 3))
        self.assertEqual(multi.selected_items, ("a", "d"))
        with self.assertRaises(IndexError):
            single.selected_index = 9

    # -- font, layout --------------------------------------------------------
    def test_controls_use_the_system_font(self):
        from barewingui._font import font_for_dpi

        with Window("t") as win:
            with VBox():
                label = Label("x")
        win.show()
        # GDI handles only have 32 significant bits; SendMessage returns them sign-extended
        got = _user32.SendMessageW(label.hwnd, WM_GETFONT, 0, 0) & 0xFFFFFFFF
        self.assertEqual(got, font_for_dpi(win.dpi) & 0xFFFFFFFF)

    def test_controls_are_laid_out(self):
        with Window("t", size=(400, 300)) as win:
            with VBox(padding=10, gap=8):
                label = Label("Name:")
                box = TextBox()
                with HBox(justify="end"):
                    ok = Button("OK")
                    cancel = Button("Cancel")
        win.show()
        scale = win.scale
        client_w = win._client_px()[0]
        self.assertEqual(rect_of(box).right - rect_of(box).left, client_w - 2 * scale.px(10))
        self.assertGreaterEqual(rect_of(ok).bottom - rect_of(ok).top, scale.px(23))
        self.assertGreaterEqual(rect_of(ok).right - rect_of(ok).left, scale.px(75))
        self.assertGreater(rect_of(cancel).left, rect_of(ok).left)
        self.assertGreater(rect_of(ok).left, rect_of(label).left)  # pushed right by justify="end"
        self.assertGreater(rect_of(box).top, rect_of(label).top)

    def test_hidden_control_leaves_the_layout(self):
        with Window("t", size=(300, 200)) as win:
            with VBox(padding=0, gap=10):
                first = Label("first")
                middle = Label("middle")
                last = Label("last")
        win.show()
        before = rect_of(last).top
        middle.visible = False
        self.assertFalse(_user32.IsWindowVisible(middle.hwnd))
        self.assertLess(rect_of(last).top, before)
        self.assertGreater(first.hwnd, 0)

    def test_group_box_contains_its_children(self):
        with Window("t", size=(400, 300)) as win:
            with VBox(padding=10):
                with GroupBox("Options") as group:
                    inside = CheckBox("Inside")
                outside = Label("Outside")
        win.show()
        g, i, o = rect_of(group._hwnd), rect_of(inside), rect_of(outside)
        self.assertTrue(g.left < i.left and i.right <= g.right)
        self.assertTrue(g.top < i.top and i.bottom <= g.bottom)
        self.assertGreaterEqual(o.top, g.bottom)

    def test_min_window_size_follows_content(self):
        with Window("t", size=(100, 100)) as win:
            with VBox(padding=10):
                Button("A fairly long button caption", min_width=300)
        win.show()
        need = win._root.min_size(win.scale)
        self.assertGreaterEqual(need.w, win.scale.px(300) + 2 * win.scale.px(10))


if __name__ == "__main__":
    unittest.main()
