import unittest

from barewingui import HBox, LayoutError, Rect, Size, Spacer, Stack, VBox
from barewingui._layout_core import Flex, adopt, current_container
from barewingui.dpi import Scale

S96 = Scale(96)


class FakeNode:
    """Stands in for a control: fixed natural size, records where it was placed."""

    def __init__(self, w, h, *, min_w=None, min_h=None, **flex):
        self.flex = Flex(**flex)
        self.visible = True
        self._nat = Size(w, h)
        self._min = Size(w if min_w is None else min_w, h if min_h is None else min_h)
        self.rect = None
        adopt(self)

    def natural_size(self, scale):
        return self._nat

    def min_size(self, scale):
        return self._min

    def place(self, rect, scale):
        self.rect = rect


def arranged(box, w, h, scale=S96):
    return [r for _, r in box.arrange(Rect(0, 0, w, h), scale)]


class VerticalTests(unittest.TestCase):
    def test_padding_gap_and_stretch(self):
        with VBox(gap=8, padding=10) as box:
            FakeNode(50, 20)
            FakeNode(50, 30)
        self.assertEqual(arranged(box, 200, 100), [Rect(10, 10, 180, 20), Rect(10, 38, 180, 30)])

    def test_grow_takes_remaining_space(self):
        with VBox(gap=0) as box:
            FakeNode(50, 20)
            FakeNode(50, 20, grow=1)
        self.assertEqual(arranged(box, 100, 100), [Rect(0, 0, 100, 20), Rect(0, 20, 100, 80)])

    def test_weighted_grow(self):
        with VBox(gap=0) as box:
            FakeNode(10, 0, grow=1)
            FakeNode(10, 0, grow=3)
        self.assertEqual([r.h for r in arranged(box, 10, 100)], [25, 75])

    def test_children_keep_natural_size_when_too_small(self):
        with VBox(gap=0) as box:
            FakeNode(50, 100)
            FakeNode(50, 100)
        rects = arranged(box, 50, 150)
        self.assertEqual([r.h for r in rects], [100, 100])  # overflow instead of squeezing
        self.assertEqual(rects[1].y, 100)

    def test_shrink_down_to_explicit_min(self):
        with VBox(gap=0) as box:
            FakeNode(50, 100, min_h=20)
            FakeNode(50, 100, min_h=20)
        self.assertEqual([r.h for r in arranged(box, 50, 150)], [75, 75])

    def test_hidden_child_is_skipped(self):
        with VBox(gap=8) as box:
            FakeNode(10, 10)
            hidden = FakeNode(10, 10)
            FakeNode(10, 10)
        hidden.visible = False
        self.assertEqual([r.y for r in arranged(box, 10, 100)], [0, 18])


class HorizontalTests(unittest.TestCase):
    def make(self, **options):
        with HBox(gap=10, **options) as box:
            FakeNode(30, 20)
            FakeNode(30, 20)
        return box

    def test_justify_start_center_end(self):
        self.assertEqual([r.x for r in arranged(self.make(), 200, 50)], [0, 40])
        self.assertEqual([r.x for r in arranged(self.make(justify="center"), 200, 50)], [65, 105])
        self.assertEqual([r.x for r in arranged(self.make(justify="end"), 200, 50)], [130, 170])

    def test_justify_space_between(self):
        with HBox(gap=0, justify="space_between") as box:
            for _ in range(3):
                FakeNode(20, 10)
        self.assertEqual([r.x for r in arranged(box, 100, 10)], [0, 40, 80])

    def test_cross_axis_alignment(self):
        def y_h(container_align, **child):
            with HBox(align=container_align) as box:
                FakeNode(10, 20, **child)
            r = arranged(box, 100, 100)[0]
            return r.y, r.h

        self.assertEqual(y_h("stretch"), (0, 100))
        self.assertEqual(y_h("start"), (0, 20))
        self.assertEqual(y_h("center"), (40, 20))
        self.assertEqual(y_h("end"), (80, 20))
        self.assertEqual(y_h("stretch", height=30), (0, 30))  # explicit size beats stretch
        self.assertEqual(y_h("start", align_self="end"), (80, 20))  # per-child override

    def test_spacer_pushes_neighbours_apart(self):
        with HBox(gap=0) as box:
            FakeNode(30, 20)
            Spacer()
            FakeNode(30, 20)
        rects = arranged(box, 200, 20)
        self.assertEqual((rects[0].x, rects[2].x), (0, 170))

    def test_fixed_spacer_uses_main_axis(self):
        with VBox(gap=0) as box:
            FakeNode(10, 20)
            Spacer(16)
            FakeNode(10, 20)
        self.assertEqual([r.y for r in arranged(box, 10, 200)], [0, 20, 36])
        with HBox(gap=0) as hbox:
            FakeNode(10, 20)
            Spacer(16)
            FakeNode(10, 20)
        self.assertEqual([r.x for r in arranged(hbox, 200, 20)], [0, 10, 26])


