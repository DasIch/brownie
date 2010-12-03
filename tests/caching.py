# coding: utf-8
"""
    tests.caching
    ~~~~~~~~~~~~~

    Tests for :mod:`brownie.caching`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, Assert

from brownie.caching import cached_property


caching_tests = Tests()


@caching_tests.test
def test_cached_property():
    class Foo(object):
        def __init__(self):
            self.counter = 0

        @cached_property
        def spam(self):
            self.counter += 1
            return self.counter
    foo = Foo()
    Assert(foo.spam) == 1
    Assert(foo.spam) == 1
