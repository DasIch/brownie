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
import math
from functools import wraps


def count_digits(n):
    if n == 0:
        return 1
    return int(math.log10(abs(n)) + (2 if n < 0 else 1))


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

    provides_size_hint = False

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

    def __init__(self, initial_hint):
        self.initial_hint = initial_hint

    def init(self, progressbar, remaining_width, **kwargs):
        return self.initial_hint

    def update(self, progressbar, remaining_width, **kwargs):
        try:
            return kwargs['hint']
        except KeyError:
            raise TypeError("expected 'hint' as a keyword argument")

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.initial_hint)


class PercentageWidget(Widget):
    """
    Represents a string showing the progress as percentage.
    """
    provides_size_hint = True

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

    def init(self, progressbar, remaining_width, **kwargs):
        return '[%s]' % ('.' * (remaining_width - 2))

    def update(self, progressbar, remaining_width, **kwargs):
        percentage = 100 / progressbar.maxsteps * progressbar.step
        marked_width = int(percentage * (remaining_width - 2) / 100)
        return '[%s]' % ('#' * marked_width).ljust(remaining_width - 2, '.')

    def finish(self, progressbar, remaining_width, **kwargs):
        return '[%s]' % ('#' * (remaining_width - 2))


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
    def __init__(self, widgets, writer, maxsteps=None):
        self.widgets = list(widgets)
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

    def __exit__(self, etype, evalue, traceback):
        if etype is None:
            self.finish()

    def __repr__(self):
        return '%s(%r, %r, maxsteps=%r)' % (
            self.__class__.__name__, self.widgets, self.writer, self.maxsteps
        )


__all__ = [
    'ProgressBar', 'TextWidget', 'HintWidget', 'PercentageWidget', 'BarWidget',
    'PercentageBarWidget'
]
