import pytest  # type: ignore
from jsonpath_ng import Child, Fields, Root

from gymnasdicts.utils import (
    _pointer_to_tuple,
    compress_two_objects,
    group_by,
    parse_pointer,
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
            [["a"], ["x", "z"]],
            {"a": {"x": [3, 4], "y": 5, "z": [9, 10]}},
        ),
        (
            {"a": {"x": [3], "y": 5, "z": 9}},
            {"a": {"x": [4], "y": 5, "z": 10}},
            [["a"], ["x", "z"]],
            {"a": {"x": [3, 4], "y": 5, "z": 19}},
        ),
        (
            {"a": {"x": [3], "y": 5, "z": 9}},
            {"a": {"x": [4], "y": 5, "z": 9}},
            [["a"], ["x"]],
            {"a": {"x": [3, 4], "y": 5, "z": 9}},
        ),
        (
            {"x": {"a": [3]}, "y": 5, "z": {"a": 9}},
            {"x": {"a": [4]}, "y": 5, "z": {"a": 10}},
            [["x", "z"], ["a"]],
            {"x": {"a": [3, 4]}, "y": 5, "z": {"a": 19}},
        ),
        (
            {"x": [{"a": [3], "b": 9}], "y": 5, "z": {"a": 9}},
            {"x": [{"a": [4], "b": 9}], "y": 5, "z": {"a": 10}},
            [["x", "z"], ["a"]],
            {"x": [{"a": [3, 4], "b": 9}], "y": 5, "z": {"a": 19}},
        ),
    ],
)
def test_compress_two_objects(left, right, pointer, expected):
    assert compress_two_objects(left, right, *pointer) == expected


def test_compress_two_objects_fails():
    with pytest.raises(ValueError) as value_error:
        compress_two_objects(1, 1, "$")
    assert str(value_error.value) == "cant use jsonpath on a primitive!"
