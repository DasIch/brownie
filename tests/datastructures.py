# coding: utf-8
"""
    tests.datastructures
    ~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import random

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import missing, MultiDict, OrderedDict, LazyList, \
                                   Counter


class TestMissing(TestBase):
    @test
    def has_false_boolean_value(self):
        Assert(not missing) == True

    @test
    def repr(self):
        Assert(repr(missing)) == 'missing'


class TestMultiDict(TestBase):
    @test
    def init(self):
        Assert(not MultiDict()) == True

        d = MultiDict({'foo': 'bar', 'spam': 'eggs'})
        Assert(d['foo']) == 'bar'
        Assert(d['spam']) == 'eggs'

        d = MultiDict({'foo': ['bar'], 'spam': ['eggs']})
        Assert(d['foo']) == 'bar'
        Assert(d['spam']) == 'eggs'

        d = MultiDict([('foo', 'bar'), ('spam', 'eggs')])
        Assert(d['foo']) == 'bar'
        Assert(d['spam']) == 'eggs'

    @test
    def get_set_item(self):
        d = MultiDict()
        with Assert.raises(KeyError):
            d['foo']
        d['foo'] = 'bar'
        Assert(d['foo']) == 'bar'

    @test
    def add(self):
        d = MultiDict()
        d.add('foo', 'bar')
        d.add('foo', 'spam')
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def getlist(self):
        d = MultiDict()
        Assert(d.getlist('foo')) == []
        d['foo'] = 'bar'
        Assert(d.getlist('foo')) == ['bar']
        d.add('foo', 'spam')
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def test_setlist(self):
        d = MultiDict()
        d.setlist('foo', ['bar', 'spam'])
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def setdefault(self):
        d = MultiDict()
        Assert(d.setdefault('foo')) is None
        Assert(d['foo']).is_(None)
        Assert(d.setdefault('foo', 'bar')).is_(None)
        Assert(d['foo']).is_(None)
        Assert(d.setdefault('spam', 'eggs')) == 'eggs'
        Assert(d['spam']) == 'eggs'

    @test
    def setlistdefault(self):
        d = MultiDict()
        Assert(d.setlistdefault('foo')) == [None]
        Assert(d['foo']).is_(None)
        Assert(d.setlistdefault('foo', ['bar'])) == [None]
        Assert(d['foo']).is_(None)
        Assert(d.setlistdefault('spam', ['eggs'])) == ['eggs']
        Assert(d['spam']) == 'eggs'

    @test
    def keys_values_items(self):
        d = MultiDict()
        Assert(d.keys()) == []
        Assert(d.values()) == []
        Assert(d.items()) == []

        d['foo'] = 'bar'
        d['spam'] = 'eggs'

        iterators = (
            zip(d.keys(), d.values(), d.items()),
            zip(d.iterkeys(), d.itervalues(), d.iteritems())
        )
        for key, value, item in iterators[0]:
            Assert(d[key]) == value
            Assert((key, value)) == item
        Assert(iterators[0]) == iterators[1]

    @test
    def multi_items(self):
        d = MultiDict()
        d.setlist('foo', ['bar'])
        d.setlist('spam', ['eggs', 'monty'])
        Assert(len(d.items())) == 2
        Assert(len(d.items(multi=True))) == 3
        Assert(d.items(multi=True)) == list(d.iteritems(multi=True))
        keys = [pair[0] for pair in d.items(multi=True)]
        Assert(set(keys)) == set(['foo', 'spam'])
        values = [pair[1] for pair in d.items(multi=True)]
        Assert(set(values)) == set(['bar', 'eggs', 'monty'])

    @test
    def lists(self):
        d = MultiDict()
        d.setlist('foo', ['bar', 'baz'])
        d.setlist('spam', ['eggs', 'monty'])
        Assert(d.lists()) == list(d.iterlists())
        ('foo', ['bar', 'baz']) in Assert(d.lists())
        ('spam', ['eggs', 'monty']) in Assert(d.lists())

    @test
    def copy(self):
        d = MultiDict({'foo': 'bar'})
        Assert(d).is_not(d.copy())
        Assert(d) == d.copy()

    @test
    def update(self):
        d = MultiDict()
        d.update({'foo': 'bar'})
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar']
        d.update([('foo', 'spam')])
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']
        d.update(MultiDict([('foo', 'eggs')]))
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam', 'eggs']

    @test
    def pop(self):
        d = MultiDict({'foo': 'bar'})
        Assert(d.pop('foo')) == 'bar'
        with Assert.raises(KeyError):
            d.pop('foo')
        Assert(d.pop('foo', 'bar')) == 'bar'

    @test
    def popitem(self):
        d = MultiDict({'foo': 'bar'})
        Assert(d.popitem()) == ('foo', 'bar')
        with Assert.raises(KeyError):
            d.popitem()
        d = MultiDict({'foo': ['bar', 'baz']})
        Assert(d.popitem()) == ('foo', 'bar')
        with Assert.raises(KeyError):
            d.popitem()

    @test
    def poplist(self):
        d = MultiDict({'foo': 'bar', 'spam': ['eggs', 'monty']})
        Assert(d.poplist('foo')) == ['bar']
        Assert(d.poplist('spam')) == ['eggs', 'monty']
        Assert(d.poplist('foo')) == []

    @test
    def popitemlist(self):
        d = MultiDict({'foo': 'bar'})
        Assert(d.popitemlist()) == ('foo', ['bar'])
        with Assert.raises(KeyError):
            d.popitemlist()
        d = MultiDict({'foo': ['bar', 'baz']})
        Assert(d.popitemlist()) == ('foo', ['bar', 'baz'])
        with Assert.raises(KeyError):
            d.popitemlist()

    @test
    def get(self):
        d = MultiDict()
        Assert(d.get('foo')).is_(None)
        Assert(d.get('foo', 'bar')) == 'bar'
        d = MultiDict({'foo': 'bar'})
        Assert(d.get('foo')) == 'bar'
        Assert(d.get('foo', 'spam')) == 'bar'
        d = MultiDict({'foo': ['bar', 'baz']})
        Assert(d.get('foo')) == 'bar'
        Assert(d.get('foo', 'spam')) == 'bar'


class TestOrderedDict(TestBase):
    @test
    def fromkeys(self):
        d = OrderedDict.fromkeys([1, 2])
        Assert(d.__class__).is_(OrderedDict)
        Assert(d.items()) == [(1, None), (2, None)]
        d = OrderedDict.fromkeys([1, 2], 'foo')
        Assert(d.items()) == [(1, 'foo'), (2, 'foo')]

    @test
    def init(self):
        with Assert.raises(TypeError):
            OrderedDict(('foo', 'bar'), ('spam', 'eggs'))
        Assert(OrderedDict([(1, 2), (3, 4)]).items()) == [(1, 2), (3, 4)]

    @test
    def insertion(self):
        d = OrderedDict()
        d[1] = 2
        d[3] = 4
        Assert(d.items()) == [(1, 2), (3, 4)]

    @test
    def setdefault(self):
        d = OrderedDict()
        d.setdefault(1)
        Assert(d[1]) == None
        d.setdefault(3, 4)
        Assert(d[3]) == 4
        Assert(d.items()) == [(1, None), (3, 4)]

    @test
    def pop(self):
        d = OrderedDict()
        d[1] = 2
        Assert(d.pop(1)) == 2
        with Assert.raises(KeyError):
            d.pop(1)
        Assert(d.pop(1, 2)) == 2

        d = OrderedDict([(1, 2), (3, 4)])
        d.pop(3)
        d[5] = 6
        d[3] = 4
        Assert(d) == OrderedDict([(1, 2), (5, 6), (3, 4)])

    @test
    def popitem(self):
        d = OrderedDict([(1, 2), (3, 4), (5, 6)])
        Assert(d.popitem()) == (5, 6)
        Assert(d.popitem(last=False)) == (1, 2)

    @test
    def update(self):
        d = OrderedDict()
        d.update([(1, 2), (3, 4)])
        Assert(d.items()) == [(1, 2), (3, 4)]
        d.update(foo='bar')
        Assert(d['foo']) == 'bar'
        Assert(d.items()) == [(1, 2), (3, 4), ('foo', 'bar')]

        d = OrderedDict()
        d.update([('foo', 'bar'), ('spam', 'eggs')], foo='baz')
        Assert(d.items()) == [('foo', 'baz'), ('spam', 'eggs')]

        with Assert.raises(TypeError):
            d.update(('foo', 'bar'), ('spam', 'eggs'))

    @test
    def clear(self):
        d = OrderedDict([(1, 2), (3, 4)])
        assert d
        d.clear()
        assert not d
        d.update([(3, 4), (1, 2)])
        Assert(d.items()) == [(3, 4), (1, 2)]

    @test
    def item_accessor_equality(self):
        d = OrderedDict([(1, 2), (3, 4)])
        Assert(list(d)) == d.keys()
        Assert(list(reversed(d))) == list(reversed(d.keys()))
        Assert(list(d.iterkeys())) == d.keys()
        Assert(list(d.itervalues())) == d.values()
        Assert(list(d.iteritems())) == d.items()
        for key, value, item in zip(d.keys(), d.values(), d.items()):
            Assert((key, value)) == item
            Assert(d[key]) == value

    @test
    def repr(self):
        d = OrderedDict()
        Assert(repr(d)) == 'OrderedDict([])'
        d = OrderedDict([(1, 2), (3, 4)])
        Assert(repr(d)) == 'OrderedDict([(1, 2), (3, 4)])'


class TestCounter(TestBase):
    @test
    def missing(self):
        c = Counter()
        Assert(c['a']) == 0

    @test
    def get(self):
        c = Counter('a')
        Assert(c.get('a')) == 1
        Assert(c.get('b')) == 0

    @test
    def setdefault(self):
        c = Counter('a')
        Assert(c.setdefault('a', 2)) == 1
        Assert(c['a']) == 1
        Assert(c.setdefault('b')) == 1
        Assert(c['b']) == 1

    @test
    def most_common(self):
        c = Counter('aababc')
        result = [('a', 3), ('b', 2), ('c', 1)]
        Assert(c.most_common()) == result
        Assert(c.most_common(2)) == result[:-1]
        Assert(c.most_common(1)) == result[:-2]
        Assert(c.most_common(0)) == []

    @test
    def elements(self):
        c = Counter('aababc')
        for element in c:
            Assert(list(c.elements()).count(element)) == c[element]

    @test
    def update(self):
        c = Counter()
        c.update('aababc')
        Assert(c) == Counter('aababc')
        c.update({'b': 1})
        Assert(c['b']) == 3
        c.update(c=2)
        Assert(c['c']) == 3

    @test
    def add(self):
        c = Counter('aababc')
        new = c + c
        Assert(new['a']) == 6
        Assert(new['b']) == 4
        Assert(new['c']) == 2

    @test
    def mul(self):
        c = Counter('abc')
        Assert(c * 2) == c + c

    @test
    def sub(self):
        c = Counter('aababc')
        assert not c - c

    @test
    def or_(self):
        c1 = Counter('abc')
        new = c1 | c1 * 2
        Assert(new.values()) == [2] * 3
        new = c1 & c1 * 2
        Assert(new.values()) == [1] * 3


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
    def getitem(self):
        data = range(10)
        l = LazyList(data)
        for a, b in zip(data, l):
            Assert(a) == b
        l = LazyList(self._genrange(10))
        l[5]
        Assert(l.exhausted) == False

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
    def iteration(self):
        l = LazyList(self._genrange(10))
        Assert(list(l)) == range(10)

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


datastructures_tests = Tests([
    TestMissing, TestMultiDict, TestOrderedDict, TestCounter, TestLazyList
])
