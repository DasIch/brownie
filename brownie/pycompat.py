# coding: utf-8
"""
    brownie.pycompat
    ~~~~~~~~~~~~~~~~

    Python compatibility tools

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
try:
    from itertools import izip, ifilter
except ImportError:
    izip = zip
    ifilter = filter
try:
    from functools import reduce
except ImportError:
    reduce = reduce
