import collections
import inspect
from itertools import product
from typing import Any, Callable, Dict, Iterator, Tuple

from gymnasdicts.utils import group_by, merge, parse_pointer

JSON = Dict[str, Any]


def select(payloads: Iterator[JSON], **pointers: str) -> Iterator[JSON]:
    """
    :example:
        >>> payload = {
        ...     "A": [
        ...         {"C": 1, "D": True, "E": "2021-01-04"},
        ...         {"C": 1, "D": False, "E": "1982-12-2"},
        ...     ],
        ...     "B": [{"F": 1, "G":.22}, {"F": 2, "G": .43}],
        ... }
        >>> list(
        ...     select(
        ...         [payload],
        ...         a="$.A[:].D",
        ...         b="$.A[:].E",
        ...         c="$.B[:].F",
        ...         d="$.B[:].G",
        ...     )
        ... )
        [{'a': True, 'b': '2021-01-04', 'c': 1, 'd': 0.22}, {'a': True, 'b': '2021-01-04', 'c': 2, 'd': 0.43}, {'a': False, 'b': '1982-12-2', 'c': 1, 'd': 0.22}, {'a': False, 'b': '1982-12-2', 'c': 2, 'd': 0.43}]
    """

    res = []

    def _select(
        _payload: JSON, _pointers: Dict[str, Tuple[str, ...]], **_values: Any
    ) -> None:
        if isinstance(_payload, dict):
            accumulated_values = dict(_values)
            pointers_for_next_level: Dict = collections.defaultdict(dict)
            for key, (head, *tail) in _pointers.items():
                if tail:
                    pointers_for_next_level[head][key] = tail
                else:
                    if head not in _payload:
                        raise ValueError(f"'{head}' not found in '{_payload}'")
                    accumulated_values[key] = _payload[head]

            for head, kw in pointers_for_next_level.items():
                _select(_payload[head], kw, **accumulated_values)

            if not pointers_for_next_level:
                res.append(accumulated_values)

        elif isinstance(_payload, (list, tuple)):
            for value in _payload:
                _select(value, _pointers, **_values)
        else:
            raise ValueError("unexpected payload type")

    parsed_pointers = {
        pointer_key: parse_pointer(pointer) for pointer_key, pointer in pointers.items()
    }
    for payload in payloads:
        _select(payload, parsed_pointers)

    return map(merge, product(*group_by(res, tuple)))


def where(payload: Iterator[JSON], *conditions: Callable) -> Iterator[JSON]:
    """
    filters an iterator of dictionaries on conditions specifies by functions
    that return a boolean and the argument names correspond to keys in the
    dictionaries.

    :param payload:
    :param conditions:
    :return:

    :example:
        >>> payload = [
        ...     dict(x=1, y=1, z=1),
        ...     dict(x=1, y=2, z=1),
        ...     dict(x=2, y=1, z=1),
        ...     dict(x=2, y=2, z=1),
        ... ]
        >>> list(where(payload, lambda x, y: x == y, lambda x, z: x > z))
        [{'x': 2, 'y': 2, 'z': 1}]
    """
    for record in payload:
        try:
            if all(
                condition(
                    *tuple(
                        record[param]
                        for param in inspect.getfullargspec(condition).args
                    )
                )
                for condition in conditions
            ):
                yield record

        except KeyError:
            raise ValueError(
                "argument-names don't match your arg-names in your payload"
            )


def into(payload: Iterator[JSON], template: Callable) -> Iterator[JSON]:
    """
    maps dictionaries to a new format via a function whoes areguments
    match the keys in the inital payload.

    :example:
        >>> payload = [
        ...     dict(x=[1, 2, 3], y=1, z=1),
        ...     dict(x=[1, 2, 3], y=2, z=2),
        ...     dict(x=[1, 2, 3], y=1, z=3),
        ...     dict(x=[1, 2, 3], y=2, z=-1),
        ... ]
        >>> list(into(payload, lambda x, y, z: {y: sum(xx * z for xx in x)}))
        [{1: 6}, {2: 12}, {1: 18}, {2: -6}]
    """
    for record in payload:
        try:
            yield template(
                *tuple(record[param] for param in inspect.getfullargspec(template).args)
            )
        except KeyError:
            raise ValueError(
                "argument-names don't match your arg-names in your payload"
            )
