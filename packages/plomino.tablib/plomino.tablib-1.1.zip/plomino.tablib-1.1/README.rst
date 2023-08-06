.. contents::

Introduction
============

Make Kenneth Reitz's tablib_ available to PlominoUtils.

Installation
============

Include ``plomino.tablib`` in the ``eggs`` section of your buildout::

    eggs =
        ...
        plomino.tablib

When this package is present, the ``dataset`` function is available to Plomino formulas. 

Examples::

    # Create a table from a list of lists:
    mytable = dataset([[1,2], [3,4]])

    # Create a table and specify headers:
    mytable = dataset([[1,2], [3,4]], headers=['col1', 'col2'])

    # Create a table from a list of dicts (sets headers):
    mytable = dataset([{'col1': 1, 'col2': 2]}, {'col1': 3, 'col2': 4}])

    # Get the table as CSV or JSON:
    mytable.csv
    mytable.json

    # Get the table as HTML or Excel:
    mytable.html
    mytable.xls

See tablib_ for more.


.. _tablib: http://pypi.python.org/pypi/tablib
