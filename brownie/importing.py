# coding: utf-8
"""
    brownie.importing
    ~~~~~~~~~~~~~~~~~

    .. versionadded:: 0.2

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import re

_identifier_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _raise_identifier(identifier):
    if _identifier_re.match(identifier) is None:
        raise ValueError('invalid identifier: %s' % identifier)


def import_string(name):
    """
    Imports and returns an object given its `name` as a string.

    As an addition to the normal way import paths are specified you can use
    a colon to delimit the object you want to import.

    If the given name is invalid a :exc:`ValueError` is raised, if the module
    cannot be imported an :exc:`ImportError`.

    Beware of the fact that in order to import a module it is executed and
    therefore any exception could be raised, especially when dealing with
    third party code e.g. if you implement a plugin system.
    """
    if ':' in name:
        module, obj = name.split(':', 1)
    elif '.' in name:
        module, obj = name.rsplit('.', 1)
    else:
        _raise_identifier(name)
        return __import__(name)
    for identifier in module.split('.') + [obj]:
        _raise_identifier(identifier)
    return getattr(
        __import__(module, globals=None, locals=None, fromlist=[obj]),
        obj
    )


__all__ = ['import_string']
