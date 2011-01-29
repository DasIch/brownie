# coding: utf-8
"""
    brownie.proxies
    ~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE for details
"""
import textwrap

from brownie.datastructures import missing


SIMPLE_CONVERSION_METHODS = {
    '__str__':     str,
    '__unicode__': unicode,
    '__complex__': complex,
    '__int__':     int,
    '__long__':    long,
    '__float__':   float,
    '__oct__':     oct,
    '__hex__':     hex,
    '__nonzero__': bool
}


CONVERSION_METHODS = set(SIMPLE_CONVERSION_METHODS) | frozenset([
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

SIMPLE_CONTAINER_METHODS = {
    '__len__': len,
    '__iter__': iter,
    '__reversed__': reversed
}


CONTAINER_METHODS = frozenset(SIMPLE_CONTAINER_METHODS) | frozenset([
    '__getitem__',  # ...[]
    '__setitem__',  # ...[] = ...
    '__delitem__',  # del ...[]
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
SPECIAL_METHODS = (
    CONVERSION_METHODS |
    set(COMPARISON_METHODS) |
    DESCRIPTOR_METHODS |
    BINARY_ARITHMETHIC_METHODS |
    UNARY_ARITHMETHIC_METHODS |
    CONTAINER_METHODS |
    SLICING_METHODS |
    TYPECHECK_METHODS |
    CONTEXT_MANAGER_METHODS |
    UNGROUPABLE_METHODS
)


SIMPLE_METHODS = {}
SIMPLE_METHODS.update(SIMPLE_CONVERSION_METHODS)
SIMPLE_METHODS.update(SIMPLE_CONTAINER_METHODS)


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

    def __force(self, proxied):
        return self.__proxied

    def __method_handler(self, proxied, name, get_result, *args, **kwargs):
        return missing

    def __getattr_handler(self, proxied, name):
        return getattr(proxied, name)

    def __setattr_handler(self, proxied, name, obj):
        return setattr(proxied, name, obj)

    def __repr_handler(self, proxied):
        return repr(proxied)

    def __dir__(self):
        return dir(self.__proxied)

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

    def __contains__(self, other):
        def get_result(proxied, other):
            return other in proxied
        result = self.__method_handler(self.__proxied, '__contains__', other)
        if result is missing:
            return get_result(self.__proxied, other)
        return result
    implemented.add('__contains__')

    def __getslice__(self, i, j):
        def get_result(proxied, i, j):
            return proxied[i:j]
        result = self.__method_handler(self.__proxied, '__getslice__', i, j)
        if result is missing:
            return get_result(self.__proxied, i, j)
        return result
    implemented.add('__getslice__')

    def __setslice__(self, i, j, value):
        def get_result(proxied, i, j, value):
            proxied[i:j] = value
        result = self.__method_handler(
            self.__proxied, '__setslice__', get_result, i, j, value
        )
        if result is missing:
            return get_result(self.__proxied, i, j, value)
        return result
    implemented.add('__setslice__')

    def __delslice__(self, i, j):
        def get_result(proxied, i, j):
            del proxied[i:j]
        result = self.__method_handler(
            self.__proxied, '__delslice__', get_result, i, j
        )
        if result is missing:
            return get_result(self.__proxied, i, j)
        return result
    implemented.add('__delslice__')

    # simple methods such as __complex__ are not necessarily defined like
    # other special methods, especially for built-in types by using the
    # built-in functions we achieve the desired behaviour.
    method_template = textwrap.dedent("""
        def %(name)s(self):
            def get_result(proxied):
                return %(func)s(proxied)
            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied, '%(name)s', get_result
            )
            if result is missing:
                return get_result(self._ProxyBase__proxied)
            return result
    """)
    for method, function in SIMPLE_METHODS.items():
        exec(method_template % dict(name=method, func=function.__name__))
    implemented.update(SIMPLE_METHODS)
    del function

    # we need to special case comparison methods due to the fact that
    # if we implement __lt__ and call it on the proxied object it might fail
    # because the proxied object implements __cmp__ instead.
    method_template = textwrap.dedent("""
        def %(name)s(self, other):
            def get_result(proxied, other):
                return proxied %(operator)s other
            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied, '%(name)s', get_result, other
            )
            if result is missing:
                return get_result(self._ProxyBase__proxied, other)
            return result
    """)

    for method, operator in COMPARISON_METHODS.items():
        exec(method_template % dict(name=method, operator=operator))
    implemented.update(COMPARISON_METHODS)
    del operator

    method_template = textwrap.dedent("""
        def %(name)s(self, *args, **kwargs):
            def get_result(proxied, *args, **kwargs):
                other = args[0]
                if type(self) is type(other):
                    other = other._ProxyBase__force(other._ProxyBase__proxied)
                return proxied.%(name)s(
                    *((other, ) + args[1:]), **kwargs
                )

            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied,
                '%(name)s',
                get_result,
                *args,
                **kwargs
            )
            if result is missing:
                return get_result(self._ProxyBase__proxied, *args, **kwargs)
            return result
    """)
    for method in BINARY_ARITHMETHIC_METHODS:
        exec(method_template % dict(name=method))
    implemented.update(BINARY_ARITHMETHIC_METHODS)

    method_template = textwrap.dedent("""
        def %(name)s(self, *args, **kwargs):
            def get_result(proxied, *args, **kwargs):
                return proxied.%(name)s(*args, **kwargs)
            result = self._ProxyBase__method_handler(
                self._ProxyBase__proxied, '%(name)s', get_result, *args, **kwargs
            )
            if result is missing:
                return get_result(self._ProxyBase__proxied, *args, **kwargs)
            return result
    """)
    for method in SPECIAL_METHODS - implemented:
        method = method_template % dict(name=method)
        exec(method)
    del method_template, method, implemented


def as_proxy(cls):
    '''
    Class decorator which returns a proxy based on the handlers defined in the
    given class defined as methods::

        @as_proxy
        class MyProxy(object):
            """
            This is an example proxy, every method defined is optional.
            """
            def method(self, proxied, name, get_result, *args, **kwargs):
                """
                Gets called when a special method is called on the proxy

                :param proxied:
                    The object wrapped by the proxy.

                :param name:
                    The name of the called method.

                :param get_result:
                    A function which takes `proxied`, `*args` and `**kwargs`
                    as arguments and returns the appropriate result for the
                    called method.

                :param \*args:
                    The positional arguments passed to the method.

                :param \*\*kwargs:
                    The keyword arguments passed to the method.
                """
                return missing

            def getattr(self, proxied, name):
                """
                Gets called when a 'regular' attribute is accessed.

                :param name:
                    The name of the attribute.
                """
                return getattr(proxied, name)

            def setattr(self, proxied, name, obj):
                """
                Gets called when a 'regular' attribute is set.

                :param obj:
                    The object which is set as attribute.
                """
                setattr(proxied, name, obj)

            def force(self, proxied):
                """
                Returns a 'real' version of `proxied`. This is required when
                `proxied` is something abstract like a function which returns
                an object like which the proxy is supposed to behave.

                Internally this is used when a binary operator is used with the
                proxy on the left side. Built-in types complain if we call the
                special method with the proxy given on the right side of the
                operator, therefore the proxy on the right side is 'forced'.
                """
                return proxied

            def repr(self, proxied):
                """
                Gets called for the representation of the proxy.
                """
                return repr(proxied)

        foo = MyProxy(1)
    '''
    attributes = {
        '__module__': cls.__module__,
        '__doc__': cls.__doc__
    }

    handler_name_mapping = {
        'method': '_ProxyBase__method_handler',
        'getattr': '_ProxyBase__getattr_handler',
        'setattr': '_ProxyBase__setattr_handler',
        'force': '_ProxyBase__force',
        'repr': '_ProxyBase__repr_handler'
    }

    for name, internal_name in handler_name_mapping.iteritems():
        handler = getattr(cls, name, None)
        if handler is not None:
            attributes[internal_name] = handler.im_func

    return ProxyMeta(cls.__name__, (ProxyBase, ), attributes)


def get_wrapped(proxy):
    """
    Returns the item wrapped by a given `proxy` whereas `proxy` is an instance
    of a class as returned by :func:`as_proxy`.
    """
    return proxy._ProxyBase__proxied


class LazyProxy(object):
    """
    Takes a callable and calls it every time this proxy is accessed to get an
    object which is then wrapped by this proxy::

        >>> from datetime import datetime

        >>> now = LazyProxy(datetime.utcnow)
        >>> now.second != now.second
        True
    """
    def method(self, proxied, name, get_result, *args, **kwargs):
        return get_result(proxied(), *args, **kwargs)

    def getattr(self, proxied, name):
        return getattr(proxied(), name)

    def setattr(self, proxied, name, attr):
        setattr(proxied(), name, attr)

    def force(self, proxied):
        return proxied()

    def repr(self, proxied):
        return '%s(%r)' % (type(self).__name__, proxied)


LazyProxy = as_proxy(LazyProxy)


__all__ = ['as_proxy', 'get_wrapped', 'LazyProxy']
