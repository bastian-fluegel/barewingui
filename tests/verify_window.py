"""
tests/verify_window.py
~~~~~~~~~~~~~~~~~~~~~~
Automatisierte Testsuite für BareWinGUI:
Validiert Fenstererzeugung, HWND-Lebenszyklus (RAII), Steuerelement-IDs,
bidirektionale Eigenschaftssynchronisation und Windows-Message-Routing ohne GUI-Hänger.
"""

from __future__ import annotations

import os
import sys
import unittest
from ctypes import wintypes

# Projekt-Wurzelverzeichnis für direkte Ausführung auffindbar machen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui.constants import ButtonNotification, EditNotification, WM
from barewingui.controls import Button, CheckBox, Label, RadioButton, TextInput
from barewingui.types import user32
from barewingui.window import Window

# Sicherstellen, dass IsWindow typisiert ist
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL


class TestBareWinGUIWindow(unittest.TestCase):
    """Testet die native Fensterverwaltung und Ereignisverarbeitung."""

    def test_window_lifecycle_and_raii(self) -> None:
        """Prüft Erzeugung, Titel-Aktualisierung und deterministisches Zerstören."""
        win = Window(title="Lifecycle Test", width=400, height=300)
        hwnd = win.hwnd

        self.assertIsNotNone(hwnd)
        self.assertTrue(bool(user32.IsWindow(hwnd)), "HWND muss ein valides Win32-Fenster sein")
        self.assertEqual(win.title, "Lifecycle Test")

        # Titel dynamisch anpassen
        win.title = "Neuer Fenstertitel"
        self.assertEqual(win.title, "Neuer Fenstertitel")

        # Deterministisches Schließen (RAII)
        win.destroy()
        self.assertFalse(bool(user32.IsWindow(hwnd)), "HWND muss nach destroy() ungültig sein")

    def test_context_manager_cleanup(self) -> None:
        """Prüft automatische Ressourcenfreigabe über Context Manager."""
        saved_hwnd = None
        with Window(title="Context Test", width=300, height=200) as win:
            saved_hwnd = win.hwnd
            self.assertTrue(bool(user32.IsWindow(saved_hwnd)))

        self.assertFalse(
            bool(user32.IsWindow(saved_hwnd)),
            "Fenster muss beim Verlassen des with-Blocks automatisch zerstört werden",
        )

    def test_control_registration_and_sequential_ids(self) -> None:
        """Validiert fortlaufende Control-IDs und native Child-Handles."""
        with Window(title="Controls Test", width=500, height=400) as win:
            lbl = Label(win, text="Label 1", pos=(10, 10))
            inp = TextInput(win, text="Text 1", pos=(10, 40))
            btn = Button(win, text="Button 1", pos=(10, 80))
            chk = CheckBox(win, text="Check 1", pos=(10, 120))
            rad = RadioButton(win, text="Radio 1", pos=(10, 160))

            # Fortlaufende Control-IDs prüfen (ab 1000)
            self.assertEqual(lbl.control_id, 1000)
            self.assertEqual(inp.control_id, 1001)
            self.assertEqual(btn.control_id, 1002)
            self.assertEqual(chk.control_id, 1003)
            self.assertEqual(rad.control_id, 1004)

            # Validität aller nativen Win32-Handles absichern
            for ctrl in (lbl, inp, btn, chk, rad):
                self.assertTrue(
                    bool(user32.IsWindow(ctrl.hwnd)),
                    f"Child-Handle für {ctrl.__class__.__name__} ungültig",
                )

    def test_text_and_state_synchronization(self) -> None:
        """Testet die Synchronisation zwischen Python-Properties und dem Win32-Subsystem."""
        with Window(title="State Sync Test", width=400, height=300) as win:
            inp = TextInput(win, text="Initialer Text")
            self.assertEqual(inp.text, "Initialer Text")

            # Text über Property ändern
            inp.text = "Geänderter Wert"
            self.assertEqual(inp.text, "Geänderter Wert")

            # CheckBox-Status prüfen und manipulieren
            chk = CheckBox(win, text="Option", checked=False)
            self.assertFalse(chk.checked)
            chk.checked = True
            self.assertTrue(chk.checked)
            chk.checked = False
            self.assertFalse(chk.checked)

            # Geometrie anpassen
            inp.move(x=50, y=60, width=220, height=35)
            self.assertEqual(inp.pos, (50, 60))
            self.assertEqual(inp.size, (220, 35))

    def test_button_click_message_routing(self) -> None:
        """Prüft, ob WM_COMMAND-Nachrichten synchron an das Python-Callback weitergeleitet werden."""
        clicked_flags = {"count": 0}

        def on_btn_click() -> None:
            clicked_flags["count"] += 1

        with Window(title="Routing Test", width=300, height=200) as win:
            btn = Button(win, text="Klick mich", on_click=on_btn_click)

            # Simuliere Win32-Benachrichtigung: WM_COMMAND mit BN_CLICKED (0)
            wparam = (int(ButtonNotification.CLICKED) << 16) | (btn.control_id & 0xFFFF)
            user32.SendMessageW(win.hwnd, int(WM.COMMAND), wparam, btn.hwnd)

            self.assertEqual(
                clicked_flags["count"],
                1,
                "Button-Callback wurde durch WM_COMMAND nicht ausgelöst",
            )

    def test_text_input_change_notification(self) -> None:
        """Prüft, ob EN_CHANGE Benachrichtigungen an das on_change-Callback geroutet werden."""
        captured_text = []

        def on_text_change(val: str) -> None:
            captured_text.append(val)

        with Window(title="Edit Routing Test", width=300, height=200) as win:
            inp = TextInput(win, text="Start", on_change=on_text_change)

            # Alte Events verwerfen, die durch Windows (Initialisierung, WM_SETFONT) entstanden sind
            captured_text.clear()

            # Text dynamisch setzen und EN_CHANGE simulieren
            inp.text = "Update 1"
            wparam = (int(EditNotification.CHANGE) << 16) | (inp.control_id & 0xFFFF)
            user32.SendMessageW(win.hwnd, int(WM.COMMAND), wparam, inp.hwnd)

            self.assertTrue(len(captured_text) >= 1, "Es muss mindestens ein Event gefeuert worden sein.")
            self.assertEqual(captured_text[-1], "Update 1", "Der zuletzt empfangene Text muss korrekt sein.")

if __name__ == "__main__":
    unittest.main(verbosity=2)