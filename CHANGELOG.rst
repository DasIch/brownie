Changelog
=========
This log contains a list of bug fixes and added, modified or even removed
features.

0.4 - [Codename to be selected]
-------------------------------
*Currently in development*

- Added Python 3.x support.
- Added :mod:`brownie.proxies`.
- Optimized :class:`brownie.datastructures.LazyList` so that the internal
  iterator is not exhausted for negative indices.

0.3.1
-----

- Fixed an issue with :meth:`brownie.datastructures.LazyList.insert`,
  which caused the internal stream not to be exhausted when used with
  negative indexes.

  Thanks to Trundle_ for the report and patch.

.. _Trundle: https://github.com/Trundle

0.3 - Tomte
-----------

- Added :class:`brownie.datastructures.SetQueue`.

0.2.2
-----

- Expose wrapper for :func:`multiprocessing.cpu_count` instead the
  function itself which was sometimes exposed as
  :func:`brownie.parallel.get_cpu_count` because the latter is supposed
  to have a `default` parameter which :func:`multiprocessing.cpu_count`
  does not.

0.2.1
-----

- Switched theme to minimalism.
- Fixed wrong use of :rst:role:`meth` in the documentation of
  :class:`brownie.abstract.AbstractClassMeta`.
- Added example to :class:`brownie.abstract.VirtualSubclassMeta`.
- Added example to :class:`brownie.abstract.AbstractClassMeta`.

0.2 - Boggart
-------------

- Added :class:`brownie.itools.chain`.
- Added :class:`brownie.datastructures.OrderedSet`.
- Added :mod:`brownie.importing`.
- Added :class:`brownie.datastructures.CombinedDict`.
- Added :class:`brownie.datastructures.CombinedMultiDict`.
- Added :class:`brownie.datastructures.ImmutableOrderedDict`.
- Added :mod:`brownie.abstract`.
- Make type checks work for dictionaries based on interfaces and
  behaviour.

0.1.1
-----

- Fixed a :exc:`KeyError` and a :exc:`ValueError` which could occur
  by calling :func:`brownie.parallel.get_cpu_count` on Windows or Linux
  respectively.

0.1 - Fairy Land
----------------

Initial Release.
