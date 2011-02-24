# coding: utf-8
"""
    brownie.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic datastructures.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


class missing(object):
    def __nonzero__(self):
        return False

    def __repr__(self):
        return 'missing'

#: Sentinel object which can be used instead of ``None``. This is useful if
#: you have optional parameters to which a user can pass ``None`` e.g. in
#: datastructures.
missing = missing()


class StackedObject(object):
    """
    An object whose attributes are looked up in a mapping residing in an
    internal stack.

    If an attribute is accessed, the value of the first mapping, which contains
    the appropriate attribute, is returned.

    .. versionadded:: 0.6
    """
    def __init__(self, mappings):
        self.mappings = list(mappings)

    @property
    def top(self):
        """
        The top-most object.
        """
        return self.mappings[-1]

    def __getattr__(self, name):
        for mapping in reversed(self.mappings):
            try:
                return mapping[name]
            except KeyError:
                pass
        raise AttributeError(name)

    def push(self, mapping):
        """
        Pushes the given `mapping` on the stack.
        """
        self.mappings.append(mapping)

    def pop(self):
        """
        Pops the given `mapping` from the stack.

        If the stack is empty a :exc:`RuntimeError` is raised.
        """
        try:
            self.mappings.pop()
        except IndexError:
            raise RuntimeError('stack is empty')

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.mappings)


__all__ = [
    'missing', 'iter_multi_items', 'MultiDict', 'OrderedDict', 'Counter',
    'OrderedMultiDict', 'ImmutableDict', 'ImmutableMultiDict',
    'ImmutableOrderedDict', 'ImmutableOrderedMultiDict', 'CombinedDict',
    'CombinedMultiDict', 'LazyList', 'OrderedSet', 'SetQueue', 'namedtuple',
    'FixedDict', 'PeekableIterator', 'StackedObject'
]

# circular imports
from brownie.datastructures.sets import *
from brownie.datastructures.queues import *
from brownie.datastructures.mappings import *
from brownie.datastructures.sequences import *
from brownie.datastructures.iterators import *
