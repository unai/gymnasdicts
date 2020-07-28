from itertools import groupby
from typing import Callable, Dict, Iterator, List, Optional


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


def strip_index(text: str) -> str:
    """strips out index tokens from jsonpath
    :example:
        >>> strip_index("abc[:]")
        'abc'
    """
    if text.endswith("[*]"):
        return text[:-3]
    if text.endswith("[:]"):
        return text[:-3]
    return text
