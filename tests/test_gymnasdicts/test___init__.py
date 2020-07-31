from gymnasdicts import Query


def test_chain():
    payload = {
        "sales": [
            {"id": 1, "number": 34, "date": "2020-01-04"},
            {"id": 2, "number": 12, "date": "2020-02-05"},
            {"id": 3, "number": -4, "date": "2020-03-06"},
        ],
        "prices": [
            {"id": 1, "cost": {"value": 0.98, "denomination": "pounds"}},
            {"id": 2, "cost": {"value": 34, "denomination": "pence"}},
            {"id": 3, "cost": {"value": 1.02, "denomination": "pounds"}},
        ],
        "accounting": [
            {"denomination": "pounds", "multiplier": 1},
            {"denomination": "pence", "multiplier": 0.01},
        ],
    }

    q = Query(payload)
    s = q.select(
        sales_id="$.sales[*].id",
        number="$.sales[*].number",
        price_id="$.prices[*].id",
        cost="$.prices[*].cost[*].value",
        denom_1="$.prices[*].cost[*].denomination",
        denom_2="$.accounting[*].denomination",
        multiplier="$.accounting[*].multiplier",
    )
    w = s.where(
        lambda sales_id, price_id: sales_id == price_id,
        lambda number: number > 0,
        lambda denom_1, denom_2: denom_1 == denom_2,
    )
    i = w.into(lambda number, cost, multiplier: number * cost * multiplier)
    assert sum(i) == 37.4
