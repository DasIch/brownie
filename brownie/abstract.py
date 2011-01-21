# coding: utf-8
"""
    brownie.abstract
    ~~~~~~~~~~~~~~~~

    Utilities to deal with abstract base classes.

    .. versionadded:: 0.2

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
try:
    from abc import ABCMeta
except ImportError:
    class ABCMeta(type):
        """Dummy :class:`abc.ABCMeta` implementation which does nothing."""

        def register(self, subclass):
            pass


class VirtualSubclassMeta(type):
    """
    A metaclass which allows you to easily define abstract super classes,
    simply inherit from this metaclass and set the
    :attr:`virtual_superclasses` attribute to an iterable:

        >>> from brownie.abstract import ABCMeta, VirtualSubclassMeta
        >>>
        >>> class VirtualBaseClass(object):
        ...     __metaclass__ = ABCMeta
        >>>
        >>> class VirtualSubclass(object):
        ...     __metaclass__ = VirtualSubclassMeta
        ...
        ...     virtual_superclasses = (VirtualBaseClass, )
        >>>
        >>> issubclass(VirtualSubclass, VirtualBaseClass)
        True
    """
    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        self._register_superclasses(attributes.get('virtual_superclasses', ()))

    def _register_superclasses(self, superclasses):
        for cls in superclasses:
            if isinstance(cls, ABCMeta):
                cls.register(self)
            if hasattr(cls, 'virtual_superclasses'):
                self._register_superclasses(cls.virtual_superclasses)


class AbstractClassMeta(ABCMeta, VirtualSubclassMeta):
    """
    A metaclass for abstract base classes which are also virtual subclasses.

    Simply set :attr:`virtual_subclasses` to an iterable of classes your class
    is supposed to virtually inherit from:

    >>> from brownie.abstract import ABCMeta, AbstractClassMeta, \\
    ...                              VirtualSubclassMeta
    >>> class Foo(object):
    ...     __metaclass__ = ABCMeta
    >>>
    >>> class Bar(object):
    ...     __metaclass__ = AbstractClassMeta
    ...
    ...     virtual_superclasses = (Foo, )
    >>>
    >>> class Baz(object):
    ...     __metaclass__ = VirtualSubclassMeta
    ...
    ...     virtual_superclasses = (Bar, )
    >>>
    >>> issubclass(Baz, Foo)
    True
    >>> issubclass(Baz, Bar)
    True

    .. note::
        All classes could use :class:`AbstractClassMeta` as `__metaclass__`
        and the result would be the same, the usage here is just to demonstrate
        the specific problem which is solved.
    """


__all__ = ['ABCMeta', 'VirtualSubclassMeta', 'AbstractClassMeta']
