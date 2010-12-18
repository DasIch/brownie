.. module:: brownie.datastructures

Datastructures
==============

This module provides various datastructures.

.. autodata:: missing

Mappings
--------

.. autofunction:: iter_multi_items

.. autoclass:: MultiDict
   :members: add, getlist, setlist, setlistdefault, lists, listvalues,
             iterlists, iterlistvalues, poplist, popitemlist

.. autoclass:: OrderedDict
   :members: popitem

.. autoclass:: Counter
   :members:

.. autoclass:: OrderedMultiDict
   :members:

Immutable Mappings
------------------

.. autoclass:: ImmutableDict
   :members:

.. autoclass:: ImmutableMultiDict
   :members:

.. autoclass:: ImmutableOrderedMultiDict
   :members:

Sequences
---------

.. autoclass:: LazyList
   :members: factory, count, insert, pop, remove, reverse, sort
