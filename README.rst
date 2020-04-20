json_modify
-----------
.. image:: https://img.shields.io/pypi/v/json_modify
   :target: https://pypi.python.org/pypi/json_modify
.. image:: https://img.shields.io/pypi/pyversions/json_modify.svg
   :target: https://pypi.org/project/json_modify/
.. image:: https://img.shields.io/github/license/Enacero/json_modify
   :target: https://github.com/Enacero/json_modify/blob/master/LICENSE
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. image:: https://travis-ci.org/Enacero/json_modify.svg?branch=master
   :target: https://travis-ci.org/Enacero/json_modify
.. image:: https://codecov.io/gh/Enacero/json_modify/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Enacero/json_modify

``json_modify`` is simple library that helps apply modifications
to json/yaml files and python representations of json.

Installation
------------

.. code-block::

    pip install json_modify

Example
-------

.. code-block:: python

    from json_modify import apply_actions

    source = {
        "spec": {
            "name": "test",
            "metadata": [
                {"name": "test1", "value": "test1"},
                {"name": "test2", "value": "test2"}
            ],
            "values": {"value1": 10, "value2": 20}
        }
    }

    actions = [
        {"action": "add",
         "path": "spec/values",
         "value": {"value3": 30, "value4": 40}}
    ]

    result = apply_actions(source, actions)

    print(result)

    {"spec": {
        "name": "test",
        "metadata": [
            {"name": "test1", "value": "test1"},
            {"name": "test2", "value": "test2"}
        ],
        "values": {
            "value1": 10, "value2": 20,
            "value3": 30, "value4": 40}
        }
    }

Markers
-------
``json_modify`` uses markers to traverse lists. Markers should be used in ``path``
for example:

.. code-block:: python

    "path": "metadata/$project_name/name"

There are two types of markers:

* Filter marker (``$<marker_name>``) - the kind of marker, that is used to select
  dictionary in list by list of ``section[key] == value``. Filter marker should be
  described in action where it's used. For example:

.. code-block:: python

    {
        "action": "delete",
        "path": "metadata/$project_name/name",
        "project_name": [{"key": "name", "value": "nginx"}]
    }

* Index marker (``$<index>``) - the kind of marker, that is used to select specific
  element in list, by it's index. For example:

.. code-block:: python

    {
        "action": "replace",
        "path": ["users", "$0"],
        "value": { "name": "test_user", "id": 0}
    }

It's allowed to use any quantity of markers and mix both types of markers in single path.

Action schema
-------------
* ``action`` (Required): Type of action, possible values are: add, replace, delete,
  rename(only for dictionaries).
* ``path`` (Required): Path to the field that we want to change.
  ``path`` can be string, separated by delimiter (default is ``\``) or list of strings.
* ``value`` (Optional for delete, Required for other): Value that should be applied
  to specified path. The type of value is described for each action separately.
* ``marker`` (Required for each non index marker in path): List of dictionaries,
  that should be applied to find value in list. Each dictionary consist of:

  * ``key`` (Required): Name of the key that should be used for search.
  * ``value`` (Required): Value that is used to find concrete dictionary in
    list of dictionaries.

Supported actions
-----------------
#. ``add``: Insert values into section, specified by last key of ``path``.
   The last key in section should lead to list or dict section.

   * For add action on list ``value`` should be of type list, so that it'll be possible
     to extend current list.

   * For add action on dict ``value`` should be of type dict, so that we can update
     current dict.

#. ``replace``: Replace section, specified by last key of ``path`` with ``value``.

#. ``delete``: Delete section, specified by last key of ``path``.

#. ``rename``: Move content of section, specified by last key of ``path`` to section
   with name specified in ``value``.


TODO
----

 1. Add documentation to ReadTheDocs
 2. Add creation of action's by diff.

License
-------

Copyright Oleksii Petrenko, 2020.

Distributed under the terms of the `MIT`_ license,
json_modify is free and open source software.

.. _`MIT`: https://github.com/Enacero/json_modify/blob/master/LICENSE