# rangestr

A Python package for generating ranges of integers from a string.

```python
>>> from rangestr import rangestr
>>> list(rangestr("1-3, 8-10"))
[1, 2, 3, 8, 9, 10]
>>> list(rangestr("5-", upper=10))
[5, 6, 7, 8, 9, 10]
```

**IMPORTANT**: This module is experimental and under development,
it still might have some bugs and the API may change.
Use at your own risk.
 
## Requirements

  - Python 3.6 or later

## Usage

Import `rangestr` function and pass a string which represents ranges of integers.
It returns an iterator which iterates through integers represented by the passed string.

`rangestr` takes the following arguments:

| Name | Type | Required? | Description |
| --- | :---: | :---: | --- |
| `src` | string | YES | A string to be parsed (see examples below) |
| `lower` | int | depends on `src` | Lower *inclusive* endpoint of the entire range |
| `upper` | int | depends on `src` | Upper *inclusive* endpoint of the entire range |
| `delimiter` | string | No | A string used as a delimiter of endpoints of a range (default: `-`) |
| `implicit_inclusion` | bool | No | Whether to include all integers when an exclusive range comes in first (default: `False`) |

  - If the `src` contains half-open inclusive intervals, you MUST specify the omitted endpoint in `lower` and/or `upper`.
    For example, `100-` needs `upper`.
    - If `implicit_inclusion` is `True`, half-open *exclusive* intervals also need `lower` and/or `upper`.
      For example, `^-99` with `implicit_inclusion=True` also needs `upper`, since it has the same effect as `100-`.

### Examples

```python
# Use dash (-) to represent a range of integers.
# Both the lower value and the upper value are included.
rangestr("1-5")
# => 1, 2, 3, 4, 5

# Use comma (,) to enumerate multiple ranges.
# The result will be an union of those ranges.
# NOTE: whitespaces are stripped with `str.strip()`.
rangestr("1-3, 8-10")
# => 1, 2, 3, 8, 9, 10

# A single integer is regarded as a range which contains just that integer itself.
rangestr("100")
# => 100

# If you want to use negative integers, you have to specify an alternate string
# for a dash symbol to deal with ambiguity between dash (delimiter) and minus (negative). 
rangestr("-10..-5", delimiter="..")
# => -10, -9, -8, -7, -6, -5

# Use caret (^) to exclude a range of integers.
rangestr("1-5, ^2-4")
# => 1, 5

# Ranges are parsed from left to right just like addition and subtraction.
rangestr("1-5, ^2-4, 3")
# => 1, 3, 5 (Include 1-5, exclude 2-4, and then include 3)

# You can omit an endpoint of range as long as required endpoints are given.
# Both `lower` and `upper` are inclusive.
rangestr("6-", upper=10)
rangestr("-10", lower=6)
# => 6, 7, 8, 9, 10

# Once `lower` and/or `upper` are given, the result will be cropped as specified.
rangestr("1-100", lower=1, upper=5)
# => 1, 2, 3, 4, 5

# When `implicit_inclusion` is True and the first range is exclusive one, all integers are
# implicitly included beforehand.
# Note that if you set it to True you always have to specify both `lower` and `upper` to specify the
# range of 'all integers'.
rangestr("^6-10", lower=1, upper=10, implicit_inclusion=True)  
# => 1, 2, 3, 4, 5  (Exclude 6-10 from 1-10)

# Again, the implicit inclusion mentioned above is applied to only the first range.
rangestr("^6-10, ^4-5", lower=1, upper=10, implicit_inclusion=True)
# => 1, 2, 3  (Exclude 6-10 from 1-10, and then exclude 4-5)

# The implicit inclusion is disabled by default.
# In the following case, rangestr doesn't need neither `lower` nor `upper` because
# inclusion won't be caused by the exclusive range,
rangestr("^6-10", implicit_inclusion=False)
# => (empty)
```

### Extras

Q. I'm tired of passing the `delimiter` argument every time.

A. [functools.partial](https://docs.python.org/ja/3/library/functools.html#functools.partial)
would help.

```python
from functools import partial

from rangestr import rangestr as _rangestr

rangestr = partial(_rangestr, delimiter="..")

assert [-2, -1, 0, 1, 2] == [*rangestr("-2..2")], "No more delimiter!"
assert [1, 2, 3, 4, 5] == [*rangestr("1-5", delimiter="-")], "You can still overwrite"
```

## Testing

Clone this repository, install dependencies in `requirements.txt`, and then run `tox`.

You can also run tests individually:

- To perform unittests, run `python -m pytest`
- To perform type checking, run `mypy rangestr`

## License

rangestr is released under the MIT License, see [LICENSE](https://github.com/keyfox/rangestr/blob/main/LICENSE).
