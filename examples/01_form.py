"""Registration form with live validation (Label, TextBox, CheckBox, Button)."""

from __future__ import annotations

import re

from barewingui import (
    App, Button, CheckBox, HBox, Label, Spacer, TextBox, VBox, Window, show_info,
)


def validate(name: str, email: str, password: str, accepted: bool) -> str | None:
    """The first problem with the input as a message, or None when it is fine."""
    if not name.strip():
        return "Please enter your name."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
        return "Please enter a valid e-mail address."
    if len(password) < 8:
        return "The password needs at least 8 characters."
    if not accepted:
        return "Please accept the terms."
    return None


def build() -> Window:
    with Window("Registration", size=(420, 330), resizable=False) as win:
        with VBox(padding=16, gap=8):
            Label("Name")
            name = TextBox(placeholder="First and last name")
            Label("E-mail")
            email = TextBox(placeholder="name@example.org")
            Label("Password")
            password = TextBox(password=True)
            terms = CheckBox("I accept the terms of use", checked=False)
            problem = Label("")
            Spacer(grow=1)
            with HBox(gap=8):
                Spacer(grow=1)
                register = Button("Register", default=True, enabled=False)
                quit_button = Button("Cancel")

    def check() -> None:
        message = validate(name.text, email.text, password.text, bool(terms.checked))
        problem.text = message or ""
        register.enabled = message is None

    def submit() -> None:
        show_info(f"Welcome, {name.text.strip()}!", "Registration", parent=win)
        win.close()

    for control in (name, email, password):
        control.on_change(check)
    terms.on_change(check)
    register.on_click(submit)
    quit_button.on_click(win.close)
    win.cancel_button = quit_button
    win.default_button = register
    return win


if __name__ == "__main__":
    app = App()
    build()
    app.run()
