from typing import Tuple, List, Any, Union

Endpoints = Tuple[int, int]
Ranges = List[Endpoints]


def _test_ranges_sorted(ranges: Ranges):
    return len(ranges) == 0 or (
        all(r[0] < r[1] for r in ranges)
        and all(prev[1] < next[0] for prev, next in zip(ranges, ranges[1:]))
    )


def find_index(ranges: Ranges, n: int) -> Tuple[bool, int]:
    """Search for the range which involves `n` in its endpoint, and return a tuple of
    a boolean which tells if such range exists and the index of the range.

    Even if `n` is not involved in any ranges, an index of the nearest range will be
    returned. For example, when (False, i) is returned it means
    ``ranges[i][1] < n < ranges[i+1][0]` would be True.

    :param ranges: A list of ranges to search.
    :param n: An integer to be searched for.
    :return: A 2-tuple; a boolean which indicates whether a range which involves `n` is
             in the list, and an index of the (perhaps nearest) range.
    """
    # ensure ranges are sorted
    assert _test_ranges_sorted(ranges)

    # do binary search
    start = 0
    end = len(ranges)
    while start < end:
        mid = start + (end - start) // 2
        mid_lower, mid_upper = ranges[mid]
        if mid_lower <= n <= mid_upper:
            # NOTE: we don't have to compare `n` by `n < mid_upper`
            #       since we're checking if `n` is involved, not contained, in the range.
            return True, mid
        elif n < mid_lower:
            end = mid
        else:
            assert mid_upper <= n
            start = mid + 1

    return False, start


def _splice_list(ls: List[Any], index: int, remove_count: int, *additions: Any) -> None:
    """Insert some elements to the given list and also remove some elements from the list.

    :param ls: A list to modify.
    :param index: A position to insert elements to and/or remove elements from.
    :param remove_count: The number of elements to be removed.
    :param additions: The elements to be added.
    """
    assert index >= 0
    assert 0 <= remove_count
    addition_count = len(additions) if additions else 0
    overwrite_count = min(remove_count, addition_count)
    for i in range(overwrite_count):
        ls[index + i] = additions[i]
    for a in range(addition_count - overwrite_count):
        ls.insert(index + overwrite_count + a, additions[overwrite_count + a])
    if remove_count - overwrite_count >= 1:
        del ls[index + overwrite_count : index + remove_count]


def _splice_ranges(
    ranges: Ranges, index: int, remove_count: int, *additions: Endpoints
) -> None:
    """``splice_list`` for ranges. Empty ranges are ignored and won't be added.

    :param ranges: A ranges list to modify.
    :param index: A position to put ranges to and/or remove ranges from.
    :param remove_count: The number of ranges to be removed.
    :param additions: The ranges to be added.
    """
    assert _test_ranges_sorted(ranges)
    assert all(a[0] <= a[1] for a in additions)
    _splice_list(ranges, index, remove_count, *((l, u) for l, u in additions if l < u))
    assert _test_ranges_sorted(ranges)


def add(ranges: Ranges, addition: Endpoints) -> None:
    """Add a range to a list.

    :param ranges: A ranges list to add into.
    :param addition: A range to be added.
    """
    if addition[0] == addition[1]:
        # do nothing as adding an empty range
        return

    assert addition[0] < addition[1]

    found_lower, index_lower = find_index(ranges, addition[0])
    found_upper, index_upper = find_index(ranges, addition[1])

    assert index_lower <= index_upper

    # this range will be eventually added in to the ranges list
    new_range = (
        (ranges[index_lower] if found_lower else addition)[0],
        (ranges[index_upper] if found_upper else addition)[1],
    )

    _splice_ranges(
        ranges,
        index_lower,
        index_upper - index_lower + (1 if found_upper else 0),
        new_range,
    )


def subtract(ranges: Ranges, subtraction: Endpoints) -> None:
    """Subtract a range from a list.

    :param ranges: A ranges list to removed from.
    :param subtraction: A range to be removed.
    """

    if not ranges or subtraction[0] == subtraction[1]:
        # do nothing as removing [from] an empty range
        return None

    sub_lower, sub_upper = subtraction

    assert sub_lower <= sub_upper

    found_lower, index_lower = find_index(ranges, sub_lower)
    found_upper, index_upper = find_index(ranges, sub_upper)

    assert index_lower <= index_upper

    # subtraction eventually adds 2 ranges at most to both smaller side and
    # larger side of the subtraction range.
    # None means there won't be addition on a side.
    side_ranges = tuple(
        e
        for e in (
            # smaller side
            ((ranges[index_lower][0], sub_lower) if found_lower else None),
            # larger side
            ((sub_upper, ranges[index_upper][1]) if found_upper else None),
        )
        if e is not None
    )

    _splice_ranges(
        ranges,
        index_lower,
        index_upper - index_lower + (1 if side_ranges else 0),
        *side_ranges,
    )


def crop(ranges: Ranges, lower: Union[int, None], upper: Union[int, None]) -> None:
    """Crop ranges to fit the given endpoints.

    :param ranges: A ranges list to be cropped.
    :param lower: The *inclusive* lower endpoint.
    :param upper: The *exclusive* upper endpoint.
    """
    assert (
        lower is None or upper is None or lower <= upper
    ), "lower <= upper if both lower and upper are specified"

    if not ranges:
        return None

    if lower is not None:
        found_lower, index_lower = find_index(ranges, lower)
        if found_lower:
            _splice_ranges(ranges, 0, index_lower + 1, (lower, ranges[index_lower][1]))
        else:
            _splice_ranges(ranges, 0, index_lower)
    if upper is not None:
        found_upper, index_upper = find_index(ranges, upper)
        if found_upper:
            _splice_ranges(
                ranges,
                index_upper,
                len(ranges) - index_upper,
                (ranges[index_upper][0], upper),
            )
        else:
            _splice_ranges(ranges, index_upper, len(ranges) - index_upper)
