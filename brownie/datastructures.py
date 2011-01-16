# coding: utf-8
"""
    brownie.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic datastructures.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from heapq import nlargest
from operator import itemgetter
from functools import wraps
from itertools import count, izip, repeat, ifilter
try:
    import queue
except ImportError:
    import Queue as queue

from brownie.itools import izip_longest, starmap, unique, chain
from brownie.abstract import AbstractClassMeta


class Missing(object):
    def __nonzero__(self):
        return False

    def __repr__(self):
        return 'missing'

#: Sentinel object which can be used instead of ``None``. This is useful if
#: you have optional parameters to which a user can pass ``None`` e.g. in
#: datastructures.
missing = Missing()

del Missing


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
    """An immutable :class:`dict`."""
    __metaclass__ = AbstractClassMeta


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
    """
    __metaclass__ = AbstractClassMeta
    virtual_superclasses = (ImmutableDict, )


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
    """An immutable :class:`MultiDict`."""
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (MultiDict, ImmutableDict)


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
    """
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (ImmutableDict, )

    __repr__ = OrderedDict.__repr__


class OrderedMultiDict(MultiDictMixin, OrderedDict):
    """An ordered :class:`MultiDict`."""
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (MultiDict, )


class ImmutableOrderedMultiDict(ImmutableMultiDictMixin, OrderedDict):
    """An immutable :class:`OrderedMultiDict`."""
    __metaclass__ = AbstractClassMeta

    virtual_superclasses = (ImmutableMultiDict, OrderedMultiDict)

    def __repr__(self):
        content = repr(self.items()) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)


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


class LazyList(object):
    """
    Implements a lazy list which computes items based on the given `iterable`.

    This allows you to create :class:`list`\-like objects of unlimited size.
    However although most operations don't exhaust the internal iterator
    completely some of them do, so if the given iterable is of unlimited size
    making such an operation will eventually cause a :exc:`MemoryError`.

    Cost in terms of laziness of supported operators, this does not include
    supported operators without any cost:

    +-----------------+-------------------------------------------------------+
    | Operation       | Result                                                |
    +=================+=======================================================+
    | ``list[i]``     | This exhausts the `list` up until the given index.    |
    +-----------------+                                                       |
    | ``list[i] = x`` |                                                       |
    +-----------------+                                                       |
    | ``del list[i]`` |                                                       |
    +-----------------+-------------------------------------------------------+
    | ``len(list)``   | Exhausts the internal iterator.                       |
    +-----------------+-------------------------------------------------------+
    | ``x in list``   | Exhausts the `list` up until `x` or until the `list`  |
    |                 | is exhausted.                                         |
    +-----------------+-------------------------------------------------------+
    | ``l1 == l2``    | Exhausts both lists.                                  |
    +-----------------+-------------------------------------------------------+
    | ``l1 != l2``    | Exhausts both lists.                                  |
    +-----------------+-------------------------------------------------------+
    | ``bool(list)``  | Exhausts the `list` up to the first item.             |
    +-----------------+-------------------------------------------------------+
    | ``l1 < l2``     | Exhausts the list up to the first item which shows    |
    |                 | the result. In the worst case this exhausts both      |
    +-----------------+ lists.                                                |
    | ``l1 > l2``     |                                                       |
    +-----------------+-------------------------------------------------------+
    | ``l1 + l2``     | Creates a new :class:`LazyList` without exhausting    |
    |                 | `l1` or `l2`.                                         |
    +-----------------+-------------------------------------------------------+
    | ``list * n``    | Exhausts the `list`.                                  |
    +-----------------+                                                       |
    | ``list *= n``   |                                                       |
    +-----------------+-------------------------------------------------------+
    """
    @classmethod
    def factory(cls, callable):
        """
        Returns a wrapper for a given callable which takes the return value
        of the wrapped callable and converts it into a :class:`LazyList`.
        """
        @wraps(callable)
        def wrap(*args, **kwargs):
            return cls(callable(*args, **kwargs))
        return wrap

    def exhausting(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            self._exhaust()
            return func(self, *args, **kwargs)
        return wrap

    def __init__(self, iterable):
        if isinstance(iterable, (list, tuple, basestring)):
            #: ``True`` if the internal iterator is exhausted.
            self.exhausted = True
            self._collected_data = list(iterable)
        else:
            self._iterator = iter(iterable)
            self.exhausted = False
            self._collected_data = []
        self._added_data = []

    def _exhaust(self, i=None):
        if self.exhausted:
            return
        elif i is None or i < 0:
            index_range = count(self.known_length)
        elif isinstance(i, slice):
            start, stop = i.start, i.stop
            if start < 0 or stop < 0:
                index_range = count(self.known_length)
            else:
                index_range = xrange(self.known_length, stop)
        else:
            index_range = xrange(self.known_length, i + 1)
        for i in index_range:
            try:
                self._collected_data.append(self._iterator.next())
            except StopIteration:
                self.exhausted = True
                break

    @property
    def known_length(self):
        """
        The number of items which have been taken from the internal iterator.
        """
        return len(self._collected_data)

    def append(self, object):
        """
        Appends the given `object` to the list.
        """
        self.extend([object])

    def extend(self, objects):
        """
        Extends the list with the given `objects`.
        """
        if self.exhausted:
            self._collected_data.extend(objects)
        else:
            self._iterator = chain(self._iterator, objects)

    def insert(self, index, object):
        """
        Inserts the given `object` at the given `index`.

        This method exhausts the internal iterator up until the given `index`.
        """
        if index >= self.known_length or index < 0:
            self._exhaust(index)
        self._collected_data.insert(index, object)

    def pop(self, index=None):
        """
        Removes and returns the item at the given `index`, if no `index` is
        given the last item is used.

        This method exhausts the internal iterator up until the given `index`.
        """
        self._exhaust(index)
        if index is None:
            return self._collected_data.pop()
        return self._collected_data.pop(index)

    def remove(self, object):
        """
        Looks for the given `object` in the list and removes the first
        occurrence.

        If the item is not found a :exc:`ValueError` is raised.

        This method exhausts the internal iterator up until the first
        occurrence of the given `object` or entirely if it is not found.
        """
        while True:
            try:
                self._collected_data.remove(object)
                return
            except ValueError:
                try:
                    self._added_data.remove(object)
                except ValueError:
                    if self.exhausted:
                        raise
                    else:
                        self._exhaust(self.known_length)

    @exhausting
    def reverse(self):
        """
        Reverses the list.

        This method exhausts the internal iterator.
        """
        self._collected_data.reverse()

    @exhausting
    def sort(self, cmp=None, key=None, reverse=False):
        """
        Sorts the list using the given `cmp` or `key` function and reverses it
        if `reverse` is ``True``.

        This method exhausts the internal iterator.
        """
        self._collected_data.sort(cmp=cmp, key=key, reverse=reverse)

    @exhausting
    def count(self, object):
        """
        Counts the occurrences of the given `object` in the list.

        This method exhausts the internal iterator.
        """
        return self._collected_data.count(object)

    def __getitem__(self, i):
        """
        Returns the object or objects at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        return self._collected_data[i]

    def __setitem__(self, i, obj):
        """
        Sets the given object or objects at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        self._collected_data[i] = obj

    def __delitem__(self, i):
        """
        Removes the item or items at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        del self._collected_data[i]

    @exhausting
    def __len__(self):
        """
        Returns the length of the list.

        This method exhausts the internal iterator.
        """
        return self.known_length + len(self._added_data)

    def __contains__(self, other):
        for obj in self:
            if obj == other:
                return True
        return False

    @exhausting
    def __eq__(self, other):
        """
        Returns ``True`` if the list is equal to the given `other` list, which
        may be another :class:`LazyList`, a :class:`list` or a subclass of
        either.

        This method exhausts the internal iterator.
        """
        if isinstance(other, (self.__class__, list)):
            return self._collected_data == other
        return False

    def __ne__(self, other):
        """
        Returns ``True`` if the list is unequal to the given `other` list, which
        may be another :class:`LazyList`, a :class:`list` or a subclass of
        either.

        This method exhausts the internal iterator.
        """
        return not self.__eq__(other)

    __hash__ = None

    def __nonzero__(self):
        """
        Returns ``True`` if the list is not empty.

        This method takes one item from the internal iterator.
        """
        self._exhaust(0)
        return bool(self._collected_data)

    def __lt__(self, other):
        """
        This method returns ``True`` if this list is "lower than" the given
        `other` list. This is the case if...

        - this list is empty and the other is not.
        - the first nth item in this list which is unequal to the
          corresponding item in the other list, is lower than the corresponding
          item.

        If this and the other list is empty this method will return ``False``.
        """
        if not self and other:
            return True
        elif self and not other:
            return False
        elif not self and not other:
            return False
        missing = object()
        for a, b in izip_longest(self, other, fillvalue=missing):
            if a < b:
                return True
            elif a == b:
                continue
            elif a is missing and b is not missing:
                return True
            return False

    def __gt__(self, other):
        """
        This method returns ``True`` if this list is "greater than" the given
        `other` list. This is the case if...

        - this list is not empty and the other is
        - the first nth item in this list which is unequal to the
          corresponding item in the other list, is greater than the
          corresponding item.

        If this and the other list is empty this method will return ``False``.
        """

        if not self and not other:
            return False
        return not self.__lt__(other)

    def __add__(self, other):
        if isinstance(other, (list, self.__class__)):
            return self.__class__(chain(self, other))
        raise TypeError("can't concatenate with non-list: {0}".format(other))

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, other):
        if isinstance(other, int):
            self._exhaust()
            return self.__class__(self._collected_data * other)
        raise TypeError("can't multiply sequence by non-int: {0}".format(other))

    def __imul__(self, other):
        if isinstance(other, int):
            self._exhaust()
            self._collected_data *= other
            return self
        else:
            raise TypeError(
                "can't multiply sequence by non-int: {0}".format(other)
            )

    def __repr__(self):
        """
        Returns the representation string of the list, if the list exhausted
        this looks like the representation of any other list, otherwise the
        "lazy" part is represented by "...", like "[1, 2, 3, ...]".
        """
        if self.exhausted:
            return repr(self._collected_data)
        elif not self._collected_data:
            return '[...]'
        return '[%s, ...]' % ', '.join(
            repr(obj) for obj in self._collected_data
        )

    del exhausting


