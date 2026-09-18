"""
verify_dialogs.py
~~~~~~~~~~~~~~~~~
Interaktiver Härtetest für alle 10 nativen Win32-Systemdialoge in barewingui.
"""

from barewingui.dialogs import (
    about_dialog,
    choose_color,
    choose_font,
    input_box,
    message_box,
    open_file,
    page_setup,
    print_dialog,
    save_file,
    select_folder,
)


def run_dialog_suite():
    print("=" * 60)
    print(" BareWinGUI // Win32 Dialog Verification Suite")
    print("=" * 60)

    # 1. MessageBox
    print("\n[1/10] Teste MessageBox...")
    res = message_box(
        text="Funktioniert die MessageBox einwandfrei?",
        title="1. MessageBox Test",
        style=0x00000004 | 0x00000020  # MB_YESNO | MB_ICONQUESTION
    )
    print(f"  -> Ergebnis-ID: {res} ({'Ja' if res == 6 else 'Nein'})")

    # 2. InputBox (Custom Modal Win32 Loop)
    print("\n[2/10] Teste InputBox...")
    text_val = input_box(
        prompt="Gib einen Test-String für das native EDIT-Control ein:",
        title="2. InputBox Test",
        default_value="BareWinGUI Systemtest"
    )
    print(f"  -> Eingabe: {text_val!r}")

    # 3. Datei öffnen (GetOpenFileNameW)
    print("\n[3/10] Teste Datei-Öffnen-Dialog...")
    opened = open_file(
        title="3. Datei zum Öffnen wählen",
        filters=(
            ("Python-Dateien (*.py)", "*.py"),
            ("Textdateien (*.txt)", "*.txt"),
            ("Alle Dateien (*.*)", "*.*")
        ),
        allow_multi=False
    )
    print(f"  -> Gewählte Datei: {opened}")

    # 4. Datei speichern (GetSaveFileNameW)
    print("\n[4/10] Teste Datei-Speichern-Dialog...")
    saved = save_file(
        title="4. Zieldatei definieren",
        default_name="export_test.txt",
        default_ext="txt",
        filters=(("Textdokument (*.txt)", "*.txt"),)
    )
    print(f"  -> Speicherpfad: {saved}")

    # 5. Ordnerauswahl (SHBrowseForFolderW)
    print("\n[5/10] Teste Ordner-Auswahl (Shell PIDL)...")
    folder = select_folder(title="5. Basisverzeichnis auswählen")
    print(f"  -> Verzeichnis: {folder}")

    # 6. Farbauswahl (ChooseColorW)
    print("\n[6/10] Teste Farbwähler (BGR-Decoding)...")
    color = choose_color(initial_color=(255, 120, 0))  # Orange-Vorauswahl
    if color:
        r, g, b = color
        print(f"  -> RGB: ({r}, {g}, {b}) | Hex: #{r:02X}{g:02X}{b:02X}")
    else:
        print("  -> Farbwahl abgebrochen")

    # 7. Schriftartauswahl (ChooseFontW)
    print("\n[7/10] Teste Schriftart-Auswahl (LOGFONTW)...")
    font = choose_font(initial_font="Consolas", point_size=11)
    if font:
        print(f"  -> Font: {font.name}, {font.size_pt}pt, Stärke: {font.weight}")
        print(f"  -> Stil: Kursiv={font.italic}, Unterstrichen={font.underline}, Farbe={font.color}")
    else:
        print("  -> Schriftauswahl abgebrochen")

    # 8. Druckerdialog (PrintDlgW)
    print("\n[8/10] Teste Druckerauswahl (GDI DevMode)...")
    p_info = print_dialog(min_page=1, max_page=10)
    if p_info:
        print(f"  -> Kopien: {p_info.copies}, Seiten: {p_info.from_page}-{p_info.to_page}")
        print(f"  -> Modus: Alle Seiten={p_info.all_pages}, Nur Markierung={p_info.selection_only}")
    else:
        print("  -> Druckdialog abgebrochen")

    # 9. Seiteneinrichtung (PageSetupDlgW)
    print("\n[9/10] Teste Seiteneinrichtung...")
    page = page_setup()
    if page:
        print(f"  -> Papierformat: {page.width_mm:.1f}mm x {page.height_mm:.1f}mm")
        print(f"  -> Ränder: L={page.margin_left_mm:.1f}mm, O={page.margin_top_mm:.1f}mm, R={page.margin_right_mm:.1f}mm, U={page.margin_bottom_mm:.1f}mm")
    else:
        print("  -> Seiteneinrichtung abgebrochen")

    # 10. Shell About (ShellAboutW)
    print("\n[10/10] Teste Shell About Box...")
    about_dialog(
        app_name="BareWinGUI Suite#v0.1.0",
        other_info="Deterministische Win32 Ctypes-Architektur\nAlle Handles freigegeben."
    )
    print("  -> About-Box geschlossen")

    print("\n" + "=" * 60)
    print(" Alle 10 Dialog-Schnittstellen erfolgreich durchlaufen.")
    print("=" * 60)


if __name__ == "__main__":
    run_dialog_suite()