.. highlight:: text


Testing Brownie
===============

Brownie uses the attest_ framework for testing in combination with tox_.
This allows us to easily create unit tests, to test our documentation and
to run all tests using various configurations defined through their
:ref:`test environments <test-environments>`.

Usually you just want to run all tests, in order to do that simply
execute::

    $ make test

Sometimes you may want to run tests only in a specific test environment,
in order to do that you need to use tox_ directly::

    $ tox -e <testenv>

``<testenv>`` has to be a :ref:`test environment <test-environments>` or a
comma-separated list of :ref:`test environments <test-environments>`.


.. _attest: http://packages.python.org/Attest/
.. _tox: http://codespeak.net/tox/


Selectively Running Tests
-------------------------

If you are developing a specific feature you rarely care about the tests
for all the modules you are currently not working on. In this case you can
select the module you want to test by calling tox_ and passing the name
of the module::

    $ tox -- <module>

``<module>`` can be any module in `brownie.tests` which has a
:class:`attest.Tests` collection under the attribute `tests`. If you want
to run the tests in multiple modules you can do that by passing each name
as an argument to `tox`.


.. _test-environments:

Test Environments
-----------------

At the moment the following test environments are available:

`docs`
    Tests that the documentation builds to HTML without any warnings and
    that all links are working.

`py25`, `pypy`
    Runs all unit tests on Python 2.5

`py26`, `py27`
    Runs all unit tests on Python 2.6 or 2.7 respectively as well as
    doctests and examples in the documentation.

`py31`
    Runs all unit tests on Python 3.1.
