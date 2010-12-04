# coding: utf-8
"""
    tests
    ~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests

from tests.itools import itools_tests
from tests.caching import caching_tests
from tests.functional import functional_tests
from tests.datastructures import datastructures_tests


all_tests = Tests([
    itools_tests, caching_tests, functional_tests, datastructures_tests
])
