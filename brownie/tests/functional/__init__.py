# coding: utf-8
"""
    brownie.tests.functional
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.functional`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement

from attest import Tests, Assert, TestBase, test

from brownie.functional import compose, flip, curried
from brownie.tests.functional import signature


tests = Tests([signature.tests])


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


class TestCurried(TestBase):
    @test
    def positional(self):
        func = curried(lambda a, b, c: (a, b, c))
        Assert(func(1, 2, 3)) == (1, 2, 3)
        Assert(func(1, 2)(3)) == (1, 2, 3)
        Assert(func(1)(2, 3)) == (1, 2, 3)
        Assert(func(1)(2)(3)) == (1, 2, 3)

        Assert(func(c=3, b=2, a=1)) == (1, 2, 3)
        Assert(func(c=3)(a=1)(2)) == (1, 2, 3)

    @test
    def keyword_arguments(self):
        func = curried(lambda a=1, b=2, c=3: (a, b, c))
        Assert(func()) == (1, 2, 3)
        Assert(func(c=4)) == (1, 2, 4)
        Assert(func(4)) == (4, 2, 3)

    @test
    def mixed_positional_keyword_arguments(self):
        func = curried(lambda a, b, c=3: (a, b, c))
        Assert(func(1, 2)) == (1, 2, 3)
        Assert(func(1, 2, 4)) == (1, 2, 4)

    @test
    def arbitary_positionals(self):
        func = curried(lambda a, b, c, *args: (a, b, c, args))
        Assert(func(1, 2, 3)) == (1, 2, 3, ())
        Assert(func(1, 2, 3, 4, 5)) == (1, 2, 3, (4, 5))
        Assert(func(1)(2, 3, 4, 5)) == (1, 2, 3, (4, 5))
        Assert(func(1, 2)(3, 4, 5)) == (1, 2, 3, (4, 5))
        Assert(func(1)(2, 3, 4, 5)) == (1, 2, 3, (4, 5))

        Assert(func(1)(b=2)(3, 4, 5)) == (1, 2, 3, (4, 5))
        Assert(func(a=1)(b=2)(3, 4, 5)) == (1, 2, 3, (4, 5))
        Assert(func(a=1, b=2)(3, 4, 5)) == (1, 2, 3, (4, 5))

    @test
    def arbitary_keyword_arguments(self):
        func = curried(lambda a, b, c, **kwargs: (a, b, c, kwargs))
        Assert(func(1, 2, 3)) == (1, 2, 3, {})
        with Assert.raises(TypeError):
            func(1, 2)(3, c=4)
        Assert(func(1, 2, 3, foo=4)) == (1, 2, 3, dict(foo=4))
        Assert(func(1)(2, 3, foo=4)) == (1, 2, 3, dict(foo=4))
        Assert(func(1, 2)(3, foo=4)) == (1, 2, 3, dict(foo=4))

    @test
    def mixed_arbitary_arguments(self):
        func = curried(lambda a, b, c, *args, **kwargs: (a, b, c, args, kwargs))
        Assert(func(1, 2, 3)) == (1, 2, 3, (), {})
        Assert(func(1, 2, 3, 4, 5)) == (1, 2, 3, (4, 5), {})
        Assert(func(1, 2, 3, foo=4)) == (1, 2, 3, (), dict(foo=4))
        Assert(func(1, 2, 3, 4, foo=5)) == (1, 2, 3, (4, ), dict(foo=5))


tests.register(TestCurried)
