from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui import Button, ComboBox, HBox, Label, ListBox, VBox, Window


def main() -> int:
    win = Window(title="Netzwerk & Forensik Profile", width=460, height=380)

    root = VBox(padding=14, spacing=10)

    # 1. Dropdown mit Segoe UI
    root.add(Label(win, text="Zielprofil auswählen:"))
    profile_combo = ComboBox(
        win,
        items=["SCADA / OT Leitstelle", "Active Directory DC", "Web-Proxy DMZ"],
        size=(0, 32),
    )
    root.add(profile_combo)

    # 2. Status-Anzeige
    status = Label(win, text="Gewählt: SCADA / OT Leitstelle")
    root.add(status)

    def on_profile_changed(idx: int, val: str) -> None:
        status.text = f"Profil geändert: [{idx}] {val}"

    profile_combo.on_change = on_profile_changed

    # 3. ListBox mit flexiblem Höhenanteil
    root.add(Label(win, text="Gefundene Artefakte:"))
    artefacts = ListBox(
        win,
        items=[
            "Security EventLog ID 4624 (Erfolgreiche Anmeldung)",
            "Sysmon Event ID 1 (Prozesserstellung: powershell.exe)",
            "Prefetch: MIMIKATZ.EXE-B1398B43.pf",
            "MFT Record $LogFile Anomalie entdeckt",
        ],
    )
    root.add(artefacts, stretch=1)

    # 4. Button-Leiste mit padding=0 gegen Clipping
    bottom_bar = HBox(spacing=8, padding=0, fixed_size=32)
    bottom_bar.add_stretch()
    bottom_bar.add(Button(win, text="Schließen", size=(100, 32), on_click=win.close))
    root.add(bottom_bar)

    root.attach(win)
    return win.run()


if __name__ == "__main__":
    sys.exit(main())
