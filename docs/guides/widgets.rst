Creating Progress Bar Widgets
=============================

If you want to add a dynamic element to a progress bar you have to
implement it as a so-called widget. This guide will give you additional
information on the topic.

The :class:`~brownie.terminal.progress.Widget` Class
----------------------------------------------------

If you are going to implement your own widget, you will most likely
inherit from :class:`brownie.terminal.progress.Widget`, this class
sets some sane defaults and implements the interface a widget is expected
to have. If you are not going to inherit from it, you will have to
implement its interface so either way you might want to take a look at the
API documentation now in either case you will need it later.


The Basics
----------

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
--------

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
------------

Your widget might have certain expectations for the progress bar, at the
moment like requiring the maximum number of steps to be known (which would
otherwise be ``None``). If your widget does set the
:attr:`~brownie.terminal.progress.Widget.requires_fixed_size` attribute to
``True``, this will result in a nice error message, for users of your
widgets, if an attempt is made to use it with a progress bar without
providing a maximum number of steps.
