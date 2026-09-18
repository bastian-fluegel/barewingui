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
    ComboBox,
    Control,
    Label,
    ListBox,
    RadioButton,
    TextInput,
)
from barewingui.core import Application
from barewingui.dialogs import (
    ask_yes_no,
    choose_color,
    choose_font,
    confirm_box,
    error_box,
    info_box,
    input_box,
    message_box,
    open_file,
    pick_folder,
    save_file,
    select_folder,
    warning_box,
)
from barewingui.layout import Box, HBox, VBox
from barewingui.window import Window

__version__ = "0.1.0"

__all__ = [
    "Application",
    "Button",
    "ButtonNotification",
    "ButtonStyle",
    "CheckBox",
    "ComboBox",
    "Control",
    "ListBox",
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
    "message_box",
    "info_box",
    "warning_box",
    "error_box",
    "confirm_box",
    "ask_yes_no",
    "input_box",
    "open_file",
    "save_file",
    "pick_folder",
    "select_folder",
    "choose_color",
    "choose_font",
]