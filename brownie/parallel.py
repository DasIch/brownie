# coding: utf-8
"""
    brownie.parallel
    ~~~~~~~~~~~~~~~~

    Implements useful parallelization stuff.

    :copyright: 2010 by Daniel Neuhaeuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import os
import sys
from threading import Condition, Lock

try:
    from multiprocessing import _get_cpu_count

    def get_cpu_count(default=None):
        try:
            return _get_cpu_count()
        except NotImplementedError:
            if default is None:
                raise
            return default

except ImportError:
    def get_cpu_count(default=None):
        if sys.platform == 'win32':
            try:
                return int(os.environ['NUMBER_OF_PROCESSORS'])
            except (ValueError, KeyError):
                # value could be anything or not existing
                pass
        if sys.platform in ('bsd', 'darwin'):
            try:
                return int(os.popen('sysctl -n hw.ncpu').read())
            except ValueError:
                # don't trust the outside world
                pass
        try:
            cpu_count = os.sysconf('SC_NPROCESSORS_ONLN')
            if cpu_count >= 1:
                return cpu_count
        except (AttributeError, ValueError):
            # availability is restricted to unix
            pass
        if default is not None:
            return default
        raise NotImplementedError()

get_cpu_count.__doc__ = """
Returns the number of available processors on this machine.

If default is ``None`` and the number cannot be determined a
:exc:`NotImplementedError` is raised.
"""


class TimeoutError(Exception):
    """Exception raised in case of timeouts."""


class AsyncResult(object):
    """
    Helper object for providing asynchronous results.

    :param callback:
        Callback which is called if the result is a success.

    :param errback:
        Errback which is called if the result is an exception.
    """
    def __init__(self, callback=None, errback=None):
        self.callback = callback
        self.errback = errback

        self.condition = Condition(Lock())
        #: ``True`` if a result is available.
        self.ready = False

    def wait(self, timeout=None):
        """
        Blocks until the result is available or the given `timeout` has been
        reached.
        """
        with self.condition:
            if not self.ready:
                self.condition.wait(timeout)

    def get(self, timeout=None):
        """
        Returns the result or raises the exception which has been set, if
        the result is not available this method is blocking.

        If `timeout` is given this method raises a :exc:`TimeoutError`
        if the result is not available soon enough.
        """
        self.wait(timeout)
        if not self.ready:
            raise TimeoutError(timeout)
        if self.success:
            return self.value
        else:
            raise self.value

    def set(self, obj, success=True):
        """
        Sets the given `obj` as result, set `success` to ``False`` if `obj`
        is an exception.
        """
        self.value = obj
        self.success = success
        if self.callback and success:
            self.callback(obj)
        if self.errback and not success:
            self.errback(obj)
        with self.condition:
            self.ready = True
            self.condition.notify()

    def __repr__(self):
        parts = []
        if self.callback is not None:
            parts.append(('callback', self.callback))
        if self.errback is not None:
            parts.append(('errback', self.errback))
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join('%s=%r' % part for part in parts)
        )


__all__ = ['get_cpu_count', 'TimeoutError', 'AsyncResult']
