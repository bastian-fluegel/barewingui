"""
barewingui
~~~~~~~~~~
Deterministisches, abhängigkeitsfreies Win32-GUI-Framework für Python.
"""

from __future__ import annotations

from barewingui.constants import (
    ButtonNotification,
    ButtonStyle,
    EditMessage,
    EditNotification,
    EditStyle,
    ShowWindowCmd,
    StaticStyle,
    WindowStyle,
    WindowStyleEx,
    WM,
)
from barewingui.controls import (
    Button,
    CheckBox,
    Control,
    Label,
    RadioButton,
    TextInput,
)
from barewingui.core import Application
from barewingui.layout import Box, HBox, VBox
from barewingui.window import Window

__version__ = "0.1.0"

__all__ = [
    "Application",
    "Button",
    "ButtonNotification",
    "ButtonStyle",
    "CheckBox",
    "Control",
    "EditMessage",
    "EditNotification",
    "EditStyle",
    "Label",
    "RadioButton",
    "ShowWindowCmd",
    "StaticStyle",
    "TextInput",
    "Window",
    "WindowStyle",
    "WindowStyleEx",
    "WM",
    "__version__",
    "Box",
    "HBox",
    "VBox",
]