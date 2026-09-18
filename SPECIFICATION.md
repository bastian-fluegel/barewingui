# BareWinGUI – Technical Specification & Constraints

## 1. Project Identity & Philosophy
* **Name:** BareWinGUI (`barewingui`)
* **Objective:** Ultra-lightweight, deterministic Windows GUI framework built directly on native Win32 APIs.
* **Core Principle:** *Zero-Dependency.* Absolute elimination of third-party wheels, C++ runtime dependencies, and web engines.
* **Target Audience:** Systems administration, incident response, OT/SCADA human-machine interfaces, digital forensics, and hardened enterprise networks.

## 2. Supported Platforms & Runtime
* **Operating Systems:** Windows 10 (Build 1809+), Windows 11, Windows Server (2016+).
* **Baseline Limit:** Windows 10 (Windows 7/8/8.1 are strictly unsupported).
* **CPU Architectures:** x64 (64-bit), x86 (32-bit), ARM64.
* **Python Runtime:** Python >= 3.11 (strictly typed, leveraging modern union types, slots, and stdlib performance enhancements).

## 3. Architectural Invariants
* **Dependencies:** `dependencies = []`. Only standard library modules are permitted (`ctypes`, `wintypes`, `enum`, `dataclasses`, `typing`, `sys`, `math`).
* **Pointer Adaptability:** Zero hardcoded pointer widths. Messages and handles must adapt dynamically via `ctypes.c_ssize_t`, `wintypes.WPARAM`, `wintypes.LPARAM`, and `wintypes.HWND`.
* **Resource Safety (RAII):** Every allocated OS handle (`HWND`, `HDC`, `HGDIOBJ`, `PIDL`) must be tied to a predictable lifecycle and destroyed deterministically (`DestroyWindow`, `DeleteDC`, `DeleteObject`, `CoTaskMemFree`).
* **Garbage Collector Anchoring:** Window procedure function pointers (`WNDPROC`) must remain referenced in memory for the lifespan of the window to prevent silent fatal access violations.
* **Look & Feel:** No proprietary theme engines or CSS emulators. Controls render strictly via native Windows Common Controls v6 (`comctl32.dll`) using current system typography (`Segoe UI`).

## 4. Non-Goals
* No cross-platform abstraction (no Linux, no macOS).
* No web/DOM runtimes.
* No custom skinning or legacy OS theme emulation.
* No backward compatibility for end-of-life Python releases (< 3.11).

## 5. Performance Budget
* **Idle Memory:** < 15 MB RAM.
* **Cold Start Time:** < 15 ms to first interactive frame.
* **Frozen Binary Footprint:** < 12 MB (via PyInstaller / Nuitka).