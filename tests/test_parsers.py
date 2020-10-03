import pytest
from parameterized import parameterized, param

from rangestr.parsers import parse_ranges, parse_endpoints, parse_single_range
from tests import testcases


class TestParseEndpoints:
    def test_empty(self):
        with pytest.raises(ValueError):
            parse_endpoints("", delimiter="-")

    @parameterized.expand(
        [
            param((0, 6), "0-5", delimiter="-"),
            param((0, None), "0-", delimiter="-"),
            param((None, 6), "-5", delimiter="-"),
            param((-5, -4), "-5", delimiter=".."),
        ]
    )
    def test_parse_endpoints(self, expected, src, **kwargs):
        assert expected == parse_endpoints(src, **kwargs)

    @parameterized.expand(
        [
            param("-5-0", delimiter="-"),
            param("-5..0..5", delimiter=".."),
        ]
    )
    def test_invalid_delimiter(self, src, **kwargs):
        with pytest.raises(ValueError):
            parse_endpoints(src, **kwargs)


class TestParseSingleRange:
    # This test won't focus on parsing endpoints because the parsing of input is
    # supposed to be done in `parsers.parse_endpoints`.

    @parameterized.expand(
        [
            param((True, (0, 6)), "0-5", delimiter="-"),
            param((False, (0, 6)), "^0-5", delimiter="-"),
        ]
    )
    def test_parse_single_range(self, expected, src, **kwargs):
        assert expected == parse_single_range(src, **kwargs)


class TestParseRanges:
    @parameterized.expand(testcases.valid_cases)
    def test_valid_cases(self, expected, src, *args, **kwargs):
        assert expected == parse_ranges(src, *args, **kwargs)

    @parameterized.expand(testcases.error_cases_missing_endpoint)
    def test_missing_endpoint(self, src, *args, **kwargs):
        with pytest.raises(ValueError):
            parse_ranges(src, *args, **kwargs)
