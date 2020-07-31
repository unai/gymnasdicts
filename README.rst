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


This package exposes on class with three functions that can be chained together so that they
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

example
=======

.. code-block:: python

    from gymnasdicts import select

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
            {"denomination": "pounds", "multiplier": 1, },
            {"denomination": "pence", "multiplier": 0.01, }
        ]
    }

    s = select(
        payload,
        sales_id = "$.sales[:].id",
        number = "$.sales[:].number",
        price_id = "$.prices[:].id",
        cost = "$.prices[:].cost[:].value",
        denom_1 = "$.prices[:].cost[:].denomination",
        denom_2 = "$.accounting[:].denomination",
        multiplier = "$.accounting[:].multiplier"
    )
    w = s.where(
        lambda sales_id, price_id: sales_id == price_id,
        lambda number: number > 0,
        lambda denom_1, denom_2 : denom_1 == denom_2
    )
    i = w.into(lambda number, cost, multiplier: number * cost * multiplier)
    assert sum(i) == 37.4


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

so that `where` can be used in to do the job of `on`.

This is hideous, what about memory?!
=======================================
Generators take care of this.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
