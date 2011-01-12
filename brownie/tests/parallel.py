# coding: utf-8
"""
    brownie.tests.parallel
    ~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.parallel`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import time
from threading import Thread

from attest import Tests, Assert, TestBase, test

from brownie.parallel import get_cpu_count, AsyncResult, TimeoutError


tests = Tests()


@tests.test
def test_get_cpu_count():
    try:
        Assert(get_cpu_count()) > 0
        Assert(get_cpu_count()) == get_cpu_count()
    except NotImplementedError:
        # make sure default is returned if the number of processes cannot be
        # determined
        Assert(get_cpu_count(2)) == 2


class TestAsyncResult(TestBase):
    @test
    def wait(self):
        aresult = AsyncResult()

        def setter(aresult):
            time.sleep(1)
            aresult.set('foo')
        t = Thread(target=setter, args=(aresult, ))
        t.start()
        with Assert.not_raising(TimeoutError):
            aresult.wait(2)

    @test
    def get(self):
        aresult = AsyncResult()

        with Assert.raises(TimeoutError):
            aresult.get(0.1)

        def setter(aresult):
            time.sleep(1)
            aresult.set('foo')
        t = Thread(target=setter, args=(aresult, ))
        t.start()
        with Assert.not_raising(TimeoutError):
            Assert(aresult.get(2)) == 'foo'

        aresult.set('foo')
        Assert(aresult.get()) == 'foo'

        aresult = AsyncResult()
        aresult.set(ValueError(), success=False)
        with Assert.raises(ValueError):
            aresult.get()

    @test
    def callback_errback(self):
        testruns = (['callback', True], ['errback', False])
        for kwarg, success in testruns:
            l = []
            callback = lambda obj, l=l: l.append(obj)
            aresult = AsyncResult(**{kwarg: callback})
            assert not aresult.ready
            aresult.set('foo', success=success)
            Assert(len(l)) == 1
            Assert(l[0]) == 'foo'

    @test
    def repr(self):
        aresult = AsyncResult()
        Assert(repr(aresult)) == 'AsyncResult()'

        aresult = AsyncResult(callback=1)
        Assert(repr(aresult)) == 'AsyncResult(callback=1)'

        aresult = AsyncResult(errback=1)
        Assert(repr(aresult)) == 'AsyncResult(errback=1)'

        aresult = AsyncResult(callback=1, errback=2)
        Assert(repr(aresult)) == 'AsyncResult(callback=1, errback=2)'

tests.register(TestAsyncResult)
