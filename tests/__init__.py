# coding: utf-8
"""
    tests
    ~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests

from tests.caching import caching_tests
from tests.datastructures import datastructures_tests


all_tests = Tests([caching_tests, datastructures_tests])
