# coding: utf-8
"""
    brownie.functional
    ~~~~~~~~~~~~~~~~~~

    Implements functions known from functional programming languages and other
    things which are useful when dealing with functions.

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from inspect import getargspec
from functools import wraps

from brownie.itools import izip_longest, unique
from brownie.pycompat import reduce
from brownie.datastructures import namedtuple, FixedDict


def compose(*functions):
    """
    Returns a function which acts as a composition of several `functions`. If
    one function is given it is returned if no function is given a
    :exc:`TypeError` is raised.

    >>> from brownie.functional import compose
    >>> compose(lambda x: x + 1, lambda x: x * 2)(1)
    3

    .. note:: Each function (except the last one) has to take the result of the
              last function as argument.
    """
    if not functions:
        raise TypeError('expected at least 1 argument, got 0')
    elif len(functions) == 1:
        return functions[0]
    return reduce(lambda f, g: lambda *a, **kws: f(g(*a, **kws)), functions)


def flip(function):
    """
    Returns a function which behaves like `function` but gets the given
    positional arguments reversed; keyword arguments are passed through.

    >>> from brownie.functional import flip
    >>> def f(a, b): return a
    >>> f(1, 2)
    1
    >>> flip(f)(1, 2)
    2
    """
    @wraps(function)
    def wrap(*args, **kwargs):
        return function(*reversed(args), **kwargs)
    return wrap


class Signature(namedtuple('SignatureBase', [
            'positionals', 'kwparams', 'varargs', 'varkwargs'
        ])):
    """
    A named tuple representing a function signature.

    :param positionals:
       A list of required positional parameters.

    :param kwparams:
       A list containing the keyword arguments, each as a tuple containing the
       name and default value, in order of their appearance in the function
       definition.

    :param varargs:
       The name used for arbitrary positional arguments or `None`.

    :param varkwargs:
       The name used for arbitary keyword arguments or `None`.

    .. warning::
       The size of :class:`Signature` tuples may change in the future to
       accommodate additional information like annotations. Therefore you
       should not rely on it.

    .. versionadded:: 0.5
    """
    @classmethod
    def from_function(cls, func):
        """
        Constructs a :class:`Signature` from the given function or method.
        """
        func = getattr(func, 'im_func', func)
        params, varargs, varkwargs, defaults = getargspec(func)
        defaults = [] if defaults is None else defaults
        return cls(
            params[
                :0 if len(defaults) == len(params)
                else -len(defaults) or len(params)
            ],
            zip(params[-len(defaults):], defaults),
            varargs,
            varkwargs
        )

    def bind_arguments(self, args=(), kwargs=None):
        """
        Returns a dictionary with the names of the parameters as keys with
        their arguments as values.

        Raises a :exc:`ValueError` if there are too many `args` and/or `kwargs`
        that are missing or repeated.
        """
        kwargs = {} if kwargs is None else kwargs

        required = set(self.positionals)
        overwritable = set(name for name, default in self.kwparams)
        settable = required | overwritable

        positional_count = len(self.positionals)
        kwparam_count = len(self.kwparams)

        result = dict(self.kwparams, **dict(zip(self.positionals, args)))

        remaining = args[positional_count:]
        for (param, _), arg in zip(self.kwparams, remaining):
            result[param] = arg
            overwritable.discard(param)
        if len(remaining) > kwparam_count:
            if self.varargs is None:
                raise ValueError(
                    'expected at most %d positional arguments, got %d' % (
                        positional_count + kwparam_count,
                        len(args)
                    )
                )
            else:
                result[self.varargs] = tuple(remaining[kwparam_count:])

        remaining = {}
        unexpected = []
        for key, value in kwargs.iteritems():
            if key in result and key not in overwritable:
                raise ValueError("got multiple values for '%s'" % key)
            elif key in settable:
                result[key] = value
            elif self.varkwargs:
                result_kwargs = result.setdefault(self.varkwargs, {})
                result_kwargs[key] = value
            else:
                unexpected.append(key)
        if len(unexpected) == 1:
            raise ValueError(
                "got unexpected keyword argument '%s'" % unexpected[0]
            )
        elif len(unexpected) == 2:
            raise ValueError(
                "got unexpected keyword arguments '%s' and '%s'" % tuple(unexpected)
            )
        elif unexpected:
            raise ValueError("got unexpected keyword arguments %s and '%s'" % (
                ', '.join("'%s'" % arg for arg in unexpected[:-1]), unexpected[-1]
            ))

        if set(result) < set(self.positionals):
            missing = set(result) ^ set(self.positionals)
            if len(missing) == 1:
                raise ValueError("'%s' is missing" % missing.pop())
            elif len(missing) == 2:
                raise ValueError("'%s' and '%s' are missing" % tuple(missing))
            else:
                missing = tuple(missing)
                raise ValueError("%s and '%s' are missing" % (
                    ', '.join("'%s'" % name for name in missing[:-1]), missing[-1]
                ))
        if self.varargs:
            result.setdefault(self.varargs, ())
        if self.varkwargs:
            result.setdefault(self.varkwargs, {})
        return result


class curried(object):
    """
    :class:`curried` is a decorator providing currying for callable objects.

    Each call to the curried callable returns a new curried object unless it
    is called with every argument required for a 'successful' call to the
    function::

        >>> foo = curried(lambda a, b, c: a + b * c)
        >>> foo(1, 2, 3)
        6
        >>> bar = foo(c=2)
        >>> bar(2, 3)
        8
        >>> baz = bar(3)
        >>> baz(3)
        9

    By the way if the function takes arbitrary positional and/or keyword
    arguments this will work as expected.

    .. versionadded:: 0.5
    """
    def __init__(self, function):
        self.function = function

        self.signature = Signature.from_function(function)
        self.params = self.signature.positionals + [
            name for name, default in self.signature.kwparams
        ]
        self.args = {}
        self.changeable_args = set(
            name for name, default in self.signature.kwparams
        )

    @property
    def remaining_params(self):
        return unique(self.params, set(self.args) - self.changeable_args)

    def _updated(self, args):
        result = object.__new__(self.__class__)
        result.__dict__.update(self.__dict__)
        result.args = args
        return result

    def __call__(self, *args, **kwargs):
        collected_args = self.args.copy()
        for remaining, arg in izip_longest(self.remaining_params, args):
            if remaining is None:
                if self.signature.varargs is None:
                    raise TypeError('unexpected positional argument: %r' % arg)
                collected_args.setdefault(self.signature.varargs, []).append(arg)
            elif arg is None:
                break
            else:
                if (remaining in collected_args and
                    remaining in self.signature.positionals
                        ):
                    raise TypeError(
                        "'%s' has been repeated: %r" % (remaining, arg)
                    )
                collected_args[remaining] = arg
                self.changeable_args.discard(remaining)
        for key, value in kwargs.iteritems():
            if key in self.params:
                if key in collected_args:
                    raise TypeError("'%s' has been repeated: %r" % (key, value))
                self.changeable_args.discard(key)
                collected_args[key] = value
            else:
                if self.signature.varkwargs is None:
                    raise TypeError('unexpected keyword argument')
                else:
                    collected_args.setdefault(
                        self.signature.varkwargs,
                        FixedDict()
                    )[key] = value
        if set(self.signature.positionals) <= set(collected_args):
            func_kwargs = dict(self.signature.kwparams)
            func_kwargs = FixedDict(self.signature.kwparams, **collected_args)
            func_kwargs.update(func_kwargs.pop(self.signature.varkwargs, {}))
            args = map(func_kwargs.pop, self.params)
            args += func_kwargs.pop(self.signature.varargs, [])
            return self.function(*args, **func_kwargs)
        return self._updated(collected_args)


__all__ = ['compose', 'flip', 'Signature', 'curried']
