"""
tests/verify_window.py
~~~~~~~~~~~~~~~~~~~~~~
Automatisierte Testsuite für BareWinGUI:
Validiert Fenstererzeugung, HWND-Lebenszyklus (RAII), Steuerelement-IDs,
bidirektionale Eigenschaftssynchronisation und Windows-Message-Routing ohne GUI-Hänger.
"""

from __future__ import annotations

import ctypes
import os
import sys
import unittest
from ctypes import wintypes

# Projekt-Wurzelverzeichnis für direkte Ausführung auffindbar machen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui.constants import ButtonNotification, EditNotification, WindowLong, WindowStyleEx, WM
from barewingui.controls import Button, CheckBox, ComboBox, Label, ListBox, RadioButton, TextInput
from barewingui.controls.choice import CBN_SELCHANGE, LBN_SELCHANGE
from barewingui.core import Application, enable_visual_styles, get_system_font
from barewingui.types import GA_ROOT, GetWindowLongPtrW, load_comctl32, user32
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

    def test_combobox_and_listbox_selection(self) -> None:
        """Prüft Einträge, Auswahl und WM_COMMAND-Routing für ComboBox und ListBox."""
        combo_events: list[tuple[int, str]] = []
        list_events: list[tuple[int, str]] = []

        def on_combo(idx: int, val: str) -> None:
            combo_events.append((idx, val))

        def on_list(idx: int, val: str) -> None:
            list_events.append((idx, val))

        with Window(title="Choice Controls Test", width=400, height=300) as win:
            combo = ComboBox(
                win,
                items=["Alpha", "Beta", "Gamma"],
                selected_index=1,
                on_change=on_combo,
            )
            lst = ListBox(
                win,
                items=["Eins", "Zwei", "Drei"],
                on_change=on_list,
            )

            self.assertTrue(bool(user32.IsWindow(combo.hwnd)))
            self.assertTrue(bool(user32.IsWindow(lst.hwnd)))
            self.assertEqual(combo.selected_index, 1)
            self.assertEqual(combo.selected_text, "Beta")

            combo.selected_index = 2
            self.assertEqual(combo.selected_text, "Gamma")

            lst.selected_index = 0
            self.assertEqual(lst.selected_text, "Eins")

            combo_wparam = (CBN_SELCHANGE << 16) | (combo.control_id & 0xFFFF)
            user32.SendMessageW(win.hwnd, int(WM.COMMAND), combo_wparam, combo.hwnd)
            self.assertEqual(combo_events[-1], (2, "Gamma"))

            list_wparam = (LBN_SELCHANGE << 16) | (lst.control_id & 0xFFFF)
            user32.SendMessageW(win.hwnd, int(WM.COMMAND), list_wparam, lst.hwnd)
            self.assertEqual(list_events[-1], (0, "Eins"))

            combo.clear()
            self.assertIsNone(combo.selected_text)
            lst.clear()
            self.assertIsNone(lst.selected_text)

    def test_comctl_v6_actctx_and_dialog_keys(self) -> None:
        """Prüft ActCtx/ComCtl v6, WS_EX_CONTROLPARENT und IsDialogMessageW."""
        self.assertTrue(enable_visual_styles())
        Application.initialize()
        self.assertTrue(enable_visual_styles())

        comctl32 = load_comctl32()
        self.assertIsNotNone(comctl32)
        self.assertTrue(hasattr(comctl32, "InitCommonControlsEx"))

        class DLLVERSIONINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("dwMajorVersion", wintypes.DWORD),
                ("dwMinorVersion", wintypes.DWORD),
                ("dwBuildNumber", wintypes.DWORD),
                ("dwPlatformID", wintypes.DWORD),
            ]

        if hasattr(comctl32, "DllGetVersion"):
            comctl32.DllGetVersion.argtypes = [ctypes.POINTER(DLLVERSIONINFO)]
            comctl32.DllGetVersion.restype = ctypes.HRESULT
            info = DLLVERSIONINFO()
            info.cbSize = ctypes.sizeof(DLLVERSIONINFO)
            hr = comctl32.DllGetVersion(ctypes.byref(info))
            self.assertEqual(hr, 0)
            self.assertGreaterEqual(info.dwMajorVersion, 6)

        self.assertFalse(hasattr(Window, "__del__"))
        h_font = get_system_font()
        self.assertTrue(bool(h_font))

        with Window(title="Keyboard Nav Test", width=360, height=180) as win:
            ex_style = int(GetWindowLongPtrW(win.hwnd, int(WindowLong.EXSTYLE)))
            self.assertTrue(
                ex_style & int(WindowStyleEx.CONTROLPARENT),
                "WS_EX_CONTROLPARENT ist für IsDialogMessageW erforderlich",
            )
            btn_a = Button(win, text="Eins", pos=(12, 12), size=(90, 28))
            btn_b = Button(win, text="Zwei", pos=(112, 12), size=(90, 28), default=True)

            msg = wintypes.MSG()
            msg.hWnd = btn_a.hwnd
            msg.message = int(WM.KEYDOWN)
            msg.wParam = 0x09  # VK_TAB
            root = user32.GetAncestor(btn_a.hwnd, GA_ROOT)
            self.assertTrue(bool(root))
            # Darf nicht werfen; Rückgabewert hängt vom Fokus ab
            user32.IsDialogMessageW(root, ctypes.byref(msg))
            self.assertTrue(bool(user32.IsWindow(btn_b.hwnd)))

            from barewingui.core import apply_window_chrome

            apply_window_chrome(win.hwnd)

    def test_vbox_preserves_natural_height_after_squeeze(self) -> None:
        """VBox darf die natürliche Höhe nicht dauerhaft durch set_bounds überschreiben."""
        from barewingui.layout import VBox

        with Window(title="Layout Freeze Test", width=400, height=500) as win:
            stretchy = ListBox(win, size=(200, 80))
            detail = TextInput(win, multiline=True, readonly=True, size=(200, 110))
            root = VBox(padding=0, spacing=0)
            root.add(stretchy, stretch=1)
            root.add(detail)

            root.apply(0, 0, 400, 80)
            self.assertLessEqual(detail.size[1], 80)

            root.apply(0, 0, 400, 500)
            self.assertEqual(detail.size[1], 110)
            self.assertGreater(stretchy.size[1], 110)

    def test_multiline_tab_advances_to_next_control(self) -> None:
        """Tab in ES_MULTILINE darf nicht im Edit hängenbleiben."""
        from barewingui.constants import VirtualKey
        from barewingui.core import _hwnd_int, _tab_out_of_multiline_edit

        with Window(title="Multiline Tab Test", width=360, height=220) as win:
            detail = TextInput(win, multiline=True, readonly=True, pos=(12, 12), size=(300, 80))
            nxt = Button(win, text="Weiter", pos=(12, 110), size=(90, 32))
            user32.SetFocus(detail.hwnd)

            msg = wintypes.MSG()
            msg.hWnd = detail.hwnd
            msg.message = int(WM.KEYDOWN)
            msg.wParam = int(VirtualKey.TAB)

            moved = _tab_out_of_multiline_edit(win.hwnd, msg)
            self.assertTrue(moved, "Tab muss aus dem Multiline-Edit herausspringen")
            self.assertEqual(_hwnd_int(user32.GetFocus()), _hwnd_int(nxt.hwnd))

if __name__ == "__main__":
    unittest.main(verbosity=2)