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


def _pointer_to_tuple(pointer: Any) -> Tuple[Tuple[str, ...], ...]:
    """recursively flattens jsonpath-ng tree into a tuple of tuple of str
    :example:
        >>> ptr = Child(Fields("A"), Child(Fields("B"), Fields("C", "D")))
        >>> _pointer_to_tuple(ptr)
        (('A',), ('B',), ('C', 'D'))
    """
    if isinstance(pointer, Child):
        return _pointer_to_tuple(pointer.left) + _pointer_to_tuple(pointer.right)
    if isinstance(pointer, Fields):
        return (pointer.fields,)
    return tuple()


def parse_pointer(pointer_str: str, flatten=True) -> Tuple:
    """uses jsonpath-ng lib to parse various path formats
    into a standard form returning only the relevant fields
    """
    try:
        pointer = parse(pointer_str)
    except Exception as exception:  # not my fault,
        # it really is implemented as a raw Exception in this package
        raise ValueError(f"{exception}")

    nested_tuples = _pointer_to_tuple(pointer)
    if not flatten:
        return nested_tuples
    return sum(nested_tuples, tuple())


def compress_two_objects(left, right, *path):
    """
    :example:
        >>> a = {"a": {"x": [3], "y": 5, "z": 9}}
        >>> b = {"a": {"x": [4], "y": 5, "z": 10}}
        >>> compress_two_objects(a, b, ["a"], ["x", "z"])
        {'a': {'x': [3, 4], 'y': 5, 'z': 19}}

    """
    if not path:
        assert left == right  # check objects are the same
        return left  # return one of them

    assert type(left) == type(right)

    if isinstance(left, list):
        assert len(left) == len(right)
        return [
            compress_two_objects(left_item, right_item, *path)
            for left_item, right_item in zip(left, right)
        ]

    if isinstance(left, dict):
        assert left.keys() == right.keys()

        head, *tail = path
        ret = {}
        for key in left:
            if key not in head:  # check equal and move on
                ret[key] = compress_two_objects(left[key], right[key])
            elif not tail:  # end of the line, sum these objects
                ret[key] = left[key] + right[key]
            else:  # ..continue
                ret[key] = compress_two_objects(left[key], right[key], *tail)

        return ret

    raise ValueError("cant use jsonpath on a primitive!")
