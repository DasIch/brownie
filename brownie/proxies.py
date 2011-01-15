# coding: utf-8
"""
    brownie.proxies
    ~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE for details
"""
import textwrap
from functools import partial
from itertools import repeat

from brownie.itools import starmap
from brownie.datastructures import missing


CONVERSION_METHODS = frozenset([
    '__str__',     # str()
    '__unicode__', # unicode()

    '__complex__', # complex()
    '__int__',     # int()
    '__long__',    # long()
    '__float__',   # float()
    '__oct__',     # oct()
    '__hex__',     # hex()

    '__nonzero__', # truth-testing, bool()
    '__index__',   # slicing, operator.index()
    '__coerce__',  # mixed-mode numeric arithmetic
])


COMPARISON_METHODS = {
    '__lt__': '<',
    '__le__': '<=',
    '__eq__': '==',
    '__ne__': '!=',
    '__gt__': '>',
    '__ge__': '>='
}


DESCRIPTOR_METHODS = frozenset([
    '__get__',
    '__set__',
    '__delete__',
])


REGULAR_BINARY_ARITHMETIC_METHODS = frozenset([
    '__add__',
    '__sub__',
    '__mul__',
    '__div__',
    '__truediv__',
    '__floordiv__',
    '__mod__',
    '__divmod__',
    '__pow__',
    '__lshift__',
    '__rshift__',
    '__and__',
    '__xor__',
    '__or__',
])


REVERSED_ARITHMETIC_METHODS = frozenset([
    '__radd__',
    '__rsub__',
    '__rmul__',
    '__rdiv__',
    '__rtruediv__',
    '__rfloordiv__',
    '__rmod__',
    '__rdivmod__',
    '__rpow__',
    '__rlshift__',
    '__rrshift__',
    '__rand__',
    '__rxor__',
    '__ror__',
])


AUGMENTED_ASSIGNMENT_METHODS = frozenset([
    '__iadd__',
    '__isub__',
    '__imul__',
    '__idiv__',
    '__itruediv__'
    '__ifloordiv__',
    '__imod__',
    '__ipow__',
    '__ipow__',
    '__ilshift__',
    '__rlshift__',
    '__iand__',
    '__ixor__',
    '__ior__',
])


BINARY_ARITHMETHIC_METHODS = (
    REGULAR_BINARY_ARITHMETIC_METHODS |
    REVERSED_ARITHMETIC_METHODS |
    AUGMENTED_ASSIGNMENT_METHODS
)


UNARY_ARITHMETHIC_METHODS = frozenset([
    '__neg__',   # -
    '__pos__',   # +
    '__abs__',   # abs()
    '__invert__' # ~
])


CONTAINER_METHODS = frozenset([
    '__len__',      # len()
    '__getitem__',  # ...[]
    '__setitem__',  # ...[] = ...
    '__delitem__',  # del ...[]
    '__iter__',     # iter()
    '__reversed__', # reversed()
    '__contains__'  # ... in ...
])


SLICING_METHODS = frozenset([
    '__getslice__',
    '__setslice__',
    '__delslice__',
])


TYPECHECK_METHODS = frozenset([
    '__instancecheck__', # isinstance()
    '__issubclass__',    # issubclass()
])


CONTEXT_MANAGER_METHODS = frozenset([
    '__enter__',
    '__exit__'
])

UNGROUPABLE_METHODS = frozenset([
    # special comparison
    '__cmp__', # cmp()

    # hashability, required if ==/!= are implemented
    '__hash__', # hash()

    '__call__', # ...()
])


#: All special methods with exception of :meth:`__new__` and :meth:`__init__`.
SPECIAL_METHODS = frozenset().union(
    CONVERSION_METHODS,
    COMPARISON_METHODS,
    DESCRIPTOR_METHODS,
    BINARY_ARITHMETHIC_METHODS,
    UNARY_ARITHMETHIC_METHODS,
    CONTAINER_METHODS,
    SLICING_METHODS,
    TYPECHECK_METHODS,
    CONTEXT_MANAGER_METHODS,
    UNGROUPABLE_METHODS
)


