# coding: utf-8
"""
    brownie.tests.datastructures.iterators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures.iterators`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import PeekableIterator


class TestPeekableIterator(TestBase):
    @test
    def iter(self):
        original = range(10)
        iterator = PeekableIterator(original)
        for item, expected in zip(original, iterator):
            Assert(item) == expected

    @test
    def iter_returns_self(self):
        iterator = PeekableIterator(range(10))
        Assert(iter(iterator)).is_(iterator)

    @test
    def peek(self):
        iterator = PeekableIterator(range(10))
        with Assert.raises(ValueError):
            iterator.peek(0)
        with Assert.raises(ValueError):
            iterator.peek(-1)
        with Assert.raises(StopIteration):
            iterator.peek(11)

        Assert(iterator.peek(10)) == range(10)
        for item, expected in zip(iterator, range(10)):
            Assert(item) == expected

        iterator = PeekableIterator(range(10))
        Assert(iterator.peek()) == iterator.peek()
        Assert(iterator.peek()) == [0]

    @test
    def repr(self):
        original = iter(xrange(10))
        iterator = PeekableIterator(original)
        Assert(repr(iterator)) == 'PeekableIterator(%r)' % iter(original)


tests = Tests([TestPeekableIterator])
