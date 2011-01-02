Design Defence
==============
Certain design decisions as well as the entire project itself have and
will receive criticism in the future. This document will try to respond to
this criticism by explaining the reasoning behind those design decisions.

This should be part of the stdlib ("Write a PEP")
-------------------------------------------------
This is indeed the case, however the currently actively developed version
of Python is 3.x, the 2.x branch has ended with 2.7 and is in maintenance
only. As much as one might dislike this decision by the Python developers
it has been made and we have to live with it.

Now the problem is if I start writing PEPs for changes and/or new features
these will, if they are accepted, be part of the next Python 3.x release.
In practice however a lot of people do not and cannot use Python 3.x and
given that RHEL_ still uses Python 2.4 (which makes porting to Python 3.x
very hard) and `PEP 3333`_ has not found a wide adoption, yet, this will
not change in the near future.

Therefore even though I might be able to get the features I want into
Python I am effectively unable to use them. This, along with the `effort
required to write a PEP`__, is reason enough not to pursue this
(primarily) and to create this project instead.

.. _RHEL: http://www.redhat.com/rhel/
.. _PEP 3333: http://www.python.org/dev/peps/pep-3333/
.. __: http://www.python.org/dev/peps/pep-0001/

Utilities should be individual to a Project
-------------------------------------------
This claim is usually made in combination with the assumption that Brownie
either covers too much compared to what is needed for a specific Project
or that Brownie cannot cover enough.

Obviously it is a problem to choose the right balance between utilities
which are quite common and those which are too rarely used to be included.
In any case I doubt the criticism truly appreciates the effort required to
implement, document, test and maintain those utilities.

Even though this is not a particularly difficult task there is a lot of time
involved which is better spent on developing the features, of your library or
application, you want to provide.

Brownie might not be able to prevent you from spending any time at all on
internals but that is neither possible nor the goal. The goal is to make it
easier for you and if that is done by providing just this one function you
need, it has been achieved.
