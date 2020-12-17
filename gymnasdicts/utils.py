import collections
from itertools import groupby
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple

from jsonpath_ng import Child, Fields, parse


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


def merge(dictionaries: Sequence[Dict]) -> Dict:
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
    return dict(collections.ChainMap(*reversed(dictionaries)))


def _pointer_to_tuple(pointer: Any) -> Tuple[str, ...]:
    """recursively flattens jsonpath-ng tree into a tuple of str
    :example:
        >>> ptr = Child(Fields("A"), Child(Fields("B"), Fields("C")))
        >>> _pointer_to_tuple(ptr)
        ('A', 'B', 'C')
    """
    if isinstance(pointer, Child):
        return _pointer_to_tuple(pointer.left) + _pointer_to_tuple(pointer.right)
    if isinstance(pointer, Fields):
        return pointer.fields
    return tuple()


def parse_pointer(pointer_str: str) -> Tuple[str, ...]:
    """uses jsonpath-ng lib to parse various path formats
    into a standard form returning only the relevant fields
    """
    try:
        pointer = parse(pointer_str)
    except Exception as exception:  # not my fault,
        # it really is implemented as a raw Exception in this package
        raise ValueError(f"{exception}")

    return _pointer_to_tuple(pointer)
