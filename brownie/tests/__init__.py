# coding: utf-8
"""
    brownie.tests
    ~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests


all = Tests('brownie.tests.%s.tests' % module for module in [
    'itools',
    'caching',
    'proxies',
    'abstract',
    'parallel',
    'importing',
    'functional',
    'datastructures'
])
