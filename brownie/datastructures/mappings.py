# coding: utf-8
"""
    brownie.datastructures.mappings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from heapq import nlargest
from operator import itemgetter
from itertools import izip, repeat, ifilter

from brownie.itools import chain, unique, starmap
from brownie.abstract import AbstractClassMeta
from brownie.datastructures import missing


def iter_multi_items(mapping):
    """
    Iterates over the items of the given `mapping`.

    If a key has multiple values a ``(key, value)`` item is yielded for each::

        >>> for key, value in iter_multi_items({1: [2, 3]}):
        ...     print key, value
        1 2
        1 3
        >>> for key, value in iter_multi_items(MultiDict({1: [2, 3]})):
        ...     print key, value
        1 2
        1 3
    """
    if isinstance(mapping, MultiDict):
        for item in mapping.iteritems(multi=False):
            yield item
    elif isinstance(mapping, dict):
        for key, value in mapping.iteritems():
            if isinstance(value, (tuple, list)):
                for value in value:
                    yield key, value
            else:
                yield key, value
    else:
        for item in mapping:
            yield item


@classmethod
def raise_immutable(cls, *args, **kwargs):
    raise TypeError('%r objects are immutable' % cls.__name__)


class ImmutableDictMixin(object):
    @classmethod
    def fromkeys(cls, keys, value=None):
        return cls(zip(keys, repeat(value)))

    __setitem__ = __delitem__ = setdefault = update = pop = popitem = clear = \
        raise_immutable

    def __repr__(self):
        content = dict.__repr__(self) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)


class ImmutableDict(ImmutableDictMixin, dict):
    """
    An immutable :class:`dict`.

    .. versionadded:: 0.5
       :class:`ImmutableDict` is now hashable, given the content is.
    """
    __metaclass__ = AbstractClassMeta

    def __hash__(self):
        return hash(tuple(self.items()))


class CombinedDictMixin(object):
    @classmethod
    def fromkeys(cls, keys, value=None):
        raise TypeError('cannot create %r instances with .fromkeys()' %
            cls.__class__.__name__
        )

    def __init__(self, dicts=None):
        #: The list of combined dictionaries.
        self.dicts = [] if dicts is None else list(dicts)

    def __getitem__(self, key):
        for d in self.dicts:
            if key in d:
                return d[key]
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __iter__(self):
        return unique(chain.from_iterable(d.iterkeys() for d in self.dicts))

    iterkeys = __iter__

    def itervalues(self):
        for key in self:
            yield self[key]

    def iteritems(self):
        for key in self:
            yield key, self[key]

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return any(key in d for d in self.dicts)

    has_key = __contains__

    def __repr__(self):
        content = repr(self.dicts) if self.dicts else ''
        return '%s(%s)' % (self.__class__.__name__, content)


class CombinedDict(CombinedDictMixin, ImmutableDictMixin, dict):
    """
    An immutable :class:`dict` which combines the given `dicts` into one.

    You can use this class to combine dicts of any type, however different
    interfaces as provided by e.g. :class:`MultiDict` or :class:`Counter` are
    not supported, the same goes for additional keyword arguments.

    .. versionadded:: 0.2

    .. versionadded:: 0.5
       :class:`CombinedDict` is now hashable, given the content is.
    """
    __metaclass__ = AbstractClassMeta
    virtual_superclasses = (ImmutableDict, )

    def __hash__(self):
        return hash(tuple(self.dicts))


class MultiDictMixin(object):
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got %d' % len(args)
            )
        arg = []
        if args:
            mapping = args[0]
            if isinstance(mapping, self.__class__):
                arg = ((k, l[:]) for k, l in mapping.iterlists())
            elif hasattr(mapping, 'iteritems'):
                for key, value in mapping.iteritems():
                    if isinstance(value, (tuple, list)):
                        value = list(value)
                    else:
                        value = [value]
                    arg.append((key, value))
            else:
                keys = []
                tmp = {}
                for key, value in mapping or ():
                    tmp.setdefault(key, []).append(value)
                    keys.append(key)
                arg = ((key, tmp[key]) for key in unique(keys))
        kws = {}
        for key, value in kwargs.iteritems():
            if isinstance(value, (tuple, list)):
                value = list(value)
            else:
                value = [value]
            kws[key] = value
        super(MultiDictMixin, self).__init__(arg, **kws)

    def __getitem__(self, key):
        """
        Returns the first value associated with the given `key`. If no value
        is found a :exc:`KeyError` is raised.
        """
        return super(MultiDictMixin, self).__getitem__(key)[0]

    def __setitem__(self, key, value):
        """
        Sets the values associated with the given `key` to ``[value]``.
        """
        super(MultiDictMixin, self).__setitem__(key, [value])

    def get(self, key, default=None):
        """
        Returns the first value associated with the given `key`, if there are
        none the `default` is returned.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def add(self, key, value):
        """
        Adds the `value` for the given `key`.
        """
        super(MultiDictMixin, self).setdefault(key, []).append(value)

    def getlist(self, key):
        """
        Returns the :class:`list` of values for the given `key`. If there are
        none an empty :class:`list` is returned.
        """
        try:
            return super(MultiDictMixin, self).__getitem__(key)
        except KeyError:
            return []

    def setlist(self, key, values):
        """
        Sets the values associated with the given `key` to the given `values`.
        """
        super(MultiDictMixin, self).__setitem__(key, list(values))

    def setdefault(self, key, default=None):
        """
        Returns the value for the `key` if it is in the dict, otherwise returns
        `default` and sets that value for the `key`.
        """
        if key not in self:
            MultiDictMixin.__setitem__(self, key, default)
        else:
            default = MultiDictMixin.__getitem__(self, key)
        return default

    def setlistdefault(self, key, default_list=None):
        """
        Like :meth:`setdefault` but sets multiple values and returns the list
        associated with the `key`.
        """
        if key not in self:
            default_list = list(default_list or (None, ))
            MultiDictMixin.setlist(self, key, default_list)
        else:
            default_list = MultiDictMixin.getlist(self, key)
        return default_list

    def iteritems(self, multi=False):
        """Like :meth:`items` but returns an iterator."""
        for key, values in super(MultiDictMixin, self).iteritems():
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]

    def items(self, multi=False):
        """
        Returns a :class:`list` of ``(key, value)`` pairs.

        :param multi:
            If ``True`` the returned :class:`list` will contain a pair for
            every value associated with a key.
        """
        return list(self.iteritems(multi))

    def itervalues(self):
        """Like :meth:`values` but returns an iterator."""
        for values in super(MultiDictMixin, self).itervalues():
            yield values[0]

    def values(self):
        """
        Returns a :class:`list` with the first value of every key.
        """
        return list(self.itervalues())

    def iterlists(self):
        """Like :meth:`lists` but returns an iterator."""
        for key, values in super(MultiDictMixin, self).iteritems():
            yield key, list(values)

    def lists(self):
        """
        Returns a :class:`list` of ``(key, values)`` pairs, where `values` is
        the list of values associated with the `key`.
        """
        return list(self.iterlists())

    def iterlistvalues(self):
        """Like :meth:`listvalues` but returns an iterator."""
        return super(MultiDictMixin, self).itervalues()

    def listvalues(self):
        """
        Returns a :class:`list` of all values.
        """
        return list(self.iterlistvalues())

    def pop(self, key, default=missing):
        """
        Returns the first value associated with the given `key` and removes
        the item.
        """
        value = super(MultiDictMixin, self).pop(key, default)
        if value is missing:
            raise KeyError(key)
        elif value is default:
            return default
        return value[0]

    def popitem(self, *args, **kwargs):
        """
        Returns a key and the first associated value. The item is removed.
        """
        key, values = super(MultiDictMixin, self).popitem(*args, **kwargs)
        return key, values[0]

    def poplist(self, key):
        """
        Returns the :class:`list` of values associated with the given `key`,
        if the `key` does not exist in the :class:`MultiDict` an empty list is
        returned.
        """
        return super(MultiDictMixin, self).pop(key, [])

    def popitemlist(self):
        """Like :meth:`popitem` but returns all associated values."""
        return super(MultiDictMixin, self).popitem()

    def update(self, *args, **kwargs):
        """
        Extends the dict using the given mapping and/or keyword arguments.
        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got %d' % len(args)
            )
        mappings = [args[0] if args else [], kwargs.iteritems()]
        for mapping in mappings:
            for key, value in iter_multi_items(mapping):
                MultiDictMixin.add(self, key, value)


class MultiDict(MultiDictMixin, dict):
    """
    A :class:`MultiDict` is a dictionary customized to deal with multiple
    values for the same key.

    Internally the values for each key are stored as a :class:`list`, but the
    standard :class:`dict` methods will only return the first value of those
    :class:`list`\s. If you want to gain access to every value associated with
    a key, you have to use the :class:`list` methods, specific to a
    :class:`MultiDict`.
    """
    __metaclass__ = AbstractClassMeta

    def __repr__(self):
        content = dict.__repr__(self) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)


class ImmutableMultiDictMixin(ImmutableDictMixin, MultiDictMixin):
    def add(self, key, value):
        raise_immutable(self)

    def setlist(self, key, values):
        raise_immutable(self)

    def setlistdefault(self, key, default_list=None):
        raise_immutable(self)

    def poplist(self, key):
        raise_immutable(self)

    def popitemlist(self):
        raise_immutable(self)


class ImmutableMultiDict(ImmutableMultiDictMixin, dict):
    """
    An immutable :class:`MultiDict`.

    .. versionadded:: 0.5
       :class:`ImmutableMultiDict` is now hashable, given the content is.
    """
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (MultiDict, ImmutableDict)

    def __hash__(self):
        return hash(tuple((key, tuple(value)) for key, value in self.lists()))


class CombinedMultiDict(CombinedDictMixin, ImmutableMultiDictMixin, dict):
    """
    An :class:`ImmutableMultiDict` which combines the given `dicts` into one.

    .. versionadded:: 0.2
    """
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (ImmutableMultiDict, )

    def getlist(self, key):
        return sum((d.getlist(key) for d in self.dicts), [])

    def iterlists(self):
        result = OrderedDict()
        for d in self.dicts:
            for key, values in d.iterlists():
                result.setdefault(key, []).extend(values)
        return result.iteritems()

    def iterlistvalues(self):
        for key in self:
            yield self.getlist(key)

    def iteritems(self, multi=False):
        for key in self:
            if multi:
                yield key, self.getlist(key)
            else:
                yield key, self[key]

    def items(self, multi=False):
        return list(self.iteritems(multi))


class _Link(object):
    def __init__(self, key=None, prev=None, next=None):
        self.key = key
        self.prev = prev
        self.next = next


class OrderedDict(dict):
    """
    A :class:`dict` which remembers insertion order.

    Big-O times for every operation are equal to the ones :class:`dict` has
    however this comes at the cost of higher memory usage.

    This dictionary is only equal to another dictionary of this type if the
    items on both dictionaries were inserted in the same order.
    """
    @classmethod
    def fromkeys(cls, iterable, value=None):
        """
        Returns a :class:`OrderedDict` with keys from the given `iterable`
        and `value` as value for each item.
        """
        return cls(izip(iterable, repeat(value)))

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got %d' % len(args)
            )
        self._root = _Link()
        self._root.prev = self._root.next = self._root
        self._map = {}
        OrderedDict.update(self, *args, **kwargs)

    def __setitem__(self, key, value):
        """
        Sets the item with the given `key` to the given `value`.
        """
        if key not in self:
            last = self._root.prev
            link = _Link(key, last, self._root)
            last.next = self._root.prev = self._map[key] = link
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        """
        Deletes the item with the given `key`.
        """
        dict.__delitem__(self, key)
        link = self._map.pop(key)
        prev, next = link.prev, link.next
        prev.next, next.prev = link.next, link.prev

    def setdefault(self, key, default=None):
        """
        Returns the value of the item with the given `key`, if not existant
        sets creates an item with the `default` value.
        """
        if key not in self:
            OrderedDict.__setitem__(self, key, default)
        return OrderedDict.__getitem__(self, key)

    def pop(self, key, default=missing):
        """
        Deletes the item with the given `key` and returns the value. If the
        item does not exist a :exc:`KeyError` is raised unless `default` is
        given.
        """
        try:
            value = dict.__getitem__(self, key)
            del self[key]
            return value
        except KeyError:
            if default is missing:
                raise
            return default

    def popitem(self, last=True):
        """
        Pops the last or first item from the dict depending on `last`.
        """
        if not self:
            raise KeyError('dict is empty')
        key = (reversed(self) if last else iter(self)).next()
        return key, OrderedDict.pop(self, key)

    def move_to_end(self, key, last=True):
        """
        Moves the item with the given `key` to the end of the dictionary if
        `last` is ``True`` otherwise to the beginning.

        Raises :exc:`KeyError` if no item with the given `key` exists.

        .. versionadded:: 0.4
        """
        if key not in self:
            raise KeyError(key)
        link = self._map[key]
        prev, next = link.prev, link.next
        prev.next, next.prev = next, prev
        if last:
            replacing = self._root.prev
            replacing.next = self._root.prev = link
            link.prev, link.next = replacing, self._root
        else:
            replacing = self._root.next
            self._root.next = replacing.prev = link
            link.prev, link.next = self._root, replacing

    def update(self, *args, **kwargs):
        """
        Updates the dictionary with a mapping and/or from keyword arguments.
        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got %d' % len(args)
            )
        mappings = []
        if args:
            if hasattr(args[0], 'iteritems'):
                mappings.append(args[0].iteritems())
            else:
                mappings.append(args[0])
        mappings.append(kwargs.iteritems())
        for mapping in mappings:
            for key, value in mapping:
                OrderedDict.__setitem__(self, key, value)

    def clear(self):
        """
        Clears the contents of the dict.
        """
        self._root = _Link()
        self._root.prev = self._root.next = self._root
        self._map.clear()
        dict.clear(self)

    def __eq__(self, other):
        """
        Returns ``True`` if this dict is equal to the `other` one. If the
        other one is a :class:`OrderedDict` as well they are only considered
        equal if the insertion order is identical.
        """
        if isinstance(other, self.__class__):
            return all(
                i1 == i2 for i1, i2 in izip(self.iteritems(), other.iteritems())
            )
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        curr = self._root.next
        while curr is not self._root:
            yield curr.key
            curr = curr.next

    def __reversed__(self):
        curr = self._root.prev
        while curr is not self._root:
            yield curr.key
            curr = curr.prev

    def iterkeys(self):
        """
        Returns an iterator over the keys of all items in insertion order.
        """
        return OrderedDict.__iter__(self)

    def itervalues(self):
        """
        Returns an iterator over the values of all items in insertion order.
        """
        return (dict.__getitem__(self, k) for k in OrderedDict.__iter__(self))

    def iteritems(self):
        """
        Returns an iterator over all the items in insertion order.
        """
        return izip(OrderedDict.iterkeys(self), OrderedDict.itervalues(self))

    def keys(self):
        """
        Returns a :class:`list` over the keys of all items in insertion order.
        """
        return list(OrderedDict.iterkeys(self))

    def values(self):
        """
        Returns a :class:`list` over the values of all items in insertion order.
        """
        return list(OrderedDict.itervalues(self))

    def items(self):
        """
        Returns a :class:`list` over the items in insertion order.
        """
        return zip(OrderedDict.keys(self), OrderedDict.values(self))

    def __repr__(self):
        content = repr(self.items()) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)


