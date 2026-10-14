"""Long task in a worker thread that reports back with App.invoke (ProgressBar, Timer-free)."""

from __future__ import annotations

import threading
import time

from barewingui import App, Button, HBox, Label, ProgressBar, Spacer, VBox, Window


def build(steps: int = 100, delay: float = 0.03) -> Window:
    app = App.current()
    cancel_flag = threading.Event()
    with Window("Progress", size=(420, 170), resizable=False) as win:
        with VBox(padding=16, gap=10):
            info = Label("Ready.")
            bar = ProgressBar(0, maximum=steps)
            Spacer(grow=1)
            with HBox(gap=8):
                Spacer(grow=1)
                start = Button("Start", default=True)
                cancel = Button("Cancel", enabled=False)

    def set_progress(done: int) -> None:  # runs on the UI thread
        if not win.alive:
            return
        bar.value = done
        info.text = f"{done} of {steps}"

    def finished(cancelled: bool) -> None:  # runs on the UI thread
        if not win.alive:
            return
        info.text = "Cancelled." if cancelled else "Done."
        start.enabled = True
        cancel.enabled = False

    def work() -> None:  # runs on the worker thread: never touch controls here
        for done in range(1, steps + 1):
            if cancel_flag.is_set():
                app.invoke(finished, True)
                return
            time.sleep(delay)
            app.invoke(set_progress, done)
        app.invoke(finished, False)

    def begin() -> None:
        cancel_flag.clear()
        bar.value = 0
        start.enabled = False
        cancel.enabled = True
        threading.Thread(target=work, daemon=True).start()

    start.on_click(begin)
    cancel.on_click(cancel_flag.set)
    win.on_close = lambda: cancel_flag.set()  # the worker stops by itself
    return win


if __name__ == "__main__":
    app = App()
    build()
    app.run()
