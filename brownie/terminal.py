# coding: utf-8
"""
    brownie.terminal
    ~~~~~~~~~~~~~~~~

    Utilities for handling simple output on a terminal.


    .. versionadded:: 0.6

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import re
import sys
import codecs
try:
    import termios
except ImportError:
    termios = None
from contextlib import contextmanager


_ansi_sequence = '\033[%sm'


ATTRIBUTES = dict((key, _ansi_sequence % value) for key, value in [
    ('reset','00'),
    ('bold',  '01'),
    ('faint', '02'),
    ('standout', '03'),
    ('underline', '04'),
    ('blink', '05')
])
TEXT_COLOURS = {'reset': _ansi_sequence % '39'}
BACKGROUND_COLOURS = {'reset': _ansi_sequence % '49'}
_colour_names = [
    ('black',      'darkgrey'),
    ('darkred',    'red'),
    ('darkgreen',  'green'),
    ('darkyellow', 'yellow'),
    ('darkblue',   'blue'),
    ('purple',     'fuchsia'),
    ('turquoise',  'teal'),
    ('lightgray',  'white')
]
for i, (dark, light) in enumerate(_colour_names):
    TEXT_COLOURS[dark] = _ansi_sequence % str(i + 30)
    TEXT_COLOURS[light] = _ansi_sequence % ('%i;01' % (i + 30))

    BACKGROUND_COLOURS[dark] = _ansi_sequence % str(i + 40)
    BACKGROUND_COLOURS[light] = _ansi_sequence % ('%i;01' % (i + 40))


class TerminalWriter(object):
    """
    This is a helper for dealing with output to a terminal.

    :param stream:
        A stream which takes unicode for writing.

    :param prefix:
        A prefix used when an entire line is written.

    :param indent:
        String used for indentation.

    :param autoescape:
        Defines if everything written is escaped (unless explicitly turned
        off), see :func:`escape` for more information.
    """
    @classmethod
    def from_bytestream(cls, stream, encoding=None, errors='strict', **kwargs):
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
        return cls(codecs.lookup(encoding).streamwriter(stream, errors), **kwargs)

    def __init__(self, stream, prefix=u'', indent='\t', autoescape=True):
        #: The stream to which the output is written.
        self.stream = stream
        #: The current prefix, includes indentation.
        self.prefix = prefix
        #: The string used for indentation.
        self.indent_string = indent
        #: ``True`` if escaping should be done automatically.
        self.autoescape = autoescape

        self.optionstack = []

        if getattr(stream, 'istty', lambda: False)() and termios:
            self.control_characters = [
                unicode(c) for c in termios.tcgetattr(stream)[-1]
                if isinstance(c, basestring)
            ]
        else:
            # just to be on the safe side...
            self.control_characters = map(chr, range(32) + [127])
        self.ansi_re = re.compile(u'[%s]' % ''.join(self.control_characters))

    def escape(self, string):
        """
        Escapes all control characters in the given `string`.

        This is useful if you are dealing with 'untrusted' strings you want to
        write to a file, stdout or stderr which may be viewed using tools such
        as `cat` which execute ANSI escape sequences.

        .. seealso::

           http://www.ush.it/team/ush/hack_httpd_escape/adv.txt
        """
        return self.ansi_re.sub(
            lambda m: m.group().encode('unicode-escape'),
            string
        )

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

    def _get_options(self, kwargs):
        result = {}
        text_colour = kwargs.pop('text_colour', None)
        background_colour = kwargs.pop('background_colour', None)
        try:
            if text_colour:
                result['text_colour'] = TEXT_COLOURS[text_colour]
            if background_colour:
                result['background_colour'] = BACKGROUND_COLOURS[background_colour]
        except KeyError, exc:
            raise ValueError(*exc.args)
        if kwargs:
            used = []
            attributes = []
            for attr in kwargs:
                if attr in ATTRIBUTES:
                    attributes.append(ATTRIBUTES[attr])
                    used.append(attr)
            for attribute in used:
                kwargs.pop(attribute)
            result['attributes'] = attributes
        return result

    @contextmanager
    def options(self, **kwargs):
        """
        A contextmanager which allows you to set certain text properties for
        body.

        Works only on terminals which implement ANSI escape sequences.

        :param text_colour:
            The desired text colour.

        :param background_colour:
            The desired background colour.

        :param bold:
            If present the text is displayed bold.

        :param faint:
            If present the text is displayed faint.

        :param standout:
            If present the text stands out.

        :param blink:
            If present the text blinks.

        .. note::
           The properties supported depend on the terminal, especially the
           attributes (`bold`, `faint`, `standout` and `blink`) are not
           necessarily available.

        The following colours are available, the exact colour varies between
        terminals and their configuration.

        .. ansi-block::
           :string_escape:

           Dark       Light
           ====       =====
           \x1b[30mblack\x1b[0m      \x1b[30;01mdarkgrey\x1b[0m
           \x1b[31mdarkred\x1b[0m    \x1b[31;01mred\x1b[0m
           \x1b[32mdarkgreen\x1b[0m  \x1b[32;01mgreen\x1b[0m
           \x1b[33mdarkyellow\x1b[0m \x1b[33;01myellow\x1b[0m
           \x1b[34mdarkblue\x1b[0m   \x1b[34;01mblue\x1b[0m
           \x1b[35mpurple\x1b[0m     \x1b[35;01mfuchsia\x1b[0m
           \x1b[36mturquoise\x1b[0m  \x1b[36;01mteal\x1b[0m
           \x1b[37mlightgray\x1b[0m  \x1b[37;01mwhite\x1b[0m
        """
        options = self._get_options(kwargs)
        if kwargs:
            raise TypeError('got unexpected argument')
        self.optionstack.append(options)
        self.apply_options(**options)
        try:
            yield self
        finally:
            self.reset_options(**options)
            self.optionstack.pop()
            if self.optionstack:
                self.apply_options(**self.optionstack[-1])

    def apply_options(self, text_colour=None, background_colour=None, attributes=()):
        if text_colour:
            self.stream.write(text_colour)
        if background_colour:
            self.stream.write(background_colour)
        for attribute in attributes:
            self.stream.write(attribute)

    def reset_options(self, text_colour=None, background_colour=None, attributes=None):
        if text_colour:
            self.stream.write(TEXT_COLOURS['reset'])
        if background_colour:
            self.stream.write(BACKGROUND_COLOURS['reset'])
        if attributes:
            self.stream.write(ATTRIBUTES['reset'])

    @contextmanager
    def line(self):
        """
        A contextmanager which writes a newline to the :attr:`stream` after
        the body is executed.

        This is useful if you want to write a line with multiple different options.
        """
        try:
            yield
        finally:
            self.stream.write(u'\n')

    @contextmanager
    def escaping(self, shall_escape):
        """
        A contextmanager which lets you change the escaping behaviour for the block.
        """
        previous_setting = self.autoescape
        self.autoescape = shall_escape
        try:
            yield self
        finally:
            self.autoescape = previous_setting

    def should_escape(self, escape):
        """
        Returns :attr:`autoescape` if `escape` is None otherwise `escape`.
        """
        return self.autoescape if escape is None else escape

    def write(self, string, escape=None, **options):
        """
        Writes the `given` string to the :attr:`stream`.

        :param escape:
            Overrides :attr:`autoescape` if given.

        :param options:
            Options for this operation, see :meth:`options`.
        """
        with self.options(**options):
            self.stream.write(
                self.escape(string) if self.should_escape(escape) else string
            )

    def writeline(self, line, escape=None, **options):
        """
        Writes the given `line` to the :attr:`stream` respecting indentation.

        :param escape:
            Overrides :attr:`autoescape` if given.

        :param options:
            Options for this operation, see :meth:`options`.
        """
        with self.options(**options):
            self.write(
                self.prefix + (
                    self.escape(line) if self.should_escape(escape) else line
                ) + u'\n',
                escape=False
            )

    def writelines(self, lines, escape=None, **options):
        """
        Writes each line in the given iterable to the :attr:`stream` respecting
        indentation.

        :param escape:
            Overrides :attr:`autoescape` if given.

        :param options:
            Options for this operation, see :meth:`options`.
        """
        with self.options(**options):
            for line in lines:
                self.writeline(line, escape=escape)

    def __repr__(self):
        return '%s(%r, prefix=%r, indent=%r, autoescape=%r)' % (
            self.__class__.__name__, self.stream, self.prefix,
            self.indent_string, self.autoescape
        )


def main():
    writer = TerminalWriter.from_bytestream(sys.stdout)
    for dark, light in _colour_names:
        with writer.line():
            writer.write(light, text_colour=light)
            writer.write(' ')
            writer.write(dark, text_colour=dark)

        with writer.line():
            writer.write(light, background_colour=light)
            writer.write(' ')
            writer.write(dark, background_colour=dark)

    for name in ATTRIBUTES:
        writer.writeline(name, **{name: True})
    with writer.line():
        with writer.options(underline=True):
            writer.write('underline')
            with writer.options(background_colour='red'):
                writer.write('background')
                writer.write('text', text_colour='green')
                writer.write('background')
            writer.write('underline')

if __name__ == '__main__':
    main()
