# coding: utf-8
"""
    brownie.tests.context
    ~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.context`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import time
from Queue import Queue
from threading import Thread, Event

from attest import Tests, TestBase, Assert, test, test_if

try:
    import eventlet
except ImportError:
    eventlet = None

from brownie.context import (
    ContextStackManagerBase, ContextStackManagerThreadMixin,
    ContextStackManagerEventletMixin
)


class TestContextStackManagerBase(TestBase):
    @test
    def application_context(self):
        csm = ContextStackManagerBase()
        csm.push_application('foo')
        Assert(list(csm.iter_current_stack())) == ['foo']
        csm.push_application('bar')
        Assert(list(csm.iter_current_stack())) == ['bar', 'foo']
        Assert(csm.pop_application()) == 'bar'
        Assert(csm.pop_application()) == 'foo'

        with Assert.raises(RuntimeError):
            csm.pop_application()

    @test_if(eventlet)
    def context_inheritance(self):
        class FooContextManager(
                ContextStackManagerEventletMixin,
                ContextStackManagerThreadMixin,
                ContextStackManagerBase
            ):
            pass
        csm = FooContextManager()
        csm.push_application('foo')

        def foo(csm, queue):
            csm.push_thread('bar')
            queue.put(list(csm.iter_current_stack()))
            eventlet.spawn(bar, csm, queue).wait()
            queue.put(list(csm.iter_current_stack()))

        def bar(csm, queue):
            csm.push_coroutine('baz')
            queue.put(list(csm.iter_current_stack()))

        queue = Queue()
        thread = Thread(target=foo, args=(csm, queue))
        thread.start()
        Assert(queue.get()) == ['bar', 'foo']
        Assert(queue.get()) == ['baz', 'bar', 'foo']
        Assert(queue.get()) == ['bar', 'foo']
        Assert(list(csm.iter_current_stack())) == ['foo']


class ThreadContextStackManager(
        ContextStackManagerThreadMixin,
        ContextStackManagerBase
    ):
    pass


class TestContextStackManagerThreadMixin(TestBase):
    @test
    def inherits_application_stack(self):
        csm = ThreadContextStackManager()
        csm.push_application('foo')

        def foo(csm, queue):
            queue.put(list(csm.iter_current_stack()))
            csm.push_thread('bar')
            queue.put(list(csm.iter_current_stack()))

        queue = Queue()
        thread = Thread(target=foo, args=(csm, queue))
        thread.start()
        thread.join()
        Assert(queue.get()) == ['foo']
        Assert(queue.get()) == ['bar', 'foo']
        Assert(list(csm.iter_current_stack())) == ['foo']

    @test
    def multiple_thread_contexts(self):
        csm = ThreadContextStackManager()

        def make_func(name):
            def func(csm, queue, event):
                csm.push_thread(name)
                queue.put(list(csm.iter_current_stack()))
                event.wait()
            func.__name__ = name
            return func

        foo_queue = Queue()
        bar_queue = Queue()
        foo_event = Event()
        bar_event = Event()
        foo_thread = Thread(
            target=make_func('foo'), args=(csm, foo_queue, foo_event)
        )
        bar_thread = Thread(
            target=make_func('bar'), args=(csm, bar_queue, bar_event)
        )
        foo_thread.start()
        # during that time foo should have pushed an object on
        # the thread local stack
        time.sleep(1)
        bar_thread.start()
        foo_event.set()
        bar_event.set()
        Assert(foo_queue.get()) == ['foo']
        Assert(bar_queue.get()) == ['bar']
        Assert(list(csm.iter_current_stack())) == []


class EventletContextStackManager(
        ContextStackManagerEventletMixin,
        ContextStackManagerBase
    ):
    pass


class TestContextStackManagerEventletMixin(TestBase):
    @test_if(not eventlet)
    def init(self):
        with Assert.raises(RuntimeError):
            EventletContextStackManager()

    @test
    def inherits_application_stack(self):
        csm = EventletContextStackManager()
        csm.push_application('foo')

        def foo(csm, queue):
            queue.put(list(csm.iter_current_stack()))
            csm.push_coroutine('bar')
            queue.put(list(csm.iter_current_stack()))

        queue = eventlet.Queue()
        greenthread = eventlet.spawn(foo, csm, queue)
        greenthread.wait()
        Assert(queue.get()) == ['foo']
        Assert(queue.get()) == ['bar', 'foo']

    @test
    def multiple_greenthread_contexts(self):
        csm = EventletContextStackManager()

        def make_func(name):
            def func(csm, queue):
                csm.push_coroutine(name)
                queue.put(list(csm.iter_current_stack()))
            func.__name__ = name
            return func

        foo_queue = eventlet.Queue()
        bar_queue = eventlet.Queue()
        foo = eventlet.spawn(make_func('foo'), csm, foo_queue)
        bar = eventlet.spawn(make_func('bar'), csm, bar_queue)
        foo.wait()
        bar.wait()
        Assert(foo_queue.get()) == ['foo']
        Assert(bar_queue.get()) == ['bar']


tests = Tests([TestContextStackManagerBase, TestContextStackManagerThreadMixin])
if eventlet is not None:
    tests.register(TestContextStackManagerEventletMixin)
