# coding: utf-8
"""
    brownie.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic datastructures.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


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

    def copy(self):
        """Returns a shallow copy of this object."""
        return self.__class__(self)

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
        except KeyError as err:
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
