"""
verify_dialogs.py
~~~~~~~~~~~~~~~~~
Härtetest für alle nativen Win32-Systemdialoge in barewingui.
Ohne Argumente: interaktive Suite. Mit unittest: reiner Import-/API-Check.
"""

from __future__ import annotations

import os
import sys
import unittest

# Projekt-Root zur Laufzeit auffindbar machen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    _build_filter_string,
)


_PUBLIC_DIALOG_NAMES = (
    "ask_yes_no",
    "choose_color",
    "choose_font",
    "confirm_box",
    "error_box",
    "info_box",
    "input_box",
    "message_box",
    "open_file",
    "pick_folder",
    "save_file",
    "select_folder",
    "warning_box",
)


class TestDialogExports(unittest.TestCase):
    """Prüft, dass jedes Dialogsymbol importierbar und aufrufbar ist."""

    def test_module_symbols(self) -> None:
        import barewingui.dialogs as dialogs

        for name in _PUBLIC_DIALOG_NAMES:
            self.assertTrue(hasattr(dialogs, name), f"dialogs.{name} fehlt")
            self.assertTrue(callable(getattr(dialogs, name)), f"dialogs.{name} ist nicht callable")

    def test_package_reexports(self) -> None:
        import barewingui as bw

        for name in _PUBLIC_DIALOG_NAMES:
            self.assertTrue(hasattr(bw, name), f"barewingui.{name} fehlt")
            self.assertTrue(callable(getattr(bw, name)))
            self.assertIn(name, bw.__all__)

    def test_aliases(self) -> None:
        self.assertIs(ask_yes_no, confirm_box)
        self.assertIs(select_folder, pick_folder)

    def test_filter_string_double_null(self) -> None:
        raw = _build_filter_string([("Python-Dateien (*.py)", "*.py")])
        self.assertTrue(raw.endswith("\0\0"))
        self.assertIn("Python-Dateien (*.py)", raw.split("\0"))
        self.assertIn("*.py", raw.split("\0"))


def run_dialog_suite() -> None:
    print("=" * 60)
    print(" BareWinGUI // Win32 Dialog Verification Suite")
    print("=" * 60)

    # 1. Universelle MessageBox
    print("\n[1/10] Teste message_box (Ja/Nein)...")
    res = message_box(
        "Funktioniert die MessageBox einwandfrei?",
        title="1. MessageBox Test",
        icon="question",
        buttons="yes_no",
    )
    print(f"  -> Ergebnis: {res}")

    # 2. Information
    print("\n[2/10] Teste info_box...")
    info_box("Native Informationsmeldung mit Segoe UI.", title="2. Info")
    print("  -> info_box geschlossen")

    # 3. Warnung
    print("\n[3/10] Teste warning_box...")
    warning_box("Dies ist eine Warnung.", title="3. Warnung")
    print("  -> warning_box geschlossen")

    # 4. Fehler
    print("\n[4/10] Teste error_box...")
    error_box("Dies ist eine Fehlermeldung.", title="4. Fehler")
    print("  -> error_box geschlossen")

    # 5. Bestätigung
    print("\n[5/10] Teste confirm_box / ask_yes_no...")
    confirmed = confirm_box("Fortfahren?", title="5. Bestätigung")
    print(f"  -> confirm_box: {confirmed}")

    # 6. InputBox
    print("\n[6/10] Teste input_box...")
    text_val = input_box(
        prompt="Gib einen Test-String für das native EDIT-Control ein:",
        title="6. InputBox Test",
        default="BareWinGUI Systemtest",
    )
    print(f"  -> Eingabe: {text_val!r}")

    # 7. Datei öffnen
    print("\n[7/10] Teste open_file...")
    opened = open_file(
        title="7. Datei zum Öffnen wählen",
        filters=[
            ("Python-Dateien (*.py)", "*.py"),
            ("Textdateien (*.txt)", "*.txt"),
        ],
    )
    print(f"  -> Gewählte Datei: {opened}")

    # 8. Datei speichern
    print("\n[8/10] Teste save_file...")
    saved = save_file(
        title="8. Zieldatei definieren",
        default_name="export_test.txt",
        default_ext="txt",
        filters=[("Textdokument (*.txt)", "*.txt")],
    )
    print(f"  -> Speicherpfad: {saved}")

    # 9. Ordner
    print("\n[9/10] Teste pick_folder / select_folder...")
    folder = select_folder(title="9. Basisverzeichnis auswählen")
    print(f"  -> Verzeichnis: {folder}")

    # 10. Farbe und Schrift
    print("\n[10/10] Teste choose_color und choose_font...")
    color = choose_color(initial_color=(255, 120, 0))
    if color:
        r, g, b = color
        print(f"  -> RGB: ({r}, {g}, {b}) | Hex: #{r:02X}{g:02X}{b:02X}")
    else:
        print("  -> Farbwahl abgebrochen")

    font = choose_font()
    if font:
        print(f"  -> Font: {font['name']}, {font['size']}pt, Bold={font['bold']}")
        print(f"  -> Stil: Kursiv={font['italic']}, Unterstrichen={font['underline']}, Farbe={font['color']}")
    else:
        print("  -> Schriftauswahl abgebrochen")

    print("\n" + "=" * 60)
    print(" Alle Dialog-Schnittstellen erfolgreich durchlaufen.")
    print("=" * 60)


if __name__ == "__main__":
    run_dialog_suite()
