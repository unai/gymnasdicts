import pytest  # type: ignore
from jsonpath_ng import Child, Fields, Root

from gymnasdicts.utils import _pointer_to_tuple, group_by, parse_pointer


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
