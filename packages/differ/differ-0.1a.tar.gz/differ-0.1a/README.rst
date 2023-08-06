Differ
######

.. image:: https://travis-ci.org/rshk/differ.svg?branch=master
    :target: https://travis-ci.org/rshk/differ

.. image:: https://coveralls.io/repos/rshk/differ/badge.png
    :target: https://coveralls.io/r/rshk/differ


Python library to calculate differences between objects.

Right now, it supports calculating differences between objects built
up of dicts, lists, tuples and base types.

The major advantage compared to other diff tools is it is able to detect
"slightly" changed objects that were repositioned in a list:

.. code-block:: python

    from differ import compare_objects

    seq1 = [
        {'a': 1, 'b': 1, 'c': 1},
        {'a': 2, 'b': 2, 'c': 2},
        {'a': 3, 'b': 3, 'c': 3},
    ]

    seq2 = [
        {'a': 30, 'b': 30, 'c': 3},
        {'a': 2, 'b': 20, 'c': 2},
        {'a': 1, 'b': 1, 'c': 10},
    ]

    diff = compare_objects(seq1, seq2)

Result:

.. code-block:: python

    {'added': [],
     'changed': [0, 1, 2],
     'distance': 1.0,
     'equal': [],
     'removed': [],
     'total': 3,
     'changes': {
        0: {
            'diff': {
                'added': [],
                'changed': ['c'],
                'changes': {'c': {'distance': 1.0, 'left': 1, 'right': 10}},
                'distance': 0.3333333333333333,
                'equal': ['a', 'b'],
                'removed': [],
                'total': 3},
            'distance': 0.3333333333333333,
            'pos': 2},
        1: {
            'diff': {
                'added': [],
                'changed': ['b'],
                'changes': {'b': {'distance': 1.0, 'left': 2, 'right': 20}},
                'distance': 0.3333333333333333,
                'equal': ['a', 'c'],
                'removed': [],
                'total': 3},
            'distance': 0.3333333333333333,
            'pos': 1},
        2: {
            'diff': {
                'added': [],
                'changed': ['a', 'b'],
                'changes': {'a': {'distance': 1.0, 'left': 3, 'right': 30},
                            'b': {'distance': 1.0, 'left': 3, 'right': 30}},
                'distance': 0.6666666666666666,
                'equal': ['c'],
                'removed': [],
                'total': 3},
            'distance': 0.6666666666666666,
            'pos': 0}}}
