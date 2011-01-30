# coding: utf-8
"""
    brownie.tests.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.datastructures.queues`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
from threading import Thread

from attest import Tests, TestBase, test, Assert

from brownie.datastructures import SetQueue


class TestSetQueue(TestBase):
    @test
    def ordering_behaviour(self):
        class QueuedItem(object):
            def __init__(self, a, b):
                self.a, self.b = a, b

            @property
            def _key(self):
                return self.a, self.b

            def __eq__(self, other):
                return self._key == other._key

            def __ne__(self, other):
                return self._key != other._key

            def __hash__(self):
                return hash(self._key)

        foo = QueuedItem('foo', 'bar')
        bar = QueuedItem('foo', 'bar')
        item_list = [
            foo,
            foo,
            foo,
            foo,
            bar,
            bar,
            foo,
            foo,
            foo,
            bar,
            bar,
            bar,
            foo,
            foo,
            foo,
            foo,
            bar,
            bar
        ]
        item_set = set(item_list)
        queue = SetQueue()
        for item in item_list:
            queue.put(item)

        def item_consumer(tasks):
            item_list = []
            while True:
                try:
                    item = tasks.get(timeout=0.2)
                    item_list.append(item)
                    tasks.task_done()
                except queue.Empty:
                    break

            Assert(len(item_list)) == 2
            Assert(set(item_list)) == item_set
            Assert(item_list[0]) == foo
            Assert(item_list[1]) == bar

        consumer = Thread(target=item_consumer, args=(queue, ))
        consumer.start()
        consumer.join()


tests = Tests([TestSetQueue])
