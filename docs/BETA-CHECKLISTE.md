# BareWinGUI: Weg zu Beta (0.2.0-beta)

Stand: 13.10.2026, ausgehend von 0.1.11 (Alpha). Sortiert nach Aufwand. Abhaken, wenn wirklich erledigt.
Hinweis: Nach README, Changelog und pyproject.toml erstellt; Code und Tests wurden nicht gelesen.

## Beta-Definition (festlegen, bevor es losgeht)
- [ ] Kern-API ist benannt und stabil; was wackelt, steht als „experimentell" in der Doku
- [ ] Tests laufen automatisch in CI auf Windows
- [ ] Installation per `pip install barewingui` (PyPI)
- [ ] Bekannte Grenzen sind dokumentiert
- [ ] Classifier in pyproject: `Development Status :: 4 - Beta`

## 1. Schnell (je unter 1 Stunde)
- [ ] Prüfen, ob die „Unreleased"-Änderungen (README Status/Limits, Workflow, CVE-Text) gepusht sind (`git status`, `git push`)
- [ ] Stand `0.1.11` mit Tag `v0.1.11` und GitHub-Release markieren
- [ ] README: „Window (Preview)" streichen, Fenster gilt seit 0.1.2
- [ ] README: Positionierung auf „reines GUI-Projekt" umstellen (Forensik/OT/SCADA/KRITIS auf eine Zeile „Eignet sich z. B. für"), Demos neutral benennen
- [ ] README: sauberen Screenshot einer neutralen Demo-App einbauen (Win+Shift+S, kein Handyfoto)
- [ ] Repo-Beschreibung und Topics auf GitHub setzen (python, win32, ctypes, gui, windows)

## 2. Mittel (halber Tag)
- [ ] CI: Workflow nicht nur manuell, sondern bei Push und Pull Request
- [ ] CI: Matrix Python 3.11, 3.12, 3.13 auf `windows-latest` (x64); x86 über `setup-python` mit `architecture: x86`
- [ ] Tests auf pytest umstellen (`verify_*.py` bleiben als Smoke-Tests oder werden Tests)
- [ ] Ruff und mypy in pyproject konfigurieren, in CI laufen lassen
- [ ] Benchmarks real auf Windows messen (RAM im Leerlauf, Kaltstart), Werte in README eintragen oder Zahlen streichen
- [ ] `SECURITY.md` (Meldeweg), Issue-Vorlagen, kurzes `CONTRIBUTING.md`

## 3. Größer (mehrere Sessions)
- [ ] Feature-Umfang für Beta entscheiden, im Changelog stehen aktuell nicht: Menüleiste, Statusleiste, Tabs, Tabelle/Baum, Fortschrittsbalken, Tastenkürzel, Timer, thread-sicheres UI-Update, DPI-Verhalten
  - [ ] Pro Punkt: „kommt in Beta" oder „ausdrücklich später" (in Doku unter „Bekannte Grenzen")
- [ ] DPI-Awareness (Manifest, Skalierung bei Monitorwechsel) prüfen und dokumentieren
- [ ] Unicode und IME (Eingabe in TextInput) testen
- [ ] API-Referenz aus den Docstrings erzeugen oder `docs/reference.html` auf Stand bringen
- [ ] Beispiele auf neutralen Satz bringen (Hello, Layout, Formular, Auswahl, Dialoge)

## 4. Veröffentlichung
- [ ] Probelauf auf TestPyPI (Trusted Publishing über GitHub Actions)
- [ ] `0.2.0-beta` taggen, Release mit Changelog-Auszug, PyPI-Upload
- [ ] Website-Projekttext und LinkedIn-Artikel erst jetzt auf die Beta stützen

## Offen, bewusst später
- [ ] ARM64 (Windows-on-ARM) testen, aktuell „experimentell/ungetestet"
- [ ] Mac-Schicht erst beginnen, wenn dieser Punkt hier fertig ist
