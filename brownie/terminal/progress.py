# coding: utf-8
"""
    brownie.terminal.progress
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    A widget-based progress bar implementation.


    .. versionadded:: 0.6

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import division
import re
import math
from functools import wraps
from datetime import datetime

from brownie.caching import LFUCache
from brownie.datastructures import ImmutableDict


#: Binary prefixes, largest first.
BINARY_PREFIXES = [
    (u'Yi', 2 ** 80), # yobi
    (u'Zi', 2 ** 70), # zebi
    (u'Ei', 2 ** 60), # exbi
    (u'Pi', 2 ** 50), # pebi
    (u'Ti', 2 ** 40), # tebi
    (u'Gi', 2 ** 30), # gibi
    (u'Mi', 2 ** 20), # mebi
    (u'Ki', 2 ** 10)  # kibi
]

#: Positive SI prefixes, largest first.
SI_PREFIXES = [
    (u'Y', 10 ** 24), # yotta
    (u'Z', 10 ** 21), # zetta
    (u'E', 10 ** 18), # exa
    (u'P', 10 ** 15), # peta
    (u'T', 10 ** 12), # tera
    (u'G', 10 ** 9),  # giga
    (u'M', 10 ** 6),  # mega
    (u'k', 10 ** 3)   # kilo
]


_progressbar_re = re.compile(ur"""
    (?<!\$)\$([a-zA-Z]+) # identifier
    (:                   # initial widget value

        (?: # grouping to avoid : to be treated as part of
            # the left or operand

            "( # quoted string
                (?:
                    [^"]|    # any character except " or ...
                    (?<=\\)" # ... " preceded by a backslash
                )*
            )"|

            ([a-zA-Z]+) # identifiers can be used instead of strings
        )
    )?|
    (\$\$) # escaped $
