# coding: utf-8
"""
    brownie.tests.functional.signature
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :class:`brownie.functional.Signature`.

    :copyright: 2010-2011 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import with_statement
import re

from attest import Tests, Assert, TestBase, test

from brownie.functional import Signature


class TestFromFunction(TestBase):
    @test
    def positionals(self):
        func = lambda a, b, c: None
        Assert(Signature.from_function(func)) == (['a', 'b', 'c'], [], None, None)

    @test
    def keyword_arguments(self):
        func = lambda a=1, b=2, c=3: None
        Assert(Signature.from_function(func)) == (
            [], [('a', 1), ('b', 2), ('c', 3)], None, None
        )

    @test
    def mixed_positionals_keyword_arguments(self):
        func = lambda a, b, c=3: None
        Assert(Signature.from_function(func)) == (
            ['a', 'b'], [('c', 3)], None, None
        )
        func = lambda a, b, c=3, d=4: None
        Assert(Signature.from_function(func)) == (
            ['a', 'b'], [('c', 3), ('d', 4)], None, None
        )

    @test
    def arbitary_positionals(self):
        foo = lambda *foo: None
        bar = lambda *bar: None
        for func, name in [(foo, 'foo'), (bar, 'bar')]:
            Assert(Signature.from_function(func)) == ([], [], name, None)

    @test
    def arbitary_keyword_arguments(self):
        spam = lambda **spam: None
        eggs = lambda **eggs: None
        for func, name in [(spam, 'spam'), (eggs, 'eggs')]:
            Assert(Signature.from_function(func)) == ([], [], None, name)


class TestBindArguments(TestBase):
    @test
    def arguments_no_args(self):
        sig = Signature.from_function(lambda: None)

        Assert(sig.bind_arguments()) == {}

        with Assert.raises(ValueError) as exc:
            sig.bind_arguments((1, ), {})
        Assert(exc.args[0]) == 'expected at most 0 positional arguments, got 1'

        tests = [
            ({'a': 1}, "got unexpected keyword argument '.'"),
            ({'a': 1, 'b': 2}, "got unexpected keyword arguments '.' and '.'"),
            (
                {'a': 1, 'b': 2, 'c': 3},
                "got unexpected keyword arguments '.', '.' and '.'"
            )
        ]

        for kwargs, message in tests:
            with Assert.raises(ValueError) as exc:
                sig.bind_arguments(kwargs=kwargs)
            err_msg = exc.args[0].obj
            assert re.match(message, err_msg) is not None
            for name in kwargs:
                assert name in err_msg

    @test
    def arguments_only_positionals(self):
        sig = Signature.from_function(lambda a, b, c: None)

        Assert(sig.bind_arguments((1, 2, 3))) == dict(a=1, b=2, c=3)
        Assert(sig.bind_arguments((1, 2), {'c': 3})) == dict(a=1, b=2, c=3)

        tests = [
            ([('a', 1), ('b', 2)], "'.' is missing"),
            ([('a', 1)], "'.' and '.' are missing"),
            ([], "'.', '.' and '.' are missing")
        ]
        all_names = set('abc')
        for args, message in tests:
            names, values = [], []
            for name, value in args:
                names.append(name)
                values.append(value)

            with Assert.raises(ValueError) as exc_args:
                sig.bind_arguments(values)

            with Assert.raises(ValueError) as exc_kwargs:
                sig.bind_arguments(kwargs=dict(args))

            for exc in [exc_args, exc_kwargs]:
                err_msg = exc.args[0].obj
                assert re.match(message, err_msg) is not None
                for name in all_names.difference(names):
                    assert name in err_msg

        with Assert.raises(ValueError) as exc:
            sig.bind_arguments((1, 2, 3), {'c': 4})
        Assert(exc.args[0]) == "got multiple values for 'c'"

    @test
    def arguments_only_keyword_arguments(self):
        sig = Signature.from_function(lambda a=1, b=2, c=3: None)

        Assert(sig.bind_arguments()) == dict(a=1, b=2, c=3)
        Assert(sig.bind_arguments(('a', ))) == dict(a='a', b=2, c=3)
        Assert(sig.bind_arguments((), {'a': 'a'})) == dict(a='a', b=2, c=3)

    @test
    def arguments_arbitary_positionals(self):
        sig = Signature.from_function(lambda *args: None)

        Assert(sig.bind_arguments()) == {'args': ()}
        Assert(sig.bind_arguments((1, 2, 3))) == {'args': (1, 2, 3)}

    @test
    def arguments_mixed_positionals(self):
        sig = Signature.from_function(lambda a, b, *args: None)

        Assert(sig.bind_arguments((1, 2))) == dict(a=1, b=2, args=())
        Assert(sig.bind_arguments((1, 2, 3))) == dict(a=1, b=2, args=(3, ))
        with Assert.raises(ValueError):
            Assert(sig.bind_arguments())

    @test
    def arguments_arbitary_keyword_arguments(self):
        sig = Signature.from_function(lambda **kwargs: None)

        Assert(sig.bind_arguments()) == {'kwargs': {}}
        Assert(sig.bind_arguments((), {'a': 1})) == {'kwargs': {'a': 1}}

    @test
    def arguments_mixed_keyword_arguments(self):
        sig = Signature.from_function(lambda a=1, b=2, **kwargs: None)

        Assert(sig.bind_arguments()) == dict(a=1, b=2, kwargs={})
        Assert(sig.bind_arguments((3, 4))) == dict(a=3, b=4, kwargs={})
        Assert(sig.bind_arguments((), {'c': 3})) == dict(
            a=1,
            b=2,
            kwargs=dict(c=3)
        )

    @test
    def arguments_mixed_positional_arbitary_keyword_arguments(self):
        sig = Signature.from_function(lambda a, b, **kwargs: None)

        Assert(sig.bind_arguments((1, 2))) == dict(a=1, b=2, kwargs={})
        Assert(sig.bind_arguments((1, 2), {'c': 3})) == dict(
            a=1,
            b=2,
            kwargs=dict(c=3)
        )
        Assert(sig.bind_arguments((), dict(a=1, b=2))) == dict(
            a=1,
            b=2,
            kwargs={}
        )
        with Assert.raises(ValueError):
            sig.bind_arguments()
        with Assert.raises(ValueError):
            sig.bind_arguments((1, 2), {'a': 3})

    @test
    def arguments_mixed_keyword_arguments_arbitary_positionals(self):
        sig = Signature.from_function(lambda a=1, b=2, *args: None)

        Assert(sig.bind_arguments()) == dict(a=1, b=2, args=())
        Assert(sig.bind_arguments((3, 4))) == dict(a=3, b=4, args=())
        Assert(sig.bind_arguments((3, 4, 5))) == dict(a=3, b=4, args=(5, ))
        Assert(sig.bind_arguments((), {'a': 3, 'b': 4})) == dict(
            a=3, b=4, args=()
        )
        with Assert.raises(ValueError):
            sig.bind_arguments((3, ), {'a': 4})


tests = Tests([TestFromFunction, TestBindArguments])
