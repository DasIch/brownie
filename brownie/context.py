# coding: utf-8
"""
    brownie.context
    ~~~~~~~~~~~~~~~

    Utilities to deal with context managers.

    .. versionadded:: 0.6

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import thread
import threading
from operator import itemgetter
from itertools import count

from brownie.caching import LFUCache


def _make_stack_methods(name, lockname, stackname):
    def push(self, obj):
        """
        Pushes the given object onto the %s stack.
        """
        with getattr(self, lockname):
            self._add_object(getattr(self, stackname), obj)
            self._cache.clear()

    def pop(self):
        """
        Pops and returns an object from the %s stack.
        """
        with getattr(self, lockname):
            stack = self._get_stack(getattr(self, stackname))
            if stack is None:
                raise RuntimeError('no objects on stack')
            self._cache.clear()
            return stack.pop()[1]

    push.__name__ = 'push_' + name
    push.__doc__ = push.__doc__ % name
    pop.__name__ = 'pop_' + name
    pop.__doc__ = pop.__doc__ % name
    return push, pop


class ContextStackManagerBase(object):
    """
    Helper which manages context dependant stacks.

    A common API pattern is using context managers to change options; those
    options are internally stored on a stack.

    However larger applications have multiple execution contexts such as
    processes, threads and/or coroutines/greenthreads and such an API becomes
    a problem as each modification of the stack becomes visible to every
    execution context.

    This helper allows you to make stack operations local to the current
    execution context, ensuring that the stack remains the same in other
    contexts unless you want it to change there.

    As applications tend to have very different requirements and use different
    contexts each is implemented in a separate mixin, this way it easily
    possible to create a `ContextStackManager` for your needs.

    Assuming your application uses threads and eventlet for greenthreads you
    would create a `ContextStackManager` like this::

        class ContextStackManager(
                ContextStackManagerEventletMixin,
                ContextStackManagerThreadMixin,
                ContextStackManagerBase
            ):
            pass

    Greenthreads are executed in a thread, whereas threads are executed in
    the application thread (handled by the base class) this is why
    `ContextStackManager` inherits from these classes exactly in this order.

    Currently available mixins are:

    - :class:`ContextStackManagerThreadMixin`
    - :class:`ContextStackManagerEventletMixin`
    """
    def __init__(self, _object_cache_maxsize=256):
        self._application_stack = []
        self._cache = LFUCache(maxsize=_object_cache_maxsize)
        self._contexts = []
        self._stackop = count().next

    def _get_ident(self):
        return ()

    def _make_item(self, obj):
        return self._stackop(), obj

    def _get_objects(self, index):
        return getattr(self._contexts[index], 'objects', None)

    def _add_object(self, index, obj):
        item = self._make_item(obj)
        objects = self._get_objects(index)
        if objects is None:
            self._contexts[index].objects = [item]
        else:
            objects.append(item)

    def iter_current_stack(self):
        """
        Returns an iterator over the items in the 'current' stack, ordered
        from top to bottom.
        """
        ident = self._get_ident()
        objects = self._cache.get(ident)
        if objects is None:
            objects = self._application_stack[:]
            for context in self._contexts:
                objects.extend(getattr(context, 'objects', ()))
            objects.reverse()
            self._cache[ident] = objects = map(itemgetter(1), objects)
        return iter(objects)

    def push_application(self, obj):
        """
        Pushes the given object onto the application stack.
        """
        self._application_stack.append(self._make_item(obj))
        self._cache.clear()

    def pop_application(self):
        """
        Pops and returns an object from the application stack.
        """
        if not self._application_stack:
            raise RuntimeError('no objects on application stack')
        self._cache.clear()
        return self._application_stack.pop()[1]


class ContextStackManagerThreadMixin(object):
    """
    A :class:`ContextStackManagerBase` mixin providing thread context support.
    """
    def __init__(self, *args, **kwargs):
        super(ContextStackManagerThreadMixin, self).__init__(*args, **kwargs)
        self._contexts.append(threading.local())
        self._thread_stack = len(self._contexts) - 1
        self._thread_lock = threading.Lock()

    def _get_ident(self):
        return super(
            ContextStackManagerThreadMixin,
            self
        )._get_ident() + (thread.get_ident(), )

    push_thread, pop_thread = _make_stack_methods(
        'thread', '_thread_lock', '_thread_stack'
    )


class ContextStackManagerEventletMixin(object):
    """
    A :class:`ContextStackManagerBase` mixin providing coroutine/greenthread
    context support using eventlet_.

    .. _eventlet: http://eventlet.net
    """
    def __init__(self, *args, **kwargs):
        super(ContextStackManagerEventletMixin, self).__init__(*args, **kwargs)
        from eventlet.corolocal import local
        from eventlet.semaphore import BoundedSemaphore
        self._contexts.append(local())
        self._coroutine_stack = len(self._contexts) - 1
        self._coroutine_lock = BoundedSemaphore()

    def _get_ident(self):
        from eventlet.corolocal import get_ident
        return super(
            ContextStackManagerEventletMixin,
            self
        )._get_ident() + (get_ident(), )

    push_coroutine, pop_coroutine = _make_stack_methods(
        'coroutine', '_coroutine_lock', '_coroutine_stack'
    )


__all__ = [
    'ContextStackManagerBase', 'ContextStackManagerThreadMixin',
    'ContextStackManagerEventletMixin'
]
