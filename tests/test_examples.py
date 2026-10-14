"""The example apps: pure helpers everywhere, the windows on Windows only."""

import importlib.util
import tempfile
import threading
import unittest
from pathlib import Path

from barewingui import App, Button, Label, ProgressBar, TextBox
from winhelpers import WINDOWS

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def load(name):
    spec = importlib.util.spec_from_file_location("example_" + name, EXAMPLES / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def controls_of(win, cls):
    return [c for c in win._controls.values() if isinstance(c, cls)]


class HelperTests(unittest.TestCase):
    def test_form_validation(self):
        validate = load("01_form").validate
        self.assertIn("name", validate("", "a@b.de", "12345678", True))
        self.assertIn("e-mail", validate("A", "nope", "12345678", True))
        self.assertIn("8", validate("A", "a@b.de", "123", True))
        self.assertIn("terms", validate("A", "a@b.de", "12345678", False))
        self.assertIsNone(validate("A", "a@b.de", "12345678", True))

    def test_file_browser_helpers(self):
        module = load("02_file_browser")
        self.assertEqual(module.human_size(512), "512 B")
        self.assertEqual(module.human_size(2048), "2.0 KB")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "b").mkdir()
            (root / "a").mkdir()
            (root / ".hidden").write_text("x")
            (root / "f.txt").write_text("x")
            dirs, files = module.list_dir(root, False)
            self.assertEqual([d.name for d in dirs], ["a", "b"])
            self.assertEqual([f.name for f in files], ["f.txt"])
            self.assertEqual(len(module.list_dir(root, True)[1]), 2)
        self.assertEqual(module.list_dir(Path(tmp) / "missing", True), ([], []))


@unittest.skipUnless(WINDOWS, "needs Windows")
class ExampleWindowTests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        if App._instance is not None:
            App._instance.shutdown()

    def test_form_starts_with_disabled_register_button(self):
        win = load("01_form").build()
        win.show()
        register = [b for b in controls_of(win, Button) if b.text == "Register"][0]
        self.assertFalse(register.enabled)
        self.assertIs(win.default_button, register)

    def test_settings_collects_values(self):
        win = load("03_settings").build()
        win.show()
        values = win.collect()
        self.assertEqual(values["language"], "English")
        self.assertEqual(values["density"], "normal")
        self.assertEqual((values["autosave_minutes"], values["zoom"]), (5, 100))

    def test_editor_opens_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "note.txt"
            target.write_text("Hello\nWorld", encoding="utf-8")
            win = load("04_editor").build(str(target))
            win.show()
            editor = controls_of(win, TextBox)[0]
            self.assertEqual(editor.text, "Hello\nWorld")
            self.assertEqual(win.title, "note.txt - Editor")

    def test_file_browser_lists_a_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "sub").mkdir()
            (Path(tmp) / "a.txt").write_text("abc")
            win = load("02_file_browser").build(Path(tmp))
            win.show()
            from barewingui import ListView

            table = controls_of(win, ListView)[0]
            self.assertEqual([row[0] for row in table.rows], ["sub\\", "a.txt"])
            self.assertEqual(win.status_bar[1], "1 folders, 1 files")

    def test_progress_runs_in_a_worker_thread(self):
        win = load("05_progress").build(steps=5, delay=0)
        win.show()
        bar = controls_of(win, ProgressBar)[0]
        start = [b for b in controls_of(win, Button) if b.text == "Start"][0]
        label = controls_of(win, Label)[0]
        seen = {}

        def finish():
            seen["value"], seen["text"] = bar.value, label.text
            win.close()

        start.click()
        timer = threading.Timer(1.5, lambda: self.app.invoke(finish))
        timer.daemon = True
        timer.start()
        self.app.run()
        self.assertEqual(seen, {"value": 5, "text": "Done."})


if __name__ == "__main__":
    unittest.main()
