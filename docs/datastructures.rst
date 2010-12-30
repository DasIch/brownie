.. module:: brownie.datastructures

Datastructures
==============

This module provides various datastructures.

.. autodata:: missing

.. autofunction:: iter_multi_items

Mappings
--------

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

Combining Mappings
------------------

.. autoclass:: CombinedDict
   :members:

.. autoclass:: CombinedMultiDict
   :members:

Sequences
---------

.. autoclass:: LazyList
   :members: factory, count, insert, pop, remove, reverse, sort


Sets
----

.. autoclass:: OrderedSet
   :members:
