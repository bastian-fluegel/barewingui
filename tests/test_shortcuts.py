import unittest

from barewingui.shortcuts import Shortcut, parse_shortcut


class ShortcutTests(unittest.TestCase):
    def test_letters_and_modifiers(self):
        s = parse_shortcut("ctrl+shift+s")
        self.assertEqual((s.vk, s.ctrl, s.shift, s.alt), (0x53, True, True, False))
        self.assertEqual(s.label, "Ctrl+Shift+S")

    def test_function_and_named_keys(self):
        self.assertEqual(parse_shortcut("F5").vk, 0x74)
        self.assertEqual(parse_shortcut("F12").label, "F12")
        self.assertEqual(parse_shortcut("Alt+Left").label, "Alt+Left")
        self.assertEqual(parse_shortcut("Del").vk, 0x2E)
        self.assertEqual(parse_shortcut("Strg+Entf"), Shortcut(0x2E, ctrl=True))

    def test_digits(self):
        self.assertEqual(parse_shortcut("Ctrl+1").vk, ord("1"))

    def test_spaces_are_ignored(self):
        self.assertEqual(parse_shortcut(" Ctrl + O "), parse_shortcut("Ctrl+O"))

    def test_invalid_shortcuts(self):
        for bad in ("", "Ctrl+", "Ctrl", "S", "Shift+S", "Ctrl+Ctrl+S", "Ctrl+A+B", "Ctrl+Ö", "F25"):
            with self.assertRaises(ValueError, msg=bad):
                parse_shortcut(bad)

    def test_non_string(self):
        with self.assertRaises(ValueError):
            parse_shortcut(None)


if __name__ == "__main__":
    unittest.main()
