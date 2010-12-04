# coding: utf-8
"""
    tests.itools
    ~~~~~~~~~~~~

    Tests for :mod:`brownie.itools`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, Assert

from brownie.itools import combinations_with_replacement


itools_tests = Tests()


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
