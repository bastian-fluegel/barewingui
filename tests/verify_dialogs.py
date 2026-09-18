"""
tests/verify_dialogs.py
~~~~~~~~~~~~~~~~~~~~~~~
Interaktive Testsuite für alle nativen Win32-Systemdialoge.
Prüft Modalfunktion, Rückgabewerte und korrekte Parent-Window-Bindung.
"""

from __future__ import annotations

import os
import sys

# Projekt-Root zur Laufzeit auffindbar machen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui import Button, HBox, Label, TextInput, VBox, Window
from barewingui.dialogs import (
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
    warning_box,
)


def main() -> int:
    win = Window(title="BareWinGUI — Dialog Verification Suite", width=620, height=540)
    root = VBox(padding=16, spacing=10)

    root.add(Label(win, text="Wählen Sie einen Dialog zum Testen aus:"))

    # 1. Message-Boxen (Info, Warning, Error)
    row_msg = HBox(spacing=8, padding=0, fixed_size=32)
    row_msg.add(
        Button(
            win,
            text="1. Info",
            size=(90, 32),
            on_click=lambda: (
                info_box("Systembereit für forensische Erfassung.", title="Audit-Info", parent=win),
                log("Info-Box bestätigt."),
            ),
        )
    )
    row_msg.add(
        Button(
            win,
            text="2. Warnung",
            size=(100, 32),
            on_click=lambda: (
                warning_box("Netzwerkverbindung instabil.", title="Warnung", parent=win),
                log("Warnungs-Box bestätigt."),
            ),
        )
    )
    row_msg.add(
        Button(
            win,
            text="3. Fehler",
            size=(90, 32),
            on_click=lambda: (
                error_box("Zugriff auf SAM-Registry verweigert.", title="Fehler", parent=win),
                log("Fehler-Box bestätigt."),
            ),
        )
    )
    root.add(row_msg)

    # 2. Entscheidungen & Custom MessageBox
    row_decide = HBox(spacing=8, padding=0, fixed_size=32)
    row_decide.add(
        Button(
            win,
            text="4. Confirm (Ja/Nein)",
            size=(150, 32),
            on_click=lambda: log(
                f"Confirm-Box Ergebnis: {confirm_box('Vorgang jetzt starten?', title='Frage', parent=win)}"
            ),
        )
    )
    row_decide.add(
        Button(
            win,
            text="5. Message (Retry/Cancel)",
            size=(170, 32),
            on_click=lambda: log(
                f"Custom MessageBox Ergebnis: '{message_box('Host antwortet nicht.', title='Retry?', buttons='retry_cancel', icon='warning', parent=win)}'"
            ),
        )
    )
    root.add(row_decide)

    # 3. Modale Eingabeboxen (Text / Passwort)
    row_input = HBox(spacing=8, padding=0, fixed_size=32)
    row_input.add(
        Button(
            win,
            text="6a. Input (Text)",
            size=(140, 32),
            on_click=lambda: log(
                f"Input-Box Text: '{input_box('Server-Adresse eingeben:', default='192.168.1.1', parent=win)}'"
            ),
        )
    )
    row_input.add(
        Button(
            win,
            text="6b. Input (Passwort)",
            size=(150, 32),
            on_click=lambda: log(
                f"Input-Box Passwort: '{input_box('Root-Passwort:', password=True, parent=win)}'"
            ),
        )
    )
    root.add(row_input)

    # 4. Datei- & Ordnerpicker
    row_files = HBox(spacing=8, padding=0, fixed_size=32)
    row_files.add(
        Button(
            win,
            text="7. Datei öffnen",
            size=(120, 32),
            on_click=lambda: log(
                f"Open File: '{open_file(title='Log-Datei wählen', filters=[('Logdateien', '*.log;*.txt')], parent=win)}'"
            ),
        )
    )
    row_files.add(
        Button(
            win,
            text="8. Datei speichern",
            size=(130, 32),
            on_click=lambda: log(
                f"Save File: '{save_file(title='Bericht sichern', default_name='report.txt', default_ext='txt', parent=win)}'"
            ),
        )
    )
    row_files.add(
        Button(
            win,
            text="9. Ordner wählen",
            size=(130, 32),
            on_click=lambda: log(
                f"Ordner ausgewählt: '{pick_folder(title='Zielordner für Dump', parent=win)}'"
            ),
        )
    )
    root.add(row_files)

    # 5. Farbwähler & Schriftartdialog
    row_pickers = HBox(spacing=8, padding=0, fixed_size=32)
    row_pickers.add(
        Button(
            win,
            text="10. Farbe wählen",
            size=(130, 32),
            on_click=lambda: log(
                f"Farbe (RGB): {choose_color(initial_color=(0, 120, 215), parent=win)}"
            ),
        )
    )
    row_pickers.add(
        Button(
            win,
            text="11. Schriftart wählen",
            size=(140, 32),
            on_click=lambda: log(f"Schriftart: {choose_font(parent=win)}"),
        )
    )
    root.add(row_pickers)

    # Protokollanzeige
    root.add(Label(win, text="Ergebnisprotokoll:"))
    log_view = TextInput(win, multiline=True, readonly=True)
    root.add(log_view, stretch=1)

    log_history: list[str] = ["=== BareWinGUI Dialog-Testsuite gestartet ==="]
    log_view.text = "\r\n".join(log_history)

    def log(msg: str) -> None:
        print(f"[TEST] {msg}")
        log_history.append(msg)
        log_view.text = "\r\n".join(log_history)

    root.attach(win)
    return win.run()


if __name__ == "__main__":
    sys.exit(main())