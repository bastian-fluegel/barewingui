"""
examples/02_triage_tool.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Praxisnahes Incident-Response- und Triage-Dashboard.
Demonstriert die Kombination aus responsivem Box-Layout, nativen Datei-Pickern,
dynamischer ListBox-Befüllung und modalen Systemdialogen.
"""

from __future__ import annotations

from datetime import datetime
import os
import sys

# Projekt-Root zur Laufzeit auffindbar machen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from barewingui import (
    Button,
    ComboBox,
    HBox,
    Label,
    ListBox,
    TextInput,
    VBox,
    Window,
)
from barewingui.dialogs import (
    confirm_box,
    info_box,
    open_file,
    pick_folder,
    save_file,
    warning_box,
)


def main() -> int:
    win = Window(
        title="BareWinGUI — Forensic Triage & Acquisition Console",
        width=740,
        height=580,
    )

    root = VBox(padding=14, spacing=10)

    # -----------------------------------------------------------------------
    # 1. Ziel-Auswahl (Datei oder Verzeichnis)
    # -----------------------------------------------------------------------
    root.add(Label(win, text="Zielpfad / Evidenzquelle:"))

    target_bar = HBox(spacing=8, padding=0, fixed_size=32)
    target_input = TextInput(win, text=os.getcwd(), size=(0, 32))
    target_bar.add(target_input, stretch=1)

    def on_pick_folder() -> None:
        folder = pick_folder(title="Evidenz-Verzeichnis wählen", parent=win)
        if folder:
            target_input.text = folder

    def on_pick_file() -> None:
        file_path = open_file(
            title="Dump- oder Logdatei öffnen",
            filters=[
                ("Forensische Abbilder & Logs", "*.raw;*.dd;*.vmdk;*.evtx;*.log"),
                ("Alle Dateien", "*.*"),
            ],
            parent=win,
        )
        if file_path:
            target_input.text = file_path

    target_bar.add(Button(win, text="Ordner...", size=(90, 32), on_click=on_pick_folder))
    target_bar.add(Button(win, text="Datei...", size=(80, 32), on_click=on_pick_file))
    root.add(target_bar)

    # -----------------------------------------------------------------------
    # 2. Prüfprofil & Ausführung
    # -----------------------------------------------------------------------
    profile_bar = HBox(spacing=8, padding=0, fixed_size=32)
    profile_bar.add(Label(win, text="Triage-Profil:", size=(85, 20)))

    profiles = [
        "Persistence & Autostarts (Registry / Tasks)",
        "Netzwerk-Sockets & DNS-Cache",
        "MFT & Prefetch Auswertung",
        "Kritische Windows EventLogs (Security / Sysmon)",
    ]
    profile_combo = ComboBox(win, items=profiles, size=(380, 32))
    profile_bar.add(profile_combo, stretch=1)

    btn_scan = Button(win, text="Triage starten", size=(130, 32), default=True)
    profile_bar.add(btn_scan)
    root.add(profile_bar)

    # -----------------------------------------------------------------------
    # 3. Artefakte-Liste (ListBox)
    # -----------------------------------------------------------------------
    root.add(Label(win, text="Gefundene Artefakte & Indikatoren (Doppelklick für Rohdaten):"))

    artefact_data: dict[str, str] = {}
    artefacts_list = ListBox(win)
    root.add(artefacts_list, stretch=1)

    # -----------------------------------------------------------------------
    # 4. Detailansicht
    # -----------------------------------------------------------------------
    root.add(Label(win, text="Detailinformationen zum ausgewählten Indikator:"))
    detail_view = TextInput(win, multiline=True, readonly=True, size=(0, 110))
    root.add(detail_view)

    # -----------------------------------------------------------------------
    # Event-Verdrahtung
    # -----------------------------------------------------------------------
    def on_item_selected(idx: int, label: str) -> None:
        raw_detail = artefact_data.get(label, "Keine Zusatzdaten vorhanden.")
        detail_view.text = raw_detail

    def on_item_double_clicked(idx: int, label: str) -> None:
        raw_detail = artefact_data.get(label, "Keine Zusatzdaten vorhanden.")
        info_box(f"Artefakt: {label}\n\nDetails:\n{raw_detail}", title="Artefakt-Inspektor", parent=win)

    artefacts_list.on_change = on_item_selected
    artefacts_list.on_double_click = on_item_double_clicked

    def run_triage() -> None:
        path = target_input.text.strip()
        if not path:
            warning_box("Bitte geben Sie einen gültigen Zielpfad an.", title="Eingabe fehlt", parent=win)
            return

        artefacts_list.clear()
        artefact_data.clear()
        detail_view.clear()

        selected_profile = profile_combo.selected_text or profiles[0]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Mock-Befüllung abgestimmt auf das gewählte Profil
        mock_findings = [
            (
                f"[{timestamp}] Anomalie: Unsignierte Binary in Shell Startup",
                f"Quelle: {path}\r\nTyp: Registry RunKey\r\nPfad: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\r\nWert: 'svchost_update.exe' -> C:\\Users\\Public\\svchost.exe",
            ),
            (
                f"[{timestamp}] Verdächtige PowerShell-Befehlszeile mit Base64",
                f"Quelle: {path}\r\nEvent-ID: 4104 (ScriptBlock Logging)\r\nPayload: powershell.exe -NoP -NonI -W Hidden -Enc SUVY...",
            ),
            (
                f"[{timestamp}] MFT Anomalie: Zeitstempel-Manipulation (Timestomp)",
                f"Quelle: {path}\r\nAttribut: $STANDARD_INFORMATION unterscheidet sich um mehr als 120 Tage von $FILE_NAME.\r\nDatei: C:\\Windows\\Temp\\srvmgr.tmp",
            ),
            (
                f"[{timestamp}] Ausgehende Verbindung zu externer IP ohne DNS-Eintrag",
                f"Quelle: {path}\r\nSocket: 192.168.1.45:49822 -> 198.51.100.24:443\r\nProzess: rundll32.exe (PID 3412)",
            ),
        ]

        for title, detail in mock_findings:
            artefacts_list.add(title)
            artefact_data[title] = detail

        artefacts_list.selected_index = 0
        on_item_selected(0, mock_findings[0][0])

    btn_scan.on_click = run_triage

    # -----------------------------------------------------------------------
    # 5. Aktionsleiste unten
    # -----------------------------------------------------------------------
    bottom_bar = HBox(spacing=8, padding=0, fixed_size=32)

    def on_export_clicked() -> None:
        if not artefact_data:
            warning_box("Es liegen keine Artefakte zum Exportieren vor.", title="Export leer", parent=win)
            return

        target_file = save_file(
            title="Triage-Bericht speichern",
            default_name=f"Triage_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            default_ext="txt",
            filters=[("Textdateien (*.txt)", "*.txt"), ("Alle Dateien (*.*)", "*.*")],
            parent=win,
        )

        if not target_file:
            return

        try:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write("=== BAREWINGUI FORENSIC TRIAGE REPORT ===\n")
                f.write(f"Zeitstempel: {datetime.now().isoformat()}\n")
                f.write(f"Untersuchungspfad: {target_input.text}\n")
                f.write(f"Gewähltes Profil: {profile_combo.selected_text}\n")
                f.write("=" * 45 + "\n\n")

                for title, details in artefact_data.items():
                    f.write(f"FINDING: {title}\n")
                    f.write(f"{details}\n")
                    f.write("-" * 45 + "\n")

            info_box(f"Bericht erfolgreich gespeichert:\n{target_file}", title="Export abgeschlossen", parent=win)
        except OSError as err:
            warning_box(f"Fehler beim Schreiben des Berichts:\n{err}", title="Schreibfehler", parent=win)

    def on_clear_clicked() -> None:
        if artefact_data and confirm_box("Möchten Sie alle geladenen Artefakte verwerfen?", title="Liste leeren", parent=win):
            artefacts_list.clear()
            artefact_data.clear()
            detail_view.clear()

    btn_export = Button(win, text="Bericht exportieren...", size=(160, 32), on_click=on_export_clicked)
    btn_clear = Button(win, text="Liste leeren", size=(100, 32), on_click=on_clear_clicked)
    btn_exit = Button(win, text="Beenden", size=(90, 32), on_click=win.close)

    bottom_bar.add(btn_export)
    bottom_bar.add(btn_clear)
    bottom_bar.add_stretch()
    bottom_bar.add(btn_exit)
    root.add(bottom_bar)

    # Layout an das Fenster binden und starten
    root.attach(win)
    return win.run()


if __name__ == "__main__":
    sys.exit(main())