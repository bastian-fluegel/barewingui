# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.11] - 2026-09-19

### Added

- `VirtualKey` constants (`TAB`, `SHIFT`, `CONTROL`) for type-safe key handling.
- Tab navigation for multiline `TextInput` controls.
- Window smoke tests covering tab order and themed painting.

### Changed

- Layout engine now preserves natural control sizes instead of collapsing them on resize.
- Theme painting for buttons, edits, and static controls to keep a consistent light surface.

## [0.1.10] - 2026-09-19

### Added

- `theme` module with Sysinternals-style light canvas (`#F3F3F3`), white control surfaces, and Explorer visual styles.
- Custom painting for buttons and text inputs, including edit field margins.

### Changed

- Window and dialog chrome apply the new light theme.
- Examples and window verification updated to the themed look.

## [0.1.9] - 2026-09-19

### Removed

- Internal `.old/260917` archive directory (not part of the public API).

## [0.1.8] - 2026-09-19

### Changed

- Merged remote `main` with local work and resolved the README conflict.

## [0.1.7] - 2026-09-19

### Added

- Common Controls v6 activation-context manifest handling.
- Dialog message-handling tests and explicit resource cleanup.

### Changed

- README and specification docs with performance corridor and architecture notes.
- Window and control lifecycle in `core` / `window` for more reliable HWND management.

## [0.1.6] - 2026-09-19

### Fixed

- README license and “back to top” links (they previously pointed at Google Search).
- Document title anchor (`#document-title`) for in-page navigation.

## [0.1.5] - 2026-09-18

### Changed

- HTML technical reference: title, design-system variables for dark/light themes, sidebar, and navigation layout.

## [0.1.4] - 2026-09-18

### Added

- HTML technical reference (`docs/reference.html`) with dark/light theme.
- Forensic triage dashboard example (`examples/04_triage_tool.py`) showing responsive layout and native file pickers.

### Changed

- Dialog verification suite expanded around the new example flows.

## [0.1.3] - 2026-09-18

### Added

- Native `ComboBox` and `ListBox` selection controls.
- Convenience message boxes: `info_box`, `warning_box`, `error_box`, `confirm_box` / `ask_yes_no`.
- Choice-controls example (`examples/03_choice_controls.py`) and matching tests.

### Changed

- Window message processing for selection-control notifications.
- Dialog wrappers aligned with the new helper functions.

## [0.1.2] - 2026-09-18

### Added

- Window stack: `Application`, pointer-safe ctypes types, `Window`, `Button`, `CheckBox`, `RadioButton`, `Label`, `TextInput`.
- Box layout engine (`Box`, `VBox`, `HBox`).
- Examples `01_minimal_window.py` and `02_layout_showcase.py`.
- Window verification suite (`tests/verify_window.py`).
- Technical specifications in English (`SPECIFICATION.md`) and German (`SPEZIFIKATION.de.md`).

### Changed

- Project description and metadata in `pyproject.toml`.
- README with framework features, supported platforms, and installation.
- Public package exports in `barewingui/__init__.py`.

## [0.1.1] - 2026-09-17

### Added

- Native Win32 dialog wrappers: `message_box`, `input_box`, `open_file`, `save_file`, `pick_folder` / `select_folder`, `choose_color`, `choose_font`.
- Type-safe Win32 constants (`WM`, window styles, dialog flags).
- Dialog verification suite (`tests/verify_dialogs.py`).
- PEP 561 marker (`py.typed`).

### Changed

- `.gitignore` coverage for build artifacts and IDE files.

## [0.1.0] - 2026-09-17

### Added

- Project scaffold: MIT license, README, `pyproject.toml`, and `.gitignore`.

[unreleased]: https://github.com/bastian-fluegel/barewingui/compare/9830ab5...HEAD
[0.1.11]: https://github.com/bastian-fluegel/barewingui/compare/47388e4...9830ab5
[0.1.10]: https://github.com/bastian-fluegel/barewingui/compare/23f2f82...47388e4
[0.1.9]: https://github.com/bastian-fluegel/barewingui/compare/5cc3485...23f2f82
[0.1.8]: https://github.com/bastian-fluegel/barewingui/compare/40ffce4...5cc3485
[0.1.7]: https://github.com/bastian-fluegel/barewingui/compare/239144a...40ffce4
[0.1.6]: https://github.com/bastian-fluegel/barewingui/compare/5318c18...239144a
[0.1.5]: https://github.com/bastian-fluegel/barewingui/compare/79ce019...5318c18
[0.1.4]: https://github.com/bastian-fluegel/barewingui/compare/24693b3...79ce019
[0.1.3]: https://github.com/bastian-fluegel/barewingui/compare/0d72cd5...24693b3
[0.1.2]: https://github.com/bastian-fluegel/barewingui/compare/b61c094...0d72cd5
[0.1.1]: https://github.com/bastian-fluegel/barewingui/compare/809f707...b61c094
[0.1.0]: https://github.com/bastian-fluegel/barewingui/commit/809f707
