import sys
import unittest

import barewingui
from barewingui import App, PlatformError


@unittest.skipIf(sys.platform == "win32", "checks the behaviour on non-Windows systems")
class NonWindowsTests(unittest.TestCase):
    def test_package_imports_everywhere(self):
        self.assertTrue(barewingui.__version__)

    def test_creating_an_app_fails_clearly(self):
        with self.assertRaises(PlatformError):
            App()
        # a failed start must not leave a half-initialised singleton behind
        with self.assertRaises(PlatformError):
            App()


if __name__ == "__main__":
    unittest.main()
