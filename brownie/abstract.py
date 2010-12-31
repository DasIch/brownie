# coding: utf-8
"""
    brownie.abstract
    ~~~~~~~~~~~~~~~~

    Utilities to deal with abstract base classes.

    .. versionadded:: 0.2

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


class VirtualSubclassMeta(type):
    """
    A metaclass which allows you to easily define abstract super classes,
    simply inherit from this metaclass and set the
    :attr:`virtual_superclasses` attribute to an iterable.
    """
    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        for virtual_superclass in attributes.get('virtual_superclasses', ()):
            virtual_superclass.register(self)
