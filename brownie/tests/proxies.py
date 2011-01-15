# coding: utf-8
"""
    brownie.tests.proxies
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, TestBase, test, Assert

from brownie.proxies import make_proxy_class
from brownie.datastructures import missing


class TestMakeProxyClass(TestBase):
    @test
    def default_repr(self):
        proxy_class = make_proxy_class('FooProxy')
        Assert(repr(proxy_class(1))) == '1'

    @test
    def setting_repr(self):
        proxy_cls = make_proxy_class('FooProxy')

        @proxy_cls.repr
        def __repr__(self, proxied):
            return 'FooProxy(%s)' % repr(proxied)

        p = proxy_cls(1)
        Assert(repr(p)) == 'FooProxy(1)'

    @test
    def default_attribute_handling(self):
        proxy_cls = make_proxy_class('FooProxy')

        class Foo(object):
            a = 1

        proxy = proxy_cls(Foo())
        Assert(proxy.a) == 1
        proxy.a = 2
        Assert(proxy.a) == 2

    @test
    def attribute_handling(self):
        proxy_cls = make_proxy_class('FooProxy')

        getattr_access = []
        setattr_access = []

        @proxy_cls.getattr
        def handle_getattr(self, proxied, name):
            getattr_access.append(name)
            return getattr(proxied, name)

        @proxy_cls.setattr
        def handle_setattr(self, proxied, name, obj):
            setattr_access.append((name, obj))
            return getattr(proxied, name, obj)

        class Foo(object):
            a = 1

        proxy = proxy_cls(Foo())
        Assert(proxy.a) == 1
        proxy.a = 2
        Assert(getattr_access) == ['a']
        Assert(setattr_access) == [('a', 2)]

    @test
    def default_special_method_handling(self):
        proxy_cls = make_proxy_class('FooProxy')
        proxy = proxy_cls(1)
        Assert(proxy + 1) == 2

    @test
    def special_method_handling(self):
        proxy_cls = make_proxy_class('FooProxy')
        method_calls = []

        @proxy_cls.method
        def method_handler(self, proxied, name, *args, **kwargs):
            method_calls.append((name, args, kwargs))
            return missing

        proxy = proxy_cls(1)
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


tests = Tests([TestMakeProxyClass])
