# coding: utf-8
"""
    brownie.caching
    ~~~~~~~~~~~~~~~

    Caching utilities.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


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
