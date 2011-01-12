# coding: utf-8
"""
    brownie.tests.functional
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.functional`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
from attest import Tests, Assert

from brownie.functional import compose, flip


tests = Tests()


@tests.test
def test_compose():
    with Assert.raises(TypeError):
        compose()
    add_one = lambda x: x + 1
    mul_two = lambda x: x * 2
    Assert(compose(add_one, mul_two)(1)) == 3


@tests.test
def test_flip():
    f = lambda a, b, **kws: (a, kws)
    Assert(f(1, 2)) == (1, {})
    Assert(flip(f)(1, 2)) == (2, {})
    kwargs = {'foo': 'bar'}
    Assert(flip(f)(1, 2, **kwargs)) == (2, kwargs)
