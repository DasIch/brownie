# coding: utf-8
"""
    brownie.parallel
    ~~~~~~~~~~~~~~~~

    Implements useful parallelization stuff.

    :copyright: 2010 by Daniel Neuhaeuser
    :license: BSD, see LICENSE.rst for details
"""
import os
import sys

try:
    from multiprocessing import cpu_count as get_cpu_count
except ImportError:
    def get_cpu_count(default=None):
        if sys.platform == 'win32':
            try:
                return int(os.environ['NUMBER_OF_PROCESSORS'])
            except ValueError, KeyError:
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
        except AttributeError, ValueError:
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
