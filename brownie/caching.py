# coding: utf-8
"""
    brownie.caching
    ~~~~~~~~~~~~~~~

    Caching utilities.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from functools import wraps

from brownie.datastructures import OrderedDict


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


class LRUCache(OrderedDict):
    """
    :class:`~brownie.datastructures.OrderedDict` which removes the least
    recently used item once `maxsize` is reached.

    .. note:: The order of the dict is changed each time you access the dict.
    """
    @classmethod
    def decorate(cls, maxsize=float('inf')):
        """
        Returns a decorator which can be used to create functions whose
        results are cached using the :class:`LRUCache` with the given
        `maxsize`.

        In order to clear the cache of the decorated function call `.clear()`
        on it.
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

    def __init__(self, mapping=(), maxsize=float('inf')):
        OrderedDict.__init__(self, mapping)
        self.maxsize = maxsize

    def __getitem__(self, key):
        value = self.pop(key)
        self[key] = value
        return value

    def __setitem__(self, key, value):
        if len(self) >= self.maxsize:
            self.popitem(last=False)
        OrderedDict.__setitem__(self, key, value)

    def __repr__(self):
        return '%s(%s, %f)' % (
            self.__class__.__name__, dict.__repr__(self), self.maxsize
        )