""", re.VERBOSE)


def count_digits(n):
    if n == 0:
        return 1
    return int(math.log10(abs(n)) + (2 if n < 0 else 1))


def bytes_to_readable_format(bytes, binary=True):
    prefixes = BINARY_PREFIXES if binary else SI_PREFIXES
    for prefix, size in prefixes:
        if bytes >= size:
            result = bytes / size
            return result, prefix + 'B'
    return bytes, 'B'


def bytes_to_string(bytes, binary=True):
    """
    Provides a nice readable string representation for `bytes`.

    :param binary:
        If ``True`` uses binary prefixes otherwise SI prefixes are used.
    """
    result, prefix = bytes_to_readable_format(bytes, binary=binary)
    if isinstance(result, int) or getattr(result, 'is_integer', lambda: False)():
        return '%i%s' % (result, prefix)
    return '%.02f%s' % (result, prefix)


@LFUCache.decorate(maxsize=64)
def parse_progressbar(string):
    """
    Parses a string representing a progress bar.
    """
    def add_text(text):
        if not rv or rv[-1][0] != 'text':
            rv.append(['text', text])
        else:
            rv[-1][1] += text
    rv = []
    remaining = string
    while remaining:
        match = _progressbar_re.match(remaining)
        if match is None:
            add_text(remaining[0])
            remaining = remaining[1:]
        elif match.group(5):
            add_text(u'$')
            remaining = remaining[match.end():]
        else:
            if match.group(3) is None:
                value = match.group(4)
            else:
                value = match.group(3).decode('string-escape')
            rv.append([match.group(1), value])
            remaining = remaining[match.end():]
    return rv


class Widget(object):
    """
    Represents a part of a progress bar.
    """
    #: The priority of the widget defines in which order they are updated. The
    #: default priority is 0.
    #:
    #: This is important as the first widget being updated has the entire
    #: line available.
    priority = 0

    #: Should be ``True`` if :meth:`size_hint` returns not ``None``.
    provides_size_hint = False

    #: Should be ``True`` if this widget depends on
    #: :attr:`ProgressBar.maxsteps` being set to something other than ``None``.
    requires_fixed_size = False

    def size_hint(self, progressbar):
        """
        Should return the required size or ``None`` if it cannot be given.
        """
        return None

    def init(self, progressbar, remaining_width, **kwargs):
        """
        Called when the progress bar is initialized.

        Should return the output of the widget as string.
        """
        raise NotImplementedError('%s.init' % self.__class__.__name__)

    def update(self, progressbar, remaining_width, **kwargs):
        """
        Called when the progress bar is updated, not necessarily with each
        step.

        Should return the output of the widget as string.
        """
        raise NotImplementedError('%s.update' % self.__class__.__name__)

    def finish(self, progressbar, remaining_width, **kwargs):
        """
        Called when the progress bar is finished, not necessarily after
        maxsteps has been reached, per default this calls :meth:`update`.

        Should return the output of the widget as string.
        """
        return self.update(progressbar, remaining_width, **kwargs)

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class TextWidget(Widget):
    """
    Represents static text in a progress bar.
    """
    provides_size_hint = True

    def __init__(self, text):
        self.text = text

    def size_hint(self, progressbar):
        return len(self.text)

    def update(self, progressbar, remaining_width, **kwargs):
        return self.text

    init = update

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.text)


class HintWidget(Widget):
    """
    Represents a 'hint', changing text passed with each update, in a progress
    bar.

    Requires that :meth:`ProgressBar.next` is called with a `hint` keyword
    argument.

    This widget has a priority of 2.
    """
    priority = 2

    def __init__(self, initial_hint=u''):
        self.initial_hint = initial_hint

    def init(self, progressbar, remaining_width, **kwargs):
        return self.initial_hint

    def update(self, progressbar, remaining_width, **kwargs):
        try:
            return kwargs.get('hint', u'')
        except KeyError:
            raise TypeError("expected 'hint' as a keyword argument")

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.initial_hint)


class PercentageWidget(Widget):
    """
    Represents a string showing the progress as percentage.
    """
    provides_size_hint = True
    requires_fixed_size = True

    def calculate_percentage(self, progressbar):
        return 100 / progressbar.maxsteps * progressbar.step

    def size_hint(self, progressbar):
        return count_digits(self.calculate_percentage(progressbar)) + 1

    def init(self, progressbar, remaining_width, **kwargs):
        return '0%'

    def update(self, progressbar, remaining_width, **kwargs):
        return '%i%%' % self.calculate_percentage(progressbar)

    def finish(self, progressbar, remaining_width, **kwargs):
        return '100%'


class BarWidget(Widget):
    """
    A simple bar which moves with each update not corresponding with the
    progress being made.

    The bar is enclosed in brackets, progress is visualized by tree hashes
    `###` moving forwards or backwards with each update; the rest of the bar is
    filled with dots `.`.

    This widget has a priority of 1.
    """
    priority = 1

    def __init__(self):
        self.position = 0
        self.going_forward = True

    def make_bar(self, width):
        parts = ['.'] * (width - 2)
        parts[self.position:self.position+3] = '###'
        return '[%s]' % ''.join(parts)

    def init(self, progressbar, remaining_width, **kwargs):
        return self.make_bar(remaining_width)

    def update(self, progressbar, remaining_width, **kwargs):
        width = remaining_width - 2
        if (self.position + 3) > width:
            self.position = width - 4
            self.going_forward = False
        elif self.going_forward:
            self.position += 1
            if self.position + 3 == width:
                self.going_forward = False
        else:
            self.position -= 1
            if self.position == 0:
                self.going_forward = True
        return self.make_bar(remaining_width)


class PercentageBarWidget(Widget):
    """
    A simple bar which shows the progress in terms of a bar being filled
    corresponding to the percentage of progress.

    The bar is enclosed in brackets, progress is visualized with hashes `#`
    the remaining part uses dots `.`.

    This widget has a priority of 1.
    """
    priority = 1
    requires_fixed_size = True

    def init(self, progressbar, remaining_width, **kwargs):
        return '[%s]' % ('.' * (remaining_width - 2))

    def update(self, progressbar, remaining_width, **kwargs):
        percentage = 100 / progressbar.maxsteps * progressbar.step
        marked_width = int(percentage * (remaining_width - 2) / 100)
        return '[%s]' % ('#' * marked_width).ljust(remaining_width - 2, '.')

    def finish(self, progressbar, remaining_width, **kwargs):
        return '[%s]' % ('#' * (remaining_width - 2))


class StepWidget(Widget):
    """
    Shows at which step we are currently at and how many are remaining as
    `step of steps`.

    :param unit:
        If each step represents something other than a simple task e.g. a byte
        when doing file transactions, you can specify a unit which is used.

    Supported units:

    - `'bytes'` - binary prefix only, SI might be added in the future
    """
    provides_size_hint = True
    requires_fixed_size = True
    units = ImmutableDict({
        'bytes': bytes_to_string,
        None: unicode
    })

    def __init__(self, unit=None):
        if unit not in self.units:
            raise ValueError('unknown unit: %s' % unit)
        self.unit = unit

    def get_values(self, progressbar):
        convert = self.units[self.unit]
        return convert(progressbar.step), convert(progressbar.maxsteps)

    def size_hint(self, progressbar):
        step, maxsteps = self.get_values(progressbar)
        return len(step) + len(maxsteps) + 4 # ' of '

    def init(self, progressbar, remaining_width, **kwargs):
        return u'%s of %s' % self.get_values(progressbar)

    update = init


class TimeWidget(Widget):
    """
    Shows the elapsed time in hours, minutes and seconds as
    ``$hours:$minutes:$seconds``.

    This widget has a priority of 3.
    """
    priority = 3

    def init(self, progressbar, remaining_width, **kwargs):
        self.start_time = datetime.now()
        return '00:00:00'

    def update(self, progressbar, remaining_width, **kwargs):
        seconds = (datetime.now() - self.start_time).seconds
        minutes = 0
        hours = 0

        minute = 60
        hour = minute * 60

        if seconds > hour:
            hours, seconds = divmod(seconds, hour)
        if seconds > minute:
            minutes, seconds = divmod(seconds, minute)

        return '%02i:%02i:%02i' % (hours, minutes, seconds)


class DataTransferSpeedWidget(Widget):
    """
    Shows the data transfer speed in bytes per second using SI prefixes.

    This widget has a priority of 3.
    """
    priority = 3

    def init(self, progressbar, remaining_width, **kwargs):
        self.begin_timing = datetime.now()
        self.last_step = 0
        return '0kb/s'

    def update(self, progressbar, remaining_width, **kwargs):
        end_timing = datetime.now()
        # .seconds is an integer so our calculations result in 0 if each update
        # takes less than a second, therefore we have to calculate the exact
        # time in seconds
        elapsed = (end_timing - self.begin_timing).microseconds * 10 ** -6
        step = progressbar.step - self.last_step
        if elapsed == 0:
            result = '%.02f%s/s' % bytes_to_readable_format(0, binary=False)
        else:
            result = '%.02f%s/s' % bytes_to_readable_format(
                step / elapsed,
                binary=False
            )
        self.begin_timing = end_timing
        self.last_step = progressbar.step
        return result


class ProgressBar(object):
    """
    A progress bar which acts as a container for various widgets which may be
    part of a progress bar.

    Initializing and finishing can be done by using the progress bar as a
    context manager instead of calling :meth:`init` and :meth:`finish`.

    :param widgets:
        An iterable of widgets which should be used.

    :param writer:
        A :class:`~brownie.terminal.TerminalWriter` which is used by the
        progress bar.

    :param maxsteps:
        The number of steps, not necessarily updates, which are to be made.
    """
    @classmethod
    def from_string(cls, string, writer, maxsteps=None, widgets=None):
        """
        Returns a :class:`ProgressBar` from a string.

        The string is used as a progressbar, ``$[a-zA-Z]+`` is substituted with
        a widget as defined by `widgets`.

        ``$`` can be escaped with another ``$`` e.g. ``$$foo`` will not be
        substituted.

        Initial values as required for the :class:`HintWidget` are given like
        this ``$hint:initial``, if the initial value is supposed to contain a
        space you have to use a quoted string ``$hint:"foo bar"``; quoted can
        be escaped using a backslash.

        If you want to provide your own widgets or overwrite existing ones
        pass a dictionary mapping the desired names to the widget classes to
        this method using the `widgets` keyword argument. The default widgets
        are:

        +--------------+----------------------------------+-------------------+
        | Name         | Class                            | Requires maxsteps |
        +==============+==================================+===================+
        | `text`       | :class:`TextWidget`              | No                |
        +--------------+----------------------------------+-------------------+
        | `hint`       | :class:`HintWidget`              | No                |
        +--------------+----------------------------------+-------------------+
        | `percentage` | :class:`Percentage`              | Yes               |
        +--------------+----------------------------------+-------------------+
        | `bar`        | :class:`BarWidget`               | No                |
        +--------------+----------------------------------+-------------------+
        | `sizedbar`   | :class:`PercentageBarWidget`     | Yes               |
        +--------------+----------------------------------+-------------------+
        | `step`       | :class:`StepWidget`              | Yes               |
        +--------------+----------------------------------+-------------------+
        | `time`       | :class:`TimeWidget`              | No                |
        +--------------+----------------------------------+-------------------+
        | `speed`      | :class:`DataTransferSpeedWidget` | No                |
        +--------------+----------------------------------+-------------------+
        """
        default_widgets = {
            'text': TextWidget,
            'hint': HintWidget,
            'percentage': PercentageWidget,
            'bar': BarWidget,
            'sizedbar': PercentageBarWidget,
            'step': StepWidget,
            'time': TimeWidget,
            'speed': DataTransferSpeedWidget
        }
        widgets = dict(default_widgets.copy(), **(widgets or {}))
        rv = []
        for name, initial in parse_progressbar(string):
            if name not in widgets:
                raise ValueError('widget not found: %s' % name)
            if initial:
                widget = widgets[name](initial)
            else:
                widget = widgets[name]()
            rv.append(widget)
        return cls(rv, writer, maxsteps=maxsteps)

    def __init__(self, widgets, writer, maxsteps=None):
        widgets = list(widgets)
        if maxsteps is None:
            for widget in widgets:
                if widget.requires_fixed_size:
                    raise ValueError(
                        '%r requires maxsteps to be given' % widget
                    )

        self.widgets = widgets
        self.writer = writer
        self.maxsteps = maxsteps
        self.step = 0

    def get_step(self):
        return self._step

    def set_step(self, new_step):
        if self.maxsteps is None or new_step <= self.maxsteps:
            self._step = new_step
        else:
            raise ValueError('step cannot be larger than maxsteps')

    step = property(get_step, set_step)
    del get_step, set_step

    def __iter__(self):
        return self

    def get_widgets_by_priority(self):
        """
        Returns an iterable of tuples consisting of the position of the widget
        and the widget itself ordered by each widgets priority.
        """
        return sorted(
            enumerate(self.widgets),
            key=lambda x: x[1].priority,
            reverse=True
        )

    def get_usable_width(self):
        """
        Returns the width usable by all widgets which don't provide a size
        hint.
        """
        return self.writer.get_usable_width() - sum(
            widget.size_hint(self) for widget in self.widgets
            if widget.provides_size_hint
        )

    def write(self, string, update=True):
        if update:
            self.writer.write('\r', escape=False, flush=False)
        self.writer.begin_line()
        self.writer.write(string)

    def make_writer(updating=True, finishing=False):
        def decorate(func):
            @wraps(func)
            def wrapper(self, **kwargs):
                if finishing and self.step == self.maxsteps:
                    return
                if updating and not finishing:
                    self.step += kwargs.get('step', 1)
                parts = []
                remaining_width = self.get_usable_width()
                for i, widget in self.get_widgets_by_priority():
                    part = func(self, widget, remaining_width, **kwargs)
                    if not widget.provides_size_hint:
                        remaining_width -= len(part)
                    parts.append((i, part))
                parts.sort()
                self.write(''.join(part for _, part in parts), update=updating)
                if finishing:
                    self.writer.newline()
            return wrapper
        return decorate

    @make_writer(updating=False)
    def init(self, widget, remaining_width, **kwargs):
        """
        Writes the initial progress bar to the terminal.
        """
        return widget.init(self, remaining_width, **kwargs)

    @make_writer()
    def next(self, widget, remaining_width, step=1, **kwargs):
        """
        Writes an updated version of the progress bar to the terminal.

        If the update corresponds to multiple steps, pass the number of steps
        which have been made as an argument. If `step` is larger than
        `maxsteps` a :exc:`ValueError` is raised.
        """
        return widget.update(self, remaining_width, **kwargs)

    @make_writer(finishing=True)
    def finish(self, widget, remaining_width, **kwargs):
        """
        Writes the finished version of the progress bar to the terminal.

        This method may be called even if `maxsteps` has not been reached or
        has not been defined.
        """
        return widget.finish(self, remaining_width, **kwargs)

    del make_writer

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, etype, evalue, traceback):
        if etype is None:
            self.finish()

    def __repr__(self):
        return '%s(%r, %r, maxsteps=%r)' % (
            self.__class__.__name__, self.widgets, self.writer, self.maxsteps
        )


__all__ = [
    'ProgressBar', 'TextWidget', 'HintWidget', 'PercentageWidget', 'BarWidget',
    'PercentageBarWidget', 'StepWidget', 'TimeWidget', 'DataTransferSpeedWidget'
]
