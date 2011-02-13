# coding: utf-8
"""
    brownie.terminal
    ~~~~~~~~~~~~~~~~

    Utilities for handling simple output on a terminal.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys
import codecs
from contextlib import contextmanager


class TerminalWriter(object):
    """
    This is a helper for dealing with output to a terminal.

    :param stream:
        A stream which takes unicode for writing.

    :param prefix:
        A prefix used when an entire line is written.

    :param indent:
        String used for indentation.

    .. versionadded:: 0.6
    """
    @classmethod
    def from_bytestream(cls, stream, encoding=None, errors='strict'):
        """
        Returns a :class:`TerminalWriter` for the given byte `stream`.

        If an encoding cannot be determined from the stream it will fallback
        to the given `encoding`, if it is `None` :meth:`sys.getdefaultencoding`
        will be used.

        Should an error occur during encoding you can specify what should
        happen with the `errors` parameter:

        ``'strict'``
            Raise an exception if an error occurs.

        ``'ignore'``
            Ignore the characters for which the error occurs, these will be
            removed from the string.

        ``'replace'``
            Replaces the characters for which the error occurs with 'safe'
            characters, usually '?'.
        """
        encoding = getattr(stream, 'encoding', encoding)
        if encoding is None:
            encoding = sys.getdefaultencoding()
        return cls(codecs.lookup(encoding).streamwriter(stream, errors))

    def __init__(self, stream, prefix=u'', indent='\t'):
        #: The stream to which the output is written.
        self.stream = stream
        #: The current prefix, includes indentation.
        self.prefix = prefix
        #: The string used for indentation.
        self.indent_string = indent

    def indent(self):
        """
        Indent the following lines with the given :attr:`indent`.
        """
        self.prefix += self.indent_string

    def dedent(self):
        """
        Dedent the following lines.
        """
        self.prefix = self.prefix[:-len(self.indent_string)]

    @contextmanager
    def indentation(self):
        """
        Contextmanager which indents every line in the body.
        """
        self.indent()
        try:
            yield self
        finally:
            self.dedent()

    def write(self, string):
        """
        Writes the `given` string to the :attr:`stream`.
        """
        self.stream.write(string)

    def writeline(self, line):
        """
        Writes the given `line` to the :attr:`stream` respecting indentation.
        """
        self.write(self.prefix + line + '\n')

    def writelines(self, lines):
        """
        Writes each line in the given iterable to the :attr:`stream` respecting
        indentation.
        """
        for line in lines:
            self.writeline(line)

    def __repr__(self):
        return '%s(%r, prefix=%r, indent=%r)' % (
            self.__class__.__name__, self.stream, self.prefix, self.indent_string
        )
