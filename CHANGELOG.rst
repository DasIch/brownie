Changelog
=========
This log contains a list of bug fixes and added, modified or even removed
features.

0.3 - [Codename to be selected]
-------------------------------
*Currently in development*

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
