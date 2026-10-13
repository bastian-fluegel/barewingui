import unittest

from barewingui.dpi import BASE_DPI, Scale


class ScaleTests(unittest.TestCase):
    def test_identity_at_96_dpi(self):
        s = Scale(BASE_DPI)
        self.assertEqual(s.factor, 1.0)
        self.assertEqual(s.px(10), 10)
        self.assertEqual(s.dip(10), 10)

    def test_150_percent(self):
        s = Scale(144)
        self.assertEqual(s.px(10), 15)
        self.assertEqual(s.px(0), 0)
        self.assertAlmostEqual(s.dip(15), 10)

    def test_rounds_half_up(self):
        self.assertEqual(Scale(120).px(10), 13)  # 12.5 -> 13
        self.assertEqual(Scale(120).px(1), 1)  # 1.25 -> 1

    def test_invalid_dpi(self):
        with self.assertRaises(ValueError):
            Scale(0)
        with self.assertRaises(ValueError):
            Scale(-96)

    def test_equality_and_hash(self):
        self.assertEqual(Scale(96), Scale(96))
        self.assertNotEqual(Scale(96), Scale(120))
        self.assertEqual(len({Scale(96), Scale(96)}), 1)


if __name__ == "__main__":
    unittest.main()
