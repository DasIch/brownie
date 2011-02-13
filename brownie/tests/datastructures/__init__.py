# coding: utf-8
"""
    brownie.tests.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import missing
from brownie.tests.datastructures import (sets, queues, sequences, mappings,
                                          iterators)


class TestMissing(TestBase):
    @test
    def has_false_boolean_value(self):
        if missing:
            raise AssertionError()

    @test
    def repr(self):
        Assert(repr(missing)) == 'missing'


tests = Tests([
    TestMissing, queues.tests, sets.tests, sequences.tests, mappings.tests,
    iterators.tests
])
