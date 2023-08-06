Mocki aims to be an easy-to-use but full featured mocking library for Python.

Installation
============

Here is how to install Mocki using pip : ::

    pip install Mocki

Starting with Mocki
===================

Here is how to instantiate a new mock with Mocki :

.. code:: python

    >>> import mocki.core
    >>>
    >>> mock = mocki.core.Mock('myMock')

There are basically two things we can do with this mock :

* stub it to do a particular action on a particular call :

.. code:: python

    >>> mock.on_call('myCall').do_return('myValue')
    >>>
    >>> mock('myCall')
    'myValue'

* verify whether or not a particular call was invoked on it :

.. code:: python

    >>> mock.verify_call('myCall').invoked_once()
    >>>
    >>> mock.verify_call('myCall').invoked_exactly(2)
    Traceback (most recent call last):
    ...
    AssertionError: Found one matching call invoked from myMock :
    > myMock('myCall')

Documentation
=============

See the `online documentation`_ for more information on how to use Mocki.

.. _`online documentation`: http://mocki.readthedocs.org/en/latest/
