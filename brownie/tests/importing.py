# coding: utf-8
"""
    brownie.tests.importing
    ~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :mod:`brownie.importing`.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
from attest import Tests, TestBase, Assert, test

from brownie.importing import import_string


class TestImportString(TestBase):
    @test
    def by_name(self):
        import __main__
        module = import_string('__main__')
        Assert(module).is_(__main__)

    @test
    def by_path(self):
        import brownie.itools
        module = import_string('brownie.itools')
        Assert(module).is_(brownie.itools)

    @test
    def import_object(self):
        from brownie.itools import chain
        func = import_string('brownie.itools.chain')
        Assert(func).is_(chain)

    @test
    def colon_notation(self):
        import brownie.itools
        module = import_string('brownie:itools')
        Assert(module).is_(brownie.itools)

        func = import_string('brownie.itools:chain')
        Assert(func).is_(brownie.itools.chain)

    @test
    def invalid_name(self):
        cases = [
            ('brownie:itools.chain', 'itools.chain'),
            ('brownie-itools:chain', 'brownie-itools')
        ]
        for test, invalid_identifier in cases:
            with Assert.raises(ValueError) as exc:
                import_string(test)
            Assert(invalid_identifier).in_(exc.args[0])

    @test
    def import_non_existing_module(self):
        with Assert.raises(ImportError):
            import_string('foobar')


tests = Tests([TestImportString])