class ProxyMeta(type):
    def _set_private(self, name, obj):
        setattr(self, '_ProxyBase__' + name, obj)

    def method(self, handler):
        self._set_private('method_handler', handler)

    def getattr(self, handler):
        self._set_private('getattr_handler', handler)

    def setattr(self, handler):
        self._set_private('setattr_handler', handler)

    def repr(self, repr_handler):
        self._set_private('repr_handler', repr_handler)


class ProxyBase(object):
    def __init__(self, proxied):
        self.__proxied = proxied

    def __method_handler(self, proxied, name, *args, **kwargs):
        return missing

    def __getattr_handler(self, proxied, name):
        return getattr(proxied, name)

    def __setattr_handler(self, proxied, name, obj):
        return setattr(proxied, name, obj)

    def __repr_handler(self, proxied):
        return repr(proxied)

    def __getattribute__(self, name):
        if name.startswith('_ProxyBase__'):
            return object.__getattribute__(self, name)
        return self.__getattr_handler(self.__proxied, name)

    def __setattr__(self, name, obj):
        if name.startswith('_ProxyBase__'):
            return object.__setattr__(self, name, obj)
        return self.__setattr_handler(self.__proxied, name, obj)

    def __repr__(self):
        return self.__repr_handler(self.__proxied)

    # the special methods we implemented so far (for special cases)
    implemented = set()

    # we need to special case comparision methods due to the fact that
    # if we implement __lt__ and call it on the proxied object it might fail
    # because the proxied object implements __cmp__ instead.
    method_template = textwrap.dedent("""
        def %(name)s(self, other):
            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied, '%(name)s', other
            )
            if result is missing:
                return self._ProxyBase__proxied %(operator)s other
    """)

    for method, operator in COMPARISON_METHODS.iteritems():
        exec(method_template % dict(name=method, operator=operator))
    implemented.update(COMPARISON_METHODS)
    del operator


    method_template = textwrap.dedent("""
        def %(name)s(self, *args, **kwargs):
            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied, '%(name)s', *args, **kwargs
            )
            if result is missing:
                return self._ProxyBase__proxied.%(name)s(*args, **kwargs)
            return result
    """)
    for method in SPECIAL_METHODS - implemented:
        method = method_template % dict(name=method)
        exec(method)
    del method_template, method, implemented


def make_proxy_class(name, doc=None):
    """
    Creates a generic proxy class like :class:`ProxyClass` with the given `name`
    and `doc` as it's docstring.

    .. class:: .ProxyClass(proxied)

       .. classmethod:: method(handler)

          Decorator which takes a `handler` which gets called with the
          `proxied` object, the name of the called special method, positional
          and keyword arguments of the called method. If the handler returns
          :data:`brownie.datastructures.missing` the special method is called,
          to achieve the usual behaviour.

       .. classmethod:: getattr(handler)

          Decorator which takes a `handler` which gets called with the
          `proxied` object and the name of the accessed attribute.

       .. classmethod:: setattr(handler)

          Decorator which takes a `handler` which gets called with the
          `proxied` object, the name of the attribute which is set and the
          object it is set with.

       .. classmethod:: repr(handler)

          Decorator which takes a `handler` which gets called with the
          `proxied` object and is supposed to return a representation of the
          object per default ``repr(proxied)`` is returned.

    .. warning::

        At the moment there are several issues:

        - When checking the type of a :class:`ProxyClass` instance using
          :class:`type()` the :class:`ProxyClass` will be returned.

        - Especially with built-in objects this may yield otherwise unexpected
          results such as ``proxy(1) + proxy(1)`` not working.
    """
    return ProxyMeta(name, (ProxyBase, ), {'__doc__': doc})
