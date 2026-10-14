"""Settings dialog: TabControl, GroupBox, RadioButton, ComboBox, Slider, SpinBox."""

from __future__ import annotations

from barewingui import (
    App, Button, CheckBox, ComboBox, GroupBox, HBox, Label, RadioButton, Slider,
    Spacer, SpinBox, TabControl, TabPage, VBox, Window, show_info,
)


def build() -> Window:
    with Window("Settings", size=(460, 380), resizable=False) as win:
        with VBox(padding=12, gap=10):
            with TabControl(grow=1):
                with TabPage("General"):
                    with GroupBox("Language"):
                        language = ComboBox(["English", "Deutsch", "Français"], selected=0)
                    with GroupBox("Startup"):
                        restore = CheckBox("Restore the last session", checked=True)
                        updates = CheckBox("Check for updates", checked=False)
                    with HBox(gap=8):
                        Label("Autosave every (minutes)")
                        autosave = SpinBox(5, minimum=1, maximum=60)
                with TabPage("Appearance"):
                    with GroupBox("Density"):
                        compact = RadioButton("Compact")
                        normal = RadioButton("Normal", checked=True)
                        relaxed = RadioButton("Relaxed")
                    with HBox(gap=8):
                        Label("Zoom")
                        zoom = Slider(100, minimum=50, maximum=200, tick_frequency=25, grow=1)
                        zoom_label = Label("100 %")
            with HBox(gap=8):
                Spacer(grow=1)
                ok = Button("OK", default=True)
                cancel = Button("Cancel")

    def density() -> str:
        return "compact" if compact.checked else "relaxed" if relaxed.checked else "normal"

    def collect() -> dict[str, object]:
        return {
            "language": language.text,
            "restore_session": bool(restore.checked),
            "check_updates": bool(updates.checked),
            "autosave_minutes": autosave.value,
            "density": density(),
            "zoom": zoom.value,
        }

    def apply() -> None:
        win.result = collect()  # type: ignore[attr-defined]
        show_info("\n".join(f"{k}: {v}" for k, v in win.result.items()), "Settings", parent=win)  # type: ignore[attr-defined]
        win.close()

    zoom.on_change(lambda: setattr(zoom_label, "text", f"{zoom.value} %"))
    ok.on_click(apply)
    cancel.on_click(win.close)
    win.cancel_button = cancel
    win.default_button = ok
    win.collect = collect  # type: ignore[attr-defined]
    return win


if __name__ == "__main__":
    app = App()
    build()
    app.run()