class ImmutableOrderedDict(ImmutableDictMixin, OrderedDict):
    """
    An immutable :class:`OrderedDict`.

    .. versionadded:: 0.2

    .. versionadded:: 0.5
       :class:`ImmutableOrderedDict` is now hashable, given the content is.
    """
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (ImmutableDict, )

    move_to_end = raise_immutable

    def __hash__(self):
        return hash(tuple(self.iteritems()))

    __repr__ = OrderedDict.__repr__


class OrderedMultiDict(MultiDictMixin, OrderedDict):
    """An ordered :class:`MultiDict`."""
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (MultiDict, )


class ImmutableOrderedMultiDict(ImmutableMultiDictMixin, ImmutableOrderedDict):
    """An immutable :class:`OrderedMultiDict`."""
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (ImmutableMultiDict, OrderedMultiDict)

    def __repr__(self):
        content = repr(self.items()) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)


class FixedDict(dict):
    """
    A :class:`dict` whose items can only be created or deleted not changed.

    If you attempt to change an item a :exc:`KeyError` is raised.

    .. versionadded:: 0.5
    """
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError('already set')
        dict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got %d' % len(args)
            )
        mappings = []
        if args:
            if hasattr(args[0], 'iteritems'):
                mappings.append(args[0].iteritems())
            else:
                mappings.append(args[0])
        mappings.append(kwargs.iteritems())
        for mapping in mappings:
            for key, value in mapping:
                FixedDict.__setitem__(self, key, value)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            dict.__repr__(self) if self else ''
        )


