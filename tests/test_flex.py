import math
import unittest

from barewingui._layout_core import resolve_flex

INF = math.inf


def flex(bases, space, *, mins=None, maxs=None, grows=None, shrinks=None):
    n = len(bases)
    return resolve_flex(
        bases,
        mins if mins is not None else [0] * n,
        maxs if maxs is not None else [INF] * n,
        grows if grows is not None else [0] * n,
        shrinks if shrinks is not None else [1] * n,
        space,
    )


class GrowTests(unittest.TestCase):
    def test_equal_grow(self):
        self.assertEqual(flex([10, 10], 100, grows=[1, 1]), [50, 50])

    def test_weighted_grow(self):
        self.assertEqual(flex([0, 0], 40, grows=[1, 3]), [10, 30])

    def test_grow_respects_max_and_redistributes(self):
        self.assertEqual(flex([0, 0], 100, grows=[1, 1], maxs=[10, INF]), [10, 90])

    def test_all_capped_leaves_space_unused(self):
        self.assertEqual(flex([0, 0], 100, grows=[1, 1], maxs=[10, 20]), [10, 20])

    def test_no_grow_keeps_base(self):
        self.assertEqual(flex([10, 20], 100), [10, 20])

    def test_zero_grow_item_is_untouched(self):
        self.assertEqual(flex([10, 10], 60, grows=[0, 1]), [10, 50])

    def test_rounding_keeps_exact_total(self):
        result = flex([0, 0, 0], 10, grows=[1, 1, 1])
        self.assertEqual(sum(result), 10)
        self.assertEqual(sorted(result), [3, 3, 4])

    def test_rounding_total_for_many_items(self):
        for space in range(0, 60):
            result = flex([0] * 7, space, grows=[1] * 7)
            self.assertEqual(sum(result), space)
            self.assertLessEqual(max(result) - min(result), 1)


class ShrinkTests(unittest.TestCase):
    def test_equal_shrink(self):
        self.assertEqual(flex([100, 100], 150), [75, 75])

    def test_shrink_is_weighted_by_base(self):
        self.assertEqual(flex([100, 50], 120), [80, 40])

    def test_shrink_respects_min(self):
        self.assertEqual(flex([100, 100], 100, mins=[90, 0]), [90, 10])

    def test_overflow_when_minimums_do_not_fit(self):
        self.assertEqual(flex([100, 100], 50, mins=[100, 100]), [100, 100])

    def test_shrink_zero_is_rigid(self):
        self.assertEqual(flex([100, 100], 150, shrinks=[0, 1]), [100, 50])

    def test_empty(self):
        self.assertEqual(flex([], 100), [])


class ValidationTests(unittest.TestCase):
    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            resolve_flex([1, 2], [0], [INF, INF], [0, 0], [1, 1], 10)


if __name__ == "__main__":
    unittest.main()
