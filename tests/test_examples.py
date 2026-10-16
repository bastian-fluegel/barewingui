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

    def test_support_helper_helpers(self):
        module = load("06_support_helper")
        self.assertEqual(module.human_size(1536), "1.5 KB")
        self.assertEqual(module.parse_ping("Antwort von 1.1.1.1: Bytes=32 Zeit=12ms TTL=57"), (True, "12 ms"))
        self.assertEqual(module.parse_ping("Reply from 1.1.1.1: bytes=32 time<1ms TTL=57"), (True, "1 ms"))
        self.assertEqual(module.parse_ping("Request timed out."), (False, ""))
        facts = module.system_facts()
        self.assertEqual(facts[0][0], "Computer name")
        report = module.format_report(
            facts, [("Internet", "1.1.1.1", "\u2713 reachable", "9 ms")], [("C:\\", "100 GB", "40 GB", "60 %")]
        )
        self.assertIn("reachable   9 ms", report)  # the columns do not run together
        for part in ("Support report", "This PC", "Drives", "Network", "1.1.1.1", "60 %"):
            self.assertIn(part, report)
        # ping output in the OEM code page (umlauts) must not matter
        self.assertEqual(module.parse_ping("Antwort von 1.1.1.1: Bytes=32 Zeit=5ms TTL=57"), (True, "5 ms"))
        self.assertIn(module.run_check("tcp", "localhost-does-not-exist.invalid")[0], (False,))


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

    def test_support_helper_has_three_tabs_and_lists_facts(self):
        from barewingui import ListView, TabControl

        win = load("06_support_helper").build()
        win.show()
        tabs = controls_of(win, TabControl)[0]
        self.assertEqual([p.title for p in tabs.pages], ["This PC", "Network", "Drives"])
        views = controls_of(win, ListView)
        self.assertEqual(views[0].rows[0][0], "Computer name")
        self.assertEqual(len(views[1]), 0)  # the network checks run on demand


if __name__ == "__main__":
    unittest.main()
