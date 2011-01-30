# coding: utf-8
"""
    brownie.datastructures.sequences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from keyword import iskeyword
from operator import itemgetter
from functools import wraps
from itertools import count

from brownie.itools import chain, izip_longest


class LazyList(object):
    """
    Implements a lazy list which computes items based on the given `iterable`.

    This allows you to create :class:`list`\-like objects of unlimited size.
    However although most operations don't exhaust the internal iterator
    completely some of them do, so if the given iterable is of unlimited size
    making such an operation will eventually cause a :exc:`MemoryError`.

    Cost in terms of laziness of supported operators, this does not include
    supported operators without any cost:

    +-----------------+-------------------------------------------------------+
    | Operation       | Result                                                |
    +=================+=======================================================+
    | ``list[i]``     | This exhausts the `list` up until the given index.    |
    +-----------------+                                                       |
    | ``list[i] = x`` |                                                       |
    +-----------------+                                                       |
    | ``del list[i]`` |                                                       |
    +-----------------+-------------------------------------------------------+
    | ``len(list)``   | Exhausts the internal iterator.                       |
    +-----------------+-------------------------------------------------------+
    | ``x in list``   | Exhausts the `list` up until `x` or until the `list`  |
    |                 | is exhausted.                                         |
    +-----------------+-------------------------------------------------------+
    | ``l1 == l2``    | Exhausts both lists.                                  |
    +-----------------+-------------------------------------------------------+
    | ``l1 != l2``    | Exhausts both lists.                                  |
    +-----------------+-------------------------------------------------------+
    | ``bool(list)``  | Exhausts the `list` up to the first item.             |
    +-----------------+-------------------------------------------------------+
    | ``l1 < l2``     | Exhausts the list up to the first item which shows    |
    |                 | the result. In the worst case this exhausts both      |
    +-----------------+ lists.                                                |
    | ``l1 > l2``     |                                                       |
    +-----------------+-------------------------------------------------------+
    | ``l1 + l2``     | Creates a new :class:`LazyList` without exhausting    |
    |                 | `l1` or `l2`.                                         |
    +-----------------+-------------------------------------------------------+
    | ``list * n``    | Exhausts the `list`.                                  |
    +-----------------+                                                       |
    | ``list *= n``   |                                                       |
    +-----------------+-------------------------------------------------------+


    .. versionadded:: 0.5
       It is now possible to pickle :class:`LazyList`\s, however this will
       exhaust the list.
    """
    @classmethod
    def factory(cls, callable):
        """
        Returns a wrapper for a given callable which takes the return value
        of the wrapped callable and converts it into a :class:`LazyList`.
        """
        @wraps(callable)
        def wrap(*args, **kwargs):
            return cls(callable(*args, **kwargs))
        return wrap

    def exhausting(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            self._exhaust()
            return func(self, *args, **kwargs)
        return wrap

    def __init__(self, iterable):
        if isinstance(iterable, (list, tuple, basestring)):
            #: ``True`` if the internal iterator is exhausted.
            self.exhausted = True
            self._collected_data = list(iterable)
        else:
            self._iterator = iter(iterable)
            self.exhausted = False
            self._collected_data = []

    def _exhaust(self, i=None):
        if self.exhausted:
            return
        elif i is None or i < 0:
            index_range = count(self.known_length)
        elif isinstance(i, slice):
            start, stop = i.start, i.stop
            if start < 0 or stop < 0:
                index_range = count(self.known_length)
            else:
                index_range = xrange(self.known_length, stop)
        else:
            index_range = xrange(self.known_length, i + 1)
        for i in index_range:
            try:
                self._collected_data.append(self._iterator.next())
            except StopIteration:
                self.exhausted = True
                break

    @property
    def known_length(self):
        """
        The number of items which have been taken from the internal iterator.
        """
        return len(self._collected_data)

    def append(self, object):
        """
        Appends the given `object` to the list.
        """
        self.extend([object])

    def extend(self, objects):
        """
        Extends the list with the given `objects`.
        """
        if self.exhausted:
            self._collected_data.extend(objects)
        else:
            self._iterator = chain(self._iterator, objects)

    def insert(self, index, object):
        """
        Inserts the given `object` at the given `index`.

        This method exhausts the internal iterator up until the given `index`.
        """
        self._exhaust(index)
        self._collected_data.insert(index, object)

    def pop(self, index=None):
        """
        Removes and returns the item at the given `index`, if no `index` is
        given the last item is used.

        This method exhausts the internal iterator up until the given `index`.
        """
        self._exhaust(index)
        if index is None:
            return self._collected_data.pop()
        return self._collected_data.pop(index)

    def remove(self, object):
        """
        Looks for the given `object` in the list and removes the first
        occurrence.

        If the item is not found a :exc:`ValueError` is raised.

        This method exhausts the internal iterator up until the first
        occurrence of the given `object` or entirely if it is not found.
        """
        while True:
            try:
                self._collected_data.remove(object)
                return
            except ValueError:
                if self.exhausted:
                    raise
                else:
                    self._exhaust(self.known_length)

    @exhausting
    def reverse(self):
        """
        Reverses the list.

        This method exhausts the internal iterator.
        """
        self._collected_data.reverse()

    @exhausting
    def sort(self, cmp=None, key=None, reverse=False):
        """
        Sorts the list using the given `cmp` or `key` function and reverses it
        if `reverse` is ``True``.

        This method exhausts the internal iterator.
        """
        self._collected_data.sort(cmp=cmp, key=key, reverse=reverse)

    @exhausting
    def count(self, object):
        """
        Counts the occurrences of the given `object` in the list.

        This method exhausts the internal iterator.
        """
        return self._collected_data.count(object)

    def __getitem__(self, i):
        """
        Returns the object or objects at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        return self._collected_data[i]

    def __setitem__(self, i, obj):
        """
        Sets the given object or objects at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        self._collected_data[i] = obj

    def __delitem__(self, i):
        """
        Removes the item or items at the given index.

        This method exhausts the internal iterator up until the given index.
        """
        self._exhaust(i)
        del self._collected_data[i]

    @exhausting
    def __len__(self):
        """
        Returns the length of the list.

        This method exhausts the internal iterator.
        """
        return self.known_length

    def __contains__(self, other):
        for obj in self:
            if obj == other:
                return True
        return False

    @exhausting
    def __eq__(self, other):
        """
        Returns ``True`` if the list is equal to the given `other` list, which
        may be another :class:`LazyList`, a :class:`list` or a subclass of
        either.

        This method exhausts the internal iterator.
        """
        if isinstance(other, (self.__class__, list)):
            return self._collected_data == other
        return False

    def __ne__(self, other):
        """
        Returns ``True`` if the list is unequal to the given `other` list, which
        may be another :class:`LazyList`, a :class:`list` or a subclass of
        either.

        This method exhausts the internal iterator.
        """
        return not self.__eq__(other)

    __hash__ = None

    def __nonzero__(self):
        """
        Returns ``True`` if the list is not empty.

        This method takes one item from the internal iterator.
        """
        self._exhaust(0)
        return bool(self._collected_data)

    def __lt__(self, other):
        """
        This method returns ``True`` if this list is "lower than" the given
        `other` list. This is the case if...

        - this list is empty and the other is not.
        - the first nth item in this list which is unequal to the
          corresponding item in the other list, is lower than the corresponding
          item.

        If this and the other list is empty this method will return ``False``.
        """
        if not self and other:
            return True
        elif self and not other:
            return False
        elif not self and not other:
            return False
        missing = object()
        for a, b in izip_longest(self, other, fillvalue=missing):
            if a < b:
                return True
            elif a == b:
                continue
            elif a is missing and b is not missing:
                return True
            return False

    def __gt__(self, other):
        """
        This method returns ``True`` if this list is "greater than" the given
        `other` list. This is the case if...

        - this list is not empty and the other is
        - the first nth item in this list which is unequal to the
          corresponding item in the other list, is greater than the
          corresponding item.

        If this and the other list is empty this method will return ``False``.
        """

        if not self and not other:
            return False
        return not self.__lt__(other)

    def __add__(self, other):
        if isinstance(other, (list, self.__class__)):
            return self.__class__(chain(self, other))
        raise TypeError("can't concatenate with non-list: {0}".format(other))

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, other):
        if isinstance(other, int):
            self._exhaust()
            return self.__class__(self._collected_data * other)
        raise TypeError("can't multiply sequence by non-int: {0}".format(other))

    def __imul__(self, other):
        if isinstance(other, int):
            self._exhaust()
            self._collected_data *= other
            return self
        else:
            raise TypeError(
                "can't multiply sequence by non-int: {0}".format(other)
            )

    @exhausting
    def __getstate__(self):
        return self._collected_data

    def __setstate__(self, state):
        self.exhausted = True
        self._collected_data = state

    def __repr__(self):
        """
        Returns the representation string of the list, if the list exhausted
        this looks like the representation of any other list, otherwise the
        "lazy" part is represented by "...", like "[1, 2, 3, ...]".
        """
        if self.exhausted:
            return repr(self._collected_data)
        elif not self._collected_data:
            return '[...]'
        return '[%s, ...]' % ', '.join(
            repr(obj) for obj in self._collected_data
        )

    del exhausting


class CombinedSequence(object):
    """
    A sequence combining other sequences.

    .. versionadded:: 0.5
    """
    def __init__(self, sequences):
        self.sequences = list(sequences)

    def at_index(self, index):
        """
        Returns the sequence and the 'sequence local' index::

            >>> foo = [1, 2, 3]
            >>> bar = [4, 5, 6]
            >>> cs = CombinedSequence([foo, bar])
            >>> cs[3]
            4
            >>> cs.at_index(3)
            ([4, 5, 6], 0)
        """
        seen = 0
        if index >= 0:
            for sequence in self.sequences:
                if seen <= index < seen + len(sequence):
                    return sequence, index - seen
                seen += len(sequence)
        else:
            for sequence in reversed(self.sequences):
                if seen >= index > seen - len(sequence):
                    return sequence, index - seen
                seen -= len(sequence)
        raise IndexError(index)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(iter(self))[index]
        sequence, index = self.at_index(index)
        return sequence[index]

    def __len__(self):
        return sum(map(len, self.sequences))

    def __iter__(self):
        return chain.from_iterable(self.sequences)

    def __reversed__(self):
        return chain.from_iterable(reversed(map(reversed, self.sequences)))

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        elif isinstance(other, self.__class__):
            return self.sequences == other.sequences
        return False

    def __ne__(self, other):
        return not self == other

    __hash__ = None

    def __mul__(self, times):
        if not isinstance(times, int):
            return NotImplemented
        return list(self) * times

    def __rmul__(self, times):
        if not isinstance(times, int):
            return NotImplemented
        return times * list(self)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.sequences)


class CombinedList(CombinedSequence):
    """
    A list combining other lists.

    .. versionadded:: 0.5
    """
    def count(self, item):
        """
        Returns the number of occurrences of the given `item`.
        """
        return sum(sequence.count(item) for sequence in self.sequences)

    def index(self, item, start=None, stop=None):
        """
        Returns the index of the first occurence of the given `item` between
        `start` and `stop`.
        """
        start = 0 if start is None else start
        for index, it in enumerate(self[start:stop]):
            if item == it:
                return index + start
        raise ValueError('%r not in list' % item)

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            start = 0 if index.start is None else index.start
            stop = len(self) if index.stop is None else index.stop
            step = 1 if index.step is None else index.step
            for index, item in zip(range(start, stop, step), item):
                self[index] = item
        else:
            list, index = self.at_index(index)
            list[index] = item

    def __delitem__(self, index):
        if isinstance(index, slice):
            start = 0 if index.start is None else index.start
            stop = len(self) if index.stop is None else index.stop
            step = 1 if index.step is None else index.step
            for list, index in map(self.at_index, range(start, stop, step)):
                del list[index]
        else:
            list, index = self.at_index(index)
            del list[index]

    def append(self, item):
        """
        Appends the given `item` to the end of the list.
        """
        self.sequences[-1].append(item)

    def extend(self, items):
        """
        Extends the list by appending from the given iterable.
        """
        self.sequences[-1].extend(items)

    def insert(self, index, item):
        """
        Inserts the given `item` before the item at the given `index`.
        """
        list, index = self.at_index(index)
        list.insert(index, item)

    def pop(self, index=-1):
        """
        Removes and returns the item at the given `index`.

        An :exc:`IndexError` is raised if the index is out of range.
        """
        list, index = self.at_index(index)
        return list.pop(index)

    def remove(self, item):
        """
        Removes the first occurence of the given `item` from the list.
        """
        for sequence in self.sequences:
            try:
                return sequence.remove(item)
            except ValueError:
                # we may find a value in the next sequence
                pass
        raise ValueError('%r not in list' % item)

    def _set_values(self, values):
        lengths = map(len, self.sequences)
        previous_length = 0
        for length in lengths:
            stop = previous_length + length
            self[previous_length:stop] = values[previous_length:stop]
            previous_length += length

    def reverse(self):
        """
        Reverses the list in-place::

            >>> a = [1, 2, 3]
            >>> b = [4, 5, 6]
            >>> l = CombinedList([a, b])
            >>> l.reverse()
            >>> a
            [6, 5, 4]
        """
        self._set_values(self[::-1])

    def sort(self, cmp=None, key=None, reverse=False):
        """
        Sorts the list in-place, see :meth:`list.sort`.
        """
        self._set_values(sorted(self, cmp, key, reverse))


def namedtuple(typename, field_names, verbose=False, rename=False):
    """
    Returns a :class:`tuple` subclass named `typename` with a limited number
    of possible items who are accessible under their field name respectively.

    Due to the implementation `typename` as well as all `field_names` have to
    be valid python identifiers also the names used in `field_names` may not
    repeat themselves.

    You can solve the latter issue for `field_names` by passing ``rename=True``,
    any given name which is either a keyword or a repetition is then replaced
    with `_n` where `n` is an integer increasing with every rename starting by
    1.

    :func`namedtuple` creates the code for the subclass and executes it
    internally you can view that code by passing ``verbose==True``, which will
    print the code.

    Unlike :class:`tuple` a named tuple provides several methods as helpers:

    .. class:: SomeNamedTuple(foo, bar)

       .. classmethod:: _make(iterable)

          Returns a :class:`SomeNamedTuple` populated with the items from the
          given `iterable`.

       .. method:: _asdict()

          Returns a :class:`dict` mapping the field names to their values.

       .. method:: _replace(**kwargs)

          Returns a :class:`SomeNamedTuple` values replaced with the given
          ones::

              >>> t = SomeNamedTuple(1, 2)
              >>> t._replace(bar=3)
              SomeNamedTuple(foo=1, bar=3)
              # doctest: DEACTIVATE

    .. note::
       :func:`namedtuple` is compatible with :func:`collections.namedtuple`.

    .. versionadded:: 0.5
    """
    def name_generator():
        for i in count(1):
            yield '_%d' % i
    make_name = name_generator().next

    if iskeyword(typename):
        raise ValueError('the given typename is a keyword: %s' % typename)
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split()
    real_field_names = []
    seen_names = set()
    for name in field_names:
        if iskeyword(name):
            if rename:
                name = make_name()
            else:
                raise ValueError('a given field name is a keyword: %s' % name)
        elif name in seen_names:
            if rename:
                name = make_name()
            else:
                raise ValueError('a field name has been repeated: %s' % name)
        real_field_names.append(name)
        seen_names.add(name)

    code = textwrap.dedent("""
        class %(typename)s(tuple):
            '''%(typename)s%(fields)s'''

            _fields = %(fields)s

            @classmethod
            def _make(cls, iterable):
                result = tuple.__new__(cls, iterable)
                if len(result) > %(field_count)d:
                    raise TypeError(
                        'expected %(field_count)d arguments, got %%d' %% len(result)
                    )
                return result

            def __new__(cls, %(fieldnames)s):
                return tuple.__new__(cls, (%(fieldnames)s))

            def _asdict(self):
                return dict(zip(self._fields, self))

            def _replace(self, **kwargs):
                result = self._make(map(kwargs.pop, %(fields)s, self))
                if kwargs:
                    raise ValueError(
                        'got unexpected arguments: %%r' %% kwargs.keys()
                    )
                return result

            def __getnewargs__(self):
                return tuple(self)

            def __repr__(self):
                return '%(typename)s(%(reprtext)s)' %% self
    """) % {
        'typename': typename,
        'fields': repr(tuple(real_field_names)),
        'fieldnames': ', '.join(real_field_names),
        'field_count': len(real_field_names),
        'reprtext': ', '.join(name + '=%r' for name in real_field_names)
    }

    for i, name in enumerate(real_field_names):
        code += '    %s = property(itemgetter(%d))\n' % (name, i)

    if verbose:
        print code

    namespace = {'itemgetter': itemgetter}
    try:
        exec code in namespace
    except SyntaxError, e:
        raise SyntaxError(e.args[0] + ':\n' + code)
    result = namespace[typename]

    return result


__all__ = ['LazyList', 'CombinedSequence', 'CombinedList', 'namedtuple']
