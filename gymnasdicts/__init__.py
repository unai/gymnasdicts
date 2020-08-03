from __future__ import annotations

"""Top-level package for gymnasdicts."""

__author__ = """George Burton"""
__email__ = "george.burton@unai.com"
__version__ = "__version__ = '0.1.1'"


from typing import Callable, Iterator, Union

from gymnasdicts import base


class Query:
    """

    :example:
        >>> payload = {
        ...     "sales": [
        ...         {"id": 1, "number": 34},
        ...         {"id": 2, "number": 12},
        ...         {"id": 3, "number": -4}
        ...     ],
        ...     "prices": [
        ...         {"id": 1, "cost": 0.98},
        ...         {"id": 2, "cost": 0.34},
        ...         {"id": 3, "cost": 1.02}
        ...     ],
        ... }
        >>> q = Query(payload)
        >>> s = q.select(
        ...     sales_id="$.sales[*].id",
        ...     number="$.sales[*].number",
        ...     price_id="$.prices[*].id",
        ...     cost="$.prices[*].cost",
        ... )
        >>> w = s.where(
        ...     lambda sales_id, price_id: sales_id == price_id, lambda number: number > 0
        ... )
        >>> i = w.into(lambda number, cost: number * cost)
        >>> sum(i)
        37.4
    """

    def __init__(self, json_data: Union[base.JSON, Iterator[base.JSON]]) -> None:
        if isinstance(json_data, Iterator):
            self.json_data = json_data
        else:
            self.json_data = iter([json_data])

    def select(self, **pointers: str) -> Query:
        return Query(base.select(self.json_data, **pointers))

    def where(self, *conditions: Callable) -> Query:
        return Query(base.where(self.json_data, *conditions))

    def into(self, template: Callable) -> Query:
        return Query(base.into(self.json_data, template))

    def __iter__(self) -> Iterator[base.JSON]:
        for item in self.json_data:
            yield item
