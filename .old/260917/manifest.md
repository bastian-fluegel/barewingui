# Das BareWinGUI-Manifest: Plädoyer für deterministische Desktop-Präzision

Moderne Desktop-Software leidet unter einer kollektiven Amnesie. Wir haben vergessen, wie es sich anfühlt, wenn eine Anwendung im selben Sekundenbruchteil startet, in dem der Zeigefinger die Maustaste loslässt. Wir haben akzeptiert, dass für ein Formular mit drei Eingabefeldern und zwei Knöpfen ein vollständiger Webbrowser im Hintergrund gestartet, ein Node.js-Laufzeitstack hochgefahren und 200 Megabyte Arbeitsspeicher alloziiert werden.

Wir haben uns der Doktrin der universellen Plattformunabhängigkeit unterworfen – und dafür drei Dinge eingetauscht: Leistung, Zuverlässigkeit und Würde.

BareWinGUI ist der bewusste Bruch mit dieser Haltung. Es ist die Rückkehr zu radikaler Reduktion, null Abhängigkeiten und maximaler Systemnähe für die wichtigste Produktivumgebung der Welt: das Windows-Betriebssystem.

---

### Teil I: Die Absichtserklärung

#### Das Dogma der Plattformunabhängigkeit ist gescheitert

Für Consumer-Apps mag „Write once, run everywhere“ bequem sein. Für System-Utilities, Vor-Ort-Diagnostik, Leitstände, Incident-Response-Werkzeuge und Administrations-Skripte ist es ein Desaster:

* **Tkinter** ignoriert moderne Windows-Designsprachen, wirkt wie ein Fremdkörper und leidet unter fragilen Event-Loops.
* **PyQt und PySide** sind gigantische C++-Kolosse. Ein einfaches Tool zieht 150 MB Abhängigkeiten, externe Shared Libraries und potenzielle DLL-Hell-Konflikte nach sich.
* **Web-Wrapper (Electron, PyWebView)** erzeugen untragbare Angriffsflächen, verbrauchen Hunderte Megabyte RAM und versagen auf gehärteten Systemen, auf denen Edge WebView2 deaktiviert oder reglementiert ist.

BareWinGUI verweigert den Kompromiss der Abstraktion. Anstatt zu versuchen, auf macOS, Linux und Windows gleichermaßen mittelmäßig zu sein, ist BareWinGUI ausschließlich für Windows gebaut – dort aber kompromisslos präzise.

#### Die Kernversprechen

1. **Zero Dependencies (`dependencies = []`):** Nicht eine einzige Drittanbieter-Bibliothek. Keine C++-Runtimes, kein Visual Studio Build-Tool-Zwang, keine Rad-Pakete.
2. **Deterministischer Ressourcenverbrauch:** Ein Speicher-Footprint von unter 15 Megabyte RAM und Kaltstarts in unter 10 Millisekunden.
3. **Maximale Supply-Chain-Sicherheit:** Wo kein externer Code existiert, existieren keine Fremd-Schwachstellen (CVEs). Jede Zeile Code ist auditierbar, nachvollziehbar und transparent.
4. **Vollständige Windows-Nativität:** Direkte Bindung an die System-DLLs (`user32.dll`, `kernel32.dll`, `gdi32.dll`, `comdlg32.dll`, `shell32.dll`), die auf jedem Windows-System seit Jahrzehnten gehärtet vorinstalliert sind.

---

### Teil II: Das Argumentationspapier

#### 1. Für den Sicherheitsingenieur & Incident Responder

* **Air-Gap-Fähigkeit:** Wenn ein infiziertes, isoliertes System analysiert werden muss, gibt es keine Internetverbindung für `pip install`. Ein BareWinGUI-Tool läuft als Standalone-Python-Skript oder als 8-Megabyte-Executable sofort los.
* **Auditierbarkeit:** In Hochsicherheitszonen (KRITIS, Industrie, Finanzwesen) verlangt jede Sub-Dependency eine Freigabe. BareWinGUI besitzt keine Lieferkette, die kompromittiert werden kann.

#### 2. Für den Systemadministrator & DevOps-Pionier

* **Keine Admin-Rechte erforderlich:** Keine Installation von Laufzeitumgebungen nötig. Das Tool startet unter Standard-Benutzerrechten.
* **Headless- & Server-Tauglichkeit:** Läuft nahtlos auf Windows Server (ab 2016) sowie Windows 10/11 – selbst in minimalistischen Administrations-Umgebungen.

#### 3. Für den CTO & IT-Entscheider

* **Niedriger Bus-Faktor & Wartungsaufwand:** Keine Abhängigkeit von volatilen Open-Source-Frameworks, deren Breaking Changes alle zwei Jahre Refactorings erzwingen. Die Win32-API ist Microsofts stabilste Schnittstelle mit garantierter Abwärtskompatibilität über Jahrzehnte.
* **Drastisch reduzierte Deployment-Kosten:** Kompilierte Binärdateien wiegen einen Bruchteil gängiger Alternativen, belasten Netzwerke bei Rollouts nicht und starten latenzfrei.

#### 4. Für die Python- und Entwickler-Community

* **Ende der MFC-Kryptik:** `pywin32` zwang Entwickler, C++-MFC-Konzepte der 90er-Jahre nachzuahmen. BareWinGUI beweist, dass native Systemnähe modern, typisiert und pythonisch sein kann:

```python
# Die Vision: Lesbar, typisiert, modern
from barewingui import Window, Button, Label, WindowStyle

with Window(title="Network Triage", width=400, height=250) as win:
    Label("Status: Bereit zur Analyse", pos=(20, 20))
    Button("Scan starten", pos=(20, 60), on_click=lambda: print("Scanning..."))
    win.run()

```

---

