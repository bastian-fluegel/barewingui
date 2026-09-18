"""
Demonstriert responsive Steuerelement-Anordnung via VBox und HBox.
Das Fenster passt alle Elemente beim Skalieren automatisch und flackerfrei an.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui import Button, HBox, Label, TextInput, VBox, Window


def main() -> int:
    win = Window(title="BareWinGUI Responsive Box Layout", width=520, height=400)

    # Haupt-Layout: Vertikaler Container mit 16px Padding
    root = VBox(padding=16, spacing=12)

    root.add(Label(win, text="Target Hostname / IP-Adresse:", size=(0, 20)))
    root.add(TextInput(win, text="10.0.0.1", size=(0, 26)))

    root.add(Label(win, text="Erweiterte Notizen & Protokoll:", size=(0, 20)))

    # Multiline-Input nimmt den verbleibenden Raum flexibel ein (stretch=1)
    root.add(TextInput(win, multiline=True), stretch=1)

    # padding=0 verhindert, dass von den 32px Höhe oben und unten je 10px abgezogen werden
    action_bar = HBox(spacing=10, padding=0, fixed_size=32)
    action_bar.add_stretch()

    btn_cancel = Button(win, text="Abbrechen", size=(110, 32), on_click=win.close)
    btn_start = Button(win, text="Scan starten", size=(120, 32), default=True)

    action_bar.add(btn_cancel)
    action_bar.add(btn_start)

    root.add(action_bar)

    # Layout mit Fenster verdrahten (übernimmt automatisches Resizing)
    root.attach(win)

    return win.run()


if __name__ == "__main__":
    sys.exit(main())