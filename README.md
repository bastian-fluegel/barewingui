
<div align="center">

# BareWinGUI

**Deterministic, zero-dependency native Win32 GUI framework for Python.**

[🇬🇧 Switch to English](#barewingui-en) • [🇩🇪 Zu Deutsch wechseln](#barewingui-de)

</div>

---

<a id="barewingui-en"></a>
## 🇬🇧 BareWinGUI (English)

BareWinGUI is an ultra-lightweight GUI framework engineered exclusively for Windows. By binding directly to core Win32 system DLLs (`user32.dll`, `kernel32.dll`, `comctl32.dll`, `gdi32.dll`, `comdlg32.dll`) via `ctypes`, it completely eliminates external dependencies, C++ runtime installations, and web-engine overhead.

Designed for systems administration, digital forensics, incident response, OT/SCADA interfaces, and mission-critical enterprise environments.

[Jump to German Version 🇩🇪](#barewingui-de)

### Key Features

* **Zero Dependencies (`dependencies = []`):** Built strictly with the Python standard library. No wheels, no MSVC redistributables, no Node.js/Chromium runtimes.
* **Minimal Resource Footprint:** Idles at < 15 MB RAM with instantaneous cold starts (< 15 ms).
* **Supply-Chain Security:** Zero external packages means zero foreign CVEs. Fully auditable for air-gapped and hardened networks.
* **Modern Python 3.11+ Core:** Fully typed with pointer-adaptive Win32 types (`WPARAM`, `LPARAM`, `c_ssize_t`), eliminating 64-bit integer overflow errors.
* **Native Windows 10 & 11 UI:** Direct integration with Common Controls v6 (`comctl32.dll`) for an authentic OS appearance without custom theme emulation.

### Supported Environments

* **Operating Systems:** Windows 10 (Build 1809+), Windows 11, Windows Server (2016+).
* **Architectures:** 64-bit (x64) and 32-bit (x86).
* **Python Runtime:** Python >= 3.11.

### Installation

Clone and install in editable mode:

```bash
git clone [https://github.com/bastian-fluegel/barewingui.git](https://github.com/bastian-fluegel/barewingui.git)
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

### License

Distributed under the MIT License. See [LICENSE.md](https://www.google.com/search?q=LICENSE.md&utm_source=gemini) for details.

---
<a id="barewingui-de"></a>
## 🇩🇪 BareWinGUI (Deutsch)

BareWinGUI ist ein minimalistisches GUI-Framework, das kompromisslos für Windows entwickelt wurde. Durch die direkte Anbindung an die zentralen Win32-System-DLLs (`user32.dll`, `kernel32.dll`, `comctl32.dll`, `gdi32.dll`, `comdlg32.dll`) via `ctypes` verzichtet es vollständig auf externe Abhängigkeiten, C++-Laufzeitumgebungen und ressourcenhungrige Browser-Engines.

Konzipiert für Systemadministration, digitale Forensik, Incident Response, OT/SCADA-Bedienoberflächen und sicherheitskritische Unternehmensnetze.

[Zur englischen Version springen 🇬🇧](https://www.google.com/search?q=%2523barewingui-en&utm_source=gemini)

### Kernmerkmale

* **Keine externen Abhängigkeiten (`dependencies = []`):** Ausschließlich auf Basis der Python-Standardbibliothek realisiert. Keine Third-Party-Wheels, keine MSVC-Runtimes, kein WebView2.
* **Minimaler Ressourcenverbrauch:** Unter 15 MB RAM-Auslastung im Leerlauf und Kaltstarts in unter 15 Millisekunden.
* **Maximale Supply-Chain-Sicherheit:** Keine externen Pakete bedeuten null Fremdschwachstellen (CVEs). Vollständig auditierbar für Air-Gapped- und KRITIS-Umgebungen.
* **Moderne Python 3.11+ Basis:** Durchgehend typisiert mit pointer-adaptiven Win32-Typen (`WPARAM`, `LPARAM`, `c_ssize_t`) zur Vermeidung von 64-Bit-Überläufen.
* **Authentische Windows 10 & 11 Optik:** Direkte Nutzung der Windows Common Controls v6 (`comctl32.dll`) für ein natives Erscheinungsbild ohne künstliche Themes.

### Unterstützte Plattformen

* **Betriebssysteme:** Windows 10 (ab Build 1809), Windows 11, Windows Server (ab Version 2016).
* **Architekturen:** 64-Bit (x64) und 32-Bit (x86).
* **Python-Version:** Python >= 3.11.

### Installation

Entwicklungsinstallation direkt aus dem Quellcode:

```bash
git clone [https://github.com/bastian-fluegel/barewingui.git](https://github.com/bastian-fluegel/barewingui.git)
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
Button(win, text="Scan starten", pos=(20, 60), on_click=lambda: print("Scan läuft..."))

win.run()

```

### Lizenz

Lizenziert unter der MIT-Lizenz. Weitere Informationen in der Datei [LICENSE.md](https://www.google.com/search?q=LICENSE.md&utm_source=gemini).

---

[Back to Top / Nach oben](https://www.google.com/search?q=%2523barewingui&utm_source=gemini)

