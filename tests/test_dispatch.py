import threading
import unittest
from concurrent.futures import CancelledError

from barewingui._dispatch import ErrorPolicy, InvokeQueue


class ErrorPolicyTests(unittest.TestCase):
    def test_first_error_stops_once_and_is_raised(self):
        stops = []
        policy = ErrorPolicy(stop=lambda: stops.append(1))
        first, second = ValueError("first"), KeyError("second")
        policy.capture(first)
        policy.capture(second)
        self.assertEqual(stops, [1])
        with self.assertRaises(ValueError) as ctx:
            policy.raise_pending()
        self.assertIs(ctx.exception, first)
        self.assertTrue(any("second" in note for note in first.__notes__))
        policy.raise_pending()  # nothing pending anymore

    def test_handler_keeps_loop_running(self):
        stops, seen = [], []
        policy = ErrorPolicy(stop=lambda: stops.append(1))
        policy.handler = seen.append
        policy.capture(ValueError("x"))
        self.assertEqual(len(seen), 1)
        self.assertEqual(stops, [])
        self.assertIsNone(policy.pending)

    def test_failing_handler_becomes_the_unhandled_error(self):
        stops = []
        policy = ErrorPolicy(stop=lambda: stops.append(1))

        def bad_handler(exc):
            raise RuntimeError("handler broke")

        policy.handler = bad_handler
        policy.capture(ValueError("original"))
        self.assertEqual(stops, [1])
        with self.assertRaises(RuntimeError):
            policy.raise_pending()


class InvokeQueueTests(unittest.TestCase):
    def make(self):
        self.woken = 0
        self.errors = []

        def wake():
            self.woken += 1

        return InvokeQueue(wake, self.errors.append)

    def test_job_runs_on_drain_and_returns_result(self):
        q = self.make()
        future = q.submit(lambda a, b=1: a + b, (2,), {"b": 3}, report=False)
        self.assertEqual(self.woken, 1)
        self.assertFalse(future.done())
        q.drain()
        self.assertEqual(future.result(timeout=1), 5)

    def test_error_is_stored_and_reported_only_when_asked(self):
        q = self.make()
        quiet = q.submit(lambda: 1 / 0, (), {}, report=False)
        loud = q.submit(lambda: 1 / 0, (), {}, report=True)
        q.drain()
        self.assertIsInstance(quiet.exception(timeout=1), ZeroDivisionError)
        self.assertIsInstance(loud.exception(timeout=1), ZeroDivisionError)
        self.assertEqual(len(self.errors), 1)

    def test_jobs_run_in_order(self):
        q = self.make()
        order = []
        for i in range(5):
            q.submit(order.append, (i,), {}, report=True)
        q.drain()
        self.assertEqual(order, [0, 1, 2, 3, 4])

    def test_submit_from_another_thread(self):
        q = self.make()
        box = {}

        def worker():
            box["future"] = q.submit(lambda: threading.current_thread().name, (), {}, report=False)

        t = threading.Thread(target=worker, name="worker")
        t.start()
        t.join()
        q.drain()
        self.assertEqual(box["future"].result(timeout=1), threading.current_thread().name)

    def test_close_cancels_pending_and_refuses_new_jobs(self):
        q = self.make()
        pending = q.submit(lambda: 1, (), {}, report=False)
        q.close()
        with self.assertRaises(CancelledError):
            pending.result(timeout=1)
        with self.assertRaises(RuntimeError):
            q.submit(lambda: 1, (), {}, report=False)

    def test_cancelled_future_is_skipped(self):
        q = self.make()
        ran = []
        future = q.submit(lambda: ran.append(1), (), {}, report=False)
        future.cancel()
        q.drain()
        self.assertEqual(ran, [])


if __name__ == "__main__":
    unittest.main()