### Teil III: Der Architektur-Entwurf (North Star für Entwickler)

Dieses Dokument setzt die unverrückbaren Leitplanken für den Quellcode fest. Jede Codezeile, die in BareWinGUI einfließt, muss sich an diesen fünf Prinzipien messen lassen.

#### 1. Keine externen Pakete (Strict Standard Library)

Erlaubt sind ausschließlich Module der Python-Standardbibliothek: `ctypes`, `wintypes`, `enum`, `dataclasses`, `typing`, `sys`, `math`. Das Paket darf zu keinem Zeitpunkt der Projektgeschichte eine externe Abhängigkeit in `pyproject.toml` definieren.

#### 2. Pointer-adaptive Typensicherheit (32-Bit & 64-Bit Agnostik)

Das Framework unterstützt standardmäßig 64-Bit Windows (10/11/Server) und bleibt gleichzeitig lauffähig auf 32-Bit Windows 10 Umgebungen.

* **Keine hardcodierten Breiten:** Niemals feste Integer (`c_int64`, `c_uint32`) für Nachrichten-Parameter verwenden.
* **Pointer-Typen nutzen:** Ausschließlich `wintypes.WPARAM`, `wintypes.LPARAM` und `LRESULT = ctypes.c_ssize_t` einsetzen.
* **Automatische Skalierung:** Der Code muss ohne `if is_64bit:`-Weichen auf beiden Architekturen fehlerfrei und ohne Speicherüberläufe kompilieren.

#### 3. Striktes RAII (Resource Acquisition Is Initialization)

Win32 vergibt System-Handles (`HWND`, `HDC`, `HGDIOBJ`, `PIDL`), die der Garbage Collector von Python nicht kennt.

* Jedes allozierte Handle muss an einen Python-Lebenszyklus gebunden sein.
* Wrapper-Klassen müssen Context Manager (`__enter__`, `__exit__`) und deterministische Bereinigungen (`__del__` als Fallback) implementieren.
* Speicher-Hygiene ist Gesetz: GDI-Objekte werden gelöscht (`DeleteObject`), DCs freigegeben (`ReleaseDC`), Shell-Speicher bereinigt (`CoTaskMemFree`).

#### 4. GC-Anchoring für C-Callbacks

Eines der größten Probleme von Win32-Bindings in Python sind stumme C-Crashes (`Access Violation`), wenn der Python-Garbage-Collector Funktionszeiger abräumt.

* Jeder `WNDPROC`-Callback muss als Instanz-Attribut fest im Hauptfenster verankert sein, solange das Fenster existiert.
* Kein Callback darf als flüchtige lokale Variable in einer Hilfsfunktion instanziiert werden.

#### 5. Keine Pseudo-Themes – Radikale Ehrlichkeit im Design

BareWinGUI baut keine CSS-Parser oder synthetischen UI-Engines nach.

* Wir nutzen die nativen Win32-Controls des Betriebssystems (`BUTTON`, `EDIT`, `STATIC`, `COMBOBOX`).
* Visuelle Veredelung erfolgt ausschließlich über offizielle Systemmechanismen: Aktivierung von Visual Styles (`comctl32.dll` v6 via Manifest), sauberes Setzen von System-Schriftarten (`WM_SETFONT` mit `DEFAULT_GUI_FONT`) und flackerfreie Renderpfade (`WM_CTLCOLORSTATIC`, `WS_CLIPCHILDREN`).
* Ein Button unter Windows 11 sieht exakt wie ein Windows-11-Button aus. Ein Fenster unter Windows 10 verhält sich exakt wie ein Windows-10-Fenster.

---

### Technischer Vergleichsindex

| Kriterium | BareWinGUI | Tkinter | PyQt6 / PySide6 | Web-Wrapper (Electron / WebView2) |
| --- | --- | --- | --- | --- |
| **Fremd-Abhängigkeiten** | **0 (`dependencies = []`)** | 0 (im Standard-Python) | Dutzende (C++ Räder) | Hunderte (Node/NPM/Browser) |
| **Arbeitsspeicher (Idle)** | **~12 – 15 MB** | ~25 – 35 MB | ~85 – 130 MB | ~180 – 350 MB |
| **Kaltstartzeit** | **< 15 ms** | ~80 – 120 ms | ~300 – 600 ms | ~800 – 2500 ms |
| **Executable-Größe (Frozen)** | **~8 – 11 MB** | ~15 – 20 MB | ~60 – 110 MB | ~90 – 160 MB |
| **Windows-Integration** | **100 % Nativ (Win32 ABI)** | Emuliert / Tcl-Tk | Abstrahiertes QStyle | HTML/CSS DOM |
| **Gefahr von DLL-Konflikten** | **Keine (System-DLLs)** | Gering | Hoch (MSVCP/Qt-Libs) | Sehr hoch (Browser-Runtimes) |

---

### Der Leitfaden für Mitstreiter

Wer an BareWinGUI mitarbeitet, verpflichtet sich nicht dem Prinzip des Machbaren, sondern dem Prinzip des Notwendigen. Jedes neue Feature, jedes neue Control und jedes neue Abstraktionsmodul muss folgende Fragen überstehen:

1. *Funktioniert es ohne eine einzige neue Dependency?*
2. *Verhindert es unkontrollierte Speicher- und Handle-Leaks unter 32- und 64-Bit?*
3. *Erzeugt es eine pythonische, selbsterklärende API, ohne die C-Ebene unzugänglich zu machen?*
4. *Startet es noch immer in Millisekunden?*

Wenn eine Antwort Nein lautet, gehört der Code nicht in dieses Repository.

BareWinGUI ist kein Spielzeug für Allround-Experimente. Es ist das Werkzeug für Entwickler, die den Wert eines stabilen, lautlosen und unzerstörbaren Werkzeugs verstehen.