from __future__ import annotations

"""Top-level package for gymnasdicts."""

__author__ = """George Burton"""
__email__ = "george.burton@unai.com"
__version__ = "0.2.2"


from typing import Callable, Iterator, Union

from gymnasdicts import base


class Query:
    """

    :example:
    >>> payload = {
    ...     "patients": [
    ...         {"id": 1, "name": "Bob", "dob": "1982-02-05"},
    ...         {"id": 2, "name": "Sue", "dob": "2020-02-05"},
    ...         {"id": 3, "name": "Sam", "dob": "2020-03-06"},
    ...         {"id": 4, "name": "Kim", "dob": "2020-03-06"},
    ...     ],
    ...     "prescription": [
    ...         {"id": 1, "price": 3, "drug": "Paracetamol"},
    ...         {"id": 2, "price": 12, "drug": "Lisinopril"},
    ...         {"id": 3, "price": 8, "drug": "Metformin"},
    ...     ],
    ...     "encounters": [
    ...         {"id": 1, "patient_id": 1, "prescription_id": 1, "doctor": "Patel"},
    ...         {"id": 2, "patient_id": 3, "prescription_id": 2, "doctor": "Patel"},
    ...         {"id": 3, "patient_id": 3, "prescription_id": 1, "doctor": "Francis"},
    ...         {"id": 4, "patient_id": 4, "prescription_id": 3, "doctor": "Francis"},
    ...     ],
    ... }

    >>> q = Query(payload)
    >>> s = q.select(
    ...     encounter_patient_id="$.encounters[*].patient_id",
    ...     encounter_prescription_id="$.encounters[*].prescription_id",
    ...     doctor="$.encounters[*].doctor",
    ...     prescription_id="$.prescription[*].id",
    ...     patient_id="$.patients[*].id",
    ...     patient_name="$.patients[*].name",
    ...     dob="$.patients[*].dob",
    ...     price="$.prescription[*].price",
    ... )
    >>> w = s.where(
    ...     lambda encounter_prescription_id, prescription_id: encounter_prescription_id
    ...     == prescription_id,
    ...     lambda encounter_patient_id, patient_id: encounter_patient_id == patient_id,
    ...     lambda dob: dob > "2020-01-01",
    ... )
    >>> i = w.into(
    ...     lambda price, doctor, patient_name: {
    ...         "doctor": doctor,
    ...         "patients": [patient_name],
    ...         "cost": price,
    ...     }
    ... )
    >>> a = i.aggregate("$.['cost', 'patients']")
    >>> expected = [
    ...     {"doctor": "Patel", "patients": ["Sam"], "cost": 12},
    ...     {"doctor": "Francis", "patients": ["Sam", "Kim"], "cost": 11},
    ... ]
    >>> list(a) == expected
    True
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

    def aggregate(self, pointer: str) -> Query:
        return Query(base.aggregate(self.json_data, pointer))

    def __iter__(self) -> Iterator[base.JSON]:
        for item in self.json_data:
            yield item
