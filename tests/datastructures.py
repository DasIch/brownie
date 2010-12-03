# coding: utf-8
"""
    tests.datastructures
    ~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import random

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import missing, MultiDict

datastructures_tests = Tests()


@datastructures_tests.register
class TestMissing(TestBase):
    @test
    def has_false_boolean_value(self):
        Assert(not missing) == True

    @test
    def repr(self):
        Assert(repr(missing)) == 'missing'


@datastructures_tests.register
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
