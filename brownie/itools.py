# coding: utf-8
"""
    brownie.itools
    ~~~~~~~~~~~~~~

    Implements :mod:`itertools` functions for earlier version of Python.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, PSF see LICENSE.rst for details
"""
from itertools import repeat, izip


class chain(object):
    """
    An iterator which yields elements from the given `iterables` until each
    iterable is exhausted.

    .. versionadded:: 0.2
    """
    @classmethod
    def from_iterable(cls, iterable):
        """
        Alternative constructor which takes an `iterable` yielding iterators,
        this can be used to chain an infinite number of iterators.
        """
        rv = object.__new__(cls)
        rv._init(iterable)
        return rv

    def __init__(self, *iterables):
        self._init(iterables)

    def _init(self, iterables):
        self.iterables = iter(iterables)
        self.current_iterable = iter([])

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.current_iterable.next()
        except StopIteration:
            self.current_iterable = iter(self.iterables.next())
            return self.current_iterable.next()


def izip_longest(*iterables, **kwargs):
    """
    Make an iterator that aggregates elements from each of the iterables. If
    the iterables are of uneven length, missing values are filled-in with
    `fillvalue`. Iteration continues until the longest iterable is exhausted.

    If one of the iterables is potentially infinite, then the
    :func:`izip_longest` function should be wrapped with something that limits
    the number of calls (for example :func:`itertools.islice` or
    :func:`itertools.takewhile`.) If not specified, `fillvalue` defaults to
    ``None``.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    fillvalue = kwargs.get('fillvalue')
    def sentinel(counter=([fillvalue] * (len(iterables) - 1)).pop):
        yield counter()
    fillers = repeat(fillvalue)
    iters = [chain(it, sentinel(), fillers) for it in iterables]
    try:
        for tup in izip(*iters):
            yield tup
    except IndexError:
        pass


def permutations(iterable, r=None):
    """
    Return successive `r` length permutations of elements in the `iterable`.

    If `r` is not specified or is ``None``, then `r` defaults to the length of
    the `iterable` and all possible full-length permutations are generated.

    Permutations are emitted in lexicographic sort order. So, if the input
    `iterable` is sorted, the permutation tuples will be produced in sorted
    order.

    Elements are treated as unique based on their position, not on their
    value. So if the input elements are unique, there will be no repeating
    value in each permutation.

    The number of items returned is ``n! / (n - r)!`` when ``0 <= r <= n`` or
    zero when `r > n`.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)


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


def starmap(function, iterable):
    """
    Make an iterator that computes the function using arguments obtained from
    the iterable. Used instead of :func:`itertools.imap` when an argument
    parameters are already grouped in tuples from a single iterable (the data
    has been "pre-zipped"). The difference between :func:`itertools.imap` and
    :func:`starmap` parallels the distinction between ``function(a, b)`` and
    ``function(*c)``.

    .. note:: Software and documentation for this function are taken from
              CPython, :ref:`license details <psf-license>`.
    """
    for args in iterable:
        yield function(*args)


def combinations_with_replacement(iterable, r):
    """
    Return `r` length sub-sequences of elements from the `iterable` allowing
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


def grouped(n, iterable, fillvalue=None):
    """
    Groups the items in the given `iterable` to tuples of size `n`. In order
    for groups to always be of the size `n` the `fillvalue` is used for
    padding.
    """
    return izip_longest(fillvalue=fillvalue, *([iter(iterable)] * n))


def unique(iterable, seen=None):
    """
    Yields items from the given `iterable` of (hashable) items, once seen an
    item is not yielded again.

    :param seen:
       An iterable specifying already 'seen' items which will be excluded
       from the result.

       .. versionadded:: 0.5

    .. versionchanged:: 0.5
       Items don't have to be hashable any more.
    """
    seen = set() if seen is None else set(seen)
    seen_unhashable = []
    for item in iterable:
        try:
            if item not in seen:
                seen.add(item)
                yield item
        except TypeError:
            if item not in seen_unhashable:
                seen_unhashable.append(item)
                yield item


def flatten(iterable, ignore=(basestring, )):
    """
    Flattens a nested `iterable`.

    :param ignore:
        Types of iterable objects which should be yielded as-is.

    .. versionadded:: 0.5
    """
    stack = [iter(iterable)]
    while stack:
        try:
            item = stack[-1].next()
            if isinstance(item, ignore):
                yield item
            elif isinstance(item, basestring) and len(item) == 1:
                yield item
            else:
                try:
                    stack.append(iter(item))
                except TypeError:
                    yield item
        except StopIteration:
            stack.pop()


__all__ = [
    'chain', 'izip_longest', 'permutations', 'product', 'starmap',
    'combinations_with_replacement', 'compress', 'count', 'grouped', 'unique',
    'flatten'
]
