Creating Progress Bar Widgets
=============================

If you want to add a dynamic element to a progress bar you have to
implement it as a so-called widget. This guide will help you implement
one.

The :class:`~brownie.terminal.progress.Widget` Class
----------------------------------------------------

If you are going to implement your own widget, you will most likely
inherit from :class:`brownie.terminal.progress.Widget`, this class
sets some sane defaults and implements the interface a widget is expected
to have. If you are not going to inherit from it, you will have to
implement its interface so either way you might want to take a look at the
API documentation now in either case you will need it later.


Background Information
----------------------


The Basics
``````````

A progress bar is instantiated with a list of widgets, each widget
provides an interface which provides information on the widget itself, its
size and obviously methods to "render" it.

The progress bar goes through 3 stages: Before anything serious happens an
initial version is written to stdout, for this the
:meth:`~brownie.terminal.progress.Widget.init` method is called, this is
also why you want to start time measuring and similar things in this
method instead of :meth:`__init__`.

After this progress bar receives updated which each call to its
:meth:`~brownie.terminal.progress.ProgressBar.next` method, an update
represents one or more steps of progress. Such a step could correspond to
a file being processed or to a single byte of data transferred. In any
case for each update :meth:`~brownie.terminal.progress.Widget.update` is
called.

At some point, whatever operation where are doing, ends this is the case
when either :meth:`~brownie.terminal.progress.Widget.update` is called with
a progress bar whose `step` attribute is equal to it's `maxsteps`
attribute or :meth:`~bronwie.terminal.progress.Widget.finish` is called.

Now each of these methods is expected to return a string representing the
widget.


The Size
````````

A progress bar may take up only a single line of space which we want to
use wisely. Therefore each widget is called with the remaining width and
it should not use more than that, however there is no way for it to know
how much the other widgets need.

So apart from not returning a string longer than the given remaining width
there are other things you can do to make sure that the progress bar is
able to handle the widgets intelligently.

A lot of widgets know before update is called (given the number of steps)
how much space they require, if this is the case for your widget you can
implement :meth:`~brownie.terminal.progress.Widget.size_hint` so that it
returns the required size, if you do so set
:attr:`~brownie.terminal.progress.Widget.provides_size_hint` to ``True``.
This allows the progress bar to allocate the size for your widget before
any the other widgets are rendered.

If it is not possible for your widget to determine the required space, for
example because it relies on time, it can set the
:attr:`~brownie.terminal.progress.Widget.priority` attribute, this determines
in which order (highest first) the widgets are rendered and the first widget
can use most of the space.


Expectations
````````````

Your widget might have certain expectations for the progress bar, at the
moment like requiring the maximum number of steps to be known (which would
otherwise be ``None``). If your widget does set the
:attr:`~brownie.terminal.progress.Widget.requires_fixed_size` attribute to
``True``, this will result in a nice error message, for users of your
widgets, if an attempt is made to use it with a progress bar without
providing a maximum number of steps.


Tutorial
--------

After reading so much about how everything works lets make a simple
widget starting with someone really simple.

In order to represent static text a `TextWidget` is used internally, we
are going to create one just like it.

First the basics, we text is given on initialization of the widget so we
simply inherit from :class:`~brownie.terminal.progress.Widget` and
implement a :meth:`__init__` method::

    from brownie.terminal.progress import Widget

    class TextWidget(Widget):
        def __init__(self, text):
            self.text = text

In order to get the text displayed at the first stage we need to implement
:meth:`init`. The method is called with the progress bar, the remaining
width and any keyword arguments passed to the :meth:`next` method of the
progress bar::

    def init(self, progressbar, remaining_width, **kwargs):
        return self.text

The method is supposed to return a string, text is a string so we can
simply return it.

Now comes the next stage: updating. :meth:`update` is called with the same
arguments as :meth:`init` and again we simply want to display the text so
we return it::

    def update(self, progressbar, remaining_width, **kwargs):
        return self.text

As both methods have the same signature and do the same we can reduce
:meth:`update` to a simple assignment::

    update = init

We can ignore :meth:`finish` as it would do the same as :meth:`update` and
the default implementation of :meth:`finish` calls :meth:`update` and
returns the result of that call.

We want to make sure that the text is displayed and has priority over
something like a bar showing the percentage by being filled and as we know
the size of our output we can implement :meth:`size_hint` for that::

    provides_size_hint = True

    def size_hint(self, progressbar):
        return len(self.text)

So all in all our result looks like this::

    from brownie.terminal.progress import Widget

    class TextWidget(Widget):
        provides_size_hint = True

        def __init__(self, text):
            self.text = text

        def size_hint(self, progressbar):
            return len(self.text)

        def init(self, progressbar, remaining_width, **kwargs):
            return self.text

        update = init
