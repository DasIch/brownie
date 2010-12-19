# coding: utf-8
"""
    tests.parallel
    ~~~~~~~~~~~~~~

    Tests for :mod:`brownie.parallel`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from attest import Tests, Assert

from brownie.parallel import get_cpu_count


parallel_tests = Tests()


@parallel_tests.test
def test_get_cpu_count():
    try:
        Assert(get_cpu_count()) > 0
        Assert(get_cpu_count()) == get_cpu_count()
    except NotImplementedError:
        # make sure default is returned if the number of processes cannot be
        # determined
        Assert(get_cpu_count(2)) == 2
