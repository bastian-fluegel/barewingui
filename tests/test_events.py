import unittest

from barewingui.events import Event, event


class Widget:
    on_ping = event()


class EventTests(unittest.TestCase):
    def test_handlers_run_in_order(self):
        calls = []
        ev = Event()
        ev(lambda: calls.append(1))
        ev.connect(lambda: calls.append(2))
        ev.emit()
        self.assertEqual(calls, [1, 2])

    def test_decorator_returns_the_function(self):
        ev = Event()

        @ev
        def handler():
            pass

        self.assertTrue(callable(handler))
        self.assertEqual(len(ev), 1)

    def test_non_callable_is_rejected(self):
        with self.assertRaises(TypeError):
            Event().connect(42)

    def test_disconnect_and_clear(self):
        ev = Event()
        h = ev(lambda: None)
        ev.disconnect(h)
        self.assertEqual(len(ev), 0)
        ev(h)
        ev.clear()
        self.assertEqual(len(ev), 0)

    def test_exception_propagates(self):
        ev = Event()
        ev(lambda: 1 / 0)
        with self.assertRaises(ZeroDivisionError):
            ev.emit()

    def test_descriptor_is_per_instance(self):
        a, b = Widget(), Widget()
        a.on_ping(lambda: None)
        self.assertEqual(len(a.on_ping), 1)
        self.assertEqual(len(b.on_ping), 0)

    def test_assignment_replaces_handlers(self):
        w = Widget()
        calls = []
        w.on_ping(lambda: calls.append("old"))
        w.on_ping = lambda: calls.append("new")
        w.on_ping.emit()
        self.assertEqual(calls, ["new"])
        w.on_ping = None
        self.assertEqual(len(w.on_ping), 0)
        self.assertIsInstance(w.on_ping, Event)


if __name__ == "__main__":
    unittest.main()
