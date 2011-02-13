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


__all__ = [
    'missing', 'iter_multi_items', 'MultiDict', 'OrderedDict', 'Counter',
    'OrderedMultiDict', 'ImmutableDict', 'ImmutableMultiDict',
    'ImmutableOrderedDict', 'ImmutableOrderedMultiDict', 'CombinedDict',
    'CombinedMultiDict', 'LazyList', 'OrderedSet', 'SetQueue', 'namedtuple',
    'FixedDict', 'PeekableIterator'
]

# circular imports
from brownie.datastructures.sets import *
from brownie.datastructures.queues import *
from brownie.datastructures.mappings import *
from brownie.datastructures.sequences import *
from brownie.datastructures.iterators import *
