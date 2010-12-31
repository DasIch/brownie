# coding: utf-8
"""
    tests.abstract
    ~~~~~~~~~~~~~~

    Tests for mod:`brownie.abstract`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from attest import Tests

from brownie.abstract import VirtualSubclassMeta


GE_PYTHON_26 = sys.version_info >= (2, 6)


abstract_tests = Tests()

@abstract_tests.test_if(GE_PYTHON_26)
def test_virtual_subclass_meta():
    from abc import ABCMeta

    class A(object):
        __metaclass__ = ABCMeta


    class B(object):
        __metaclass__ = ABCMeta


    class C(object):
        __metaclass__ = VirtualSubclassMeta
        virtual_superclasses = [A, B]

    assert issubclass(C, A)
    assert issubclass(C, B)
    assert isinstance(C(), A)
    assert isinstance(C(), B)
