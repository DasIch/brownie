# coding: utf-8
"""
    brownie.itools
    ~~~~~~~~~~~~~~

    Implements :mod:`itertools` functions for earlier version of Python.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, PSF see LICENSE.rst for details
"""
from itertools import izip


def product(*iterables, **kwargs):
    """
    Cartesian product of input iterables.

    Equivalent to nested for-loops in a generator expression. For example,
    ``product(A, B)`` returns the same as ``((x, y) for x in A for y in B)``.

    The nested loops cycle like an odometer with the rightmost element
    advancing on every iteration. The pattern creates a lexicographic ordering
    so that if the input's iterables are sorted, the product tuples are emitted
    in sorted order.

    To compute the product of an iterable with itself, specify the number of
    repetitions with the optional `repeat` keyword argument. For example,
    ``product(A, repeat=4)`` means the same as ``product(A, A, A, A)``.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    pools = map(tuple, iterables) * kwargs.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)


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

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(xrange(n), repeat=r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)


def compress(data, selectors):
    """
    Make an iterator that filters elements from the `data` returning only
    those that have a corresponding element in `selectors` that evaluates to
    ``True``. Stops when either the `data` or `selectors` iterables have been
    exhausted.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    return (d for d, s in izip(data, selectors) if s)


def count(start=0, step=1):
    """
    Make an iterator that returns evenly spaced values starting with `start`.
    Often used as an argument to :func:`imap` to generate consecutive data
    points. Also, used with :func:`izip` to add sequence numbers.

    When counting with floating point numbers, better accuracy can sometimes
    be achieved by substituting multiplicative code such as:
    ``(start + step * i for i in count())``.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    n = start
    while True:
        yield n
        n += step
