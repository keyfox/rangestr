from parameterized import param


valid_cases_implicit_inclusion = [
    # can enable/disable by passing an argument
    param([(0, 25), (75, 101)], "^25-74", lower=0, upper=100, implicit_inclusion=True),
    param([], "^25-74", lower=0, upper=100, implicit_inclusion=False),
    # no implicit inclusion by default
    param([], "^25-74", lower=0, upper=100),
    # only the first exclusive range triggers implicit inclusion
    param([(1, 6)], "^8-10,^6-10", lower=1, upper=10, implicit_inclusion=True),
    # When implicit inclusion is disabled,
    # an exclusion range needs neither `lower` nor `upper`
    param([], "^50-", implicit_inclusion=False),
    param([], "^-50", implicit_inclusion=False),
    param([], "^25-74", implicit_inclusion=False),
]

valid_cases = [
    # empty string makes no sequence
    param([], ""),
    # single integer makes a range contains only the integer itself
    param([(0, 1)], "0"),
    param([(100, 101)], "100"),
    # range makes a sequence, both endpoints are included
    param([(0, 1)], "0-0"),
    param([(0, 2)], "0-1"),
    param([(0, 101)], "0-100"),
    # If negative integers are involved, pass `delimiter` argument to resolve ambiguity
    param([(-1, 0)], "-1", delimiter=".."),
    param([(-1, 1)], "-1..0", delimiter=".."),
    # no matter what the range requests, endpoints are respected
    param([(333, 1001)], "1-1000", lower=333),
    param([(1, 667)], "1-1000", upper=666),
    param([(333, 667)], "1-1000", lower=333, upper=666),
    # upper-only range makes a sequence, respecting `lower`
    param([(0, 51)], "-50", lower=0),
    # lower-only range makes a sequence, respecting `upper`
    param([(50, 101)], "50-", upper=100),
    # comma-separated range representation will be concatenated
    param([(0, 2)], "0,1"),
    param([(0, 3), (5, 8)], "0-2,5-7"),
    param([(0, 11)], "0-5,6-10"),
    # won't make duplicated (intersected) ranges
    param([(0, 11)], "0-8,2-10"),
    # ranges are processed from the left to right
    param([(0, 3), (8, 11)], "0-10,^3-7"),
    param([(3, 8)], "^0-10,3-7", lower=0, upper=10),
    *valid_cases_implicit_inclusion,
]

error_cases_missing_endpoint = [
    # a lower-only inclusive range requires an upper endpoint
    param("50-"),
    # a upper-only inclusive range requires a lower endpoint
    param("-50"),
    # When implicit inclusion occurs,
    # an exclusion range requires endpoints which determines universe
    param("^50-", implicit_inclusion=True),  # requires `lower`
    param("^-50", implicit_inclusion=True),  # requires `upper`
    param("^25-74", implicit_inclusion=True),  # requires both
    # requires both; upper is missing
    param("^25-74", implicit_inclusion=True, lower=1),
    # requires both; lower is missing
    param("^25-74", implicit_inclusion=True, upper=100),
]
