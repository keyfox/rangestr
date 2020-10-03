from parameterized import parameterized, param

from rangestr.ranges import (
    find_index,
    crop,
    add,
    subtract,
    _splice_list,
)


class TestListSplice:
    @parameterized.expand(
        [
            (
                ["angel", "clown", "drum", "mandarin", "sturgeon"],
                ["angel", "clown", "mandarin", "sturgeon"],
                2,
                0,
                "drum",
            ),
            (
                ["angel", "clown", "drum", "guitar", "mandarin", "sturgeon"],
                ["angel", "clown", "mandarin", "sturgeon"],
                2,
                0,
                "drum",
                "guitar",
            ),
            (
                ["angel", "clown", "drum", "sturgeon"],
                ["angel", "clown", "drum", "mandarin", "sturgeon"],
                3,
                1,
            ),
            (
                ["parrot", "anemone", "blue", "trumpet", "sturgeon"],
                ["angel", "clown", "trumpet", "sturgeon"],
                0,
                2,
                "parrot",
                "anemone",
                "blue",
            ),
        ]
    )
    def test_list_splice(self, expected, src, index, remove_count, *additions):
        _splice_list(src, index, remove_count, *additions)
        assert expected == src


class TestAdd:
    @parameterized.expand(
        [
            # add to empty ranges
            ([(0, 50)], [], (0, 50)),
            # addition with linking
            ([(0, 100)], [(0, 20), (80, 100)], (0, 100)),
            ([(0, 100)], [(0, 20), (80, 100)], (10, 90)),
            ([(0, 100)], [(0, 20), (80, 100)], (20, 80)),
            # addition without linking
            ([(0, 20), (40, 60), (80, 100)], [(0, 20), (80, 100)], (40, 60)),
            # expansions
            ([(0, 100)], [(0, 20)], (0, 100)),
            ([(0, 100)], [(0, 20)], (10, 100)),
            ([(0, 100)], [(0, 20)], (20, 100)),
            ([(0, 100)], [(80, 100)], (0, 100)),
            ([(0, 100)], [(80, 100)], (0, 90)),
            ([(0, 100)], [(80, 100)], (0, 80)),
            # no effect; already included
            ([(20, 80)], [(20, 80)], (40, 60)),
        ]
    )
    def test_add(self, expected, ranges, addition):
        add(ranges, addition)
        assert expected == ranges


class TestSubtract:
    @parameterized.expand(
        [
            # subtract from empty range
            ([], [], (0, 50)),
            # subtract with split
            ([(0, 33), (66, 100)], [(0, 100)], (33, 66)),
            # subtract which removes a range
            ([(0, 20), (80, 100)], [(0, 20), (40, 60), (80, 100)], (40, 60)),
            ([(0, 20), (80, 100)], [(0, 20), (40, 60), (80, 100)], (30, 70)),
            ([], [(0, 20), (40, 60), (80, 100)], (0, 100)),
            ([], [(0, 100)], (0, 100)),
            # shrinkage
            ([(50, 100)], [(0, 100)], (0, 50)),
            ([(0, 50)], [(0, 100)], (50, 100)),
            # shrinkage and removal
            ([(0, 20), (80, 100)], [(0, 30), (40, 60), (70, 100)], (20, 80)),
        ]
    )
    def test_subtract(self, expected, ranges, subtraction):
        subtract(ranges, subtraction)
        assert expected == ranges


class TestFindIndex:
    @parameterized.expand(
        [
            # find from empty
            ((False, 0), [], 0),
            # contains
            ((True, 0), [(0, 100)], 0),
            ((True, 0), [(0, 100)], 50),
            ((True, 0), [(0, 100)], 100),
            ((True, 0), [(0, 33), (66, 100)], 33),
            ((True, 1), [(0, 33), (66, 100)], 66),
            # doesn't contain
            ((False, 0), [(0, 100)], -1),
            ((False, 1), [(0, 100)], 101),
            ((False, 0), [(0, 33), (66, 100)], -1),
            ((False, 1), [(0, 33), (66, 100)], 34),
            ((False, 1), [(0, 33), (66, 100)], 65),
            ((False, 2), [(0, 33), (66, 100)], 101),
        ]
    )
    def test_find_index(self, expected, ranges, n):
        assert expected == find_index(ranges, n)


class TestCrop:
    @parameterized.expand(
        [
            param([(33, 66)], [(0, 100)], lower=33, upper=66),
            param([(0, 100)], [(0, 100)], lower=-100, upper=200),
            param([(50, 100)], [(0, 100)], lower=50, upper=100),
            param([(0, 50)], [(0, 100)], lower=0, upper=50),
            param([(20, 33), (66, 80)], [(0, 33), (66, 100)], lower=20, upper=80),
            param(
                [(40, 60), (80, 100)],
                [(0, 20), (40, 60), (80, 100)],
                lower=30,
                upper=None,
            ),
            param(
                [(50, 60), (80, 100)],
                [(0, 20), (40, 60), (80, 100)],
                lower=50,
                upper=None,
            ),
            param(
                [(0, 20), (40, 50)],
                [(0, 20), (40, 60), (80, 100)],
                lower=None,
                upper=50,
            ),
            param(
                [(0, 20), (40, 60)],
                [(0, 20), (40, 60), (80, 100)],
                lower=None,
                upper=70,
            ),
        ]
    )
    def test_crop(self, expected, ranges, **kwargs):
        crop(ranges, **kwargs)
        assert expected == ranges
