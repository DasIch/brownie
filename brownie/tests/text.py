# coding: utf-8
"""
    brownie.tests.text
    ~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.tests`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
try:
    import translitcodec
except ImportError:
    translitcodec = None
from attest import Tests, Assert

from brownie.text import transliterate


tests = Tests()


@tests.test
def test_transliterate():
    Assert(transliterate(u'äöü', 'one')) == u'aou'

    tests = zip(
        [
            (u'©', 'long'),
            (u'©', 'short'),
            (u'☺', 'one'),
        ],
        [u''] * 3 if translitcodec is None else [u'(c)', u'c', u'?']
    )
    for args, result in tests:
        Assert(transliterate(*args)) == result