class OrderedSet(object):
    """
    A :class:`set` which remembers insertion order.

    .. versionadded:: 0.2
    """
    def requires_set(func):
        @wraps(func)
        def wrapper(self, other):
            if isinstance(other, (self.__class__, set, frozenset)):
                return func(self, other)
            return NotImplemented
        return wrapper

    def __init__(self, iterable=None):
        self._orderedmap = OrderedDict.fromkeys(iterable or ())

    def __len__(self):
        return len(self._orderedmap)

    def __contains__(self, element):
        return element in self._orderedmap

    def add(self, element):
        self._orderedmap[element] = None

    def remove(self, element):
        del self._orderedmap[element]

    def discard(self, element):
        self._orderedmap.pop(element, None)

    def pop(self, last=True):
        """
        Returns the last element if `last` is ``True``, the first otherwise.
        """
        if not self:
            raise KeyError('set is empty')
        element = self._orderedmap.popitem(last=last)[0]
        return element

    def clear(self):
        self._orderedmap.clear()

    def update(self, *others):
        for other in others:
            for element in other:
                self._orderedmap[element] = None

    def copy(self):
        return self.__class__(self)

    @requires_set
    def __ior__(self, other):
        self.update(other)
        return self

    def issubset(self, other):
        return all(element in other for element in self)

    @requires_set
    def __le__(self, other):
        return self.issubset(other)

    @requires_set
    def __lt__(self, other):
        return self.issubset(other) and self != other

    def issuperset(self, other):
        return all(element in self for element in other)

    @requires_set
    def __ge__(self, other):
        return self.issuperset(other)

    @requires_set
    def __gt__(self, other):
        return self.issuperset(other) and self != other

    def union(self, *others):
        return self.__class__(chain.from_iterable((self, ) + others))

    @requires_set
    def __or__(self, other):
        return self.union(other)

    def intersection(self, *others):
        def intersect(a, b):
            result = self.__class__()
            smallest = min([a, b], key=len)
            for element in max([a, b], key=len):
                if element in smallest:
                    result.add(element)
            return result
        return reduce(intersect, others, self)

    @requires_set
    def __and__(self, other):
        return self.intersection(other)

    @requires_set
    def __iand__(self, other):
        intersection = self.intersection(other)
        self.clear()
        self.update(intersection)
        return self

    def difference(self, *others):
        return self.__class__(
            key for key in self if not any(key in s for s in others)
        )

    @requires_set
    def __sub__(self, other):
        return self.difference(other)

    @requires_set
    def __isub__(self, other):
        diff = self.difference(other)
        self.clear()
        self.update(diff)
        return self

    def symmetric_difference(self, other):
        other = self.__class__(other)
        return self.__class__(chain(self - other, other - self))

    @requires_set
    def __xor__(self, other):
        return self.symmetric_difference(other)

    @requires_set
    def __ixor__(self, other):
        diff = self.symmetric_difference(other)
        self.clear()
        self.update(diff)
        return self

    def __iter__(self):
        return iter(self._orderedmap)

    def __reversed__(self):
        return reversed(self._orderedmap)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == other

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = None

    def __repr__(self):
        content = repr(list(self)) if self else ''
        return '%s(%s)' % (self.__class__.__name__, content)

    del requires_set


