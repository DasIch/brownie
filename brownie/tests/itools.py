# coding: utf-8
"""
    brownie.tests.itools
    ~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.itools`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, Assert

from brownie.itools import (
    izip_longest,
    product,
    compress,
    count,
    permutations,
    combinations_with_replacement,
    starmap,
    grouped,
    unique,
    chain,
    flatten
)


tests = Tests()


@tests.test
def test_chain():
    list(chain([1, 2], [3, 4])) == [1, 2, 3, 4]
    list(chain.from_iterable([[1, 2], [3, 4]])) == [1, 2, 3, 4]


@tests.test
def test_izip_longest():
    tests = [
        (((['a', 'b'], ['c', 'd']), {}), [('a', 'c'), ('b', 'd')]),
        (((['a'], ['c', 'd']), {}), [('a', 'c'), (None, 'd')]),
        (((['a'], ['c', 'd']), {'fillvalue': 1}), [('a', 'c'), (1, 'd')])
    ]
    for test, result in tests:
        args, kwargs = test
        Assert(list(izip_longest(*args, **kwargs))) == result


@tests.test
def test_permutations():
    tests = [
        ((('abc', )), ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']),
        ((('abc', 1)), ['a', 'b', 'c']),
        ((('abc', 2)), ['ab', 'ac', 'ba', 'bc', 'ca', 'cb']),
        ((('abc', 4)), [])
    ]
    for test, result in tests:
        result = map(tuple, result)
        Assert(list(permutations(*test))) == result


@tests.test
def test_product():
    tests = [
        ((('ABCD', 'xy'), {}), ['Ax', 'Ay', 'Bx', 'By', 'Cx', 'Cy', 'Dx', 'Dy']),
        ((('01', ), {'repeat': 3}), [
            '000', '001', '010', '011', '100', '101', '110', '111'
        ])
    ]
    for test, result in tests:
        args, kwargs = test
        result = map(tuple, result)
        Assert(list(product(*args, **kwargs))) == result


@tests.test
def test_starmap():
    add = lambda a, b: a + b
    Assert(list(starmap(add, [(1, 2), (3, 4)]))) == [3, 7]


@tests.test
def test_combinations_with_replacement():
    tests = [
        (('ABC', 2), ['AA', 'AB', 'AC', 'BB', 'BC', 'CC']),
        (('ABC', 1), ['A', 'B', 'C']),
        (('ABC', 3), [
            'AAA', 'AAB', 'AAC', 'ABB', 'ABC', 'ACC', 'BBB', 'BBC', 'BCC', 'CCC'
        ])
    ]
    for test, result in tests:
        result = map(tuple, result)
        Assert(list(combinations_with_replacement(*test))) == result


@tests.test
def test_compress():
    tests = [
        (('ABCDEF', []), []),
        (('ABCDEF', [0, 0, 0, 0, 0, 0]), []),
        (('ABCDEF', [1, 0, 1, 0, 1, 0]), ['A', 'C', 'E']),
        (('ABCDEF', [0, 1, 0, 1, 0, 1]), ['B', 'D', 'F']),
        (('ABCDEF', [1, 1, 1, 1, 1, 1]), ['A', 'B', 'C', 'D', 'E', 'F'])
    ]
    for test, result in tests:
        Assert(list(compress(*test))) == result


@tests.test
def test_count():
    tests = [
        ((), [0, 1, 2, 3, 4]),
        ((1, ), [1, 2, 3, 4, 5]),
        ((0, 2), [0, 2, 4, 6, 8])
    ]
    for test, result in tests:
        c = count(*test)
        Assert([c.next() for _ in result]) == result


@tests.test
def test_grouped():
    tests = [
        ((0, 'abc'), []),
        ((2, 'abc'), [('a', 'b'), ('c', None)]),
        ((2, 'abc', 1), [('a', 'b'), ('c', 1)])
    ]
    for test, result in tests:
        Assert(list(grouped(*test))) == result


@tests.test
def test_unique():
    tests = [
        ('aabbcc', 'abc'),
        ('aa', 'a'),
        (([1, 2], [1, 2], [3, 4], 5, 5, 5), ([1, 2], [3, 4], 5))
    ]
    for test, result in tests:
        Assert(list(unique(test))) == list(result)

    Assert(list(unique('aaabbbbccc', seen='ab'))) == ['c']


@tests.test
def test_flatten():
    tests = [
        (([1, 2, 3], ), [1, 2, 3]),
        (([1, [2, 3]], ), [1, 2, 3]),
        (([1, [2, [3]]], ), [1, 2, 3]),
        (([1, [2, [3], 4], 5, 6], ), [1, 2, 3, 4, 5, 6]),
        ((['foo', 'bar'], ), ['foo', 'bar']),
        ((['ab', 'cd'], ()), ['a', 'b', 'c', 'd'])
    ]
    for args, result in tests:
        Assert(list(flatten(*args))) == result
