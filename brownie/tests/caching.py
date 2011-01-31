# coding: utf-8
"""
    brownie.tests.caching
    ~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.caching`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import time

from attest import Tests, Assert, TestBase, test

from brownie.caching import cached_property, LRUCache, LFUCache, memoize


tests = Tests()


@tests.test
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


class TestLRUCache(TestBase):
    @test
    def decorate(self):
        @LRUCache.decorate(2)
        def foo(*args, **kwargs):
            time.sleep(.1)
            return args, kwargs

        tests = [
            (('foo', 'bar'), {}),
            (('foo', 'bar'), {'spam': 'eggs'}),
            ((1, 2), {})
        ]
        times = []

        for test in tests:
            args, kwargs = test
            old = time.time()
            Assert(foo(*args, **kwargs)) == test
            new = time.time()
            uncached_time = new - old

            old = time.time()
            Assert(foo(*args, **kwargs)) == test
            new = time.time()
            cached_time = new - old
            Assert(cached_time) < uncached_time
            times.append((uncached_time, cached_time))
        old = time.time()
        foo(*tests[0][0], **tests[0][1])
        new = time.time()
        Assert(new - old) > times[0][1]

    @test
    def basics(self):
        cache = LRUCache(maxsize=2)
        cache[1] = 2
        cache[3] = 4
        cache[5] = 6
        Assert(cache.items()) == [(3, 4), (5, 6)]

    @test
    def repr(self):
        cache = LRUCache()
        Assert(repr(cache)) == 'LRUCache({}, inf)'

tests.register(TestLRUCache)


class TestLFUCache(TestBase):
    @test
    def basics(self):
        cache = LFUCache(maxsize=2)
        cache[1] = 2
        cache[3] = 4
        cache[3]
        cache[5] = 6
        Assert(cache.items()) == [(1, 2), (5, 6)]

    @test
    def repr(self):
        cache = LFUCache()
        Assert(repr(cache)) == 'LFUCache({}, inf)'

tests.register(TestLFUCache)


@tests.test
def test_memoize():
    @memoize
    def foo(a, b):
        return a + b
    Assert(foo(1, 1)) == 2
    Assert(foo(1, 1)) == 2
    Assert(foo(1, 2)) == 3
