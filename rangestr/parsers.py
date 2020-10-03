from typing import Tuple, Union, Iterable, List, Any

from . import ranges

ParsedRange = Union[ranges.Endpoints, Tuple[None, int], Tuple[int, None]]
DEFAULT_DELIMITER = "-"


def parse_endpoints(src: str, delimiter: str) -> ParsedRange:
    """Parse an endpoints.

    :param src: A string which represents endpoints.
    :param delimiter: A delimiter of endpoints.
    :return: A tuple of *inclusive* lower endpoint and *exclusive* upper endpoint.
             Each element will be None if an endpoint is omitted in the string.
    """
    delim_index = src.find(delimiter)
    if delim_index >= 0:
        if src.rfind(delimiter) != delim_index:
            # reject a string like `-500-500` (possibly forgot to specify `delimiter`)
            raise ValueError(f"`{delimiter}` can't appear more than once: {src}")
        # a range which contains *multiple* integers
        leftstr, rightstr = src[:delim_index], src[delim_index + len(delimiter) :]
        if leftstr and rightstr:
            left, right = int(leftstr), int(rightstr)
            return (left, right + 1) if left <= right else (right, left + 1)
        else:
            assert not (leftstr is None and rightstr is None)
            return (  # type: ignore
                int(leftstr) if leftstr else None,
                int(rightstr) + 1 if rightstr else None,
            )
    else:
        # a range which contains just a *single* integer
        n = int(src)
        return n, n + 1


def parse_single_range(src: str, delimiter: str) -> Tuple[bool, ParsedRange]:
    """Parse a single range.

    :param src: A string which represents a single range.
    :param delimiter: A delimiter of endpoints.
    :return: A tuple of a boolean which indicates whether this range is inclusive one,
             and a pair of endpoints.
    """
    inclusive = not src.startswith("^")
    return inclusive, parse_endpoints(
        src if inclusive else src[1:], delimiter=delimiter
    )


def _both_none(a: Any, b: Any) -> bool:
    """Shorthand function to see if both endpoints are None."""
    return a is None and b is None


def _both_filled(a: Any, b: Any) -> bool:
    """Shorthand function to see if both endpoints are *not* None."""
    return a is not None and b is not None


def parse_ranges(
    src: str,
    lower: Union[int, None] = None,
    upper: Union[int, None] = None,
    delimiter: str = DEFAULT_DELIMITER,
    implicit_inclusion: bool = False,
) -> Iterable[ranges.Endpoints]:
    """Parse a comma-separated ranges.

    :param src: A string to be parsed.
    :param lower: Inclusive lower endpoint of the entire range.
    :param upper: Inclusive upper endpoint of the entire range.
    :param delimiter: A delimiter of endpoints.
    :param implicit_inclusion: Whether to include all integers when an exclusion range
           comes in first.
    :return: An iterable of tuples which represents a range in *open-closed* form.
    """
    result: List[ranges.Endpoints] = []

    if upper is not None:
        # make `upper` an exclusive endpoint during calculation since it's programmer-friendly
        upper += 1

    for i, single_range in enumerate(
        filter(bool, map(lambda e: e.strip(), src.split(",")))
    ):
        inclusive, (range_lower, range_upper) = parse_single_range(
            single_range, delimiter
        )
        assert not _both_none(range_lower, range_upper)

        if inclusive:
            if _both_none(lower, range_lower) or _both_none(upper, range_upper):
                raise ValueError(f"Endpoint is missing: {single_range}")

            # complement endpoints with universe endpoints and crop the range to be added
            range_lower = max(l for l in (lower, range_lower) if l is not None)
            range_upper = min(u for u in (upper, range_upper) if u is not None)

            ranges.add(result, (range_lower, range_upper))

        elif i == 0 and implicit_inclusion:
            # an exclusive range is given in first place, thus `ranges` is still empty
            assert not inclusive
            assert len(result) == 0

            # it eventually results in adding 1-2 range(s) around the exclusive range
            # because all integers are included before the exclusion,

            # complement omitted endpoints with the entire range
            range_lower = lower if range_lower is None else range_lower
            range_upper = upper if range_upper is None else range_upper

            for l, u in ((lower, range_lower), (range_upper, upper)):
                if _both_none(l, u):
                    # one of 2 separated ranges is actually an empty range
                    continue
                if not _both_filled(l, u):
                    # endpoints must be specified as we're now going to an add range
                    raise ValueError(f"Endpoint is missing: {single_range}")
                assert l is not None
                assert u is not None
                ranges.add(result, (l, u))

        elif _both_filled(range_lower, range_upper):
            assert not inclusive

            # both endpoints of a range are specified
            assert range_lower is not None
            assert range_upper is not None
            ranges.subtract(result, (range_lower, range_upper))

        else:
            assert not inclusive

            # one endpoint is specified, and another is None
            assert not _both_filled(range_lower, range_upper)
            assert not _both_none(range_lower, range_upper)
            # ...thus, cropping is performed on only one side
            ranges.crop(result, lower=range_upper, upper=range_lower)

    return result
