# coding: utf-8
"""
    brownie.caching
    ~~~~~~~~~~~~~~~

    Caching utilities.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from functools import wraps, partial

from brownie.datastructures import OrderedDict, Counter, missing


class cached_property(object):
    """
    Property which caches the result of the given `getter`.

    :param doc: Optional docstring which is used instead of the `getter`\s
                docstring.
    """
    def __init__(self, getter, doc=None):
        self.getter = getter
        self.__module__ = getter.__module__
        self.__name__ = getter.__name__
        self.__doc__ = doc or getter.__doc__

    def __get__(self, obj, type=None):
        if type is None:
            return self
        value = obj.__dict__[self.__name__] = self.getter(obj)
        return value


class CacheBase(object):
    """
    Base class for all caches, which is supposed to be used as a mixin.
    """
    @classmethod
    def decorate(cls, maxsize=float('inf')):
        """
        Returns a decorator which can be used to create functions whose
        results are cached.

        In order to clear the cache of the decorated function call `.clear()`
        on it.

        ::

            @CacheBase.decorate(maxsize=1024) # items stored in the cache
            def foo(a, b):
                return a + b # imagine a very expensive operation here
        """
        def decorator(function, _maxsize=maxsize):
            cache = cls(maxsize=maxsize)
            @wraps(function)
            def wrapper(*args, **kwargs):
                key = args
                if kwargs:
                    key += tuple(sorted(kwargs.iteritems()))
                try:
                    result = cache[key]
                except KeyError:
                    result = function(*args, **kwargs)
                    cache[key] = result
                return result
            wrapper.clear = cache.clear
            return wrapper
        return decorator


class LRUCache(OrderedDict, CacheBase):
    """
    :class:`~brownie.datastructures.OrderedDict` based cache which removes the
    least recently used item once `maxsize` is reached.

    .. note:: The order of the dict is changed each time you access the dict.
    """
    def __init__(self, mapping=(), maxsize=float('inf')):
        OrderedDict.__init__(self, mapping)
        self.maxsize = maxsize

    def __getitem__(self, key):
        self.move_to_end(key)
        return OrderedDict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if len(self) >= self.maxsize:
            self.popitem(last=False)
        OrderedDict.__setitem__(self, key, value)

    def __repr__(self):
        return '%s(%s, %f)' % (
            self.__class__.__name__, dict.__repr__(self), self.maxsize
        )


class LFUCache(dict, CacheBase):
    """
    :class:`dict` based cache which removes the least frequently used item once
    `maxsize` is reached.
    """
    def __init__(self, mapping=(), maxsize=float('inf')):
        dict.__init__(self, mapping)
        self.maxsize = maxsize
        self.usage_counter = Counter()

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        self.usage_counter[key] += 1
        return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        for key, _ in self.usage_counter.most_common(len(self) - self.maxsize):
            del self[key]

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        del self.usage_counter[key]

    def pop(self, key, default=missing):
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            if default is missing:
                raise
            return default

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def popitem(self):
        item = dict.__popitem__(self)
        del self.usage_counter[item[0]]
        return item

    def __repr__(self):
        return '%s(%s, %f)' % (
            self.__class__.__name__, dict.__repr__(self), self.maxsize
        )


#: A memoization decorator, which uses a simple dictionary of infinite size as
#: cache::
#:
#:     @memoize()
#:     def foo(a, b):
#:         return a + b
#:
#: .. versionadded:: 0.5
memoize = lambda func: type(
    '_MemoizeCache', (dict, CacheBase), {}
).decorate()(func)


__all__ = ['cached_property', 'LRUCache', 'LFUCache', 'memoize']
