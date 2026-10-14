import os
import unittest

from barewingui.dialogs import _filter_chars, _parse_file_result


class FilterTests(unittest.TestCase):
    def test_default_filter(self):
        self.assertEqual(_filter_chars(None), "All files (*.*)\0*.*\0\0")

    def test_pairs_and_pattern_lists(self):
        text = _filter_chars([("Text", "*.txt"), ("Images", ["*.png", "*.jpg"])])
        self.assertEqual(text, "Text (*.txt)\0*.txt\0Images (*.png;*.jpg)\0*.png;*.jpg\0\0")


class ResultTests(unittest.TestCase):
    def test_single_path(self):
        self.assertEqual(_parse_file_result("C:\\a\\b.txt\0\0\0", False), ["C:\\a\\b.txt"])

    def test_multiple_files_are_joined_with_the_folder(self):
        raw = "C:\\docs\0a.txt\0b.txt\0\0"
        self.assertEqual(
            _parse_file_result(raw, True),
            [os.path.join("C:\\docs", "a.txt"), os.path.join("C:\\docs", "b.txt")],
        )

    def test_multiple_but_one_selection_is_a_full_path(self):
        self.assertEqual(_parse_file_result("C:\\docs\\a.txt\0\0", True), ["C:\\docs\\a.txt"])

    def test_empty_result(self):
        self.assertEqual(_parse_file_result("\0\0", False), [])


if __name__ == "__main__":
    unittest.main()
