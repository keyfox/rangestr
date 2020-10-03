"""A Python package for generating ranges of integers from a string."""
from itertools import chain as _chain
from typing import Optional, Iterator

from . import _version
from . import parsers

__author__ = "Keyfox"
__version__ = _version.version


def rangestr(
    src: str,
    lower: Optional[int] = None,
    upper: Optional[int] = None,
    delimiter: str = parsers.DEFAULT_DELIMITER,
    implicit_inclusion: bool = False,
) -> Iterator[int]:
    """Return an iterator which iterates through integers represented in the given string.

    :param src: A string to be parsed.
    :param lower: Inclusive lower endpoint of the entire range.
    :param upper: Inclusive upper endpoint of the entire range.
    :param delimiter: A delimiter of endpoints. Defaults to a dash (``-``).
    :param implicit_inclusion: Whether to include all integers when an exclusion range
           comes in first.
    :return: An iterator of integers which are represented in `src`.
    """
    ranges = parsers.parse_ranges(src, lower, upper, delimiter, implicit_inclusion)
    return _chain.from_iterable(map(lambda r: range(*r), ranges))
