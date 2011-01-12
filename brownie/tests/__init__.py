# coding: utf-8
"""
    brownie.tests
    ~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests

from brownie.tests.itools import itools_tests
from brownie.tests.caching import caching_tests
from brownie.tests.abstract import abstract_tests
from brownie.tests.parallel import parallel_tests
from brownie.tests.importing import importing_tests
from brownie.tests.functional import functional_tests
from brownie.tests.datastructures import datastructures_tests


all_tests = Tests([
    itools_tests, caching_tests, abstract_tests, parallel_tests,
    importing_tests, functional_tests, datastructures_tests
])
