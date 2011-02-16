# coding: utf-8
"""
    brownie.datastructures.iterators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from collections import deque


class PeekableIterator(object):
    """
    An iterator which allows peeking.

    .. versionadded:: 0.6
    """
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.remaining = deque()

    def next(self):
        if self.remaining:
            return self.remaining.popleft()
        return self.iterator.next()

    def peek(self, n=1):
        """
        Returns the next `n` items without consuming the iterator, if the
        iterator has less than `n` items these are returned.

        Raises :exc:`ValueError` if `n` is lower than 1.
        """
        if n < 1:
            raise ValueError('n should be greater than 0')
        items = list(self.remaining)[:n]
        while len(items) < n:
            try:
                item = self.iterator.next()
            except StopIteration:
                break
            items.append(item)
            self.remaining.append(item)
        return items

    def __iter__(self):
        return self

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.iterator)


__all__ = ['PeekableIterator']
