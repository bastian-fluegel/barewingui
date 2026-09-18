"""
barewingui.core
~~~~~~~~~~~~~~~
Application lifecycle, Per-Monitor DPI Awareness, and Windows Common Controls v6 initialization.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import TYPE_CHECKING, ClassVar

from barewingui.types import (
    INITCOMMONCONTROLSEX,
    comctl32,
    gdi32,
    kernel32,
    user32,
)

if TYPE_CHECKING:
    from barewingui.window import Window


# ---------------------------------------------------------------------------
# DPI Awareness Konstanten
# ---------------------------------------------------------------------------
# DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 (Windows 10 Creators Update / 1703+)
_DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)

# ---------------------------------------------------------------------------
# Common Controls Flags (comctl32.dll v6)
# ---------------------------------------------------------------------------
_ICC_WIN95_CLASSES = 0x000000FF
_ICC_STANDARD_CLASSES = 0x00004000
_DEFAULT_ICC_FLAGS = _ICC_WIN95_CLASSES | _ICC_STANDARD_CLASSES

_SYSTEM_FONT: wintypes.HANDLE | None = None


def get_system_font() -> wintypes.HANDLE:
    """Erzeugt die offizielle Windows 10/11 Segoe UI Schriftart mit ClearType-Glättung."""
    global _SYSTEM_FONT
    if _SYSTEM_FONT is None:
        _SYSTEM_FONT = gdi32.CreateFontW(
            -12,                    # Höhe (entspricht ca. 9pt bei Standard-DPI)
            0, 0, 0,
            400,                    # FW_NORMAL
            0, 0, 0,                # Italic, Underline, StrikeOut
            1,                      # DEFAULT_CHARSET
            0, 0,                   # OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS
            5,                      # CLEARTYPE_QUALITY
            0,                      # DEFAULT_PITCH | FF_DONTCARE
            "Segoe UI"              # Offizielle UI-Schriftart ab Windows Vista/10/11
        )
    return _SYSTEM_FONT


def init_dpi_awareness() -> bool:
    """
    Aktiviert Per-Monitor-DPI-Awareness v2 für gestochen scharfe Schrift
    und akkurates Control-Rendering auf High-DPI- und Multi-Monitor-Setups.
    """
    if hasattr(user32, "SetProcessDpiAwarenessContext"):
        success = user32.SetProcessDpiAwarenessContext(
            _DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        )
        if success:
            return True
        # Wenn der Aufruf fehlschlägt (z. B. bereits im Host-Prozess gesetzt),
        # wird kein Fehler geworfen, sondern auf System-Status geprüft.
        err = kernel32.GetLastError()
        # 5 = ERROR_ACCESS_DENIED (DPI-Kontext bereits festgelegt)
        return err == 5

    # Fallback für frühe Windows 10 Builds
    if hasattr(user32, "SetProcessDPIAware"):
        return bool(user32.SetProcessDPIAware())

    return False


def init_common_controls(flags: int = _DEFAULT_ICC_FLAGS) -> bool:
    """
    Registriert die modernen Windows Common Controls (comctl32.dll v6)
    für Buttons, Textfelder, Progressbars und Auswahlelemente.
    """
    if not comctl32 or not hasattr(comctl32, "InitCommonControlsEx"):
        return False

    icex = INITCOMMONCONTROLSEX()
    icex.dwSize = ctypes.sizeof(INITCOMMONCONTROLSEX)
    icex.dwICC = flags
    return bool(comctl32.InitCommonControlsEx(ctypes.byref(icex)))


class Application:
    """
    Zentraler Verwalter für Prozess-Initialisierung, Windows-Message-Pump
    und Anwendungs-Lebenszyklus.
    """

    _is_initialized: ClassVar[bool] = False
    _main_window: Window | None = None

    @classmethod
    def initialize(cls) -> None:
        """
        Initialisiert DPI-Awareness und Common Controls einmalig pro Prozess.
        Wird automatisch vor dem ersten Fensteraufruf ausgeführt.
        """
        if cls._is_initialized:
            return

        init_dpi_awareness()
        init_common_controls()
        cls._is_initialized = True

    @classmethod
    def run(cls, main_window: Window | None = None) -> int:
        """
        Startet die native Win32-Message-Loop und blockiert, bis PostQuitMessage
        aufgerufen wird.

        :param main_window: Optionales Hauptfenster, dessen Anzeige erzwungen wird.
        :return: Exit-Code der Anwendung (wParam aus WM_QUIT).
        """
        cls.initialize()

        if main_window is not None:
            cls._main_window = main_window
            main_window.show()

        msg = wintypes.MSG()
        p_msg = ctypes.byref(msg)

        # GetMessageW liefert > 0 für reguläre Messages, 0 bei WM_QUIT, -1 bei schwerem Fehler
        while user32.GetMessageW(p_msg, None, 0, 0) > 0:
            user32.TranslateMessage(p_msg)
            user32.DispatchMessageW(p_msg)

        return int(msg.wParam)

    @classmethod
    def quit(cls, exit_code: int = 0) -> None:
        """Beendet die Message-Loop kontrolliert mit dem angegebenen Exit-Code."""
        user32.PostQuitMessage(exit_code)