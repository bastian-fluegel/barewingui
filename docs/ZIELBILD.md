# BareWinGUI (BWG): Zielbild bis Beta

Stand: 13.10.2026 · Entwurf zur Freigabe durch Bastian

## Zweck
Ein natives Win32-GUI-Framework für Python 3.11+ ohne Abhängigkeiten. Es soll den GUI-Teil von AutoIt (GUICreate/GUICtrlCreate…) als Python-Bibliothek ersetzen: schnell eine echte Windows-Oberfläche bauen, die aussieht und sich verhält wie jede andere Windows-App. BWG ist ein reines GUI-Projekt, keine Security- oder Forensik-Bibliothek.

## Nicht-Ziele
- Kein Cross-Plattform (Mac-Schicht ist ein eigenes, späteres Projekt).
- Keine Automatisierung fremder Programme (Send, WinWait, ControlClick).
- Nichts wird selbst gezeichnet: kein Owner-Draw, kein Custom-Draw (`NM_CUSTOMDRAW`), kein eigenes `WM_PAINT` für Controls. Das Theme-Modul aus 0.1.10 entfällt.
- Keine Theme-Engine, keine Web-Engine, kein GUI-Designer.
- Keine AutoIt-Kompatibilitätsschicht: gleiche Fähigkeiten, aber Python-Namen.

## Harte Regeln
- `dependencies = []`, nur Standardbibliothek (ctypes).
- Python ≥ 3.11, Windows 10 (1809+), Windows 11, Server 2016+; x64 und x86. ARM64 später.
- Nur Unicode-APIs (`…W`), Common Controls v6 per Manifest, Per-Monitor-DPI (v2).
- Alle Größen in geräteunabhängigen Einheiten (96 dpi), BWG skaliert pro Monitor.
- UI läuft im Hauptthread; aus Threads nur über `app.invoke(fn)`.
- Fehler sind Python-Exceptions mit lesbarer Meldung, keine stillen `0`-Rückgaben.

## Code-Stil („Python-like")
- Klassen statt Control-IDs, Eigenschaften statt Get/Set, snake_case.
- Ereignisse über `on_*`-Parameter oder Decorator.
- Layout per `with`-Blöcken. Absolute Positionen nur als Ausnahme (`pos=`).
- Namen angelehnt an Windows: `TextBox`, `TabControl`, `TrackBar`, `ProgressBar`, `ListView`, `TreeView`, `DateTimePicker`, `GroupBox`, `StatusBar`, `MenuBar`.

```python
from barewingui import App, Window, VBox, HBox, Spacer, TextBox, Label, Button

app = App()
with Window("Demo", size=(480, 240)) as win:
    with VBox(padding=12, gap=8):
        name = TextBox(placeholder="Name")
        out = Label("")
        Spacer()
        with HBox(gap=8, justify="end"):
            ok = Button("OK", default=True)
            Button("Beenden", on_click=win.close)

@ok.on_click
def hello():
    out.text = f"Hallo {name.text}"

app.run()
```

## Layout
Zweistufig wie Flexbox, mit der Einfachheit der Swift-Stacks:
1. **Messen:** Jedes Control meldet seine natürliche Größe (Textmaß, `BCM_GETIDEALSIZE`).
2. **Verteilen:** Der Container verteilt den Rest nach `grow` und `shrink`.

- Container: `VBox`, `HBox`, später `Grid`. Optionen: `gap`, `padding`, `justify` (start, center, end, space-between), `align` (start, center, end, stretch).
- Kinder: `grow` (Standard 0), `shrink` (Standard 1), `width`/`height`, `min_*`/`max_*`, `align_self`.
- `Spacer()` füllt freien Platz.
- Natürliche Größen bleiben bei Resize erhalten, es wird nie unter die Mindestgröße gequetscht.

## Umfang Beta: Windows-Standard-Controls
Nur, was Windows selbst mitbringt (user32 und comctl32), mit nativem Aussehen:
- **Standard:** Window, Dialoge, Label, Button, CheckBox, RadioButton (mit Gruppen), GroupBox, TextBox (einzeilig und mehrzeilig, Passwort), ComboBox, ListBox.
- **Common Controls:** ListView (Details-Ansicht), TreeView, TabControl, ProgressBar, TrackBar, UpDown, DateTimePicker, StatusBar, Tooltips.
- **Fenster:** MenuBar, ContextMenu, Tastenkürzel, Timer, Icon/Bild (Static).
- **Dialoge:** vorhanden (message, input, open/save, folder, color, font).
- **Später:** Drag & Drop, Tray-Icon, Toolbar, Dunkelmodus (experimentell, siehe unten), Graphic-Control (wäre die einzige Stelle mit eigenem Zeichnen, nur auf ausdrücklichen Wunsch).

## Beta-Abnahme
Beta gilt als erreicht, wenn:
1. Fünf Beispielanwendungen laufen und im Repo liegen: Formular mit Prüfung, Datei-Browser (TreeView + ListView + StatusBar + Menü), Einstellungsdialog (Tabs, Gruppen, Slider, UpDown, ComboBox), Texteditor (Menü, mehrzeilig, Dialoge, Kürzel), Fortschritt mit Worker-Thread (`invoke`).
2. Die Tests laufen in CI auf `windows-latest` (Python 3.11 bis 3.13, x64; x86 soweit der Runner es erlaubt).
3. Resize und DPI-Wechsel sind auf einem echten Rechner abgenommen (Bastian).
4. README, API-Referenz und „Bekannte Grenzen" stimmen mit dem Code überein, Benchmarks sind gemessen oder gestrichen.
5. `pip install barewingui` funktioniert (PyPI), Tag und Release `0.2.0-beta` stehen.

## Arbeitspakete (je Branch, mit Tests, Doku, Changelog)
1. Kern: App, Ereignisschleife, DPI, `invoke`, Fehlerbehandlung (Code geschrieben, Windows-Lauf ausstehend)
2. Layout-Engine (Messen/Verteilen, Spacer; Grid später) (fertig, getestet)
3. Standard-Controls
4. Common Controls
5. Menü, Statusleiste, Tastenkürzel, Timer
6. Beispiele und Doku
7. CI, Packaging, Release

## Offene Annahmen (bitte prüfen)
- Das Aussehen kommt ausschließlich von Windows (Common Controls v6, Visual Styles). Das Theme-Modul mit eigener Zeichnung wird für Beta entfernt.
- Dunkelmodus: Windows hat dafür keine vollständig unterstützte Win32-API. Machbar sind nur die Titelleiste (`DwmSetWindowAttribute`, dokumentiert) und Stile wie `SetWindowTheme(..., "DarkMode_Explorer")`, teils über undokumentierte Funktionen und mit Lücken bei Button, Label und TextBox. Deshalb nach Beta, als „experimentell" markiert, ohne Zeichnen.
- Umbenennungen vor Beta sind erlaubt: `TextInput` wird `TextBox` (alter Name als Alias mit Warnung).
