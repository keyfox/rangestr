import functools

import pytest
from parameterized import param, parameterized

from rangestr import rangestr
from tests import testcases


class TestRangestr:
    # This test won't focus on parsing because the parsing of input is
    # supposed to be done in `parsers.parse_ranges`.

    def test_rangestr(self):
        assert [1, 2, 3, 4, 5] == [*rangestr("1-5")]

    @parameterized.expand(testcases.error_cases_missing_endpoint)
    def test_missing_endpoint(self, src, *args, **kwargs):
        # invalid arguments must be detected during calling `rangestr` function
        # NOTE: as the parsing process may contain `yield`, we have to ensure
        #       errors must be raised not when iterating the returned iterator.
        with pytest.raises(ValueError):
            rangestr(src, *args, **kwargs)

    def test_respects_delimiter(self):
        assert [-2, -1, 0, 1, 2] == [*rangestr("-2..2", delimiter="..")]

    @parameterized.expand(
        [
            param([]),
            param([1, 2, 3, 4, 5], implicit_inclusion=True),
            param([], implicit_inclusion=False),
        ]
    )
    def test_respects_implicit_inclusion(self, expected, **kwargs):
        assert expected == [*rangestr("^6-", lower=1, upper=10, **kwargs)]

    @parameterized.expand(
        [
            param([-2, -1, 0, 1, 2], "-2..2"),
            param([1, 2, 3, 4, 5], "1-5", delimiter="-"),
        ]
    )
    def test_with_functools_partial(self, expected, src, **kwargs):
        ellipsis_rangestr = functools.partial(rangestr, delimiter="..")
        assert expected == [*ellipsis_rangestr(src, **kwargs)]
