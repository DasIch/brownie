# coding: utf-8
"""
    brownie.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic datastructures.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from functools import wraps
from itertools import count, chain, izip, izip_longest, repeat
from collections import Sequence


class Missing(object):
    def __nonzero__(self):
        return False

    def __repr__(self):
        return 'missing'

#: Sentinel object which can be used instead of ``None``.
missing = Missing()

del Missing


def iter_multi_items(mapping):
    """
    Iterates over the items of the given `mapping` yielding keys and values
    without dropping any from more complex datastructures.
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


class MultiDict(dict):
    """
    A :class:`MultiDict` is a dictionary customized to deal with multiple
    values for the same key.

    Internally the values for each key are stored as a :class:`list`, but the
    standard :class:`dict` methods will only return the first value of those
    :class:`list`\s. If you want to gain access to every value associated with
    a key, you have to use the :class:`list` methods, specific to a
    :class:`MultiDict`.

    :param mapping:
        A :class:`MultiDict`, :class:`dict`, a :class:`list` of
        ``(key, value)`` tuples or ``None``.
    """
    def __init__(self, mapping=None):
        if isinstance(mapping, self.__class__):
            dict.__init__(self, ((k, l[:]) for k, l in mapping.iterlists()))
        elif isinstance(mapping, dict):
            tmp = {}
            for key, value in mapping.iteritems():
                if isinstance(value, (tuple, list)):
                    value = list(value)
                else:
                    value = [value]
                tmp[key] = value
            dict.__init__(self, tmp)
        else:
            tmp = {}
            for key, value in mapping or ():
                tmp.setdefault(key, []).append(value)
            dict.__init__(self, tmp)

    def __getstate__(self):
        return dict(self.lists())

    def __setstate__(self, value):
        dict.clear(self)
        dict.update(self, value)

    def __iter__(self):
        return self.iterkeys()

    def __getitem__(self, key):
        """
        Returns the first value associated with the given `key`. If no value
        is found a :exc:`KeyError` is raised.
        """
        if key in self:
            return dict.__getitem__(self, key)[0]
        raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Sets the values associated with the given `key` to the given `value`.
        """
        dict.__setitem__(self, key, [value])

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
        dict.setdefault(self, key, []).append(value)

    def getlist(self, key):
        """
        Returns the :class:`list` of values for the given `key`. If there are
        none an empty :class:`list` is returned.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return []

    def setlist(self, key, values):
        """
        Sets the values associated with a given `key` to the given `values`.
        """
        dict.__setitem__(self, key, list(values))

    def setdefault(self, key, default=None):
        """
        Returns the value for the `key` if it is in the dict, otherwise returns
        `default` and sets that value for the `key`.
        """
        if key not in self:
            self[key] = default
        else:
            default = self[key]
        return default

    def setlistdefault(self, key, default_list=None):
        """
        Like :meth:`setdefault` but sets multiple values and returns the list
        associated with the `key`.
        """
        if key not in self:
            default_list = list(default_list or (None, ))
            dict.__setitem__(self, key, default_list)
        else:
            default_list = dict.__getitem__(self, key)
        return default_list

    def items(self, multi=False):
        """
        Returns a :class:`list` of ``(key, value)`` pairs.

        :param multi:
            If ``True`` the returned :class:`list` will contain a pair for
            every value associated with a key.
        """
        return list(self.iteritems(multi))

    def lists(self):
        """
        Returns a :class:`list` of ``(key, values)`` pairs, where `values` is
        the list of values associated with the `key`.
        """
        return list(self.iterlists())

    def values(self):
        """
        Returns a :class:`list` with the first value of every key.
        """
        return [self[key] for key in self.iterkeys()]

    def listvalues(self):
        """
        Returns a :class:`list` of all values.
        """
        return list(self.iterlistvalues())

    def iteritems(self, multi=False):
        """Like :meth:`items` but returns an iterator"""
        for key, values in dict.iteritems(self):
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]

    def iterlists(self):
        """
        Like :meth:`lists` but returns an iterator.
        """
        for key, values in dict.iteritems(self):
            yield key, list(values)

    def itervalues(self):
        """Like :meth:`values` but returns an iterator."""
        for values in dict.itervalues(self):
            yield values[0]

    def iterlistvalues(self):
        """Like :meth:`listvalues` but returns an iterator."""
        return dict.itervalues(self)

    def update(self, mapping):
        """
        Extends the :class:`MultiDict` with the data from the given
        `mapping`.
        """
        for key, value in iter_multi_items(mapping):
            self.add(key, value)

    def pop(self, key, default=missing):
        """
        Returns the first value associated with the given `key` and removes
        the `key` and the associated values.
        """
        try:
            return dict.pop(self, key)[0]
        except KeyError:
            if default is not missing:
                return default
            raise

    def popitem(self):
        """
        Returns a key and the first associated value. The `key` and the
        associated values are removed.
        """
        key, values = dict.popitem(self)
        return key, values[0]

    def poplist(self, key):
        """
        Returns the :class:`list` of values associated with the given `key`,
        if the `key` does not exist in the :class:`MultiDict` an empty list is
        returned.
        """
        return dict.pop(self, key, [])

    def popitemlist(self):
        """Like :meth:`popitem` but returns all associated values."""
        return dict.popitem(self)


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
                'expected at most 1 argument, got {0}'.format(len(args))
            )
        self._root = _Link()
        self._root.prev = self._root.next = self._root
        self._map = {}
        self.update(*args, **kwargs)

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
            self[key] = default
        return self[key]

    def pop(self, key, default=missing):
        """
        Deletes the item with the given `key` and returns the value. If the
        item does not exist a :exc:`KeyError` is raised unless `default` is
        given.
        """
        if default is missing:
            return dict.pop(self, key)
        return dict.pop(self, key, default)

    def popitem(self, last=True):
        """
        Pops the last or first item from the dict depending on `last`.
        """
        if not self:
            raise KeyError('dict is empty')
        key = (reversed(self) if last else iter(self)).next()
        return key, self.pop(key)

    def update(self, *args, **kwargs):
        """
        Updates the dictionary with a mapping and/or from keyword arguments.
        """
        if len(args) > 1:
            raise TypeError(
                'expected at most 1 argument, got {0}'.format(len(args))
            )
        mappings = [args[0]] if args else []
        mappings.append(kwargs.iteritems())
        for mapping in mappings:
            for key, value in mapping:
                self[key] = value

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
        return iter(self)

    def itervalues(self):
        """
        Returns an iterator over the values of all items in insertion order.
        """
        return (self[k] for k in self)

    def iteritems(self):
        """
        Returns an iterator over all the items in insertion order.
        """
        return izip(self.iterkeys(), self.itervalues())

    def keys(self):
        """
        Returns a :class:`list` over the keys of all items in insertion order.
        """
        return list(self.iterkeys())

    def values(self):
        """
        Returns a :class:`list` over the values of all items in insertion order.
        """
        return list(self.itervalues())

    def items(self):
        """
        Returns a :class:`list` over the items in insertion order.
        """
        return zip(self.keys(), self.values())

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.items())


class LazyList(object):
    """
    Implements a lazy list which computes items based on the given `iterable`.

    This allows you to create :class:`list`\-like objects of unlimited size.
    However although most operations don't exhaust the internal iterator
    completely some of them do, so if the given iterable is of unlimited size
    making such an operation will eventually cause a :exc:`MemoryError`.

    Cost in terms of lazyness of supported operators, this does not include
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
        if isinstance(iterable, Sequence):
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
        if index >= self.known_length:
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
        occurence of the given `object` or entirely if it is not found.
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
        return '[{0}, ...]'.format(
            ', '.join(repr(obj) for obj in self._collected_data)
        )

    del exhausting
