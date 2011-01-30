# coding: utf-8
"""
    brownie.datastructures.sets
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from functools import wraps

from brownie.itools import chain
from brownie.datastructures.mappings import OrderedDict


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


__all__ = ['OrderedSet']
