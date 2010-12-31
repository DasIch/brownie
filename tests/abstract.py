# coding: utf-8
"""
    tests.abstract
    ~~~~~~~~~~~~~~

    Tests for mod:`brownie.abstract`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from attest import Tests, TestBase, test_if, test

from brownie.itools import product
from brownie.abstract import VirtualSubclassMeta, ABCMeta


GE_PYTHON_26 = sys.version_info >= (2, 6)


abstract_tests = Tests()

@abstract_tests.test_if(GE_PYTHON_26)
def test_virtual_subclass_meta():
    from abc import ABCMeta

    class Foo(object):
        __metaclass__ = ABCMeta


    class Bar(object):
        __metaclass__ = ABCMeta


    class Simple(object):
        __metaclass__ = VirtualSubclassMeta
        virtual_superclasses = [Foo, Bar]

    class InheritingSimple(Simple):
        pass

    for a, b in product([Simple, InheritingSimple], [Foo, Bar]):
        assert issubclass(a, b)
        assert isinstance(a(), b)

    assert issubclass(InheritingSimple, Simple)
    assert isinstance(InheritingSimple(), Simple)

    class Spam(object):
        __metaclass__ = ABCMeta

    class Eggs(object):
        __metaclass__ = ABCMeta

    class SimpleMonty(object):
        __metaclass__ = VirtualSubclassMeta
        virtual_superclasses = [Spam, Eggs]

    class MultiInheritance(Simple, SimpleMonty):
        pass

    class MultiVirtualInheritance(object):
        __metaclass__ = VirtualSubclassMeta
        virtual_superclasses = [Simple, SimpleMonty]

    for virtual_super_cls in [Foo, Bar, Simple, Spam, Eggs, SimpleMonty]:
        assert issubclass(MultiInheritance, virtual_super_cls)
        assert isinstance(MultiInheritance(), virtual_super_cls)


class TestABCMeta(TestBase):
    @test_if(GE_PYTHON_26)
    def type_checks_work(self):
        class Foo(object):
            __metaclass__ = ABCMeta

        class Bar(object):
            pass

        Foo.register(Bar)

        assert issubclass(Bar, Foo)
        assert isinstance(Bar(), Foo)

    @test
    def api_works_cleanly(self):
        class Foo(object):
            __metaclass__ = ABCMeta

        class Bar(object):
            pass

        Foo.register(Bar)


abstract_tests.register(TestABCMeta)
