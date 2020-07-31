import pytest  # type: ignore

from gymnasdicts.base import into, select, where


@pytest.mark.parametrize(
    "payload, conditions, expected",
    [
        (
            [
                dict(x=1, y=1, z=1),
                dict(x=1, y=2, z=1),
                dict(x=2, y=1, z=1),
                dict(x=2, y=2, z=1),
            ],
            (lambda x, y: x == y,),
            [{"x": 1, "y": 1, "z": 1}, {"x": 2, "y": 2, "z": 1}],
        ),
        (
            [
                dict(x=1, y=1, z=1),
                dict(x=1, y=2, z=1),
                dict(x=2, y=1, z=1),
                dict(x=2, y=2, z=1),
            ],
            (lambda x, y: x == y, lambda x, z: x > z),
            [{"x": 2, "y": 2, "z": 1}],
        ),
    ],
)
def test_where(payload, conditions, expected):
    assert list(where(payload, *conditions)) == expected


@pytest.mark.parametrize(
    "payload, conditions, expected",
    [
        (
            [
                dict(x=1, y=1, z=1),
                dict(x=1, y=2, z=1),
                dict(x=2, y=1, z=1),
                dict(x=2, y=2, z=1),
            ],
            lambda x, y, z: x * y + z,
            [2, 3, 3, 5],
        ),
        (
            [
                dict(x=[1, 2, 3], y=1, z=1),
                dict(x=[1, 2, 3], y=2, z=2),
                dict(x=[1, 2, 3], y=1, z=3),
                dict(x=[1, 2, 3], y=2, z=-1),
            ],
            lambda x, y, z: {y: sum(xx * z for xx in x)},
            [{1: 6}, {2: 12}, {1: 18}, {2: -6}],
        ),
    ],
)
def test_into(payload, conditions, expected):
    assert list(into(payload, conditions)) == expected


@pytest.mark.parametrize("function", [where, into])
def test_where_fail(function):
    payload = [
        dict(x=1, y=1, z=1),
        dict(x=1, y=2, z=1),
        dict(x=2, y=1, z=1),
        dict(x=2, y=2, z=1),
    ]
    with pytest.raises(ValueError) as key_error:
        next(function(payload, lambda a, b: a == b))
    assert "argument-names don't match your arg-names in your payload" == str(
        key_error.value
    )


@pytest.mark.parametrize(
    "payload, conditions, expected",
    [
        (
            {
                "db": {
                    "sales": [
                        {
                            "product": "mask",
                            "days": [
                                {"number": 4, "day": "monday"},
                                {"number": 6, "day": "wednesday"},
                            ],
                        },
                        {
                            "product": "glove",
                            "days": [
                                {"number": 1, "day": "monday"},
                                {"number": 2, "day": "tuesday"},
                            ],
                        },
                    ],
                    "prices": [
                        {"product": [{"name": "mask"}, {"name": "coat"}], "cost": 55},
                        {"product": [{"name": "glove"}], "cost": 5},
                    ],
                }
            },
            {
                "product_id_1": "$.db[*].sales[*].product",
                "number_sold": "$.db[*].sales[*].days[*].number",
                "product_id_2": "$.db[*].prices[*].product[*].name",
                "product_prices": "$.db[*].prices[*].cost",
            },
            [
                {
                    "number_sold": 4,
                    "product_id_1": "mask",
                    "product_id_2": "mask",
                    "product_prices": 55,
                },
                {
                    "number_sold": 4,
                    "product_id_1": "mask",
                    "product_id_2": "coat",
                    "product_prices": 55,
                },
                {
                    "number_sold": 4,
                    "product_id_1": "mask",
                    "product_id_2": "glove",
                    "product_prices": 5,
                },
                {
                    "number_sold": 6,
                    "product_id_1": "mask",
                    "product_id_2": "mask",
                    "product_prices": 55,
                },
                {
                    "number_sold": 6,
                    "product_id_1": "mask",
                    "product_id_2": "coat",
                    "product_prices": 55,
                },
                {
                    "number_sold": 6,
                    "product_id_1": "mask",
                    "product_id_2": "glove",
                    "product_prices": 5,
                },
                {
                    "number_sold": 1,
                    "product_id_1": "glove",
                    "product_id_2": "mask",
                    "product_prices": 55,
                },
                {
                    "number_sold": 1,
                    "product_id_1": "glove",
                    "product_id_2": "coat",
                    "product_prices": 55,
                },
                {
                    "number_sold": 1,
                    "product_id_1": "glove",
                    "product_id_2": "glove",
                    "product_prices": 5,
                },
                {
                    "number_sold": 2,
                    "product_id_1": "glove",
                    "product_id_2": "mask",
                    "product_prices": 55,
                },
                {
                    "number_sold": 2,
                    "product_id_1": "glove",
                    "product_id_2": "coat",
                    "product_prices": 55,
                },
                {
                    "number_sold": 2,
                    "product_id_1": "glove",
                    "product_id_2": "glove",
                    "product_prices": 5,
                },
            ],
        ),
    ],
)
def test_select(payload, conditions, expected):
    assert list(select([payload], **conditions)) == expected


@pytest.mark.parametrize(
    "payload, pointers, message",
    [
        ([2], {}, "unexpected payload type"),
        ([{}], {"a": "$.x"}, "'x' not found in '{}'"),
    ],
)
def test_select_fail(payload, pointers, message):
    with pytest.raises(ValueError) as value_error:
        select(payload, **pointers)
    assert str(value_error.value) == message
