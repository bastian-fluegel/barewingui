"""A complete little tool in about 30 lines: pick a host, ping it, read the answer."""

import subprocess
import threading

from barewingui import App, Button, ComboBox, HBox, Label, SpinBox, TextBox, VBox, Window

app = App()
with Window("Ping", size=(520, 380)) as win:
    with VBox(padding=16, gap=10):
        with HBox(gap=8):
            Label("Host")
            host = ComboBox(["1.1.1.1", "8.8.8.8", "github.com", "pypi.org"], selected=0, grow=1)
            Label("Packets")
            count = SpinBox(4, minimum=1, maximum=20)
            go = Button("Ping", default=True)
        output = TextBox(multiline=True, readonly=True, grow=1)


def ping(target, packets):  # runs in a worker thread, so the window stays responsive
    run = subprocess.run(["ping", "-n", str(packets), target], capture_output=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    app.invoke(show, run.stdout.decode("oem", errors="replace").strip())


def show(text):
    output.text = text.replace("\r\n", "\n")
    go.enabled = True


def start():
    go.enabled = False
    output.text = "Pinging..."
    threading.Thread(target=ping, args=(host.text, count.value), daemon=True).start()


go.on_click(start)
app.run()
