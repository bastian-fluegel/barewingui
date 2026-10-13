"""Control checks that need no Windows (misuse is reported before any Win32 call)."""

import unittest

from barewingui import Button, ComboBox, GroupBox, Label, LayoutError, TextBox, VBox


class OutsideWindowTests(unittest.TestCase):
    def test_control_outside_any_container(self):
        for factory in (Label, Button, TextBox, ComboBox, GroupBox):
            with self.assertRaises(LayoutError, msg=factory.__name__):
                factory()

    def test_control_in_a_box_without_window(self):
        with VBox():
            with self.assertRaises(LayoutError):
                Button("x")


if __name__ == "__main__":
    unittest.main()
