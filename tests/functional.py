# coding: utf-8
"""
    tests.functional
    ~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.functional`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
from attest import Tests, Assert

from brownie.functional import compose


functional_tests = Tests()

@functional_tests.test
def test_compose():
    with Assert.raises(TypeError):
        compose()
    add_one = lambda x: x + 1
    mul_two = lambda x: x * 2
    Assert(compose(add_one, mul_two)(1)) == 3
