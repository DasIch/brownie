# coding: utf-8
"""
    brownie.tests.datastructures.sequences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures.sequences`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import pickle
import random
from itertools import repeat

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import (LazyList, CombinedSequence, CombinedList,
                                    namedtuple)


class TestLazyList(TestBase):
    def _genrange(self, *args):
        """xrange() implementation which doesn't have like a sequence."""
        if len(args) == 1:
            start = 0
            stop = args[0]
            step = 1
        elif len(args) == 2:
            start, stop = args
            step = 1
        elif len(args) == 3:
            start, stop, step = args
        else:
            raise ValueError()
        i = start
        while i < stop:
            yield i
            i += step

    @test
    def _test_genrange(self):
        tests = [
            (10, ),
            (10, 20),
            (10, 20, 2)
        ]
        for test in tests:
            Assert(list(self._genrange(*test))) == range(*test)

    @test
    def factory(self):
        foo = LazyList.factory(xrange)
        Assert(foo(10).__class__).is_(LazyList)
        Assert(foo(10)) == range(10)

    @test
    def exhausted(self):
        l = LazyList(range(10))
        Assert(l.exhausted) == True
        l = LazyList(self._genrange(10))
        Assert(l.exhausted) == False
        l[-1]
        Assert(l.exhausted) == True

    @test
    def iteration(self):
        for l in [range(10), self._genrange(10)]:
            l = LazyList(l)
            result = []
            for item in l:
                result.append(item)
            Assert(result) == range(10)

    @test
    def append(self):
        data = self._genrange(10)
        l = LazyList(data)
        l.append(10)
        Assert(l.exhausted) == False
        Assert(l) == range(11)

    @test
    def extend(self):
        data = self._genrange(10)
        l = LazyList(data)
        l.extend(range(10, 20))
        Assert(l.exhausted) == False
        Assert(l) == range(10) + range(10, 20)

    @test
    def insert(self):
        data = self._genrange(10)
        l = LazyList(data)
        l.insert(5, 'foobar')
        Assert(l[5]) == 'foobar'
        Assert(l.exhausted) == False
        l.insert(-3, 'spam')
        Assert(l[-4]) == 'spam'

    @test
    def pop(self):
        data = xrange(10)
        l = LazyList(data)
        Assert(l.pop()) == 9
        Assert(l.pop(0)) == 0

    @test
    def remove(self):
        data = range(10)
        l = LazyList(self._genrange(10))
        data.remove(2)
        l.remove(2)
        Assert(l.exhausted) == False
        Assert(l) == data

    @test
    def reverse(self):
        data = range(10)
        l = LazyList(reversed(data))
        l.reverse()
        Assert(l) == data

    @test
    def sort(self):
        data = range(10)
        random.choice(data)
        l = LazyList(data)
        l.sort()
        data.sort()
        Assert(l) == data

    @test
    def count(self):
        l = LazyList(['a', 'b', 'c', 'a'])
        tests = [('a', 2), ('b', 1), ('c', 1)]
        for test, result in tests:
            Assert(l.count(test)) == result

    @test
    def index(self):
        l = LazyList(self._genrange(10))
        Assert(l.index(5)) == 5
        with Assert.raises(ValueError):
            l.index('foo')

    @test
    def getitem(self):
        data = range(10)
        l = LazyList(data)
        for a, b in zip(data, l):
            Assert(a) == b
        l = LazyList(self._genrange(10))
        l[5]
        Assert(l.exhausted) == False
        l = LazyList(self._genrange(10))
        Assert(l[-1]) == 9

    @test
    def getslice(self):
        data = range(10)
        l = LazyList(self._genrange(10))
        Assert(data[3:6]) == l[3:6]
        Assert(l.exhausted) == False

    @test
    def setitem(self):
        data = ['foo', 'bar', 'baz']
        l = LazyList(iter(data))
        l[0] = 'spam'
        Assert(l.exhausted) == False
        Assert(l[0]) == 'spam'
        Assert(l) != data

    @test
    def setslice(self):
        data = range(10)
        replacement = ['foo', 'bar', 'baz']
        l = LazyList(self._genrange(10))
        l[3:6] = replacement
        data[3:6] = replacement
        Assert(l.exhausted) == False
        Assert(l) == data

    @test
    def delitem(self):
        data = range(10)
        l = LazyList(data[:])
        del data[0]
        del l[0]
        Assert(l) == data
        l = LazyList(self._genrange(10))
        del l[2]
        Assert(l.exhausted) == False

    @test
    def delslice(self):
        data = range(10)
        l = LazyList(self._genrange(10))
        del data[3:6]
        del l[3:6]
        Assert(l.exhausted) == False
        Assert(l) == data

    @test
    def len(self):
        Assert(len(LazyList(range(10)))) == 10

        l = LazyList([])
        Assert(len(l)) == 0

        l.append(1)
        Assert(len(l)) == 1

        l.extend([2, 3])
        Assert(len(l)) == 3

        l.pop()
        Assert(len(l)) == 2

        del l[1]
        Assert(len(l)) == 1

    @test
    def contains(self):
        l = LazyList(self._genrange(10))
        Assert(5).in_(l)
        Assert('foo').not_in(l)

    @test
    def equals(self):
        Assert(LazyList(range(10))) == range(10)
        Assert(LazyList(range(10))) == LazyList(range(10))

        Assert(LazyList(range(10)) != range(10)) == False
        Assert(LazyList(range(10)) != range(10)) == False

        Assert(LazyList(range(10)) == range(20)) == False
        Assert(LazyList(range(10)) == LazyList(range(20))) == False

        Assert(LazyList(range(10))) != range(20)
        Assert(LazyList(range(10))) != range(20)

        l = LazyList(self._genrange(10))
        Assert(l == range(20)) == False

    @test
    def boolean(self):
        Assert(bool(LazyList([]))) == False
        Assert(bool(LazyList([1]))) == True

    @test
    def lower_greater_than(self):
        Assert(LazyList([]) < LazyList([])) == False
        Assert(LazyList([]) > LazyList([])) == False

        tests = [
            ([], [1]),
            ([1], [2]),
            ([1, 2], [2, 1]),
            ([2, 1], [2, 2])
        ]
        for a, b in tests:
            Assert(LazyList(a) < LazyList(b)) == True
            Assert(LazyList(a) > LazyList(b)) == False

            Assert(LazyList(b) < LazyList(a)) == False
            Assert(LazyList(b) > LazyList(a)) == True

        a = LazyList(iter([1, 2, 3]))
        b = LazyList(iter([1, 3, 3]))

        Assert(a) < b
        Assert(b) > a

        Assert(a.exhausted) == False
        Assert(b.exhausted) == False

    @test
    def add(self):
        Assert(LazyList([1, 2]) + [3, 4]) == LazyList([1, 2, 3, 4])
        Assert(LazyList([1, 2]) + LazyList([3, 4])) == LazyList([1, 2, 3, 4])

    @test
    def inplace_add(self):
        old = l = LazyList([1, 2])
        l += [3, 4]
        l += (5, 6)
        Assert(l) == LazyList([1, 2, 3, 4, 5, 6])
        Assert(l).is_(old)

    @test
    def multiply(self):
        a = LazyList(self._genrange(10))
        b = range(10)
        Assert(a * 5) == b * 5

    @test
    def inplace_multiply(self):
        old = a = LazyList(self._genrange(10))
        b = range(10)
        a *= 5
        b *= 5
        Assert(a) == b
        Assert(a).is_(old)

    @test
    def repr(self):
        Assert(repr(LazyList([]))) == '[]'
        data = range(10)
        l = Assert(LazyList(data))
        repr(l) == '[...]'
        l[1]
        repr(l) == '[0, 1, ...]'
        l[-1]
        repr(l) == repr(data)

    @test
    def picklability(self):
        l = LazyList(self._genrange(10))
        pickled = pickle.loads(pickle.dumps(l))
        Assert(pickled) == l
        Assert(pickled.__class__) == l.__class__


