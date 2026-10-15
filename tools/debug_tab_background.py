"""Shows the same tab content with different page backgrounds (Windows only).

    python tools/debug_tab_background.py

Look at every tab: are the group frames and the rows behind check boxes and
radio buttons the same colour as the page? Take a screenshot of each tab.
"""

from barewingui import (
    App, CheckBox, ComboBox, GroupBox, Label, RadioButton, TabControl, TabPage, VBox, Window,
)
from barewingui._api import uxtheme

# (tab title, flags for EnableThemeDialogTexture)
VARIANTS = [
    ("A: tab texture (now)", 6),   # ETDT_ENABLE | ETDT_USETABTEXTURE
    ("B: no texture", 1),          # ETDT_DISABLE: plain dialog colour
    ("C: enable only", 2),         # ETDT_ENABLE
]


def build():
    pages = []
    with Window("Page background variants", size=(460, 360), resizable=False) as win:
        with VBox(padding=12):
            with TabControl(grow=1):
                for title, _ in VARIANTS:
                    with TabPage(title) as page:
                        with GroupBox("Language"):
                            ComboBox(["English", "Deutsch"], selected=0)
                        with GroupBox("Options"):
                            CheckBox("Restore the last session", checked=True)
                            CheckBox("Check for updates")
                            RadioButton("Normal", checked=True)
                        Label("A label outside of any group")
                    pages.append(page)
    for page, (_, flags) in zip(pages, VARIANTS):
        uxtheme.EnableThemeDialogTexture(page._page_hwnd, flags)
    return win


if __name__ == "__main__":
    app = App()
    build()
    app.run()
