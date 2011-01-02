.. module:: brownie.abstract

Abstract Classes
================

Utilities to deal with abstract base classes and virtual subclasses.

.. versionadded:: 0.2

.. class:: ABCMeta

   On Python 2.6 this class is actually :class:`abc.ABCMeta`, on versions
   lower than that it's simply a dummy. Which makes implementing abstract
   classes easier if you want to support Python versions which don't support
   :meth:`class.__subclasscheck__` and :meth:`class.__instancecheck__`.

.. autoclass:: VirtualSubclassMeta
   :members:

.. autoclass:: AbstractClassMeta
   :members:
