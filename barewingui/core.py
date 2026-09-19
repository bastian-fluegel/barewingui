"""
barewingui.core
~~~~~~~~~~~~~~~
Application lifecycle, Per-Monitor DPI Awareness, and Windows Common Controls v6 initialization.
"""

from __future__ import annotations

import atexit
import ctypes
import os
import tempfile
from ctypes import wintypes
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from barewingui.constants import EditStyle, VirtualKey, WindowLong, WM
from barewingui.types import (
    ACTCTXW,
    DWMWA_USE_IMMERSIVE_DARK_MODE,
    DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
    DWMWA_WINDOW_CORNER_PREFERENCE,
    DWMWCP_ROUND,
    GA_ROOT,
    INITCOMMONCONTROLSEX,
    ULONG_PTR,
    GetWindowLongPtrW,
    dwmapi,
    gdi32,
    kernel32,
    load_comctl32,
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
_ACTCTX_COOKIE = ULONG_PTR(0)
_H_ACTCTX: wintypes.HANDLE | None = None

_MANIFEST_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>
"""


def get_system_font() -> wintypes.HANDLE:
    """Erzeugt Segoe UI Variable (Win11) bzw. Segoe UI mit ClearType-Glättung."""
    global _SYSTEM_FONT
    if _SYSTEM_FONT is None:
        _SYSTEM_FONT = gdi32.CreateFontW(
            -14,                    # ~14px Body-Größe unter Windows 11
            0, 0, 0,
            400,                    # FW_NORMAL
            0, 0, 0,                # Italic, Underline, StrikeOut
            1,                      # DEFAULT_CHARSET
            0, 0,                   # OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS
            5,                      # CLEARTYPE_QUALITY
            0,                      # DEFAULT_PITCH | FF_DONTCARE
            "Segoe UI Variable Text",
        )
        if _is_invalid_handle(_SYSTEM_FONT):
            _SYSTEM_FONT = gdi32.CreateFontW(
                -14, 0, 0, 0, 400, 0, 0, 0, 1, 0, 0, 5, 0, "Segoe UI"
            )
    return _SYSTEM_FONT


def _is_invalid_handle(handle: object) -> bool:
    if handle in (None, 0, -1):
        return True
    raw = getattr(handle, "value", handle)
    if raw in (None, 0, -1):
        return True
    return int(raw) == int(ctypes.c_void_p(-1).value or 0)


def _write_manifest_atomic(path: Path, payload: bytes) -> bool:
    """Schreibt das ComCtl-v6-Manifest atomar nach %TEMP%."""
    try:
        if path.exists() and path.read_bytes() == payload:
            return True
    except OSError:
        pass

    fd, tmp_name = tempfile.mkstemp(
        prefix="barewingui_comctl6_",
        suffix=".manifest",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
        os.replace(tmp_name, path)
        return True
    except OSError:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        return path.exists()


def enable_visual_styles() -> bool:
    """Aktiviert Windows Common Controls v6 dynamisch über einen Activation Context."""
    global _H_ACTCTX, _ACTCTX_COOKIE
    if _H_ACTCTX and not _is_invalid_handle(_H_ACTCTX):
        return True

    manifest_path = Path(tempfile.gettempdir()) / "barewingui_comctl6.manifest"
    if not _write_manifest_atomic(manifest_path, _MANIFEST_XML.encode("utf-8")):
        return False

    act = ACTCTXW()
    act.cbSize = ctypes.sizeof(ACTCTXW)
    act.lpSource = str(manifest_path)

    h_actctx = kernel32.CreateActCtxW(ctypes.byref(act))
    if _is_invalid_handle(h_actctx):
        return False

    _H_ACTCTX = h_actctx
    success = kernel32.ActivateActCtx(_H_ACTCTX, ctypes.byref(_ACTCTX_COOKIE))
    if not success:
        kernel32.ReleaseActCtx(_H_ACTCTX)
        _H_ACTCTX = None
        return False
    return True


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
    comctl32 = load_comctl32()
    if not comctl32 or not hasattr(comctl32, "InitCommonControlsEx"):
        return False

    icex = INITCOMMONCONTROLSEX()
    icex.dwSize = ctypes.sizeof(INITCOMMONCONTROLSEX)
    icex.dwICC = flags
    return bool(comctl32.InitCommonControlsEx(ctypes.byref(icex)))


def apply_window_chrome(hwnd: wintypes.HWND) -> None:
    """
    Sysinternals-Look: Light-Titelleiste und runde Win11-Ecken.
    Die Caption wird fest hell gehalten, passend zum #F3F3F3-Canvas.
    """
    if not hwnd or dwmapi is None:
        return

    def _set(attr: int, value: int) -> None:
        data = ctypes.c_int(value)
        dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(data), ctypes.sizeof(data))

    _set(DWMWA_USE_IMMERSIVE_DARK_MODE, 0)
    _set(DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, 0)
    _set(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)


def _cleanup_gdi() -> None:
    global _SYSTEM_FONT, _H_ACTCTX
    from barewingui.theme import cleanup_theme

    cleanup_theme()
    if _SYSTEM_FONT:
        gdi32.DeleteObject(_SYSTEM_FONT)
        _SYSTEM_FONT = None
    if _H_ACTCTX and not _is_invalid_handle(_H_ACTCTX):
        kernel32.DeactivateActCtx(0, _ACTCTX_COOKIE)
        kernel32.ReleaseActCtx(_H_ACTCTX)
        _H_ACTCTX = None


atexit.register(_cleanup_gdi)


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
        enable_visual_styles()
        init_common_controls()
        from barewingui.theme import init_theme

        init_theme()
        cls._is_initialized = True

    @classmethod
    def run(cls, main_window: Window | None = None) -> int:
        """
        Startet die native Win32-Message-Loop und blockiert, bis PostQuitMessage
        aufgerufen wird.

        :param main_window: Optionelles Hauptfenster, dessen Anzeige erzwungen wird.
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
            # Ermittle das zugehörige Top-Level-Fenster der Nachricht
            root_hwnd = user32.GetAncestor(msg.hWnd, GA_ROOT) if msg.hWnd else None

            # ES_MULTILINE beansprucht Tab (DLGC_WANTTAB). IsDialogMessageW
            # würde den Sprung schlucken — daher vorab GetNextDlgTabItem.
            if root_hwnd and _tab_out_of_multiline_edit(root_hwnd, msg):
                continue

            # IsDialogMessage verarbeitet Tab, Return, ESC und Pfeiltasten für Controls
            if root_hwnd and user32.IsDialogMessageW(root_hwnd, p_msg):
                continue

            user32.TranslateMessage(p_msg)
            user32.DispatchMessageW(p_msg)

        return int(msg.wParam)

    @classmethod
    def quit(cls, exit_code: int = 0) -> None:
        """Beendet die Message-Loop kontrolliert mit dem angegebenen Exit-Code."""
        user32.PostQuitMessage(exit_code)


def _key_down(vk: int) -> bool:
    return bool(user32.GetKeyState(vk) & 0x8000)


def _class_name(hwnd: wintypes.HWND) -> str:
    buf = ctypes.create_unicode_buffer(32)
    user32.GetClassNameW(hwnd, buf, 32)
    return buf.value


def _hwnd_int(hwnd: object) -> int:
    if not hwnd:
        return 0
    raw = getattr(hwnd, "value", hwnd)
    return 0 if raw is None else int(raw)


def _tab_out_of_multiline_edit(root_hwnd: wintypes.HWND, msg: wintypes.MSG) -> bool:
    """
    Springt bei Tab aus einem mehrzeiligen Edit zum nächsten Dialog-Tab-Item.
    Gibt True zurück, wenn die Taste verarbeitet wurde.
    """
    if msg.message != int(WM.KEYDOWN) or int(msg.wParam) != int(VirtualKey.TAB):
        return False
    if _key_down(int(VirtualKey.CONTROL)):
        return False

    focus_hwnd = user32.GetFocus()
    if not focus_hwnd:
        return False
    if _class_name(focus_hwnd).upper() != "EDIT":
        return False

    style = int(GetWindowLongPtrW(focus_hwnd, int(WindowLong.STYLE)))
    if not (style & int(EditStyle.MULTILINE)):
        return False

    backwards = _key_down(int(VirtualKey.SHIFT))
    next_ctl = user32.GetNextDlgTabItem(root_hwnd, focus_hwnd, backwards)
    if not next_ctl or _hwnd_int(next_ctl) == _hwnd_int(focus_hwnd):
        return False

    user32.SetFocus(next_ctl)
    return True
