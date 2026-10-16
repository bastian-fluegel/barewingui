"""
Support helper: the kind of small tool an admin or first-level support person builds
in an afternoon. Tabs, group boxes, list views, a worker thread, a status bar and a
save dialog, all native Windows controls.

Run it with ``python examples/06_support_helper.py``.
"""

from __future__ import annotations

import datetime as dt
import getpass
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import threading
import time

from barewingui import (
    App, Button, GroupBox, HBox, Label, ListView, ProgressBar, Spacer, StatusBar,
    TabControl, TabPage, VBox, Window, save_file, show_error, show_info,
)
import barewingui

# What the network tab checks: (title, kind, target)
CHECKS = [
    ("Internet (Cloudflare)", "ping", "1.1.1.1"),
    ("Internet (Google)", "ping", "8.8.8.8"),
    ("Name resolution", "dns", "pypi.org"),
    ("Name resolution", "dns", "github.com"),
    ("Secure web (HTTPS)", "tcp", "pypi.org"),
]


# -- helpers without any GUI (tested on every platform) ---------------------------------
def human_size(size: float) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return str(size)


def windows_name() -> str:
    """'Windows 11 (build 26100)' - the build number tells 10 and 11 apart."""
    version = getattr(sys, "getwindowsversion", None)
    if version is None:
        return platform.platform()
    build = version().build
    return f"Windows {11 if build >= 22000 else 10} (build {build})"


def local_ip() -> str:
    """The address this PC uses to reach the network (no packet is sent)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 9))
            return sock.getsockname()[0]
    except OSError:
        return "not connected"


def uptime_text() -> str:
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        kernel32.GetTickCount64.restype = ctypes.c_uint64
        seconds = kernel32.GetTickCount64() // 1000
    except (AttributeError, OSError):
        return "unknown"
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    return f"{days} d {hours} h {rest // 60} min" if days else f"{hours} h {rest // 60} min"


def system_facts() -> list[tuple[str, str]]:
    """The 'This PC' table: (property, value)."""
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 - no user name available
        user = "unknown"
    return [
        ("Computer name", platform.node() or "unknown"),
        ("User", user),
        ("Operating system", windows_name()),
        ("IP address", local_ip()),
        ("Processors", str(os.cpu_count() or "unknown")),
        ("Running since boot", uptime_text()),
        ("Python", platform.python_version()),
        ("BareWinGUI", barewingui.__version__),
    ]


def drive_rows() -> list[tuple[str, str, str, str]]:
    """Fixed and removable drives: (drive, size, free, used in percent)."""
    rows = []
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        try:
            if not os.path.exists(root):
                continue
            usage = shutil.disk_usage(root)
        except OSError:
            continue
        used = round(100 * usage.used / usage.total) if usage.total else 0
        rows.append((root, human_size(usage.total), human_size(usage.free), f"{used} %"))
    return rows


def parse_ping(output: str) -> tuple[bool, str]:
    """(reachable, time) from the output of Windows' ping, in any language."""
    if "TTL=" not in output.upper():
        return False, ""
    match = re.search(r"[=<]\s*(\d+)\s*ms", output)
    return True, (f"{match.group(1)} ms" if match else "")


def run_check(kind: str, target: str) -> tuple[bool, str]:
    """One network check. Slow (it waits for the network): call it from a worker thread."""
    started = time.perf_counter()
    try:
        if kind == "ping":
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1500", target],
                capture_output=True, timeout=6, creationflags=flags,
            )
            # ping prints in the console's OEM code page (not UTF-8): read bytes, ignore umlauts
            return parse_ping(result.stdout.decode("ascii", errors="ignore"))
        if kind == "dns":
            socket.gethostbyname(target)
        elif kind == "tcp":
            socket.create_connection((target, 443), timeout=3).close()
        else:
            raise ValueError(kind)
    except Exception:  # noqa: BLE001 - a failing check must not stop the others
        return False, ""
    return True, f"{(time.perf_counter() - started) * 1000:.0f} ms"


