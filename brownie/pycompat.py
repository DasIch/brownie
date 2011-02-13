# coding: utf-8
"""
    brownie.pycompat
    ~~~~~~~~~~~~~~~~

    Python compatibility tools

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
try:
    from functools import reduce
except ImportError:
    reduce = reduce
