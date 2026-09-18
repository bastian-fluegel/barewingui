# BareWinGUI – Technische Spezifikation & Rahmenbedingungen

## 1. Projektidentität & Philosophie
* **Name:** BareWinGUI (`barewingui`)
* **Ziel:** Ultra-leichtgewichtiges, deterministisches GUI-Framework für Windows auf Basis nativer Win32-APIs.
* **Kernprinzip:** *Zero-Dependency.* Vollständiger Verzicht auf externe Pakete, C++-Runtimes und Browser-Engines.
* **Verwendungszweck:** Werkzeuge für Systemadministration, Incident Response, OT/SCADA-Leitstände, Forensik und abgesicherte Unternehmensnetze.

## 2. Unterstützte Plattformen & Laufzeitumgebung
* **Betriebssysteme:** Windows 10 (ab Build 1809), Windows 11, Windows Server (ab 2016).
* **Minimale Plattformgrenze:** Windows 10 (Versionen vor Windows 10 wie Win 7/8.1 sind explizit ausgeschlossen).
* **Architekturen:** x64 (64-Bit), x86 (32-Bit), ARM64 (über Windows-on-ARM Win32-Subsystem).
* **Python-Version:** Python >= 3.11 (strikt typisiert, Nutzung von `slots`, modernen Union-Types und Standardbibliotheks-Optimierungen).

## 3. Technische Leitplanken (Inviolable Rules)
* **Paketabhängigkeiten:** `dependencies = []`. Es dürfen ausschließlich Module der Python-Standardbibliothek importiert werden (`ctypes`, `wintypes`, `enum`, `dataclasses`, `typing`, `sys`, `math`).
* **Architektur-Agnostik:** Keine hardcodierten Bit-Breiten. Alle Handles, Zeiger und Message-Parameter müssen pointer-adaptiv sein (`ctypes.c_ssize_t`, `wintypes.WPARAM`, `wintypes.LPARAM`, `wintypes.HWND`).
* **Speicher- und Handle-Sicherheit (RAII):** Jedes Betriebssystem-Handle (`HWND`, `HDC`, `HGDIOBJ`, `PIDL`) unterliegt einem deterministischen Lebenszyklus und muss bei Zerstörung freigegeben werden (`DestroyWindow`, `DeleteDC`, `DeleteObject`, `CoTaskMemFree`).
* **GC-Verankerung (Callback Safety):** Instanzen von `WNDPROC` müssen dauerhaft an die Lebensdauer des Fensters gebunden sein, um Garbage-Collection-Crashs (`Access Violation`) auszuschließen.
* **UI-Erscheinungsbild:** Keine synthetischen CSS- oder Theming-Engines. Steuerelemente nutzen native Windows Common Controls v6 (`comctl32.dll`) und die jeweilige System-Schriftart (`Segoe UI`).

## 4. Nicht-Ziele (Explicit Non-Goals)
* Keine Cross-Plattform-Unterstützung (kein Linux, kein macOS).
* Kein HTML/CSS/Web-Rendering.
* Keine emulierte Design-Wahl (kein Nachbau alter oder fremder OS-Themes).
* Kein Support für veraltete Python-Versionen (< 3.11).

## 5. Ziel-Leistungsmetriken
* **Arbeitsspeicher (Idle):** < 15 MB RAM.
* **Kaltstartzeit:** < 15 Millisekunden bis zur ersten Eingabebereitschaft.
* **Artefaktgröße (Frozen Executable):** < 12 MB via PyInstaller / Nuitka.