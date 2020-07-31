import pytest  # type: ignore

from gymnasdicts.utils import group_by, parse_pointer


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
    "text, expected",
    [
        ("$.a[:]", ("a",)),
        ("$.a[*].b", ("a", "b")),
        ("$['a'][*]", ("a",)),
        ("$['a'][*]['b']", ("a", "b")),
        ("$.a", ("a",)),
    ],
)
def test_parse_pointer(text, expected):
    assert parse_pointer(text) == expected


def test_parse_pointer_fail():
    with pytest.raises(ValueError) as value_error:
        parse_pointer("x&]")
    assert str(value_error.value) == "Parse error at 1:2 near token ] (])"
