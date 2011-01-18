# coding: utf-8
"""
    brownie.tests.proxies
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from attest import Tests, TestBase, test, test_if, Assert

from brownie.proxies import as_proxy, get_wrapped, LazyProxy
from brownie.datastructures import missing


GE_PYTHON_26 = sys.version_info >= (2, 6)


tests = Tests()


class TestAsProxy(TestBase):
    @test
    def default_repr(self):
        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        Assert(repr(proxy_cls(1))) == '1'

    @test
    def setting_repr(self):
        class FooProxy(object):
            def repr(self, proxied):
                return 'FooProxy(%s)' % repr(proxied)
        FooProxy = as_proxy(FooProxy)

        p = FooProxy(1)
        Assert(repr(p)) == 'FooProxy(1)'

    @test
    def default_attribute_handling(self):
        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))

        class Foo(object):
            a = 1

        proxy = proxy_cls(Foo())
        Assert(proxy.a) == 1
        proxy.a = 2
        Assert(proxy.a) == 2

    @test
    def attribute_handling(self):
        getattr_access = []
        setattr_access = []

        class FooProxy(object):
            def getattr(self, proxied, name):
                getattr_access.append(name)
                return getattr(proxied, name)

            def setattr(self, proxied, name, obj):
                setattr_access.append((name, obj))
                return setattr(proxied, name, obj)

        FooProxy = as_proxy(FooProxy)

        class Foo(object):
            a = 1

        proxy = FooProxy(Foo())
        Assert(proxy.a) == 1
        proxy.a = 2
        Assert(getattr_access) == ['a']
        Assert(setattr_access) == [('a', 2)]

    @test
    def default_special_method_handling(self):
        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        proxy = proxy_cls(1)
        Assert(proxy + 1) == 2

    @test
    def special_method_handling(self):
        def simple_method_handler(
                    self, proxied, name, get_result, *args, **kwargs
                ):
            method_calls.append((name, args, kwargs))
            return missing

        def advanced_method_handler(
                    self, proxied, name, get_result, *args, **kwargs
                ):
            method_calls.append((name, args, kwargs))
            return get_result(proxied, *args, **kwargs)

        for handler in [simple_method_handler, advanced_method_handler]:
            class FooProxy(object):
                method = handler
            FooProxy = as_proxy(FooProxy)
            method_calls = []

            proxy = FooProxy(1)
            Assert(proxy + 1) == 2
            Assert(proxy - 1) == 0
            Assert(proxy * 1) == 1
            Assert(proxy / 1) == 1
            Assert(proxy < 1) == False
            Assert(method_calls) == [
                ('__add__', (1, ), {}),
                ('__sub__', (1, ), {}),
                ('__mul__', (1, ), {}),
                ('__div__', (1, ), {}),
                ('__lt__', (1, ), {})
            ]

    @test
    def proper_wrapping(self):
        class FooProxy(object):
            """A little bit of documentation."""
        proxy_cls = as_proxy(FooProxy)
        Assert(proxy_cls.__name__) == FooProxy.__name__
        Assert(proxy_cls.__module__) == FooProxy.__module__
        Assert(proxy_cls.__doc__) == FooProxy.__doc__

    @test
    def forcing(self):
        func = lambda: 1

        class FooProxy(object):
            def method(self, proxied, name, get_result, *args, **kwargs):
                return get_result(proxied(), *args, **kwargs)

            def force(self, proxied):
                return proxied()
        FooProxy = as_proxy(FooProxy)

        proxy = FooProxy(func)
        Assert(proxy + proxy) == 2

        a = FooProxy(lambda: 1)
        b = FooProxy(lambda: 2)
        Assert(a - b) == -1
        Assert(b - a) == 1

    @test
    def getattr_not_called_on_method(self):
        getattr_access = []
        method_access = []

        class FooProxy(object):
            def method(self, proxied, name, get_result, *args, **kwargs):
                method_access.append(name)
                return get_result(proxied, *args, **kwargs)

            def getattr(self, proxied, name):
                getattr_access.append(name)
                return getattr(proxied, name)
        FooProxy = as_proxy(FooProxy)

        class Foo(object):
            spam = 1

            def __add__(self, other):
                return None

        p = FooProxy(Foo())
        p.spam
        p + p
        Assert(method_access) == ['__add__']
        Assert(getattr_access) == ['spam']

    @test
    def nonzero_via_len(self):
        class Foo(object):
            def __len__(self):
                return 0

        class Bar(object):
            def __len__(self):
                return 1

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        assert not proxy_cls(Foo())
        assert proxy_cls(Bar())

    @test
    def getitem_based_iteration(self):
        class Foo(object):
            def __getitem__(self, key):
                if key >= 3:
                    raise IndexError(key)
                return key
        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        proxy = proxy_cls(Foo())
        Assert(list(proxy)) == [0, 1, 2]

    @test
    def reversed(self):
        class Foo(object):
            def __getitem__(self, key):
                if key >= 3:
                    raise IndexError(key)
                return key

            def __len__(self):
                return 3

        class Bar(object):
            def __reversed__(self):
                yield 2
                yield 1
                yield 0

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        Assert(list(reversed(proxy_cls(Foo())))) == [2, 1, 0]
        Assert(list(reversed(proxy_cls(Bar())))) == [2, 1, 0]

    @test
    def contains(self):
        class Foo(object):
            def __getitem__(self, key):
                if key >= 3:
                    raise IndexError(key)
                return key

        class Bar(object):
            def __iter__(self):
                yield 0
                yield 1
                yield 2

        class Baz(object):
            def __contains__(self, other):
                return other in (0, 1, 2)

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        for cls in (Foo, Bar, Baz):
            for i in xrange(3):
                assert i in proxy_cls(cls())

    @test
    def getslice(self):
        class Foo(object):
            def __getitem__(self, key):
                return [0, 1, 2][key]

            def __len__(self):
                return 3

        class Bar(object):
            def __getslice__(self, i, j):
                return [0, 1, 2][i:j]

            def __len__(self):
                return 3

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        a = proxy_cls(Foo())
        b = proxy_cls(Bar())
        Assert(a[:]) == b[:] == [0, 1, 2]
        Assert(a[1:]) == b[1:] == [1, 2]
        Assert(a[1:-1]) == b[1:-1] == [2]
        Assert(a[:-1]) == b[:-1] == [0, 1]

    @test
    def setslice(self):
        class Foo(object):
            def __init__(self):
                self.sequence = [0, 1, 2]

            def __eq__(self, other):
                if isinstance(other, list):
                    return self.sequence == other
                return self.sequence == other.sequence

            def __ne__(self, other):
                return self.sequence != other.sequence

            __hash__ = None

            def __len__(self):
                return len(self.sequence)

            def __repr__(self):
                return repr(self.sequence)

        class Bar(Foo):
            def __setitem__(self, key, value):
                self.sequence[key] = value

        class Baz(Foo):
            def __setslice__(self, i, j, value):
                self.sequence[i:j] = value

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        make_proxies = lambda: (proxy_cls(Bar()), proxy_cls(Baz()))

        a, b = make_proxies()
        a[:] = b[:] = 'abc'
        Assert(a) == b == ['a', 'b', 'c']

        a, b = make_proxies()
        a[1:] = b[1:] = 'bc'
        Assert(a) == b == [0, 'b', 'c']

        a, b = make_proxies()
        a[1:-1] = b[1:-1] = ['b']
        Assert(a) == b == [0, 'b', 2]

        a, b = make_proxies()
        a[:-1] = b[:-1] = ['a', 'b']
        Assert(a) == b == ['a', 'b', 2]

    @test
    def delslice(self):
        class Foo(object):
            def __init__(self):
                self.sequence = [0, 1, 2]

            def __eq__(self, other):
                if isinstance(other, list):
                    return self.sequence == other
                return self.sequence == other.sequence

            def __ne__(self, other):
                return self.sequence != other.sequence

            __hash__ = None

            def __len__(self):
                return len(self.sequence)

            def __repr__(self):
                return repr(self.sequence)

        class Bar(Foo):
            def __delitem__(self, key):
                del self.sequence[key]

        class Baz(Foo):
            def __delslice__(self, i, j):
                del self.sequence[i:j]

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        make_proxies = lambda: (proxy_cls(Bar()), proxy_cls(Baz()))

        a, b = make_proxies()
        del a[:]
        del b[:]
        Assert(a) == b == []

        a, b = make_proxies()
        del a[1:]
        del b[1:]
        Assert(a) == b == [0]

        a, b = make_proxies()
        del a[1:-1]
        del b[1:-1]
        Assert(a) == b == [0, 2]

        a, b = make_proxies()
        del a[:-1]
        del b[:-1]
        Assert(a) == b == [2]

    @test_if(GE_PYTHON_26)
    def dir(self):
        class Foo(object):
            bar = None

            def spam(self):
                pass

            def eggs(self):
                pass

        proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
        Assert(dir(Foo)) == dir(proxy_cls(Foo))


tests.register(TestAsProxy)


@tests.test
def test_get_wrapped():
    proxy_cls = as_proxy(type('FooProxy', (object, ), {}))
    wrapped = 1
    Assert(get_wrapped(proxy_cls(wrapped))).is_(wrapped)


class TestLazyProxy(TestBase):
    @test
    def special(self):
        p = LazyProxy(lambda: 1)
        Assert(p + p) == 2
        Assert(p + 1) == 2
        Assert(1 + p) == 2

    @test
    def getattr(self):
        p = LazyProxy(int)
        Assert(p).imag = 0.0

    @test
    def setattr(self):
        class Foo(object): pass
        foo = Foo()
        p = LazyProxy(lambda: foo)
        p.a = 1
        Assert(p.a) == 1
        Assert(foo.a) == 1

    @test
    def repr(self):
        p = LazyProxy(int)
        Assert(repr(p)) == 'LazyProxy(%r)' % int


tests.register(TestLazyProxy)
