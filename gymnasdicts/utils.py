from itertools import groupby
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from jsonpath_ng import Fields, Root, parse


def group_by(iterable: List, key: Optional[Callable] = None) -> Iterator[List]:
    """
    :example:
        >>> payload = [("b", 2, True), ("a", 1, False), ("b", 1, True)]
        >>> result = group_by(payload, lambda x: x[0])
        >>> list(result)
        [[('a', 1, False)], [('b', 2, True), ('b', 1, True)]]
    """
    for _, values in groupby(sorted(iterable, key=key), key=key):
        yield list(values)


def merge(dictionaries: Iterator[Dict]) -> Dict:
    """merge and update many dictionaries
    :example:
        >>> merge(
        ...     (
        ...         {"a": 1, "b": 2},
        ...         {"b": 3, "c": 4},
        ...         {"c": 4, "d": 5}
        ...     )
        ... )
        {'a': 1, 'b': 3, 'c': 4, 'd': 5}

    """
    out = dict()
    for item in dictionaries:
        out.update(item)
    return out


def parse_pointer(pointer: str) -> Tuple[str, ...]:
    """uses jsonpath-ng lib to parse various path formats
    into a standard form returning only the relevant fields
    """
    try:
        _pointer = parse(pointer)
    except Exception as exception:  # not my fault,
        # it really is implemented as a raw Exception in this package
        raise ValueError(f"{exception}")

    res = []

    def _parse(element):
        if not isinstance(element, Root):
            _parse(element.left)
            if isinstance(element.right, Fields):
                res.append(element.right.fields[0])

    _parse(_pointer)
    return tuple(res)