class Counter(dict):
    """
    :class:`dict` subclass for counting hashable objects. Elements are stored
    as keys with the values being their respective counts.

    :param countable: An iterable of elements to be counted or a
                      :class:`dict`\-like object mapping elements to their
                      respective counts.

    This object supports several operations returning a new :class:`Counter`
    object from the common elements of `c1` and `c2`, in any case the new
    counter will not contain negative counts.

    +-------------+-----------------------------------------------------+
    | Operation   | Result contains...                                  |
    +=============+=====================================================+
    | ``c1 + c2`` | sums of common element counts.                      |
    +-------------+-----------------------------------------------------+
    | ``c1 - c2`` | difference of common element counts.                |
    +-------------+-----------------------------------------------------+
    | ``c1 | c2`` | maximum of common element counts.                   |
    +-------------+-----------------------------------------------------+
    | ``c1 & c2`` | minimum of common element counts.                   |
    +-------------+-----------------------------------------------------+

    Furthermore it is possible to multiply the counter with an :class:`int` as
    scalar.

    Accessing a non-existing element will always result in an element
    count of 0, accordingly :meth:`get` uses 0 and :meth:`setdefault` uses 1 as
    default value.
    """
    def __init__(self, countable=None, **kwargs):
        self.update(countable, **kwargs)

    def __missing__(self, key):
        return 0

    def get(self, key, default=0):
        return dict.get(self, key, default)

    def setdefault(self, key, default=1):
        return dict.setdefault(self, key, default)

    def most_common(self, n=None):
        """
        Returns a list of all items sorted from the most common to the least.

        :param n: If given only the items of the `n`\-most common elements are
                  returned.

        >>> from brownie.datastructures import Counter
        >>> Counter('Hello, World!').most_common(2)
        [('l', 3), ('o', 2)]
        """
        if n is None:
            return sorted(self.iteritems(), key=itemgetter(1), reverse=True)
        return nlargest(n, self.iteritems(), key=itemgetter(1))

    def elements(self):
        """
        Iterator over the elements in the counter, repeating as many times as
        counted.

        >>> from brownie.datastructures import Counter
        >>> sorted(Counter('abcabc').elements())
        ['a', 'a', 'b', 'b', 'c', 'c']
        """
        return chain(*starmap(repeat, self.iteritems()))

    def update(self, countable=None, **kwargs):
        """
        Updates the counter from the given `countable` and `kwargs`.
        """
        countable = countable or []
        if hasattr(countable, 'iteritems'):
            mappings = [countable.iteritems()]
        else:
            mappings = [izip(countable, repeat(1))]
        mappings.append(kwargs.iteritems())
        for mapping in mappings:
            for element, count in mapping:
                self[element] = self.get(element) + count

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = Counter()
        for element in set(self) | set(other):
            newcount = self[element] + other[element]
            if newcount > 0:
                result[element] = newcount
        return result

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = Counter()
        for element in set(self) | set(other):
            newcount = self[element] - other[element]
            if newcount > 0:
                result[element] = newcount

    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        result = Counter()
        for element in self:
            newcount = self[element] * other
            if newcount > 0:
                result[element] = newcount
        return result

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = Counter()
        for element in set(self) | set(other):
            newcount = max(self[element], other[element])
            if newcount > 0:
                result[element] = newcount
        return result

    def __and__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        result = Counter()
        if len(self) < len(other):
            self, other = other, self
        for element in ifilter(self.__contains__, other):
            newcount = min(self[element], other[element])
            if newcount > 0:
                result[element] = newcount
        return result

