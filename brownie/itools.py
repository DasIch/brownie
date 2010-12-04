# coding: utf-8
"""
    brownie.itools
    ~~~~~~~~~~~~~~

    Implements :mod:`itertools` functions for earlier version of Python.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, PSF see LICENSE.rst for details
"""
from itertools import product


def combinations_with_replacement(iterable, r):
    """
    Return `r` length subsequences of elements from the `iterable` allowing
    individual elements to be replaced more than once.

    Combinations are emitted in lexicographic sort order. So, if the input
    `iterable` is sorted, the combinations tuples will be produced in sorted
    order.

    Elements are treated as unique based on their position, not on their value.
    So if the input elements are unique, the generated combinations will also
    be unique.

    The number of items returned is ``(n + r - 1)! / r! / (n - 1)!`` when
    ``n > 0``.

    .. note:: Software and documentation for this method is taken from
              CPython, :ref:`license details <psf-license>`.
    """
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(xrange(n), repeat=r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
