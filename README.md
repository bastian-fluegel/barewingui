<div align="center">
<a id="document-title"></a>
# BareWinGUI

**Pure GUI framework for native Windows apps in Python. No dependencies.**

[🇬🇧 English](#barewingui-en) • [🇩🇪 Deutsch](#barewingui-de)

</div>

---

<a id="barewingui-en"></a>
## 🇬🇧 BareWinGUI (English)

BareWinGUI is a pure GUI framework for Windows: native windows and controls from Python, with nothing but `ctypes` and the Windows system DLLs. It is the Python successor of the GUI part of AutoIt (`GUICreate`/`GUICtrlCreate`), with a Python-like API and a flexbox-style layout.

[Jump to German Version 🇩🇪](#barewingui-de)

### Key Features

* **No dependencies:** Python standard library only. No wheels, no runtimes.
* **Native controls only:** standard controls (`user32`) and common controls (`comctl32` v6), themed by Windows. BareWinGUI draws nothing itself: no owner-draw, no custom theme.
* **Flexbox-style layout:** `VBox`, `HBox`, `Stack`, `Spacer`, options `grow`, `shrink`, `width`, `height`, `min_*`, `max_*`, `align_self`. Built with `with` blocks.
* **High DPI:** Per-Monitor-V2, all sizes in DIPs, reacts to monitor changes.
* **Python-like API:** events are handlers without arguments (`on_click=...`, `button.on_click(fn)`), properties instead of getters and setters.
* **Thread-safe UI updates:** `app.invoke(fn)` and `app.call(fn)`.
* **Targets:** Windows 10 / 11, Python 3.11+, x64 and x86. The package imports on every platform; creating an `App` needs Windows.

### Installation

```bash
pip install --pre barewingui   # beta: pip needs --pre for pre-releases
```

or from source:

```bash
git clone https://github.com/bastian-fluegel/barewingui.git
cd barewingui
pip install -e .
```

### Quickstart

```python
from barewingui import App, Button, Label, VBox, Window

app = App()
with Window("Hello", size=(320, 160)) as win:
    with VBox(padding=16, gap=10):
        label = Label("Hello, world!")
        Button("Click me", on_click=lambda: setattr(label, "text", "Clicked!"))
app.run()
```

### What is included

| Area | Classes and functions |
| --- | --- |
| Windows | `App`, `Window` (modal windows, shortcuts, `on_close`, `on_resize`) |
| Layout | `VBox`, `HBox`, `Stack`, `Spacer`, `Flex` |
| Standard controls | `Label`, `Button`, `CheckBox`, `RadioButton`, `TextBox`, `ComboBox`, `ListBox`, `GroupBox` |
| Common controls | `ProgressBar`, `Slider`, `SpinBox`, `StatusBar`, `DatePicker`, `TimePicker`, `ListView`, `TreeView`, `TabControl` / `TabPage` |
| Menus | `MenuBar`, `Menu`, `MenuItem`, `MenuSeparator`, `ContextMenu` (`context_menu=` on any control) |
| Dialogs | `message_box`, `ask_yes_no`, `show_info`, `show_error`, `input_box`, `open_file`, `save_file`, `pick_folder`, `choose_color`, `choose_font` |
| Other | `Timer`, `Event`, `Scale` |

### Examples

Run them with `python examples/<file>.py`:

* `00_ping_tool.py`: a complete little tool in about 30 lines (ComboBox, SpinBox, worker thread)
* `01_form.py`: registration form with live validation
* `02_file_browser.py`: menu, `TreeView` (lazy loading), `ListView`, `StatusBar`
* `03_settings.py`: settings dialog with tabs, groups, slider, spin box
* `04_editor.py`: text editor with file dialogs and shortcuts
* `05_progress.py`: long task in a worker thread, reporting back with `app.invoke`
* `06_support_helper.py`: a small admin tool: tabs, group boxes, network checks in a worker thread, saving a report

### Known Limits (Beta)

* Windows only, by design.
* Standard Windows controls only. Dark mode is not supported (classic controls have no documented dark mode); an experimental mode may follow later.
* No grid layout yet (`VBox`/`HBox`/`Stack` nest freely).
* No rich text, no custom-drawn controls, no images in controls yet.
* The API may still change before 1.0; unstable parts are marked in the docstrings.
* CI tests real windows on Windows (x64 and x86, Python 3.11 to 3.13) but cannot test mouse and keyboard behavior, native dialogs or multi-monitor DPI changes interactively. Reports from real machines are welcome.

### Tests

```bash
python -m unittest discover -s tests
```

Logic tests (layout, scaling, shortcuts, dispatch) run everywhere; tests that create real windows run on Windows only and are skipped elsewhere. GitHub Actions runs both.

### Feedback

This is a beta. Please try it and tell me what is missing or broken: [report a bug or give feedback](https://github.com/bastian-fluegel/barewingui/issues/new/choose). Useful details: Windows version, display scaling, Python version, and a small script.

### License

Distributed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

---

<a id="barewingui-de"></a>
## 🇩🇪 BareWinGUI (Deutsch)

BareWinGUI ist ein reines GUI-Framework für Windows: native Fenster und Steuerelemente aus Python, nur mit `ctypes` und den Windows-Systembibliotheken. Es ist der Python-Nachfolger des GUI-Teils von AutoIt (`GUICreate`/`GUICtrlCreate`), mit Python-typischer API und Flexbox-artigem Layout.

[Switch to English Version 🇬🇧](#barewingui-en)

### Kernmerkmale

* **Keine Abhängigkeiten:** nur die Python-Standardbibliothek.
* **Nur native Steuerelemente:** Standard-Controls (`user32`) und Common Controls (`comctl32` v6), von Windows gestaltet. BareWinGUI zeichnet nichts selbst.
* **Flexbox-artiges Layout:** `VBox`, `HBox`, `Stack`, `Spacer` mit `grow`, `shrink`, `width`, `height`, `min_*`, `max_*`, `align_self`, aufgebaut mit `with`-Blöcken.
* **Hohe DPI:** Per-Monitor-V2, alle Größen in DIPs.
* **Pythonische API:** Ereignisse sind Handler ohne Argumente (`on_click=...`), Eigenschaften statt Getter/Setter.
* **Thread-sichere Aktualisierung:** `app.invoke(fn)` und `app.call(fn)`.
* **Ziele:** Windows 10 / 11, Python 3.11+, x64 und x86. Das Paket lässt sich überall importieren; eine `App` braucht Windows.

### Installation

```bash
pip install --pre barewingui   # beta: pip needs --pre for pre-releases
```

### Schnellstart

```python
from barewingui import App, Button, Label, VBox, Window

app = App()
with Window("Hello", size=(320, 160)) as win:
    with VBox(padding=16, gap=10):
        label = Label("Hello, world!")
        Button("Click me", on_click=lambda: setattr(label, "text", "Clicked!"))
app.run()
```

### Beispiele

Start mit `python examples/<Datei>.py`: Formular mit Prüfung (`01_form.py`), Dateibrowser (`02_file_browser.py`), Einstellungsdialog (`03_settings.py`), Texteditor (`04_editor.py`), Fortschritt mit Arbeitsthread (`05_progress.py`), Support-Helfer mit Netzwerkprüfung (`06_support_helper.py`).

### Bekannte Grenzen (Beta)

* Nur Windows, bewusst.
* Nur Standard-Windows-Controls; kein Dark Mode (später vielleicht experimentell).
* Noch kein Grid-Layout, kein Rich Text, keine eigengezeichneten Controls.
* Die API kann sich vor 1.0 noch ändern.
* Die CI testet echte Fenster unter Windows (x64 und x86, Python 3.11 bis 3.13), aber keine Maus-/Tastaturbedienung, nativen Dialoge oder DPI-Wechsel zwischen Monitoren. Rückmeldungen von echten Rechnern sind willkommen.

### Tests

```bash
python -m unittest discover -s tests
```

### Rückmeldung

Das ist eine Beta. Probier es aus und sag mir, was fehlt oder kaputt ist: [Fehler melden oder Rückmeldung geben](https://github.com/bastian-fluegel/barewingui/issues/new/choose). Hilfreich: Windows-Version, Skalierung, Python-Version und ein kleines Skript.

### Lizenz

MIT-Lizenz, siehe [LICENSE.md](LICENSE.md).
