# coding: utf-8
"""
    tests.itools
    ~~~~~~~~~~~~

    Tests for :mod:`brownie.itools`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, Assert

from brownie.itools import product, combinations_with_replacement, compress, \
                           count


itools_tests = Tests()


@itools_tests.test
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


@itools_tests.test
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


@itools_tests.test
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


@itools_tests.test
def test_count():
    tests = [
        ((), [0, 1, 2, 3, 4]),
        ((1, ), [1, 2, 3, 4, 5]),
        ((0, 2), [0, 2, 4, 6, 8])
    ]
    for test, result in tests:
        c = count(*test)
        Assert([c.next() for _ in result]) == result
