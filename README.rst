===========
gymnasdicts
===========


.. image:: https://img.shields.io/pypi/v/gymnasdicts.svg
        :target: https://pypi.python.org/pypi/gymnasdicts

.. image:: https://img.shields.io/travis/unai/gymnasdicts.svg
        :target: https://travis-ci.com/unai/gymnasdicts

.. image:: https://readthedocs.org/projects/gymnasdicts/badge/?version=latest
        :target: https://gymnasdicts.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/unai/gymnasdicts/shield.svg
     :target: https://pyup.io/repos/github/unai/gymnasdicts/
     :alt: Updates


query json dicts


* Free software: Apache Software License 2.0
* Documentation: https://gymnasdicts.readthedocs.io.


Features
--------


`gymnasdicts` is a lightweight library for querying json compatible nested-dictionaries in Python.


This package exposes one class with four functions that can be chained together so that they
follow a sql-like convention.

Query
======
`Query` is the entry point for the library, it is the data-type that
is acted on and returned by all other methods.


select
======

`select` identifies and names the nested-keys in the json-objects to be used.
The first argument is the json object to be queried.
The remaining arguments are in the keyword-arg form where:

* the values are a restricted jsonpath, where no filtering is allowed.
* the keys are user-defined variables to which the values above are assigned.

where
=====
`where` filters the results of select by value. Its arguments are lambda functions
where the argument names correspond to the variables defined in `select`.

into
====
`into` defines the shape of the output. Its only argument is lambda function
where the argument names correspond to the variables defined in `select`.

aggregate
====
`aggregate` groups a sequence of payloads by some fields and sums the rest.
The fields to be summed are defined by a single jsonpath argument.

example
=======

.. code-block:: python

    from gymnasdicts import Query

    payload = {
        "patients": [
            {"id": 1, "name": "Bob", "dob": "1982-02-05"},
            {"id": 2, "name": "Sue", "dob": "2020-02-05"},
            {"id": 3, "name": "Sam", "dob": "2020-03-06"},
            {"id": 4, "name": "Kim", "dob": "2020-03-06"},
        ],
        "prescription": [
            {"id": 1, "price": 3, "drug": "Paracetamol"},
            {"id": 2, "price": 12, "drug": "Lisinopril"},
            {"id": 3, "price": 8, "drug": "Metformin"},
        ],
        "encounters": [
            {"id": 1, "patient_id": 1, "prescription_id": 1, "doctor": "Patel"},
            {"id": 2, "patient_id": 3, "prescription_id": 2, "doctor": "Patel"},
            {"id": 3, "patient_id": 3, "prescription_id": 1, "doctor": "Francis"},
            {"id": 4, "patient_id": 4, "prescription_id": 3, "doctor": "Francis"},
        ],
    }

    q = Query(payload)
    s = q.select(
        encounter_patient_id="$.encounters[*].patient_id",
        encounter_prescription_id="$.encounters[*].prescription_id",
        doctor="$.encounters[*].doctor",
        prescription_id="$.prescription[*].id",
        patient_id="$.patients[*].id",
        patient_name="$.patients[*].name",
        dob="$.patients[*].dob",
        price="$.prescription[*].price",
    )
    w = s.where(
        lambda encounter_prescription_id, prescription_id: encounter_prescription_id
        == prescription_id,
        lambda encounter_patient_id, patient_id: encounter_patient_id == patient_id,
        lambda dob: dob > "2020-01-01",
    )
    i = w.into(
        lambda price, doctor, patient_name: {
            "doctor": doctor,
            "patients": [patient_name],
            "cost": price,
        }
    )
    a = i.aggregate("$.['cost', 'patients']")
    expected = [
        {"doctor": "Patel", "patients": ["Sam"], "cost": 12},
        {"doctor": "Francis", "patients": ["Sam", "Kim"], "cost": 11},
    ]
    assert list(a) == expected

FAQ
---

What about joins?
===================
`select` is effectively a cartesian join on all supplied jsonpaths,
i.e.

.. code-block:: python

    Query({...}).select(x="$Tbl[:].a", y="$Tbl[:].b", z="$Tbl[:].c")

is equivalent to

.. code-block:: sql

    select A.a as x, B.b as y, C.c as z from Tbl as A, Tbl as B, Tbl as C

so that `where` can be used to do the job of `on`.

This is hideous, what about memory?!
=======================================
Generators take care of this.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

Thanks to kclaurelie_ for useful discussion re: the relationship between select/where and keys/values.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _kclaurelie: https://github.com/kclaurelie