class CombinedSequenceTestMixin(object):
    sequence_cls = None

    @test
    def at_index(self):
        foo = [1, 2, 3]
        bar = [4, 5, 6]
        s = self.sequence_cls([foo, bar])

        for iterator in xrange(len(s) - 1), xrange(0, -len(s), -1):
            for i in iterator:
                list, index = s.at_index(i)
                if 0 <= i <= 2 or -6 <= i <= -3:
                    Assert(list).is_(foo)
                    Assert(foo[index]) == s[i]
                else:
                    Assert(list).is_(bar)
                    Assert(bar[index]) == s[i]

    @test
    def getitem(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        for a, b, item in zip(xrange(len(s) - 1), xrange(-len(s)), range(6)):
            Assert(s[a]) == s[b] == item

    @test
    def getslice(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        Assert(s[:]) == range(6)
        Assert(s[:3]) == s[:-3] == [0, 1, 2]
        Assert(s[3:]) == s[-3:] == [3, 4, 5]
        Assert(s[2:]) == [2, 3, 4, 5]
        Assert(s[-2:]) == [4, 5]

    @test
    def len(self):
        tests = [
            ([], 0),
            ([[]], 0),
            ([[], []], 0),
            ([[1, 2], [3, 4]], 4)
        ]
        for args, result in tests:
            Assert(len(self.sequence_cls(args))) == result

    @test
    def iteration(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        for expected, item in zip(range(6), s):
            Assert(expected) == item
        for expected, item in zip(range(5, 0, -1), reversed(s)):
            Assert(expected) == item

    @test
    def equality(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        Assert(s) == self.sequence_cls(s.sequences)
        Assert(s) != self.sequence_cls([[]])

    @test
    def picklability(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        pickled = pickle.loads(pickle.dumps(s))
        Assert(pickled) == s
        Assert(pickled.__class__).is_(self.sequence_cls)

    @test
    def multiplication(self):
        s = self.sequence_cls([[0, 1, 2], [3, 4, 5]])
        Assert(s * 2) == 2 * s == [0, 1, 2, 3, 4, 5] * 2
        with Assert.raises(TypeError):
            s * []


class TestCombinedSequence(TestBase, CombinedSequenceTestMixin):
    sequence_cls = CombinedSequence


class TestCombinedList(TestBase, CombinedSequenceTestMixin):
    sequence_cls = CombinedList

    @test
    def count(self):
        s = self.sequence_cls([[1, 1, 2], [3, 1, 4]])
        Assert(s.count(1)) == 3
        Assert(s.count(2)) == s.count(3) == s.count(4) == 1

    @test
    def index(self):
        s = self.sequence_cls([[1, 1, 2], [3, 1, 4]])
        Assert(s.index(1)) == 0
        Assert(s.index(1, 1)) == 1
        Assert(s.index(1, 2)) == 4
        with Assert.raises(ValueError):
            s.index(1, 2, 3)

    @test
    def setitem(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        s[0] = 'foo'
        Assert(s[0]) == foo[0] == 'foo'

    @test
    def setslice(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        s[:3] = 'abc'
        Assert(s) == ['a', 'b', 'c', 3, 4, 5]
        Assert(foo) == ['a', 'b', 'c']
        s[::2] = repeat(None)
        Assert(s) == [None, 'b', None, 3, None, 5]

    @test
    def delitem(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        del s[0]
        Assert(s) == [1, 2, 3, 4, 5]
        Assert(foo) == [1, 2]

    @test
    def delslice(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        del s[2:4]
        Assert(s) == [0, 1, 4, 5]
        Assert(foo) == [0, 1]
        Assert(bar) == [4, 5]

    @test
    def append(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        s.append(6)
        Assert(s[-1]) == bar[-1] == 6

    @test
    def extend(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        s.extend([6, 7])
        Assert(s[-2:]) == bar[-2:] == [6, 7]

    @test
    def insert(self):
        foo, bar = [0, 1, 2], [3, 4, 5]
        s = self.sequence_cls([foo, bar])
        s.insert(1, 6)
        Assert(s[:4]) == foo == [0, 6, 1, 2]
        Assert(bar) == [3, 4, 5]

    @test
    def pop(self):
        s = self.sequence_cls([])
        with Assert.raises(IndexError):
            s.pop()
        s = self.sequence_cls([[0, 1, 2]])
        with Assert.raises(IndexError):
            s.pop(3)
        Assert(s.pop()) == 2
        Assert(s.pop(0)) == 0

    @test
    def remove(self):
        s = self.sequence_cls([])
        with Assert.raises(ValueError):
            s.remove(1)
        s = self.sequence_cls([[1, 1]])
        s.remove(1)
        Assert(s) == [1]
        s = self.sequence_cls([[1, 2], [1, 2]])
        s.remove(1)
        Assert(s) == [2, 1, 2]
        s = self.sequence_cls([[2], [1, 2]])
        s.remove(1)
        Assert(s) == [2, 2]

    @test
    def reverse(self):
        foo, bar = [1, 2, 3], [4, 5, 6]
        s = self.sequence_cls([foo, bar])
        s.reverse()
        Assert(s) == [6, 5, 4, 3, 2, 1]
        Assert(foo) == [6, 5, 4]
        Assert(bar) == [3, 2, 1]

    @test
    def sort(self):
        foo, bar = [3, 1, 2], [4, 6, 5]
        s = self.sequence_cls([foo, bar])
        s.sort()
        Assert(s) == [1, 2, 3, 4, 5, 6]
        Assert(foo) == [1, 2, 3]
        Assert(bar) == [4, 5, 6]


class TestNamedTuple(TestBase):
    @test
    def string_field_names(self):
        nt = namedtuple('foo', 'foo bar')
        Assert(nt._fields) == ('foo', 'bar')
        nt = namedtuple('foo', 'foo,bar')
        Assert(nt._fields) == ('foo', 'bar')

    @test
    def typename(self):
        nt = namedtuple('foo', [])
        Assert(nt.__name__) == 'foo'
        with Assert.raises(ValueError):
            namedtuple('def', [])

    @test
    def fieldnames(self):
        with Assert.raises(ValueError):
            nt = namedtuple('foo', ['foo', 'bar', 'def'])

        with Assert.raises(ValueError):
            nt = namedtuple('foo', ['foo', 'bar', 'foo'])

        nt = namedtuple('foo', ['spam', 'eggs'])
        Assert(nt._fields) == ('spam', 'eggs')

        nt = namedtuple('foo', ['foo', 'bar', 'def'], rename=True)
        Assert(nt._fields) == ('foo', 'bar', '_1')
        Assert(nt(1, 2, 3)._1) == 3

        nt = namedtuple('foo', ['foo', 'bar', 'foo'], rename=True)
        Assert(nt._fields) == ('foo', 'bar', '_1')
        Assert(nt(1, 2, 3)._1) == 3

    @test
    def renaming(self):
        nt = namedtuple('foo', ['foo', 'foo', 'foo'], rename=True)
        t = nt(1, 2, 3)
        Assert(t.foo) == 1
        Assert(t._1) == 2
        Assert(t._2) == 3

    @test
    def repr(self):
        nt = namedtuple('foo', ['spam', 'eggs'])
        Assert(nt(1, 2)) == (1, 2)
        Assert(repr(nt(1, 2))) == 'foo(spam=1, eggs=2)'

    @test
    def _make(self):
        nt = namedtuple('foo', ['spam', 'eggs'])
        Assert(nt._make((1, 2))) == (1, 2)
        with Assert.raises(TypeError):
            nt._make((1, 2, 3))

    @test
    def _asdict(self):
        nt = namedtuple('foo', ['spam', 'eggs'])
        Assert(nt(1, 2)._asdict()) == {'spam': 1, 'eggs': 2}

    @test
    def _replace(self):
        nt = namedtuple('foo', ['spam', 'eggs'])
        t = nt(1, 2)
        Assert(t._replace(spam=3)) == (3, 2)
        Assert(t._replace(eggs=4)) == (1, 4)
        with Assert.raises(ValueError):
            t._replace(foo=1)


tests = Tests([TestLazyList, TestCombinedSequence, TestCombinedList, TestNamedTuple])
