"""
barewingui.app
~~~~~~~~~~~~~~
Process setup (DPI awareness, Common Controls v6) and the message loop.

One :class:`App` exists per run. It owns the UI thread, the message loop and
the thread-safe :meth:`App.invoke` / :meth:`App.call` helpers.
"""

from __future__ import annotations

import atexit
import ctypes
import os
import tempfile
import threading
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, Callable, ClassVar, TypeVar

from barewingui import _api
from barewingui._api import comctl32, kernel32, user32
from barewingui._dispatch import ErrorPolicy, InvokeQueue

if TYPE_CHECKING:
    from barewingui.window import Window

T = TypeVar("T")

_MESSAGE_CLASS = "BareWinGUI.Messages"
_WM_INVOKE = _api.WM_APP + 1

# ICC_WIN95_CLASSES | ICC_STANDARD_CLASSES | ICC_DATE_CLASSES
_ICC_FLAGS = 0x000000FF | 0x00004000 | 0x00000100

_MANIFEST = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0" processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df" language="*" />
    </dependentAssembly>
  </dependency>
</assembly>
"""

# Process-wide state: these steps run once per process, not once per App.
_process_ready = False
_actctx_handle: Any = None
_actctx_cookie = _api.ULONG_PTR(0)
_manifest_path: str | None = None
_message_proc: Any = None  # keeps the C callback alive


def _enable_dpi_awareness() -> None:
    """Per-Monitor-V2 awareness: crisp text, correct sizes on every monitor."""
    ok = user32.SetProcessDpiAwarenessContext(
        ctypes.c_void_p(_api.DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
    )
    # ERROR_ACCESS_DENIED: the context was already set (manifest or host process).
    if not ok and ctypes.get_last_error() != _api.ERROR_ACCESS_DENIED:  # type: ignore[attr-defined]
        raise _api.last_error("SetProcessDpiAwarenessContext")


def _enable_visual_styles() -> None:
    """
    Activate Common Controls v6 for the process through an activation context.

    The manifest has to exist as a file; it gets a random name and is removed
    again at interpreter exit.
    """
    global _actctx_handle, _manifest_path
    fd, path = tempfile.mkstemp(prefix="barewingui-", suffix=".manifest")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(_MANIFEST)
    _manifest_path = path

    ctx = _api.ACTCTXW()
    ctx.cbSize = ctypes.sizeof(_api.ACTCTXW)
    ctx.lpSource = path
    handle = kernel32.CreateActCtxW(ctypes.byref(ctx))
    if handle in (None, 0, -1) or handle == ctypes.c_void_p(-1).value:
        raise _api.last_error("CreateActCtxW")
    if not kernel32.ActivateActCtx(handle, ctypes.byref(_actctx_cookie)):
        kernel32.ReleaseActCtx(handle)
        raise _api.last_error("ActivateActCtx")
    _actctx_handle = handle


def _init_common_controls() -> None:
    icex = _api.INITCOMMONCONTROLSEX()
    icex.dwSize = ctypes.sizeof(_api.INITCOMMONCONTROLSEX)
    icex.dwICC = _ICC_FLAGS
    if not comctl32.InitCommonControlsEx(ctypes.byref(icex)):
        raise _api.last_error("InitCommonControlsEx")


def _cleanup_process() -> None:
    global _actctx_handle, _manifest_path
    if _actctx_handle is not None:
        kernel32.DeactivateActCtx(0, _actctx_cookie.value)
        kernel32.ReleaseActCtx(_actctx_handle)
        _actctx_handle = None
    if _manifest_path is not None:
        try:
            os.unlink(_manifest_path)
        except OSError:
            pass
        _manifest_path = None


def _init_process() -> None:
    global _process_ready
    if _process_ready:
        return
    _enable_dpi_awareness()
    _enable_visual_styles()
    _init_common_controls()
    atexit.register(_cleanup_process)
    _process_ready = True


def _message_window_proc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    app = App._instance
    if app is not None and msg == _api.WM_TIMER:
        timer = app._timers.get(wparam)
        if timer is not None:
            try:
                timer._fire()
            except BaseException as exc:  # noqa: BLE001 - must not escape into native code
                app.errors.capture(exc)
        return 0
    if app is not None and msg == _WM_INVOKE:
        try:
            app._invoke.drain()
        except BaseException as exc:  # noqa: BLE001 - must not escape into native code
            app.errors.capture(exc)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


class App:
    """
    The application: message loop, error handling and cross-thread calls.

    Creating an :class:`App` more than once returns the same instance until
    :meth:`run` has finished. Windows create the app on demand, so
    ``App()`` is optional for single-window scripts.

    All UI work must happen on the thread that created the app. Other threads
    use :meth:`invoke` (fire and forget) or :meth:`call` (wait for the result).
    """

    _instance: ClassVar[App | None] = None
    _init_done: bool

    def __new__(cls) -> App:
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._init_done = False
            cls._instance = inst
        return cls._instance

    def __init__(self) -> None:
        if self._init_done:
            return
        try:
            _api.require_windows()
            self._thread = threading.get_ident()
            self._running = False
            self._exit_code = 0
            self._next_key = 1
            self._timers: dict[int, Any] = {}
            self._next_timer = 0
            self._pending: dict[int, Window] = {}
            self._windows: dict[int, Window] = {}
            self.errors = ErrorPolicy(stop=self._stop_loop)
            self._invoke = InvokeQueue(wake=self._wake, on_error=self.errors.capture)
            self._msg_hwnd: int | None = None
            _init_process()
            _api.ole32.CoInitializeEx(None, _api.COINIT_APARTMENTTHREADED)  # shell dialogs need an STA
            self._create_message_window()
        except BaseException:
            App._instance = None
            raise
        self._init_done = True

    # -- access --------------------------------------------------------------
    @classmethod
    def current(cls, create: bool = True) -> App | None:
        """The running app, creating it if necessary (when ``create`` is true)."""
        if cls._instance is not None and cls._instance._init_done:
            return cls._instance
        return cls() if create else None

    @property
    def on_error(self) -> Callable[[BaseException], None] | None:
        """Optional handler for exceptions raised in callbacks (keeps the loop running)."""
        return self.errors.handler

    @on_error.setter
    def on_error(self, handler: Callable[[BaseException], None] | None) -> None:
        self.errors.handler = handler

    # -- cross-thread calls --------------------------------------------------
    def invoke(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Run ``fn(*args, **kwargs)`` on the UI thread soon. Safe from any thread.
        An exception in ``fn`` is handled like any callback error.
        """
        self._invoke.submit(fn, args, kwargs, report=True)

    def call(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Run ``fn`` on the UI thread and return its result (or raise its exception).
        On the UI thread itself ``fn`` runs immediately.
        """
        if threading.get_ident() == self._thread:
            return fn(*args, **kwargs)
        return self._invoke.submit(fn, args, kwargs, report=False).result()

    # -- loop ----------------------------------------------------------------
    def run(self) -> int:
        """
        Show all windows that were not shown yet and run the message loop until
        the last window is closed or :meth:`quit` is called.

        :return: the exit code.
        :raises: the first exception raised in a callback, after the loop stopped.
        """
        self._check_thread()
        if self._running:
            raise RuntimeError("the message loop is already running")
        self._running = True
        try:
            for window in list(self._windows.values()):
                window._show_if_unseen()
            if self.errors.pending is None:  # an error before run() must not start the loop
                self._pump()
        finally:
            self._running = False
            self.shutdown()
        self.errors.raise_pending()
        return self._exit_code

    def quit(self, exit_code: int = 0) -> None:
        """Stop the message loop. Call on the UI thread (``app.invoke(app.quit)`` elsewhere)."""
        self._check_thread()
        if not self._running:
            raise RuntimeError("quit() needs a running message loop")
        self._exit_code = exit_code
        user32.PostQuitMessage(exit_code)

    def shutdown(self) -> None:
        """Destroy remaining windows and release the app (also done at the end of :meth:`run`)."""
        self._check_thread()
        self._running = False
        self._invoke.close()
        for window in list(self._windows.values()):
            window.destroy()
        if self._msg_hwnd:
            user32.DestroyWindow(self._msg_hwnd)
            self._msg_hwnd = None
        if App._instance is self:
            App._instance = None

    # -- internals -----------------------------------------------------------
    def _check_thread(self) -> None:
        if threading.get_ident() != self._thread:
            raise RuntimeError("this must be called on the thread that created the App")

    def _stop_loop(self) -> None:
        self._exit_code = 1
        if self._running:  # a WM_QUIT posted outside the loop would end the next run at once
            user32.PostQuitMessage(1)

    def _wake(self) -> None:
        hwnd = self._msg_hwnd
        if hwnd:
            user32.PostMessageW(hwnd, _WM_INVOKE, 0, 0)

    def _create_message_window(self) -> None:
        global _message_proc
        if _message_proc is None:
            _message_proc = _api.WNDPROC(_message_window_proc)
        _api.register_window_class(_MESSAGE_CLASS, _message_proc, cursor=False)
        hwnd = user32.CreateWindowExW(
            0, _MESSAGE_CLASS, "", 0, 0, 0, 0, 0,
            ctypes.c_void_p(_api.HWND_MESSAGE), None,
            kernel32.GetModuleHandleW(None), None,
        )
        if not hwnd:
            raise _api.last_error("CreateWindowExW (message window)")
        self._msg_hwnd = hwnd

    def _pump(self, until: Callable[[], bool] | None = None) -> None:
        """
        The message loop. With ``until`` (modal dialogs) it returns as soon as
        ``until()`` is true; a WM_QUIT seen then is passed on to the outer loop.
        """
        msg = wintypes.MSG()
        p_msg = ctypes.byref(msg)
        while True:
            if until is not None and until():
                return
            result = user32.GetMessageW(p_msg, None, 0, 0)
            if result == 0:  # WM_QUIT
                if until is not None:
                    user32.PostQuitMessage(int(msg.wParam))
                else:
                    self._exit_code = int(msg.wParam)
                return
            if result == -1:
                raise _api.last_error("GetMessageW")
            root = user32.GetAncestor(msg.hWnd, _api.GA_ROOT) if msg.hWnd else None
            window = self._windows.get(root) if root else None
            if window is not None:
                if window._haccel and user32.TranslateAcceleratorW(root, window._haccel, p_msg):
                    continue
                if user32.IsDialogMessageW(root, p_msg):
                    continue
            user32.TranslateMessage(p_msg)
            user32.DispatchMessageW(p_msg)
