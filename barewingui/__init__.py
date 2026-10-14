"""
barewingui
~~~~~~~~~~
Native Win32 GUIs for Python without dependencies.

Work in progress on the way to 0.2.0 (beta): the core, the layout engine and
windows and the standard controls are in place; common controls and dialogs are being ported (see docs/ZIELBILD.md).
"""

from __future__ import annotations

from barewingui.app import App
from barewingui.dpi import Scale
from barewingui.controls import (
    Button,
    CheckBox,
    ComboBox,
    DatePicker,
    GroupBox,
    Label,
    ListBox,
    ProgressBar,
    RadioButton,
    Slider,
    SpinBox,
    StatusBar,
    TextBox,
    TextInput,
    TimePicker,
)
from barewingui.errors import BareWinGUIError, LayoutError, PlatformError
from barewingui.events import Event
from barewingui.layout import Flex, HBox, Rect, Size, Spacer, Stack, VBox
from barewingui.window import Window

__version__ = "0.2.0.dev0"

__all__ = [
    "App",
    "BareWinGUIError",
    "Button",
    "CheckBox",
    "ComboBox",
    "DatePicker",
    "Event",
    "GroupBox",
    "Label",
    "ListBox",
    "ProgressBar",
    "RadioButton",
    "Slider",
    "SpinBox",
    "StatusBar",
    "TextBox",
    "TextInput",
    "TimePicker",
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
