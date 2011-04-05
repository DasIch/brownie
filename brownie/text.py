# coding: utf-8
"""
    brownie.text
    ~~~~~~~~~~~~

    Utilities to deal with text.

    .. versionadded:: 0.6

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import unicodedata

try:
    import translitcodec
except ImportError: # pragma: no cover
    translitcodec = None


def transliterate(string, length='long'):
    """
    Returns a transliterated version of the given unicode `string`.

    By specifying `length` you can specify how many characters are used for a
    replacement:

    `long`
        Use as many characters as needed to make a natural replacement.

    `short`
        Use as few characters as possible to make a replacement.

    `one`
        Use only one character to make a replacement. If a character cannot
        be transliterated with a single character replace it with `'?'`.

    If available translitcodec_ is used, which provides more natural results.

    .. _translitcodec: http://pypi.python.org/pypi/translitcodec
    """
    if length not in ('long', 'short', 'one'):
        raise ValueError('unknown length: %r' % length)
    if translitcodec is None:
        return unicodedata.normalize('NFKD', string) \
            .encode('ascii', 'ignore') \
            .decode('ascii')
    else:
        if length == 'one':
            return string.encode('translit/one/ascii', 'replace').decode('ascii')
        return string.encode('translit/%s' % length)
