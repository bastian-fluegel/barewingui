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
    ListView,
    ProgressBar,
    RadioButton,
    Slider,
    SpinBox,
    StatusBar,
    TabControl,
    TabPage,
    TextBox,
    TextInput,
    TimePicker,
    TreeNode,
    TreeView,
)
from barewingui.dialogs import (
    FontChoice,
    ask_ok_cancel,
    ask_yes_no,
    choose_color,
    choose_font,
    input_box,
    message_box,
    open_file,
    pick_folder,
    save_file,
    show_error,
    show_info,
    show_warning,
)
from barewingui.errors import BareWinGUIError, LayoutError, PlatformError
from barewingui.events import Event
from barewingui.menu import ContextMenu, Menu, MenuBar, MenuItem, MenuSeparator
from barewingui.layout import Flex, HBox, Rect, Size, Spacer, Stack, VBox
from barewingui.timer import Timer
from barewingui.window import Window

__version__ = "0.2.0.dev0"

__all__ = [
    "App",
    "FontChoice",
    "ask_ok_cancel",
    "ask_yes_no",
    "choose_color",
    "choose_font",
    "input_box",
    "message_box",
    "open_file",
    "pick_folder",
    "save_file",
    "show_error",
    "show_info",
    "show_warning",
    "ContextMenu",
    "Menu",
    "MenuBar",
    "MenuItem",
    "MenuSeparator",
    "Timer",
    "BareWinGUIError",
    "Button",
    "CheckBox",
    "ComboBox",
    "DatePicker",
    "Event",
    "GroupBox",
    "Label",
    "ListBox",
    "ListView",
    "ProgressBar",
    "RadioButton",
    "Slider",
    "SpinBox",
    "StatusBar",
    "TabControl",
    "TabPage",
    "TextBox",
    "TextInput",
    "TimePicker",
    "TreeNode",
    "TreeView",
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
