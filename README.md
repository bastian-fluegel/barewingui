
<div align="center">
<a id="document-title"></a>
# BareWinGUI

> **Work in progress:** this branch rebuilds BareWinGUI for 0.2.0 (see `docs/ZIELBILD.md`). The examples below describe the old API and will be replaced with the controls port.


**Deterministic, zero-dependency native Win32 GUI framework for Python.**

[🇬🇧 Switch to English](#barewingui-en) • [🇩🇪 Zu Deutsch wechseln](#barewingui-de)

</div>

---

<a id="barewingui-en"></a>
## 🇬🇧 BareWinGUI (English)

BareWinGUI is a lightweight GUI framework engineered exclusively for Windows. By binding directly to core Win32 system DLLs (`user32.dll`, `kernel32.dll`, `comctl32.dll`, `gdi32.dll`, `comdlg32.dll`) via `ctypes`, it completely eliminates external dependencies, C++ runtime installations, and web-engine overhead.

Designed for systems administration, digital forensics, incident response, OT/SCADA interfaces, and hardened enterprise networks.

[Jump to German Version 🇩🇪](#barewingui-de)

### Key Features

* **Zero Runtime Dependencies (`dependencies = []`):** Built strictly with the Python standard library. No wheels, no MSVC redistributables, no Node.js/Chromium runtimes. (`flit_core` is needed only to build the package.)
* **Minimal Resource Footprint:** Target corridor of < 15 MB idle RAM and < 15 ms cold start (benchmarks pending on Windows 10 x86/x64).
* **Small Supply Chain:** No runtime dependencies beyond Python itself and the Windows system DLLs, so there are no third-party package CVEs to track. The code base is small enough to audit for air-gapped and hardened networks.
* **Modern Python 3.11+ Core:** Fully typed with pointer-adaptive Win32 types (`WPARAM`, `LPARAM`, `c_ssize_t`), eliminating 64-bit integer overflow errors.
* **Native Windows 10 & 11 Controls:** Standard Windows controls via Common Controls v6 (`comctl32.dll`); no custom widget set and no skinning engine. A small `theme` module only unifies surface colors (light canvas `#F3F3F3`, white control surfaces) and applies the Explorer visual style. There is no dark mode, because classic Win32 controls have no documented dark-mode API.

### Supported Environments

* **Operating Systems:** Windows 10 (Build 1809+), Windows 11, Windows Server (2016+).
* **Architectures:** 64-bit (x64) and 32-bit (x86). ARM64 (Windows-on-ARM) is experimental / untested.
* **Python Runtime:** Python >= 3.11.

### Installation

Clone and install in editable mode:

```bash
git clone https://github.com/bastian-fluegel/barewingui.git
cd barewingui
pip install -e .
```

### Quickstart

#### 1. Native System Dialogs

```python
from barewingui.dialogs import message_box, open_file, input_box

# Native Message Box
message_box("Operation completed successfully.", title="Audit Trail")

# Modal Input Box
target_ip = input_box("Enter target IP address:", title="Network Scanner")

# Explorer File Open Picker
log_file = open_file(title="Select Log File", filters=[("Log Files", "*.log")])

```

#### 2. Application Window (Preview)

```python
from barewingui import Window, Button, Label

win = Window(title="Triage Console", width=420, height=220)
Label(win, text="System status: Nominal", pos=(20, 20))
Button(win, text="Execute Scan", pos=(20, 60), on_click=lambda: print("Scanning..."))

win.run()

```

### Status and Limits

* Alpha (`0.1.x`): the public API may still change.
* Windows only, by design. There is no cross-platform abstraction and none is planned.
* The performance figures above are targets, not measurements. Benchmarks are pending.
* The listed Windows versions are the target environment, not a tested matrix. ARM64 is untested.

### Tests

The test suites are plain `unittest` modules and run on Windows only (they create real windows):

```bash
python -m unittest discover -s tests -p "verify_*.py" -v
```

A manually triggered GitHub Actions workflow (`.github/workflows/tests.yml`) runs the same command on `windows-latest`.

### Examples

* `examples/01_minimal_window.py`: window, controls, callbacks
* `examples/02_layout_showcase.py`: box layout (`VBox`, `HBox`)
* `examples/03_choice_controls.py`: `ComboBox`, `ListBox`, message boxes
* `examples/04_triage_tool.py`: larger demo application with native file pickers

### License

Distributed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

---
<a id="barewingui-de"></a>
## 🇩🇪 BareWinGUI (Deutsch)

BareWinGUI ist ein minimalistisches GUI-Framework, das kompromisslos für Windows entwickelt wurde. Durch die direkte Anbindung an die zentralen Win32-System-DLLs (`user32.dll`, `kernel32.dll`, `comctl32.dll`, `gdi32.dll`, `comdlg32.dll`) via `ctypes` verzichtet es vollständig auf externe Abhängigkeiten, C++-Laufzeitumgebungen und ressourcenhungrige Browser-Engines.

Konzipiert für Systemadministration, digitale Forensik, Incident Response, OT/SCADA-Bedienoberflächen und sicherheitskritische Unternehmensnetze.

[Zur englischen Version springen 🇬🇧](#barewingui-en)

### Kernmerkmale

* **Keine Laufzeit-Abhängigkeiten (`dependencies = []`):** Ausschließlich auf Basis der Python-Standardbibliothek realisiert. Keine Third-Party-Wheels, keine MSVC-Runtimes, kein WebView2. (`flit_core` wird nur zum Bauen des Pakets benötigt.)
* **Minimaler Ressourcenverbrauch:** Zielkorridor unter 15 MB RAM im Leerlauf und Kaltstarts unter 15 Millisekunden (Benchmarks ausstehend auf Win10 x86/x64).
* **Überschaubare Lieferkette:** Keine Laufzeit-Abhängigkeiten außer Python selbst und den Windows-Systembibliotheken, also keine CVEs fremder Pakete zu verfolgen. Der Code ist klein genug, um ihn für Air-Gapped- und abgesicherte Netze zu prüfen.
* **Moderne Python 3.11+ Basis:** Durchgehend typisiert mit pointer-adaptiven Win32-Typen (`WPARAM`, `LPARAM`, `c_ssize_t`) zur Vermeidung von 64-Bit-Überläufen.
* **Native Windows 10 & 11 Controls:** Standard-Steuerelemente über die Common Controls v6 (`comctl32.dll`), kein eigener Widget-Satz und keine Skinning-Engine. Ein kleines `theme`-Modul vereinheitlicht nur die Flächenfarben (helle Fläche `#F3F3F3`, weiße Steuerelemente) und setzt den Explorer-Visual-Style. Einen Dunkelmodus gibt es nicht, weil klassische Win32-Controls keine dokumentierte Dark-Mode-API haben.

### Unterstützte Plattformen

* **Betriebssysteme:** Windows 10 (ab Build 1809), Windows 11, Windows Server (ab Version 2016).
* **Architekturen:** 64-Bit (x64) und 32-Bit (x86). ARM64 (Windows-on-ARM) ist experimentell / ungetestet.
* **Python-Version:** Python >= 3.11.

### Installation

Entwicklungsinstallation direkt aus dem Quellcode:

```bash
git clone https://github.com/bastian-fluegel/barewingui.git
cd barewingui
pip install -e .
```

### Schnellstart

#### 1. Native Systemdialoge

```python
from barewingui.dialogs import message_box, open_file, input_box

# Native Message Box
message_box("Vorgang erfolgreich abgeschlossen.", title="Audit-Protokoll")

# Modale Eingabebox
ziel_ip = input_box("Ziel-IP eingeben:", title="Netzwerk-Scanner")

# Explorer-Dateiauswahl
datei = open_file(title="Protokolldatei wählen", filters=[("Logdateien", "*.log")])

```

#### 2. Anwendungsfenster (Vorschau)

```python
from barewingui import Window, Button, Label

win = Window(title="Triage-Konsole", width=420, height=220)
Label(win, text="Systemstatus: Bereit", pos=(20, 20))
Button(win, text="Scan starten", pos=(20, 60), on_click=lambda: print("Scanning..."))

win.run()

```

### Stand und Grenzen

* Alpha (`0.1.x`): Die öffentliche API kann sich noch ändern.
* Nur Windows, bewusst. Es gibt keine Plattform-Abstraktion und es ist keine geplant.
* Die Leistungswerte oben sind Zielwerte, keine Messungen. Die Benchmarks stehen aus.
* Die genannten Windows-Versionen sind die Zielumgebung, keine getestete Matrix. ARM64 ist ungetestet.

### Tests

Die Testsuiten sind einfache `unittest`-Module und laufen nur unter Windows (sie erzeugen echte Fenster):

```bash
python -m unittest discover -s tests -p "verify_*.py" -v
```

Ein manuell startbarer GitHub-Actions-Workflow (`.github/workflows/tests.yml`) führt denselben Befehl auf `windows-latest` aus.

### Beispiele

* `examples/01_minimal_window.py`: Fenster, Steuerelemente, Callbacks
* `examples/02_layout_showcase.py`: Box-Layout (`VBox`, `HBox`)
* `examples/03_choice_controls.py`: `ComboBox`, `ListBox`, Meldungsfenster
* `examples/04_triage_tool.py`: größere Demo-Anwendung mit nativen Dateidialogen

### Lizenz

Lizenziert unter der MIT-Lizenz. Weitere Informationen in der Datei [LICENSE.md](LICENSE.md).

---

[Back to Top / Nach oben](#barewingui-en)
