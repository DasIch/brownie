# coding: utf-8
"""
    brownie.tests.proxies
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, TestBase, test, Assert

from brownie.proxies import as_proxy
from brownie.datastructures import missing


class TestMakeProxyClass(TestBase):
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


tests = Tests([TestMakeProxyClass])