class MeasureTests(unittest.TestCase):
    def test_natural_and_min_size(self):
        with VBox(gap=8, padding=10) as box:
            FakeNode(50, 20, min_h=10)
            FakeNode(60, 30, min_w=5)
        self.assertEqual(box.natural_size(S96), Size(80, 78))
        self.assertEqual(box.min_size(S96), Size(70, 68))

    def test_empty_stack_is_just_padding(self):
        self.assertEqual(VBox(padding=(4, 6)).natural_size(S96), Size(12, 8))

    def test_nested_stacks(self):
        with VBox(gap=0) as outer:
            FakeNode(10, 10)
            with HBox(gap=0, grow=1) as inner:
                FakeNode(20, 10)
                FakeNode(20, 10, grow=1)
        self.assertEqual(outer.natural_size(S96), Size(40, 20))
        rects = arranged(outer, 100, 60)
        self.assertEqual(rects[1], Rect(0, 10, 100, 50))
        inner_rects = arranged(inner, 100, 50)
        self.assertEqual([r.w for r in inner_rects], [20, 80])


class DpiTests(unittest.TestCase):
    def test_options_scale_with_dpi(self):
        with VBox(gap=8, padding=10) as box:
            FakeNode(20, 20)
        s150 = Scale(144)
        rects = arranged(box, 300, 300, s150)
        self.assertEqual(rects, [Rect(15, 15, 270, 20)])  # natural size is already in pixels

    def test_gap_scales(self):
        with VBox(gap=8) as box:
            FakeNode(10, 10)
            FakeNode(10, 10)
        self.assertEqual([r.y for r in arranged(box, 10, 100, Scale(144))], [0, 22])


class FlexOptionTests(unittest.TestCase):
    def test_min_wins_over_max(self):
        with VBox(gap=0) as box:
            FakeNode(10, 10, min_height=50, max_height=20)
        self.assertEqual(arranged(box, 10, 100)[0].h, 50)

    def test_max_limits_growth(self):
        with VBox(gap=0) as box:
            FakeNode(10, 10, grow=1, max_height=40)
        self.assertEqual(arranged(box, 10, 100)[0].h, 40)

    def test_invalid_values(self):
        with self.assertRaises(LayoutError):
            VBox(gap=-1)
        with self.assertRaises(LayoutError):
            VBox(justify="middle")
        with self.assertRaises(LayoutError):
            VBox(align="top")
        with self.assertRaises(LayoutError):
            VBox(padding=(1, 2, 3))
        with self.assertRaises(LayoutError):
            Stack("diagonal")
        with self.assertRaises(LayoutError):
            Flex(grow=-1)
        with self.assertRaises(LayoutError):
            Flex(align_self="top")
        with self.assertRaises(TypeError):
            VBox(colour="red")


class BuildContextTests(unittest.TestCase):
    def test_nodes_are_collected_by_with_block(self):
        with VBox() as outer:
            inner = VBox()
            leaf = FakeNode(1, 1)
        self.assertEqual(outer.children, (inner, leaf))
        self.assertEqual(inner.children, ())

    def test_stack_is_cleaned_up_after_exception(self):
        with self.assertRaises(RuntimeError):
            with VBox():
                raise RuntimeError("boom")
        self.assertIsNone(current_container())

    def test_duplicate_add_is_rejected(self):
        box = VBox()
        node = FakeNode(1, 1)
        box.add(node)
        with self.assertRaises(LayoutError):
            box.add(node)

    def test_remove(self):
        with VBox() as box:
            node = FakeNode(1, 1)
        box.remove(node)
        self.assertEqual(box.children, ())
        with self.assertRaises(LayoutError):
            box.remove(node)


if __name__ == "__main__":
    unittest.main()
