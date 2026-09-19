"""
Minimales Beispiel für BareWinGUI:
Demonstriert Fenster-Lifecycle, Steuerelemente, State-Handling und Callback-Routing.
"""

from __future__ import annotations

import os
import sys

# Projekt-Root zur Laufzeit auffindbar machen (auch ohne editable pip install)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui import Button, CheckBox, Label, RadioButton, TextInput, Window


def main() -> int:
    # 1. Hauptfenster mit zentrierter Standardgröße erzeugen
    win = Window(
        title="BareWinGUI Showcase — Zero-Dependency Win32",
        width=480,
        height=380,
    )

    # 2. Beschriftung & Eingabefeld
    Label(
        parent=win,
        text="Geben Sie einen Text oder Befehl ein:",
        pos=(25, 20),
        size=(350, 20),
    )

    input_field = TextInput(
        parent=win,
        text="Audit-Prüfung initialisieren",
        pos=(25, 45),
        size=(410, 32),
    )

    status_label = Label(
        parent=win,
        text="Status: Bereit",
        pos=(25, 85),
        size=(410, 20),
    )

    # 3. Interaktions-Button
    def on_submit_clicked() -> None:
        entered_text = input_field.text.strip()
        if entered_text:
            status_label.text = f"Ausgeführt: '{entered_text}'"
        else:
            status_label.text = "Eingabefeld darf nicht leer sein!"

    Button(
        parent=win,
        text="Befehl ausführen",
        pos=(25, 120),
        size=(150, 32),
        on_click=on_submit_clicked,
        default=True,
    )

    def on_clear_clicked() -> None:
        input_field.clear()
        status_label.text = "Status: Eingabe geleert"
        input_field.focus()

    Button(
        parent=win,
        text="Zurücksetzen",
        pos=(185, 120),
        size=(120, 32),
        on_click=on_clear_clicked,
    )

    # 4. CheckBox & RadioButtons
    def on_checkbox_toggled(is_checked: bool) -> None:
        status_label.text = f"Protokollierung: {'Aktiv' if is_checked else 'Inaktiv'}"

    chk = CheckBox(
        parent=win,
        text="Erweitertes Logging aktivieren",
        pos=(25, 180),
        size=(260, 32),
        checked=True,
        on_click=on_checkbox_toggled,
    )

    Label(
        parent=win,
        text="Modus wählen:",
        pos=(25, 220),
        size=(200, 20),
    )

    def on_mode_changed(mode_name: str) -> None:
        status_label.text = f"Ausgewählter Modus: {mode_name}"

    RadioButton(
        parent=win,
        text="Standard-Triage",
        pos=(25, 245),
        size=(180, 32),
        checked=True,
        group_start=True,
        on_click=lambda: on_mode_changed("Standard-Triage"),
    )

    RadioButton(
        parent=win,
        text="Forensische Tiefenanalyse",
        pos=(25, 270),
        size=(220, 32),
        on_click=lambda: on_mode_changed("Forensische Tiefenanalyse"),
    )

    # 5. Lifecycle-Hook: Fenster schließt sauber
    def on_window_close() -> bool:
        print("[BareWinGUI] Fenster wird geschlossen, Ressourcen werden freigegeben.")
        return True

    win.on_close = on_window_close

    # 6. Message-Loop starten
    return win.run()


if __name__ == "__main__":
    sys.exit(main())