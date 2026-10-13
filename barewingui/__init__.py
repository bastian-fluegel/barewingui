"""
barewingui
~~~~~~~~~~
Native Win32 GUIs for Python without dependencies.

Work in progress on the way to 0.2.0 (beta): the core, the layout engine and
windows are in place; controls and dialogs are being ported (see docs/ZIELBILD.md).
"""

from __future__ import annotations

from barewingui.app import App
from barewingui.dpi import Scale
from barewingui.errors import BareWinGUIError, LayoutError, PlatformError
from barewingui.layout import Flex, HBox, Rect, Size, Spacer, Stack, VBox
from barewingui.window import Window

__version__ = "0.2.0.dev0"

__all__ = [
    "App",
    "BareWinGUIError",
    "Flex",
    "HBox",
    "LayoutError",
    "PlatformError",
    "Rect",
    "Scale",
    "Size",
    "Spacer",
    "Stack",
    "VBox",
    "Window",
    "__version__",
]
