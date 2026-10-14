"""Common controls (comctl32): progress bar, slider, spin box, status bar, pickers."""

import ctypes
from ctypes import wintypes
import datetime as dt
import unittest

from barewingui import (
    App,
    Button,
    CheckBox,
    DatePicker,
    GroupBox,
    Label,
    ListView,
    ProgressBar,
    Slider,
    SpinBox,
    StatusBar,
    TabControl,
    TabPage,
    TextBox,
    TimePicker,
    TreeView,
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


@unittest.skipUnless(WINDOWS, "needs Windows")
class ViewControlTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    # -- ListView ------------------------------------------------------------
    def test_list_view_rows_and_selection(self):
        calls = []
        with Window("t", size=(400, 300)) as win:
            with VBox():
                table = ListView(
                    ["Name", ("Size", 80)],
                    rows=[("a.txt", 10), ("b.txt",)],
                    on_select=lambda: calls.append(table.selected_index),
                    grow=1,
                )
        win.show()
        self.assertEqual(table.columns, ("Name", "Size"))
        self.assertEqual(table.rows, (("a.txt", "10"), ("b.txt", "")))
        self.assertEqual(table.add_row(["c.txt", "30"]), 2)
        table.set_cell(1, 1, 20)
        self.assertEqual(table.rows[1], ("b.txt", "20"))
        self.assertEqual(len(table), 3)
        table.selected_index = 2
        self.assertEqual((table.selected_index, table.selected_row), (2, ("c.txt", "30")))
        self.assertEqual(calls, [])  # by program: silent
        table.remove_row(0)
        self.assertEqual(table.rows[0][0], "b.txt")
        table.clear()
        self.assertEqual((len(table), table.selected_index), (0, None))
        with self.assertRaises(ValueError):
            table.add_row(["too", "many", "cells"])
        with self.assertRaises(IndexError):
            table.remove_row(5)

    def test_list_view_events_come_from_notifications(self):
        calls = []
        with Window("t") as win:
            with VBox():
                table = ListView(
                    ["A", "B"], rows=[("1", "2"), ("3", "4")],
                    on_select=lambda: calls.append("select"),
                    on_activate=lambda: calls.append("activate"),
                    on_column_click=lambda: calls.append(("column", table.clicked_column)),
                )
        item = _api.NMLISTVIEW()
        item.hdr.hwndFrom = table.hwnd
        item.hdr.code = _api.LVN_ITEMCHANGED
        item.uChanged, item.uOldState, item.uNewState = _api.LVIF_STATE, 0, _api.LVIS_SELECTED
        _user32.SendMessageW(win.hwnd, _api.WM_NOTIFY, 0, ctypes.addressof(item))
        item.hdr.code = _api.LVN_ITEMACTIVATE
        _user32.SendMessageW(win.hwnd, _api.WM_NOTIFY, 0, ctypes.addressof(item))
        item.hdr.code, item.iSubItem = _api.LVN_COLUMNCLICK, 1
        _user32.SendMessageW(win.hwnd, _api.WM_NOTIFY, 0, ctypes.addressof(item))
        self.assertEqual(calls, ["select", "activate", ("column", 1)])

    def test_list_view_multi_selection(self):
        with Window("t"):
            with VBox():
                table = ListView(["A"], rows=[(str(i),) for i in range(5)], multi=True)
                single = ListView(["A"], rows=[("x",), ("y",)])
        table.selected_indices = [1, 3]
        self.assertEqual(table.selected_indices, (1, 3))
        with self.assertRaises(ValueError):
            single.selected_indices = [0, 1]
        with self.assertRaises(ValueError):
            ListView([])

    # -- TreeView ------------------------------------------------------------
    def test_tree_view_nodes(self):
        with Window("t", size=(400, 300)) as win:
            with VBox():
                tree = TreeView(grow=1)
        win.show()
        root = tree.add("root", data=1)
        child = root.add("child", data=2)
        child.add("grandchild")
        self.assertEqual(tree.roots, (root,))
        self.assertEqual(root.children, (child,))
        self.assertIs(child.parent, root)
        child.text = "renamed"
        self.assertEqual(child.text, "renamed")
        root.expand()
        child.select()
        self.assertIs(tree.selected, child)
        child.remove()
        self.assertEqual(root.children, ())
        tree.clear()
        self.assertEqual(tree.roots, ())
        self.assertIsNone(tree.selected)

    def test_tree_view_lazy_loading(self):
        loaded = []

        def load():
            node = tree.event_node
            loaded.append(node.text)
            if not node.children:
                node.add("loaded child")

        with Window("t", size=(400, 300)) as win:
            with VBox():
                tree = TreeView(on_expand=load, grow=1)
        win.show()
        folder = tree.add("folder", has_children=True)
        folder.expand()
        self.assertEqual(loaded, ["folder"])
        self.assertEqual([c.text for c in folder.children], ["loaded child"])

    def test_tree_view_select_event(self):
        seen = []
        with Window("t", size=(400, 300)) as win:
            with VBox():
                tree = TreeView(on_select=lambda: seen.append(tree.event_node.text), grow=1)
        win.show()
        a = tree.add("a")
        b = tree.add("b")
        a.select()
        self.assertEqual(seen, [])  # by program: silent
        info = _api.NMTREEVIEWW()
        info.hdr.hwndFrom = tree.hwnd
        info.hdr.code = _api.TVN_SELCHANGEDW
        info.itemNew.hItem = b._handle
        _user32.SendMessageW(win.hwnd, _api.WM_NOTIFY, 0, ctypes.addressof(info))
        self.assertEqual(seen, ["b"])

    # -- Tabs ----------------------------------------------------------------
    def test_tab_control_pages(self):
        changed = []
        with Window("t", size=(500, 400)) as win:
            with VBox(padding=8):
                with TabControl(grow=1, on_change=lambda: changed.append(tabs.selected_index)) as tabs:
                    with TabPage("General") as general:
                        name = TextBox("x")
                        with GroupBox("Options") as group:
                            remember = CheckBox("Remember")
                    with TabPage("Advanced") as advanced:
                        Label("expert mode")
                        Button("Reset")
                Button("OK")
        win.show()
        self.assertEqual([p.title for p in tabs.pages], ["General", "Advanced"])
        self.assertEqual(tabs.selected_index, 0)
        self.assertTrue(_user32.IsWindowVisible(general._page_hwnd))
        self.assertFalse(_user32.IsWindowVisible(advanced._page_hwnd))
        self.assertTrue(_user32.IsWindowVisible(name.hwnd))
        tabs.selected_index = 1
        self.assertEqual(tabs.selected_page, advanced)
        self.assertFalse(_user32.IsWindowVisible(general._page_hwnd))
        self.assertTrue(_user32.IsWindowVisible(advanced._page_hwnd))
        self.assertFalse(_user32.IsWindowVisible(name.hwnd))
        self.assertEqual(changed, [])  # by program: no event
        header = _api.NMHDR()
        header.hwndFrom = tabs.hwnd
        header.code = _api.TCN_SELCHANGE
        tabs.selected_index = 0
        _user32.SendMessageW(win.hwnd, _api.WM_NOTIFY, 0, ctypes.addressof(header))
        self.assertEqual(changed, [0])
        # the page content sits inside the tab control
        t, g = rect_of(tabs), rect_of(general._page_hwnd)
        self.assertTrue(t.left <= g.left and g.right <= t.right)
        self.assertTrue(t.top < g.top and g.bottom <= t.bottom)
        n = rect_of(name)
        self.assertTrue(g.left <= n.left and n.right <= g.right)
        # z-order: the pages are above the tab control (else its body paints over them)
        _user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
        _user32.GetWindow.restype = wintypes.HWND
        above, node = [], _user32.GetWindow(tabs.hwnd, 3)  # GW_HWNDPREV
        while node:
            above.append(node)
            node = _user32.GetWindow(node, 3)
        self.assertIn(general._page_hwnd, above)
        self.assertIn(advanced._page_hwnd, above)
        # and inside the page the group frame is below the control it contains
        node, over_group = _user32.GetWindow(group._hwnd, 3), []
        while node:
            over_group.append(node)
            node = _user32.GetWindow(node, 3)
        self.assertIn(remember.hwnd, over_group)

    def test_tab_control_rules(self):
        with Window("t"):
            with VBox():
                with self.assertRaises(Exception):
                    TabPage("outside")
                with TabControl() as tabs:
                    with self.assertRaises(Exception):
                        Label("only pages are allowed here")
        self.assertEqual(tabs.pages, ())

    def test_tab_control_sets_the_minimum_window_size(self):
        with Window("t", size=(100, 100)) as win:
            with VBox():
                with TabControl():
                    with TabPage("One"):
                        Button("A wide button", min_width=250)
        win.show()
        need = win._root.min_size(win.scale)
        self.assertGreaterEqual(need.w, win.scale.px(250))


if __name__ == "__main__":
    unittest.main()