def format_report(facts, checks, drives) -> str:
    """The whole picture as plain text, ready to attach to a ticket."""
    lines = [f"Support report - {dt.datetime.now():%Y-%m-%d %H:%M}", "", "This PC"]
    lines += [f"  {name + ':':<22}{value}" for name, value in facts]
    if drives:
        lines += ["", "Drives"]
        lines += [f"  {d:<6}{size:>10} total{free:>10} free{used:>7} used" for d, size, free, used in drives]
    if checks:
        lines += ["", "Network"]
        lines += [f"  {title:<24}{target:<14}{result:<14}{took}" for title, target, result, took in checks]
    return "\n".join(lines) + "\n"


# -- the window ------------------------------------------------------------------------------
def build(autorun: bool = False) -> Window:
    """The window. With ``autorun`` the network checks start right away."""
    app = App.current()
    facts = system_facts()
    drives = drive_rows()
    with Window("Support Helper", size=(680, 410)) as win:
        status = StatusBar(parts=[420, None])
        with VBox(padding=12, gap=10):
            with TabControl(grow=1):
                with TabPage("This PC"):
                    with GroupBox("System", grow=1):
                        system = ListView([("Property", 190), ("Value", 400)], facts, grid=True, grow=1)
                with TabPage("Network"):
                    with GroupBox("Connection check", grow=1):
                        network = ListView(
                            [("Check", 190), ("Target", 130), ("Result", 110), ("Time", 80)],
                            grid=True, grow=1,
                        )
                        with HBox(gap=10):
                            busy = ProgressBar(0, indeterminate=True, grow=1, visible=False)
                            Spacer(grow=1)
                            run = Button("Run checks")
                with TabPage("Drives"):
                    with GroupBox("Local drives", grow=1):
                        disks = ListView(
                            [("Drive", 90), ("Size", 120), ("Free", 120), ("Used", 90)],
                            drives, grid=True, grow=1,
                        )
            with HBox(gap=8):
                Spacer(grow=1)
                save = Button("Save report...")
                close = Button("Close", default=True)

    results: list[tuple[str, str, str, str]] = []

    def add_result(index: int, ok: bool, took: str) -> None:  # UI thread
        if not win.alive:
            return
        title, _, target = CHECKS[index]
        text = "✓ reachable" if ok else "✗ failed"
        results.append((title, target, text, took))
        network.add_row([title, target, text, took])

    def finished() -> None:  # UI thread
        if not win.alive:
            return
        busy.visible = False
        run.enabled = True
        failed = sum(1 for r in results if r[2].startswith("✗"))
        status.text = "All checks passed." if not failed else f"{failed} of {len(results)} checks failed."

    def work() -> None:  # worker thread: never touch controls here
        for index, (_, kind, target) in enumerate(CHECKS):
            ok, took = run_check(kind, target)
            app.invoke(add_result, index, ok, took)
        app.invoke(finished)

    def start() -> None:
        results.clear()
        network.clear()
        run.enabled = False
        busy.visible = True
        status.text = "Checking..."
        threading.Thread(target=work, daemon=True).start()

    def save_report() -> None:
        path = save_file(
            "Save report", filters=[("Text file", "*.txt")], default_ext="txt",
            initial_name=f"support-{platform.node()}.txt", parent=win,
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(format_report(facts, results, drives))
        except OSError as error:
            show_error(f"Could not save the report:\n{error}", "Support Helper", parent=win)
            return
        status.text = f"Saved {path}"
        show_info("The report was saved.", "Support Helper", parent=win)

    run.on_click(start)
    save.on_click(save_report)
    close.on_click(win.close)
    win.cancel_button = close
    win.default_button = close
    status.text = f"{facts[0][1]}  -  {facts[3][1]}"
    status[1] = "Ready"
    if autorun:
        start()
    return win


if __name__ == "__main__":
    app = App()
    build(autorun=True)
    app.run()
