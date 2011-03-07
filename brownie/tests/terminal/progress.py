# coding: utf-8
"""
    brownie.tests.terminal.progress
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.terminal.progress`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import time
from StringIO import StringIO

from brownie.terminal import TerminalWriter
from brownie.terminal.progress import (
    ProgressBar, Widget, TextWidget, HintWidget, PercentageWidget, BarWidget,
    PercentageBarWidget, parse_progressbar, StepWidget, bytes_to_string,
    count_digits, TimeWidget
)

from attest import Tests, TestBase, test, Assert


tests = Tests([])


@tests.test
def test_count_digits():
    Assert(count_digits(10)) == 2
    Assert(count_digits(0)) == 1
    Assert(count_digits(-10)) == 3


@tests.test
def test_bytes_to_string():
    Assert(bytes_to_string(1000)) == '1000B'
    si = bytes_to_string(1000, binary=False)
    Assert('kB').in_(si)
    Assert('1').in_(si)


@tests.test
def test_parse_progressbar():
    tests = [
        ('foobar', [['text', 'foobar']]),
        ('$foo bar', [['foo', None], ['text', ' bar']]),
        ('$foo $$bar', [['foo', None], ['text', ' $bar']]),
        ('$foo:spam bar', [['foo', 'spam'], ['text', ' bar']]),
        ('$foo:""', [['foo', '']]),
        ('$foo:"spam eggs" bar', [['foo', 'spam eggs'], ['text', ' bar']]),
        ('$foo:"spam\\" eggs" bar', [['foo', 'spam\" eggs'], ['text', ' bar']])
    ]
    for test, result in tests:
        Assert(parse_progressbar(test)) == result


class TestWidget(TestBase):
    @test
    def size_hint(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = Widget()
        assert not widget.provides_size_hint
        Assert(widget.size_hint(progressbar)).is_(None)

    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = Widget()
        with Assert.raises(NotImplementedError) as exc:
            widget.init(progressbar, writer.get_width())
        Assert(exc.args[0]) == 'Widget.init'

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = Widget()
        with Assert.raises(NotImplementedError) as exc:
            widget.update(progressbar, writer.get_width())
        Assert(exc.args[0]) == 'Widget.update'

    @test
    def finish(self):
        class MyWidget(Widget):
            update_called = False

            def update(self, writer, remaining_width, **kwargs):
                self.update_called = True

        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = MyWidget()
        widget.finish(progressbar, writer.get_width())
        assert widget.update_called

    @test
    def repr(self):
        widget = Widget()
        Assert(repr(widget)) == 'Widget()'

tests.register(TestWidget)


@tests.test
def test_text_widget():
    writer = TerminalWriter.from_bytestream(StringIO())
    progressbar = ProgressBar([], writer)
    widget = TextWidget('foobar')
    assert widget.provides_size_hint
    Assert(widget.size_hint(progressbar)) == len('foobar')
    Assert(widget.init(progressbar, writer.get_width())) == 'foobar'
    Assert(widget.update(progressbar, writer.get_width())) == 'foobar'
    Assert(widget.finish(progressbar, writer.get_width())) == 'foobar'

    Assert(repr(widget)) == "TextWidget('foobar')"


@tests.test
def test_hint_widget():
    writer = TerminalWriter.from_bytestream(StringIO())
    progressbar = ProgressBar([], writer)
    widget = HintWidget('foo')
    assert not widget.provides_size_hint
    Assert(widget.init(progressbar, writer.get_width())) == 'foo'
    Assert(widget.update(progressbar, writer.get_width(), hint='bar')) == 'bar'
    Assert(widget.update(progressbar, writer.get_width(), hint='baz')) == 'baz'
    Assert(widget.finish(progressbar, writer.get_width(), hint='spam')) == 'spam'

    Assert(repr(widget)) == "HintWidget('foo')"

    widget.finish(progressbar, writer.get_width()) == u''


class TestPercentageWidget(TestBase):
    @test
    def size_hint(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = PercentageWidget()
        assert widget.provides_size_hint
        Assert(widget.size_hint(progressbar)) == 2
        progressbar.step = 1
        Assert(widget.size_hint(progressbar)) == 2
        progressbar.step = 2
        Assert(widget.size_hint(progressbar)) == 3
        progressbar.step = 20
        Assert(widget.size_hint(progressbar)) == 4

    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=100)
        widget = PercentageWidget()
        Assert(widget.init(progressbar, writer.get_width())) == '0%'

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = PercentageWidget()
        widget.init(progressbar, writer.get_width())
        for i in xrange(5, 96, 5):
            progressbar.step += 1
            result = widget.update(progressbar, writer.get_width())
            Assert(result) == '%i%%' % i

    @test
    def finish(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=100)
        widget = PercentageWidget()
        widget.init(progressbar, writer.get_width())
        Assert(widget.finish(progressbar, writer.get_width())) == '100%'

    @test
    def repr(self):
        widget = PercentageWidget()
        Assert(repr(widget)) == 'PercentageWidget()'

tests.register(TestPercentageWidget)


class TestBarWidget(TestBase):
    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)

        widget = BarWidget()
        Assert(widget.init(progressbar, 8)) == '[###...]'

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        states = [
            '[.###..]',
            '[..###.]',
            '[...###]',
            '[..###.]',
            '[.###..]',
            '[###...]',
            '[.###..]'
        ]

        widget = BarWidget()
        for state in states:
            Assert(widget.update(progressbar, 8)) == state

        widget = BarWidget()
        widget.position = 10
        Assert(widget.update(progressbar, 8)) == '[..###.]'
        Assert(widget.update(progressbar, 8)) == '[.###..]'

tests.register(TestBarWidget)


class TestPercentageBarWidget(TestBase):
    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=10)
        widget = PercentageBarWidget()
        Assert(widget.init(progressbar, 12)) == '[..........]'

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=10)
        widget = PercentageBarWidget()
        states = [
            '[%s]' % (x + '.' * (10 - len(x))) for x in (
                '#' * i for i in xrange(1, 11)
            )
        ]
        for state in states:
            progressbar.step += 1
            Assert(widget.update(progressbar, 12)) == state

    @test
    def finish(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=10)
        widget = PercentageBarWidget()
        Assert(widget.finish(progressbar, 12)) == '[##########]'

tests.register(TestPercentageBarWidget)


class TestStepWidget(TestBase):
    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = StepWidget()
        Assert(widget.init(progressbar, writer.get_width())) == '0 of 20'
        Assert(widget.size_hint(progressbar)) == 7

        with Assert.raises(ValueError):
            StepWidget('foo')

        with Assert.not_raising(ValueError):
            StepWidget('bytes')

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = StepWidget()
        widget.init(progressbar, writer.get_width())
        for i in xrange(1, 21):
            progressbar.step += 1
            result = widget.update(progressbar, writer.get_width())
            Assert(len(result)) == widget.size_hint(progressbar)
            Assert(result) == '%i of 20' % i

    @test
    def finish(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = StepWidget()
        progressbar.step = progressbar.maxsteps
        Assert(widget.finish(progressbar, writer.get_width())) == '20 of 20'

    @test
    def units(self):
        class FooStepWidget(StepWidget):
            units = {'foo': lambda x: str(x) + 'spam'}

        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer, maxsteps=20)
        widget = FooStepWidget('foo')
        Assert(widget.init(progressbar, 100)) == '0spam of 20spam'
        progressbar.step +=1
        Assert(widget.init(progressbar, 100)) == '1spam of 20spam'
        progressbar.step = progressbar.maxsteps
        Assert(widget.finish(progressbar, 100)) == '20spam of 20spam'

tests.register(TestStepWidget)


class TestTimeWidget(TestBase):
    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = TimeWidget()
        Assert(widget.init(progressbar, 100)) == '00:00:00'

    @test
    def update(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        widget = TimeWidget()
        widget.init(progressbar, 100)
        time.sleep(1)
        Assert(widget.update(progressbar, 100)) == '00:00:01'

tests.register(TestTimeWidget)


class TestProgressBar(TestBase):
    @test
    def from_string(self):
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(stream)
        with Assert.raises(ValueError) as exc:
            ProgressBar.from_string('$foo', writer)
        Assert(exc.args[0]) == 'widget not found: foo'

        progressbar = ProgressBar.from_string(
            'hello $hint:world $percentage', writer, maxsteps=10
        )
        progressbar.init()
        progressbar.finish(hint='me')
        Assert(stream.getvalue()) == 'hello world 0%\rhello me 100%\n'

    @test
    def init(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        sized_widgets = PercentageWidget, PercentageBarWidget
        for sized in sized_widgets:
            with Assert.raises(ValueError):
                ProgressBar([sized()], writer)

    @test
    def step(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        Assert(progressbar.step) == 0
        progressbar.step = 100
        Assert(progressbar.step) == 100

        progressbar = ProgressBar([], writer, maxsteps=100)
        Assert(progressbar.step) == 0
        progressbar.step = 100
        Assert(progressbar.step) == 100
        with Assert.raises(ValueError):
            progressbar.step = 200

    @test
    def iter(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        Assert(iter(progressbar)).is_(progressbar)

    @test
    def get_widgets_by_priority(self):
        class ComparableWidget(Widget):
            def __eq__(self, other):
                return self.__class__ is other.__class__

            def __ne__(self, other):
                return not self.__eq__(other)

            __hash__ = None

        class FooWidget(ComparableWidget):
            priority = 1

        class BarWidget(ComparableWidget):
            priority = 2

        class BazWidget(ComparableWidget):
            priority = 3

        widgets = [BarWidget(), FooWidget(), BazWidget()]

        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar(widgets, writer)
        Assert(progressbar.get_widgets_by_priority()) == [
            (2, BazWidget()), (0, BarWidget()), (1, FooWidget())
        ]

    @test
    def get_usable_width(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([TextWidget('foobar')], writer)
        Assert(progressbar.get_usable_width()) == writer.get_usable_width() - 6

    @test
    def write(self):
        stream = StringIO()
        writer = TerminalWriter.from_bytestream(stream, prefix='spam')
        writer.indent()
        progressbar = ProgressBar([], writer)
        progressbar.write('foo', update=False)
        Assert(stream.getvalue()) == 'spam    foo'
        progressbar.write('bar')
        Assert(stream.getvalue()) == 'spam    foo\rspam    bar'

    @test
    def contextmanager_behaviour(self):
        class MyProgressBar(ProgressBar):
            init_called = False
            finish_called = False

            def init(self):
                self.init_called = True

            def finish(self):
                self.finish_called = True

        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = MyProgressBar([], writer)
        with progressbar as foo:
            pass
        Assert(foo).is_(progressbar)
        assert progressbar.init_called
        assert progressbar.finish_called

    @test
    def repr(self):
        writer = TerminalWriter.from_bytestream(StringIO())
        progressbar = ProgressBar([], writer)
        Assert(repr(progressbar)) == 'ProgressBar([], %r, maxsteps=None)' % writer

        progressbar = ProgressBar([], writer, maxsteps=100)
        Assert(repr(progressbar)) == 'ProgressBar([], %r, maxsteps=100)' % writer

tests.register(TestProgressBar)
