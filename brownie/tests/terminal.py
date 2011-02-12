# coding: utf-8
"""
    brownie.tests.terminal
    ~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.terminal`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import sys
import codecs
from StringIO import StringIO

from brownie.terminal import TerminalWriter

from attest import Tests, TestBase, test, Assert


class TestTerminalWriter(TestBase):
    def __context__(self):
        self.stream = codecs.getwriter('utf-8')(StringIO())
        self.writer = TerminalWriter(self.stream)
        yield
        del self.stream, self.writer

    @test
    def from_bytestream(self):
        # detect encoding from stream
        stream = StringIO()
        stream.encoding = 'utf-8'
        writer = TerminalWriter.from_bytestream(stream)
        with Assert.not_raising(UnicodeEncodeError):
            writer.writeline(u'äöü')
        Assert(stream.getvalue()) == u'äöü\n'.encode(stream.encoding)

        # use given encoding
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(stream, encoding='ascii')
        writer.writeline(u'foo')
        with Assert.raises(UnicodeEncodeError):
            writer.writeline(u'äöü')
        Assert(stream.getvalue()) == 'foo\n'

        # use given encoding with ignore error policy
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(
            stream, encoding='ascii', errors='ignore'
        )
        writer.writeline(u'fooäöübar')
        Assert(stream.getvalue()) == 'foobar\n'

        # use given encoding with replace error policy
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(
            stream, encoding='ascii', errors='replace'
        )
        writer.writeline(u'fooäöübar')
        Assert(stream.getvalue()) == 'foo???bar\n'

        # fallback to sys.getdefaultencoding
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(stream)
        Assert(sys.getdefaultencoding()) == 'ascii'
        with Assert.raises(UnicodeEncodeError):
            writer.writeline(u'äöü')

    @test
    def init(self):
        Assert(self.writer.stream) == self.stream
        Assert(self.writer.prefix) == u''
        Assert(self.writer.indent_string) == u'\t'

    @test
    def indent(self):
        self.writer.indent()
        Assert(self.writer.prefix) == self.writer.indent_string
        self.writer.writeline(u'foobar')
        Assert(self.stream.getvalue()) == u'\tfoobar\n'

    @test
    def dedent(self):
        self.writer.indent()
        Assert(self.writer.prefix) == self.writer.indent_string
        self.writer.dedent()
        Assert(self.writer.prefix) == u''
        self.writer.writeline(u'foobar')
        Assert(self.stream.getvalue()) == u'foobar\n'

    @test
    def indentation(self):
        self.writer.writeline(u'foo')
        with self.writer.indentation():
            self.writer.writeline(u'bar')
        self.writer.writeline(u'baz')
        Assert(self.stream.getvalue()) == u'foo\n\tbar\nbaz\n'

    @test
    def write(self):
        self.writer.write(u'foo')
        Assert(self.stream.getvalue()) == u'foo'

    @test
    def writeline(self):
        self.writer.writeline(u'foo')
        Assert(self.stream.getvalue()) == u'foo\n'

    @test
    def writelines(self):
        self.writer.writelines(u'foo bar baz'.split())
        Assert(self.stream.getvalue()) == u'foo\nbar\nbaz\n'

    @test
    def repr(self):
        Assert(repr(self.writer)) == 'TerminalWriter(%r, prefix=%r, indent=%r)' % (
            self.stream, self.writer.prefix, self.writer.indent_string
        )


tests = Tests([TestTerminalWriter])
