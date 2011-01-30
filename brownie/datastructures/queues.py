# coding: utf-8
"""
    brownie.datastructures.queues
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import Queue as queue


class SetQueue(queue.Queue):
    """Thread-safe implementation of an ordered set queue, which coalesces
    duplicate items into a single item if the older occurrence has not yet been
    read and maintains the order of items in the queue.

    Ordered set queues are useful when implementing data structures like
    event buses or event queues where duplicate events need to be coalesced
    into a single event. An example use case is the inotify API in the Linux
    kernel which shares the same behaviour.

    Queued items must be immutable and hashable so that they can be used as
    dictionary keys or added to sets. Items must have only read-only properties
    and must implement the :meth:`__hash__`, :meth:`__eq__`, and :meth:`__ne__`
    methods to be hashable.

    An example item class implementation follows::

        class QueuedItem(object):
            def __init__(self, a, b):
                self._a = a
                self._b = b

            @property
            def a(self):
                return self._a

            @property
            def b(self):
                return self._b

            def _key(self):
                return (self._a, self._b)

            def __eq__(self, item):
                return self._key() == item._key()

            def __ne__(self, item):
                return self._key() != item._key()

            def __hash__(self):
                return hash(self._key())

    .. NOTE::
        This ordered set queue leverages locking already present in the
        :class:`queue.Queue` class redefining only internal primitives. The
        order of items is maintained because the internal queue is not replaced.
        An internal set is used merely to check for the existence of an item in
        the queue.

    .. versionadded:: 0.3

    :author: Gora Khargosh <gora.khargosh@gmail.com>
    :author: Lukáš Lalinský <lalinsky@gmail.com>
    """
    def _init(self, maxsize):
        queue.Queue._init(self, maxsize)
        self._set_of_items = set()

    def _put(self, item):
        if item not in self._set_of_items:
            queue.Queue._put(self, item)
            self._set_of_items.add(item)

    def _get(self):
        item = queue.Queue._get(self)
        self._set_of_items.remove(item)
        return item


__all__ = ['SetQueue']
