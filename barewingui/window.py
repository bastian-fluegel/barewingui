"""
barewingui.window
~~~~~~~~~~~~~~~~~
Native Win32 window implementation with RAII lifecycle management,
GC-safe WNDPROC anchoring, and type-safe event dispatching.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Self

from barewingui.constants import (
    ShowWindowCmd,
    StockObject,
    SysColor,
    WindowLong,
    WindowStyle,
    WindowStyleEx,
    WM,
)
from barewingui.core import Application
from barewingui.types import (
    LONG_PTR,
    LPARAM,
    LRESULT,
    WPARAM,
    WNDCLASSEXW,
    WNDPROC,
    GetWindowLongPtrW,
    SetWindowLongPtrW,
    gdi32,
    kernel32,
    user32,
)

if TYPE_CHECKING:
    from barewingui.controls.base import Control

# Standard-Windows-Konstanten für Fensterpositionierung
CW_USEDEFAULT: int = -0x80000000
IDC_ARROW = ctypes.c_wchar_p(32512)


def _loword(val: int) -> int:
    return val & 0xFFFF


def _hiword(val: int) -> int:
    return (val >> 16) & 0xFFFF


class Window:
    """
    Kapselt ein natives Win32-Top-Level-Fenster (HWND) inklusive Message-Dispatching,
    automatischem Handle-Cleanup (RAII) und Callback-Verankerung.
    """

    _CLASS_NAME: ClassVar[str] = "BareWinGUI_Window"
    _class_registered: ClassVar[bool] = False
    _wndproc_anchor: ClassVar[WNDPROC | None] = None
    _active_windows: ClassVar[dict[int, Window]] = {}
    _pending_window: ClassVar[Window | None] = None

    def __init__(
        self,
        title: str = "BareWinGUI Application",
        width: int = 800,
        height: int = 600,
        x: int = CW_USEDEFAULT,
        y: int = CW_USEDEFAULT,
        style: WindowStyle = WindowStyle.OVERLAPPEDWINDOW,
        ex_style: WindowStyleEx = WindowStyleEx.APPWINDOW,
    ) -> None:
        self._title = title
        self._width = width
        self._height = height
        self._x = x
        self._y = y
        self._style = style
        self._ex_style = ex_style

        self._hwnd: wintypes.HWND | None = None
        self._controls: dict[int, Control] = {}
        self._next_control_id: int = 1000

        # Event-Hooks für Anwendungslogik
        self.on_close: Callable[[], bool | None] | None = None
        self.on_destroy: Callable[[], None] | None = None
        self.on_resize: Callable[[int, int], None] | None = None
        self.on_command: Callable[[int, int, int], None] | None = None

        Application.initialize()
        self._ensure_class_registered()
        self._create_native_window()

    @property
    def hwnd(self) -> wintypes.HWND:
        if self._hwnd is None:
            raise RuntimeError("Fenster wurde nicht initialisiert oder zerstört.")
        return self._hwnd

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        if self._hwnd:
            user32.SetWindowTextW(self._hwnd, value)

    @classmethod
    def _ensure_class_registered(cls) -> None:
        """Registriert die WNDCLASSEXW-Struktur einmalig pro Prozess."""
        if cls._class_registered:
            return

        # Dauerhafte Referenz hält den C-Funktionszeiger im Speicher gegen GC-Löschung
        cls._wndproc_anchor = WNDPROC(cls._static_wnd_proc)

        h_instance = kernel32.GetModuleHandleW(None)
        h_cursor = user32.LoadCursorW(None, IDC_ARROW)
        h_brush = user32.GetSysColorBrush(SysColor.WINDOW)

        wcex = WNDCLASSEXW()
        wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wcex.style = 0x0002 | 0x0001  # CS_HREDRAW | CS_VREDRAW
        wcex.lpfnWndProc = cls._wndproc_anchor
        wcex.cbClsExtra = 0
        wcex.cbWndExtra = 0
        wcex.hInstance = h_instance
        wcex.hIcon = None
        wcex.hCursor = h_cursor
        wcex.hbrBackground = h_brush
        wcex.lpszMenuName = None
        wcex.lpszClassName = cls._CLASS_NAME
        wcex.hIconSm = None

        atom = user32.RegisterClassExW(ctypes.byref(wcex))
        if not atom:
            err = kernel32.GetLastError()
            # 1410 = ERROR_CLASS_ALREADY_EXISTS
            if err != 1410:
                raise RuntimeError(f"Konnte Fensterklasse nicht registrieren (Fehler {err})")

        cls._class_registered = True

    def _create_native_window(self) -> None:
        """Erzeugt das Betriebssystem-Fenster und verdrahtet die Instanz."""
        h_instance = kernel32.GetModuleHandleW(None)
        Window._pending_window = self

        hwnd = user32.CreateWindowExW(
            int(self._ex_style),
            self._CLASS_NAME,
            self._title,
            int(self._style),
            self._x,
            self._y,
            self._width,
            self._height,
            None,
            None,
            h_instance,
            None,
        )

        Window._pending_window = None

        if not hwnd:
            raise RuntimeError(
                f"CreateWindowExW fehlgeschlagen (Fehler {kernel32.GetLastError()})"
            )

        self._hwnd = hwnd
        self._active_windows[hwnd] = self
        SetWindowLongPtrW(hwnd, int(WindowLong.USERDATA), LONG_PTR(hwnd))

    @staticmethod
    def _static_wnd_proc(
        hwnd: wintypes.HWND, msg: int, wparam: WPARAM, lparam: LPARAM
    ) -> LRESULT:
        """Zentraler Win32-Router: Leitet Systemnachrichten an das Zielobjekt."""
        win = Window._active_windows.get(hwnd)

        # Abfangen während der Erstellungsphase
        if win is None and Window._pending_window is not None:
            win = Window._pending_window
            win._hwnd = hwnd
            Window._active_windows[hwnd] = win

        if win is not None:
            return win._handle_message(hwnd, msg, wparam, lparam)

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _handle_message(
        self, hwnd: wintypes.HWND, msg: int, wparam: WPARAM, lparam: LPARAM
    ) -> LRESULT:
        """Instanzspezifische Nachrichtenverarbeitung."""
        match msg:
            case WM.CLOSE:
                if self.on_close:
                    should_close = self.on_close()
                    if should_close is False:
                        return 0
                self.destroy()
                return 0

            case WM.DESTROY:
                # Fenster sauber aus Registry austragen
                if hwnd in self._active_windows:
                    del self._active_windows[hwnd]
                self._hwnd = None

                if self.on_destroy:
                    self.on_destroy()

                # Wenn kein Fenster mehr aktiv ist, Message-Loop beenden und Python freigeben
                if not self._active_windows:
                    user32.PostQuitMessage(0)
                return 0

            case WM.SIZE:
                new_width = _loword(lparam)
                new_height = _hiword(lparam)
                self._width = new_width
                self._height = new_height
                if self.on_resize:
                    self.on_resize(new_width, new_height)
                return 0

            case WM.COMMAND:
                control_id = _loword(wparam)
                notification_code = _hiword(wparam)
                control = self._controls.get(control_id)
                if control is not None:
                    control._handle_command(notification_code)
                if self.on_command:
                    self.on_command(control_id, notification_code, lparam)
                return 0

            case WM.CTLCOLORSTATIC:
                hdc = wintypes.HDC(wparam)
                # 1 = TRANSPARENT (Hintergrund nicht deckend übermalen)
                gdi32.SetBkMode(hdc, 1)
                # Reinen Python-int des Brush-Handles zurückgeben (keine ctypes-Klasse)
                brush = user32.GetSysColorBrush(int(SysColor.WINDOW))
                return int(brush) if brush else 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def destroy(self) -> None:
        """Zerstört das native HWND deterministisch (RAII)."""
        if self._hwnd:
            hwnd_to_destroy = self._hwnd
            # Erst Windows zerstören lassen (löst synchron WM_DESTROY aus), danach Nullen
            user32.DestroyWindow(hwnd_to_destroy)
            self._hwnd = None

    def register_control(self, control: Control) -> int:
        """Registriert ein Child-Control und vergibt eine fortlaufende ID."""
        control_id = self._next_control_id
        self._next_control_id += 1
        self._controls[control_id] = control
        return control_id

    def show(self, cmd: ShowWindowCmd = ShowWindowCmd.SHOWNORMAL) -> None:
        """Macht das Fenster sichtbar und erzwingt den ersten Render-Pass."""
        if self._hwnd:
            user32.ShowWindow(self._hwnd, int(cmd))
            user32.UpdateWindow(self._hwnd)

    def hide(self) -> None:
        """Versteckt das Fenster."""
        if self._hwnd:
            user32.ShowWindow(self._hwnd, int(ShowWindowCmd.HIDE))

    def close(self) -> None:
        """Sendet ein WM_CLOSE an das Fenster."""
        if self._hwnd:
            user32.PostMessageW(self._hwnd, int(WM.CLOSE), 0, 0)

    def run(self) -> int:
        """Startet die Message-Pumpe der Application für dieses Fenster."""
        return Application.run(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.destroy()

    def __del__(self) -> None:
        self.destroy()