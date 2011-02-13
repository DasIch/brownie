# coding: utf-8
"""
    brownie.tests.datastructures.sets
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures.sets`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import OrderedSet


class TestOrderedSet(TestBase):
    @test
    def length(self):
        Assert(len(OrderedSet([1, 2, 3]))) == 3

    @test
    def contains(self):
        s = OrderedSet([1, 2, 3])
        for element in s:
            Assert(element).in_(s)
        Assert(4).not_in(s)

    @test
    def add(self):
        s = OrderedSet()
        s.add(1)
        Assert(1).in_(s)

    @test
    def remove(self):
        s = OrderedSet()
        with Assert.raises(KeyError):
            s.remove(1)
        s.add(1)
        s.remove(1)

    @test
    def discard(self):
        s = OrderedSet()
        s.discard(1)
        s.add(1)
        s.discard(1)
        Assert(1).not_in(s)

    @test
    def pop(self):
        s = OrderedSet()
        with Assert.raises(KeyError):
            s.pop()
        s = OrderedSet([1, 2, 3])
        Assert(s.pop()) == 3
        Assert(s.pop(last=False)) == 1

    @test
    def clear(self):
        s = OrderedSet([1, 2, 3])
        s.clear()
        assert not s

    @test
    def update(self):
        s = OrderedSet()
        s.update('abc')
        Assert(s) == OrderedSet('abc')

    @test
    def copy(self):
        s = OrderedSet('abc')
        Assert(s.copy()) == s
        Assert(s.copy()).is_not(s)

    @test
    def inplace_update(self):
        old = s = OrderedSet()
        with Assert.raises(TypeError):
            s |= 'abc'
        s |= OrderedSet('abc')
        Assert(s) == OrderedSet('abc')
        Assert(s).is_(old)

    @test
    def issub_super_set(self):
        a = OrderedSet('abc')
        b = OrderedSet('abcdef')

        a.issubset(a)
        a.issuperset(a)
        a.issubset(a)
        a.issuperset(a)

        assert a <= a
        assert a >= a

        assert a <= b
        assert b >= a

        assert not (a < a)
        assert not (a > a)

        assert a < b
        assert not (a > b)

    @test
    def union(self):
        a = OrderedSet('abc')
        b = OrderedSet('def')
        Assert(a.union('def', 'ghi')) == OrderedSet('abcdefghi')
        Assert(a | b) == OrderedSet('abcdef')
        with Assert.raises(TypeError):
            a | 'abc'

    @test
    def intersection(self):
        a = OrderedSet('abc')
        Assert(a.intersection('ab', 'a')) == OrderedSet('a')
        Assert(a & OrderedSet('ab')) == OrderedSet('ab')
        with Assert.raises(TypeError):
            a & 'ab'

    @test
    def intersection_update(self):
        old = s = OrderedSet('abc')
        with Assert.raises(TypeError):
            s &= 'ab'
        s &= OrderedSet('ab')
        Assert(s) == OrderedSet('ab')
        Assert(s).is_(old)

    @test
    def difference(self):
        a = OrderedSet('abc')
        Assert(a.difference('abc')) == OrderedSet()
        Assert(a.difference('a', 'b', 'c')) == OrderedSet()
        Assert(a - OrderedSet('ab')) == OrderedSet('c')
        with Assert.raises(TypeError):
            a - 'abc'

    @test
    def difference_update(self):
        s = OrderedSet('abcd')
        s -= s
        Assert(s) == OrderedSet()

        old = s = OrderedSet('abcd')
        s -= OrderedSet('abc')
        with Assert.raises(TypeError):
            s -= 'abc'
        Assert(s) == OrderedSet('d')
        Assert(s).is_(old)

    @test
    def symmetric_difference(self):
        for a, b in [('abc', 'def'), ('def', 'abc')]:
            OrderedSet(a).symmetric_difference(b) == OrderedSet(a + b)
            OrderedSet(a) ^ OrderedSet(b) == OrderedSet(a + b)

            OrderedSet(a).symmetric_difference(a + b) == OrderedSet(b)
            OrderedSet(a) ^ OrderedSet(a + b) == OrderedSet(b)

        with Assert.raises(TypeError):
            OrderedSet('abc') ^ 'def'

    @test
    def symmetric_difference_update(self):
        old = s = OrderedSet('abc')
        s ^= OrderedSet('def')
        Assert(s) == OrderedSet('abcdef')
        Assert(s).is_(old)
        with Assert.raises(TypeError):
            s ^= 'ghi'

    @test
    def iteration(self):
        s = OrderedSet([1, 2, 3])
        Assert(list(s)) == [1, 2, 3]
        Assert(list(reversed(s))) == [3, 2, 1]

    @test
    def equality(self):
        a = OrderedSet([1, 2, 3])
        b = OrderedSet([3, 2, 1])
        Assert(a) == a
        Assert(a) == set(b)
        Assert(b) == b
        Assert(b) == set(a)
        Assert(a) != b

    @test
    def hashability(self):
        with Assert.raises(TypeError):
            hash(OrderedSet())

    @test
    def repr(self):
        Assert(repr(OrderedSet())) == 'OrderedSet()'
        s = OrderedSet([1, 2, 3])
        Assert(repr(s)) == 'OrderedSet([1, 2, 3])'


tests = Tests([TestOrderedSet])
