import pytest  # type: ignore
from jsonpath_ng import Child, Fields, Root

from gymnasdicts.utils import (
    _pointer_to_tuple,
    aggregate_two_items,
    group_by,
    parse_pointer,
    set_dict_leaf_to_list,
)


@pytest.mark.parametrize(
    "iterable, key, expected",
    [
        (
            [("b", 2, True), ("a", 1, False), ("b", 1, True)],
            lambda x: x[0],
            [[("a", 1, False)], [("b", 2, True), ("b", 1, True)]],
        ),
        (
            [("b", 2, True), ("a", 1, False), ("b", 1, True)],
            lambda x: x[1],
            [[("a", 1, False), ("b", 1, True)], [("b", 2, True)]],
        ),
        (
            [("b", 2, True), ("a", 1, False), ("b", 1, True)],
            lambda x: x[2],
            [[("a", 1, False)], [("b", 2, True), ("b", 1, True)]],
        ),
    ],
)
def test_group_by(iterable, key, expected):
    assert list(group_by(iterable, key)) == expected


@pytest.mark.parametrize(
    "pointer, expected",
    [
        (Child(Fields("a"), Fields("b")), (("a",), ("b",))),
        (Child(Root(), Fields("a")), (("a",),)),
        (Child(Fields("a"), Child(Fields("b"), Fields("c"))), (("a",), ("b",), ("c",))),
    ],
)
def test__pointer_to_tuple(pointer, expected):
    assert _pointer_to_tuple(pointer) == expected


@pytest.mark.parametrize(
    "text, nested, flattened",
    [
        ("$.a[:]", (("a",),), ("a",)),
        ("$.a[*].b", (("a",), ("b",)), ("a", "b")),
        ("$['a'][*]", (("a",),), ("a",)),
        ("$['a'][*]['b']", (("a",), ("b",)), ("a", "b")),
        ("$['a'][*][b, c]", (("a",), ("b", "c")), ("a", "b", "c")),
        ("$.a", (("a",),), ("a",)),
    ],
)
def test_parse_pointer(text, nested, flattened):
    assert parse_pointer(text, False) == nested
    assert parse_pointer(text, True) == flattened


def test_parse_pointer_fail():
    with pytest.raises(ValueError) as value_error:
        parse_pointer("x&]")
    assert str(value_error.value) == "Parse error at 1:2 near token ] (])"


@pytest.mark.parametrize(
    "left, right, pointer, expected",
    [
        (
            {"a": {"x": [3], "y": 5, "z": [9]}},
            {"a": {"x": [4], "y": 5, "z": [10]}},
            {"a": ["x", "z"]},
            {"a": {"x": [3, 4], "y": 5, "z": [9, 10]}},
        ),
        (
            {"a": {"x": [3], "y": 5, "z": 9}},
            {"a": {"x": [4], "y": 5, "z": 10}},
            {"a": ["x", "z"]},
            {"a": {"x": [3, 4], "y": 5, "z": 19}},
        ),
        (
            {"a": {"x": [3], "y": 5, "z": 9}},
            {"a": {"x": [4], "y": 5, "z": 9}},
            {"a": ["x"]},
            {"a": {"x": [3, 4], "y": 5, "z": 9}},
        ),
        (
            {"x": {"a": [3]}, "y": 5, "z": {"a": 9}},
            {"x": {"a": [4]}, "y": 5, "z": {"a": 10}},
            {"x": ["a"], "z": ["a"]},
            {"x": {"a": [3, 4]}, "y": 5, "z": {"a": 19}},
        ),
        (
            {"x": [{"a": [3], "b": 9}], "y": 5, "z": {"a": 9}},
            {"x": [{"a": [4], "b": 9}], "y": 5, "z": {"a": 10}},
            {"x": ["a"], "z": ["a"]},
            {"x": [{"a": [3, 4], "b": 9}], "y": 5, "z": {"a": 19}},
        ),
    ],
)
def test_compress_two_objects(left, right, pointer, expected):
    assert aggregate_two_items(left, right, pointer, lambda x, y: x + y) == expected


def summate(x, y):
    try:
        return sum(x + y)
    except TypeError:
        return x + y


@pytest.mark.parametrize(
    "aggregation_function, expected",
    [
        (lambda x, y: [x, y], {"a": {"x": [[3], [4, 5, 5]], "y": 5, "z": [9, 10]}}),
        (lambda x, y: summate(x, y), {"a": {"x": 17, "y": 5, "z": 19}}),
        (lambda x, y: x == y, {"a": {"x": False, "y": 5, "z": False}}),
    ],
)
def test_compress_two_objects_with_aggregation_func(aggregation_function, expected):
    """same input, different outputs"""
    a = {"a": {"x": [3], "y": 5, "z": 9}}
    b = {"a": {"x": [4, 5, 5], "y": 5, "z": 10}}
    assert (
        aggregate_two_items(a, b, {"a": ["x", "z"]}, aggregation=aggregation_function)
        == expected
    )


@pytest.mark.parametrize(
    "left, right, path, message",
    [
        (1, 1, "$", "cant use jsonpath on a primitive!"),
        ({"a": 1}, {"a": 1}, ["a", "b"], "path contains fields not in payload!"),
    ],
)
def test_compress_two_objects_fails(left, right, path, message):
    with pytest.raises(AssertionError) as value_error:
        aggregate_two_items(left, right, path, lambda x, y: x + y)
    assert str(value_error.value) == message


@pytest.mark.parametrize(
    "dictionary, keys, expected",
    [
        (
            {"a": {"b": {"c": None, "d": 2}}},
            [["a"], ["b"], ["c"]],
            {"a": {"b": {"c": [None], "d": 2}}},
        ),
        (
            {"a": {"b": {"c": None, "d": 2}}},
            [["a"], ["b"]],
            {"a": {"b": [{"c": None, "d": 2}]}},
        ),
        (
            {"a": {"b": {"c": None, "d": 2}}},
            [["a"], ["b"], ["c", "d"]],
            {"a": {"b": {"c": [None], "d": [2]}}},
        ),
    ],
)
def test_set_dict_leaf_to_list(dictionary, keys, expected):
    set_dict_leaf_to_list(dictionary, *keys)
    assert dictionary == expected
