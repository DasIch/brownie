# coding: utf-8
"""
    brownie.tests.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import sys
import pickle

from attest import Tests, TestBase, test, Assert, test_if

from brownie.datastructures import (
    missing,
    MultiDict,
    ImmutableDict,
    ImmutableMultiDict,
    OrderedDict,
    ImmutableOrderedDict,
    OrderedMultiDict,
    ImmutableOrderedMultiDict,
    Counter,
    CombinedDict,
    CombinedMultiDict,
    FixedDict
)
from brownie.tests.datastructures import sets
from brownie.tests.datastructures import queues
from brownie.tests.datastructures import sequences


GE_PYTHON_26 = sys.version_info >= (2, 6)


class TestMissing(TestBase):
    @test
    def has_false_boolean_value(self):
        if missing:
            raise AssertionError()

    @test
    def repr(self):
        Assert(repr(missing)) == 'missing'


class DictTestMixin(object):
    dict_class = None

    @test
    def fromkeys(self):
        d = self.dict_class.fromkeys([1, 2])
        Assert(d[1]) == None
        Assert(d[2]) == None
        d = self.dict_class.fromkeys([1, 2], 'foo')
        Assert(d[1]) == 'foo'
        Assert(d[2]) == 'foo'

        Assert(d.__class__).is_(self.dict_class)

    @test
    def init(self):
        data = [(1, 2), (3, 4)]
        with Assert.raises(TypeError):
            self.dict_class(*data)
        for mapping_type in [lambda x: x, self.dict_class]:
            d = self.dict_class(mapping_type(data))
            Assert(d[1]) == 2
            Assert(d[3]) == 4
        d = self.dict_class(foo='bar', spam='eggs')
        Assert(d['foo']) == 'bar'
        Assert(d['spam']) == 'eggs'
        d = self.dict_class([('foo', 'bar'), ('spam', 'eggs')], foo='baz')
        Assert(d['foo']) == 'baz'
        Assert(d['spam']) == 'eggs'

    @test
    def copy(self):
        d = self.dict_class()
        Assert(d.copy()).is_not(d)

    @test
    def setitem(self):
        d = self.dict_class()
        d[1] = 2
        Assert(d[1]) == 2
        d[1] = 3
        Assert(d[1]) == 3

    @test
    def getitem(self):
        d = self.dict_class([(1, 2), (3, 4)])
        Assert(d[1]) == 2
        Assert(d[3]) == 4

    @test
    def delitem(self):
        d = self.dict_class()
        d[1] = 2
        Assert(d[1]) == 2
        del d[1]
        with Assert.raises(KeyError):
            del d[1]

    @test
    def get(self):
        d = self.dict_class()
        Assert(d.get(1)) == None
        Assert(d.get(1, 2)) == 2
        d = self.dict_class({1: 2})
        Assert(d.get(1)) == 2
        Assert(d.get(1, 3)) == 2

    @test
    def setdefault(self):
        d = self.dict_class()
        Assert(d.setdefault(1)) == None
        Assert(d[1]) == None
        Assert(d.setdefault(1, 2)) == None
        Assert(d.setdefault(3, 4)) == 4
        Assert(d[3]) == 4

    @test
    def pop(self):
        d = self.dict_class()
        d[1] = 2
        Assert(d.pop(1)) == 2
        with Assert.raises(KeyError):
            d.pop(1)
        Assert(d.pop(1, 2)) == 2

    @test
    def popitem(self):
        d = self.dict_class([(1, 2), (3, 4)])
        items = iter(d.items())
        while d:
            Assert(d.popitem()) == items.next()

    @test
    def clear(self):
        d = self.dict_class([(1, 2), (3, 4)])
        assert d
        d.clear()
        assert not d

    @test
    def item_accessor_equality(self):
        d = self.dict_class([(1, 2), (3, 4)])
        Assert(list(d)) == d.keys()
        Assert(list(d.iterkeys())) == d.keys()
        Assert(list(d.itervalues())) == d.values()
        Assert(list(d.iteritems())) == d.items()
        for key, value, item in zip(d.keys(), d.values(), d.items()):
            Assert((key, value)) == item
            Assert(d[key]) == value

    @test
    def update(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.update((1, 2), (3, 4))

        for mapping in ([(1, 2), (3, 4)], self.dict_class([(1, 2), (3, 4)])):
            d.update(mapping)
            Assert(d[1]) == 2
            Assert(d[3]) == 4

        d = self.dict_class()
        d.update([('foo', 'bar'), ('spam', 'eggs')], foo='baz')
        Assert(d['foo']) == 'baz'
        Assert(d['spam']) == 'eggs'

    @test
    def repr(self):
        d = self.dict_class()
        Assert(repr(d)) == '%s()' % d.__class__.__name__
        original = {1: 2}
        d = self.dict_class(original)
        Assert(repr(d)) == '%s(%s)' % (d.__class__.__name__, repr(original))

    @test
    def test_custom_new(self):
        class D(self.dict_class):
            def __new__(cls, *args, **kwargs):
                return 42
        Assert(D.fromkeys([])) == 42

    @test
    def picklability(self):
        d = self.dict_class([(1, 2), (3, 4)])
        pickled = pickle.loads(pickle.dumps(d))
        Assert(pickled == d)
        Assert(pickled.__class__).is_(d.__class__)


class ImmutableDictTestMixin(DictTestMixin):
    @test
    def setitem(self):
        for d in (self.dict_class(), self.dict_class({1: 2})):
            with Assert.raises(TypeError):
                d[1] = 2

    @test
    def delitem(self):
        for d in (self.dict_class(), self.dict_class({1: 2})):
            with Assert.raises(TypeError):
                del d[1]

    @test
    def setdefault(self):
        for d in (self.dict_class(), self.dict_class({1: 2})):
            with Assert.raises(TypeError):
                d.setdefault(1)
            with Assert.raises(TypeError):
                d.setdefault(1, 3)

    @test
    def pop(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.pop(1)
        with Assert.raises(TypeError):
            d.pop(1, 2)
        d = self.dict_class({1: 2})
        with Assert.raises(TypeError):
            d.pop(1)

    @test
    def popitem(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.popitem()

    @test
    def update(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.update([])
        with Assert.raises(TypeError):
            d.update(foo='bar')

    @test
    def clear(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.clear()


class ImmutableDictTest(TestBase, ImmutableDictTestMixin):
    dict_class = ImmutableDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        assert isinstance(self.dict_class(), dict)

    @test
    def hashability(self):
        a = self.dict_class([(1, 2), (3, 4)])
        b = self.dict_class(a)
        Assert(hash(a)) == hash(b)
        Assert(hash(a)) != hash(ImmutableDict([(1, 2), (5, 6)]))
        with Assert.raises(TypeError):
            hash(ImmutableDict({1: []}))


class CombinedDictTestMixin(object):
    # .fromkeys() doesn't work here, so we don't need that test
    test_custom_new = None

    @test
    def fromkeys(self):
        with Assert.raises(TypeError):
            self.dict_class.fromkeys(['foo', 'bar'])

    @test
    def init(self):
        with Assert.raises(TypeError):
            self.dict_class(foo='bar')
        self.dict_class([{}, {}])

    @test
    def getitem(self):
        d = self.dict_class([{1: 2, 3: 4}, {1: 4, 3: 2}])
        Assert(d[1]) == 2
        Assert(d[3]) == 4

    @test
    def get(self):
        d = self.dict_class()
        Assert(d.get(1)) == None
        Assert(d.get(1, 2)) == 2

        d = self.dict_class([{1: 2}, {1: 3}])
        Assert(d.get(1)) == 2
        Assert(d.get(1, 4)) == 2

    @test
    def item_accessor_equality(self):
        d = self.dict_class([{1: 2}, {1: 3}, {2: 4}])
        Assert(d.keys()) == [1, 2]
        Assert(d.values()) == [2, 4]
        Assert(d.items()) == [(1, 2), (2, 4)]
        Assert(list(d)) == list(d.iterkeys()) == d.keys()
        Assert(list(d.itervalues())) == d.values()
        Assert(list(d.iteritems())) == d.items()

    @test
    def repr(self):
        Assert(repr(self.dict_class())) == '%s()' % self.dict_class.__name__
        d = self.dict_class([{}, {1: 2}])
        Assert(repr(d)) == '%s([{}, {1: 2}])' % self.dict_class.__name__


class TestCombinedDict(TestBase, CombinedDictTestMixin, ImmutableDictTestMixin):
    dict_class = CombinedDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        assert isinstance(d, ImmutableDict)
        assert isinstance(d, dict)

    @test
    def hashability(self):
        a = CombinedDict([ImmutableDict({1: 2}), ImmutableDict({3: 4})])
        Assert(hash(a)) == hash(CombinedDict(a.dicts))
        Assert(hash(a)) != hash(CombinedDict(reversed(a.dicts)))
        with Assert.raises(TypeError):
            hash(CombinedDict([{}]))


class MultiDictTestMixin(object):
    dict_class = None

    @test
    def init_with_lists(self):
        d = self.dict_class({'foo': ['bar'], 'spam': ['eggs']})
        Assert(d['foo']) == 'bar'
        Assert(d['spam']) == 'eggs'

    @test
    def add(self):
        d = self.dict_class()
        d.add('foo', 'bar')
        d.add('foo', 'spam')
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def getlist(self):
        d = self.dict_class()
        Assert(d.getlist('foo')) == []
        d = self.dict_class({'foo': 'bar'})
        Assert(d.getlist('foo')) == ['bar']
        d = self.dict_class({'foo': ['bar', 'spam']})
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def setlist(self):
        d = self.dict_class()
        d.setlist('foo', ['bar', 'spam'])
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def setlistdefault(self):
        d = self.dict_class()
        Assert(d.setlistdefault('foo')) == [None]
        Assert(d['foo']).is_(None)
        Assert(d.setlistdefault('foo', ['bar'])) == [None]
        Assert(d['foo']).is_(None)
        Assert(d.setlistdefault('spam', ['eggs'])) == ['eggs']
        Assert(d['spam']) == 'eggs'

    @test
    def multi_items(self):
        d = self.dict_class({
            'foo': ['bar'],
            'spam': ['eggs', 'monty']
        })
        Assert(len(d.items())) == 2
        Assert(len(d.items(multi=True))) == 3
        Assert(d.items(multi=True)) == list(d.iteritems(multi=True))
        keys = [pair[0] for pair in d.items(multi=True)]
        Assert(set(keys)) == set(['foo', 'spam'])
        values = [pair[1] for pair in d.items(multi=True)]
        Assert(set(values)) == set(['bar', 'eggs', 'monty'])

    @test
    def lists(self):
        d = self.dict_class({
            'foo': ['bar', 'baz'],
            'spam': ['eggs', 'monty']
        })
        Assert(d.lists()) == list(d.iterlists())
        ('foo', ['bar', 'baz']) in Assert(d.lists())
        ('spam', ['eggs', 'monty']) in Assert(d.lists())

    @test
    def update(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.update((1, 2), (3, 4))
        d.update({'foo': 'bar'})
        Assert(d['foo']) == 'bar'
        d.update([('foo', 'spam')])
        Assert(d['foo']) == 'bar'
        Assert(d.getlist('foo')) == ['bar', 'spam']

    @test
    def poplist(self):
        d = self.dict_class({'foo': 'bar', 'spam': ['eggs', 'monty']})
        Assert(d.poplist('foo')) == ['bar']
        Assert(d.poplist('spam')) == ['eggs', 'monty']
        Assert(d.poplist('foo')) == []

    @test
    def popitemlist(self):
        d = self.dict_class({'foo': 'bar'})
        Assert(d.popitemlist()) == ('foo', ['bar'])
        with Assert.raises(KeyError):
            d.popitemlist()
        d = self.dict_class({'foo': ['bar', 'baz']})
        Assert(d.popitemlist()) == ('foo', ['bar', 'baz'])
        with Assert.raises(KeyError):
            d.popitemlist()

    @test
    def repr(self):
        d = self.dict_class()
        Assert(repr(d)) == '%s()' % d.__class__.__name__
        original = {1: [2, 3]}
        d = self.dict_class(original)
        Assert(repr(d)) == '%s(%s)' % (d.__class__.__name__, repr(original))


class TestMultiDict(TestBase, MultiDictTestMixin, DictTestMixin):
    dict_class = MultiDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        assert isinstance(self.dict_class(), dict)


class ImmutableMultiDictTestMixin(MultiDictTestMixin):
    @test
    def add(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.add(1, 2)

    @test
    def setlist(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.setlist(1, [2, 3])

    @test
    def setlistdefault(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.setlistdefault(1)
        with Assert.raises(TypeError):
            d.setlistdefault(1, [2, 3])

    @test
    def poplist(self):
        for d in (self.dict_class(), self.dict_class({1: [2, 3]})):
            with Assert.raises(TypeError):
                d.poplist(1)

    @test
    def popitemlist(self):
        for d in (self.dict_class(), self.dict_class({1: [2, 3]})):
            with Assert.raises(TypeError):
                d.popitemlist()

    @test
    def update(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.update({1: 2})
        with Assert.raises(TypeError):
            d.update(foo='bar')


class TestImmutableMultiDict(TestBase, ImmutableMultiDictTestMixin,
                             ImmutableDictTestMixin):
    dict_class = ImmutableMultiDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        types = [dict, ImmutableDict, MultiDict]
        for type in types:
            assert isinstance(d, type), type

    @test
    def hashability(self):
        d = self.dict_class({1: [2, 3]})
        Assert(hash(d)) == hash(self.dict_class(d))
        with Assert.raises(TypeError):
            hash(self.dict_class({1: [[]]}))


class TestCombinedMultiDict(TestBase, CombinedDictTestMixin,
                            ImmutableMultiDictTestMixin,
                            ImmutableDictTestMixin):
    dict_class = CombinedMultiDict

    # we don't need this special kind of initalization
    init_with_lists = None

    @test
    def getlist(self):
        d = self.dict_class()
        Assert(d.getlist(1)) == []
        d = self.dict_class([MultiDict({1: 2}), MultiDict({1: 3})])
        Assert(d.getlist(1)) == [2, 3]

    @test
    def lists(self):
        d = self.dict_class([
            MultiDict({'foo': ['bar', 'baz']}),
            MultiDict({'foo': ['spam', 'eggs']})
        ])
        Assert(list(d.iterlists())) == d.lists()
        Assert(d.lists()) == [('foo', ['bar', 'baz', 'spam', 'eggs'])]

    @test
    def listvalues(self):
        d = self.dict_class([
            MultiDict({'foo': ['bar', 'baz']}),
            MultiDict({'foo': ['spam', 'eggs']})
        ])
        Assert(list(d.iterlistvalues())) == d.listvalues()
        Assert(d.listvalues()) == [['bar', 'baz', 'spam', 'eggs']]

    @test
    def multi_items(self):
        d = self.dict_class([
            MultiDict({'foo': ['bar', 'baz']}),
            MultiDict({'foo': ['spam', 'eggs']})
        ])
        Assert(list(d.iteritems(multi=True))) == d.items(multi=True)
        Assert(d.items(multi=True)) == [
            ('foo', ['bar', 'baz', 'spam', 'eggs'])
        ]

    @test
    def item_accessor_equality(self):
        CombinedDictTestMixin.item_accessor_equality(self)
        d = self.dict_class([
            MultiDict({'foo': ['bar', 'baz']}),
            MultiDict({'foo': ['spam', 'eggs']})
        ])
        Assert(d.values()) == [d['foo']]
        Assert(d.lists()) == [(key, d.getlist(key)) for key in d]
        Assert(d.items()) == [(k, vs[0]) for k, vs in d.lists()]

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        types = [dict, ImmutableDict, MultiDict, ImmutableMultiDict]
        d = self.dict_class()
        for type in types:
            assert isinstance(d, type), type


class OrderedDictTestMixin(object):
    dict_class = None

    @test
    def fromkeys_is_ordered(self):
        d = self.dict_class.fromkeys([1, 2])
        Assert(d.items()) == [(1, None), (2, None)]

        d = self.dict_class.fromkeys([1, 2], 'foo')
        Assert(d.items()) == [(1, 'foo'), (2, 'foo')]

    @test
    def init_keeps_ordering(self):
        Assert(self.dict_class([(1, 2), (3, 4)]).items()) == [(1, 2), (3, 4)]

    @test
    def setitem_order(self):
        d = self.dict_class()
        d[1] = 2
        d[3] = 4
        Assert(d.items()) == [(1, 2), (3, 4)]

    @test
    def setdefault_order(self):
        d = self.dict_class()
        d.setdefault(1)
        d.setdefault(3, 4)
        Assert(d.items()) == [(1, None), (3, 4)]

    @test
    def pop_does_not_keep_ordering(self):
        d = self.dict_class([(1, 2), (3, 4)])
        d.pop(3)
        d[5] = 6
        d[3] = 4
        modified = self.dict_class([(1, 2), (5, 6), (3, 4)])
        Assert(d) == modified

    @test
    def popitem(self):
        d = self.dict_class([(1, 2), (3, 4), (5, 6)])
        Assert(d.popitem()) == (5, 6)
        Assert(d.popitem(last=False)) == (1, 2)

    @test
    def move_to_end(self):
        d = self.dict_class([(1, 2), (3, 4), (5, 6)])
        d.move_to_end(1)
        Assert(d.items()) == [(3, 4), (5, 6), (1, 2)]
        d.move_to_end(5, last=False)
        Assert(d.items()) == [(5, 6), (3, 4), (1, 2)]

    @test
    def update_order(self):
        d = self.dict_class()
        d.update([(1, 2), (3, 4)])
        items = Assert(d.items())
        items == [(1, 2), (3, 4)]

    @test
    def clear_does_not_keep_ordering(self):
        d = self.dict_class([(1, 2), (3, 4)])
        d.clear()
        d.update([(3, 4), (1, 2)])
        Assert(d.items()) == [(3, 4), (1, 2)]

    @test
    def repr(self):
        d = self.dict_class()
        Assert(repr(d)) == '%s()' % d.__class__.__name__
        original = [(1, 2), (3, 4)]
        d = self.dict_class(original)
        Assert(repr(d)) == '%s(%s)' % (d.__class__.__name__, repr(original))


class TestOrderedDict(TestBase, OrderedDictTestMixin, DictTestMixin):
    dict_class = OrderedDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        assert isinstance(d, dict)


class ImmutableOrderedDictTextMixin(OrderedDictTestMixin):
    update_order = setitem_order = setdefault_order = \
        pop_does_not_keep_ordering = clear_does_not_keep_ordering = None

    @test
    def popitem(self):
        d = self.dict_class()
        with Assert.raises(TypeError):
            d.popitem()
        d = self.dict_class([(1, 2)])
        with Assert.raises(TypeError):
            d.popitem()

    @test
    def move_to_end(self):
        d = self.dict_class([(1, 2), (3, 4)])
        with Assert.raises(TypeError):
            d.move_to_end(1)


class TestImmutableOrderedDict(TestBase, ImmutableOrderedDictTextMixin,
                               ImmutableDictTestMixin):
    dict_class = ImmutableOrderedDict


    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        assert isinstance(d, OrderedDict)
        assert isinstance(d, ImmutableDict)
        assert isinstance(d, dict)

    @test
    def hashability(self):
        d = self.dict_class([(1, 2), (3, 4)])
        Assert(hash(d)) == hash(self.dict_class(d))
        Assert(hash(d)) != hash(self.dict_class(reversed(d.items())))
        with Assert.raises(TypeError):
            hash(self.dict_class(foo=[]))


class TestOrderedMultiDict(TestBase, OrderedDictTestMixin, MultiDictTestMixin,
                           DictTestMixin):
    dict_class = OrderedMultiDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        types = [dict, MultiDict, OrderedDict]
        for type in types:
            assert isinstance(d, type), type


class TestImmutableOrderedMultiDict(TestBase, ImmutableOrderedDictTextMixin,
                                    ImmutableMultiDictTestMixin,
                                    ImmutableDictTestMixin):
    dict_class = ImmutableOrderedMultiDict

    @test_if(GE_PYTHON_26)
    def type_checking(self):
        d = self.dict_class()
        types = [dict, ImmutableDict, MultiDict, ImmutableMultiDict,
                 OrderedDict]
        for type in types:
            assert isinstance(d, type), type


class TestFixedDict(TestBase, DictTestMixin):
    dict_class = FixedDict

    @test
    def setitem(self):
        d = self.dict_class()
        d[1] = 2
        Assert(d[1]) == 2
        with Assert.raises(KeyError):
            d[1] = 3

    @test
    def update(self):
        d = self.dict_class()
        d.update({1: 2})
        Assert(d[1]) == 2
        with Assert.raises(KeyError):
            d.update({1: 3})


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
    def or_and(self):
        c1 = Counter('abc')
        new = c1 | c1 * 2
        Assert(new.values()) == [2] * 3
        new = c1 & c1 * 2
        Assert(new.values()) == [1] * 3


tests = Tests([
    TestMissing, ImmutableDictTest, TestMultiDict, TestOrderedDict,
    TestCounter, TestImmutableMultiDict, TestOrderedMultiDict,
    TestImmutableOrderedMultiDict, TestCombinedDict, TestCombinedMultiDict,
    TestImmutableOrderedDict, TestFixedDict, queues.tests, sets.tests,
    sequences.tests
])
