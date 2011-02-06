.. highlight:: text

Introduction to developing Brownie
==================================

Developing Brownie is really easy, this is going to show you how to do it.
However if you are not already familiar with virtualenv_, you might want
to familiarize yourself with it first.

.. _virtualenv: http://virtualenv.openplans.org/

So the first thing we do is cloning the repository::

   $ git clone git://github.com/DasIch/brownie.git

This will clone the repository in a directory called `brownie`, now `cd`
into that directory.

As I mentioned earlier we use virtualenv_ to create an environment. If you
are in the `brownie` directory simply execute ``make dev-env``, this will
create a virtualenv in the `env` directory and install everything required
for development.

.. note:: By specifying the `DIR` environment variable you can change the
          location of the virtualenv_ created my ``make dev-env``.

Now activate the environment and you are "done"::

   $ . env/bin/activate

Building the documentation
--------------------------

During development you usually write documentation, you want to check that
everything looks right or want to lookup something without having to
access the documentation online.

In order to view the documentation simply execute::

   $ make view-doc

This will build the documentation and open it in your web browser, if you
just want to build the documentation a simple ``make doc`` will do.


Further Information
-------------------

For further information run the ``make help`` command which will give you
an overview. If you have specific questions ask on the :ref:`irc-channel` for
help.

.. seealso::

   - :ref:`testing`
   - :ref:`contributing`
