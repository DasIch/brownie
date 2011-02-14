# coding: utf-8
"""
    brownie.tests.terminal
    ~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.terminal`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import os
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
        Assert(self.writer.autoescape) == True
        Assert(self.writer.ignore_options) == True

        stream = StringIO()
        stream.isatty = lambda: True
        writer = TerminalWriter.from_bytestream(stream)
        Assert(writer.ignore_options) == False
        writer = TerminalWriter.from_bytestream(stream, ignore_options=True)
        Assert(writer.ignore_options) == True

        stream = StringIO()
        writer = TerminalWriter.from_bytestream(stream)
        Assert(writer.ignore_options) == True
        writer = TerminalWriter.from_bytestream(stream, ignore_options=False)
        Assert(writer.ignore_options) == False

    @test
    def get_dimensions(self):
        with Assert.raises(NotImplementedError):
            self.writer.get_dimensions()
        writer = TerminalWriter.from_bytestream(sys.__stdout__)
        with Assert.not_raising(NotImplementedError):
            dimensions = writer.get_dimensions()
        height, width = dimensions
        Assert.isinstance(height, int)
        Assert.isinstance(width, int)
        Assert(height) == dimensions.height
        Assert(width) == dimensions.width

    @test
    def get_width(self):
        with Assert.not_raising(Exception):
            self.writer.get_width()
        writer = TerminalWriter.from_bytestream(sys.__stdout__)
        Assert(writer.get_width()) == writer.get_dimensions()[1]

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

        self.stream = StringIO()
        self.writer = TerminalWriter.from_bytestream(self.stream)
        try:
            with self.writer.indentation():
                self.writer.writeline(u'foo')
                raise Exception() # arbitary exception
        except Exception:
            self.writer.writeline(u'bar')
        Assert(self.stream.getvalue()) == '\tfoo\nbar\n'

    @test
    def line(self):
        with self.writer.line():
            self.writer.write(u'foo')
            Assert(self.stream.getvalue()) == 'foo'
        Assert(self.stream.getvalue()) == 'foo\n'

        self.stream = StringIO()
        self.writer = TerminalWriter.from_bytestream(self.stream)
        try:
            with self.writer.line():
                self.writer.write(u'foo')
                raise Exception()
        except Exception:
            self.writer.writeline(u'bar')
        Assert(self.stream.getvalue()) == 'foo\nbar\n'

    @test
    def escaping(self):
        with self.writer.escaping(False):
            self.writer.writeline(u'\x1b[31mfoo')
            with self.writer.escaping(True):
                self.writer.writeline(u'\x1b[31mbar')
            self.writer.writeline(u'\x1b[31mbaz')
        self.writer.writeline(u'\x1b[31mspam')
        Assert(self.stream.getvalue()) == '\n'.join([
            '\x1b[31mfoo',
            '\\x1b[31mbar',
            '\x1b[31mbaz',
            '\\x1b[31mspam\n'
        ])

    @test
    def should_escape(self):
        Assert(self.writer.should_escape(None)) == True
        Assert(self.writer.should_escape(True)) == True
        Assert(self.writer.should_escape(False)) == False

        writer = TerminalWriter(self.stream, autoescape=False)
        Assert(writer.should_escape(None)) == False
        Assert(writer.should_escape(True)) == True
        Assert(writer.should_escape(False)) == False

    @test
    def write(self):
        self.writer.write(u'foo')
        Assert(self.stream.getvalue()) == u'foo'

    @test
    def write_escaped(self):
        self.writer.write(u'\x1b[31mfoo')
        Assert(self.stream.getvalue()) == '\\x1b[31mfoo'

    @test
    def writeline(self):
        self.writer.writeline(u'foo')
        Assert(self.stream.getvalue()) == u'foo\n'

    @test
    def writeline_escaped(self):
        self.writer.writeline(u'\x1b[31mfoo')
        Assert(self.stream.getvalue()) == '\\x1b[31mfoo\n'

    @test
    def writelines(self):
        self.writer.writelines(u'foo bar baz'.split())
        Assert(self.stream.getvalue()) == u'foo\nbar\nbaz\n'

    @test
    def writelines_escaped(self):
        self.writer.writelines(
            u'\x1b[31m' + line for line in u'foo bar baz'.split()
        )
        Assert(self.stream.getvalue()) == '\n'.join([
            '\\x1b[31mfoo',
            '\\x1b[31mbar',
            '\\x1b[31mbaz\n'
        ])

    @test
    def repr(self):
        Assert(repr(self.writer)) == ('TerminalWriter('
            '%r, '
            'prefix=%r, '
            'indent=%r, '
            'autoescape=%r'
            ')'
        ) % (
            self.stream, self.writer.prefix, self.writer.indent_string,
            self.writer.autoescape
        )


tests = Tests([TestTerminalWriter])