class SetQueue(queue.Queue):
    """Thread-safe implementation of an ordered set queue, which coalesces
    duplicate items into a single item if the older occurrence has not yet been
    read and maintains the order of items in the queue.

    Ordered set queues are useful when implementing data structures like
    event buses or event queues where duplicate events need to be coalesced
    into a single event. An example use case is the inotify API in the Linux
    kernel which shares the same behavior.

    Queued items must be immutable and hashable so that they can be used as
    dictionary keys or added to sets. Items must have only read-only properties
    and must implement the :meth:`__hash__`, :meth:`__eq__`, and :meth:`__ne__`
    methods to be hashable.

    An example item class implementation follows::

        class QueuedItem(object):
            def __init__(self, a, b):
                self._a = a
                self._b = b

            @property
            def a(self):
                return self._a

            @property
            def b(self):
                return self._b

            def _key(self):
                return (self._a, self._b)

            def __eq__(self, item):
                return self._key() == item._key()

            def __ne__(self, item):
                return self._key() != item._key()

            def __hash__(self):
                return hash(self._key())

    .. NOTE::
        This ordered set queue leverages locking already present in the
        :class:`queue.Queue` class redefining only internal primitives. The
        order of items is maintained because the internal queue is not replaced.
        An internal set is used merely to check for the existence of an item in
        the queue.

    .. versionadded:: 0.3

    :author: Gora Khargosh <gora.khargosh@gmail.com>
    :author: Lukáš Lalinský <lalinsky@gmail.com>
    """
    def _init(self, maxsize):
        queue.Queue._init(self, maxsize)
        self._set_of_items = set()

    def _put(self, item):
        if item not in self._set_of_items:
            queue.Queue._put(self, item)
            self._set_of_items.add(item)

    def _get(self):
        item = queue.Queue._get(self)
        self._set_of_items.remove(item)
        return item
