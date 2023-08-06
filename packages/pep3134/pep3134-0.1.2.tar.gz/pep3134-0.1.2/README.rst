pep3134
=======

|Build Status| |Code Coverage| |Static Analysis| |PyPI Package|

This library is intended to give you an ability to use exception chaining and embedded tracebacks with both
Python 2 and Python 3 (>= 3.3 only). Exception Chaining and Embedded Tracebacks are also well known as
PEP3134 that's why I have such geeky name for that library.

No, it is not. Geeky name is kinda ``PEP3134 (feat. PEP409, PEP415 Remix)`` but I think it is an overkill.

If you want to get more about exception chaining and tracebacks please refer to the documentation for
`Python 3 <https://docs.python.org/3/>`__ with modifications done 
in `Python 3.3 <https://docs.python.org/3/whatsnew/3.3.html>`__.

Short excerpt for those who still sit with Python 2 as me.

1. Exceptions have new attributes: ``__traceback__``, ``__context__``, ``__suppress_context__`` 
   and ``__cause__``.
2. Exceptions have new syntax for explicit chaining: 
   ``raise CustomError("Cannot read settings") from IOError("Cannot open /etc/settings")``.
3. Exceptions always have their own tracebacks attached in ``__traceback__`` attribute.
4. If exception was raised without explicit cause, it has its own context 
   (say, from ``sys.exc_info()``) in ``__context__`` attribute. In this case ``__cause__`` 
   keeps ``None``.
5. If exception was raised by implicit cause, then ``__suppress_context__`` is ``False``.
6. If exception was raised with explicit cause (``raise ... from ...``) then
   ``__cause__`` has a cause, ``__suppress_context__`` is ``True`` and ``__context__`` is
   (suddenly) ``None``.

So this is pretty convenient to have chaining if you want to build human-readable error messages
afterwards, right? 

This library helps you to keep the same ``__context__``, ``__cause__`` and ``__suppress_context__``
behavior with both Python 2 and Python 3.

I did not mentioned ``__traceback__``. This is a reason



``__traceback__`` in Python 2
-----------------------------

Tracebacks are very convenient data structure to work with but really irritating and magical
if you want to deal with it using pure Python, without patching code or hacking interpreter 
internals. If you want to see some magic, please checkout, let's say, 
`Jinja sources <https://github.com/mitsuhiko/jinja2/blob/master/jinja2/debug.py#L267>`__. Armin is rather
good but I am trying to escape magic if possible.

I cannot keep the same tracebacks to any exceptions even if I want because it requires to do some
work on interpreter internals. But anyway this method will return you something.

The rule of thumb is: if it returns an object, it is the proper object you expect. If it returns None
then no luck. Moreover: ``__traceback__`` implemented as property so sometimes it raises traceback but afterwards
it returns ``None`` on the same object. Unfortunately I do not know a good way how to deal with it.

But I can you give some guarantees:

1. ``__traceback__`` on implicit (``__context__``) and explicit causes (``__cause__``) always correct.
2. ``__traceback__`` in the associated ``except`` clause is always correct.
3. Sometimes it works in other cases but do not rely on that.

This works like this because of _fixed_ ``sys.exc_info()`` behavior. Let's check one example.

.. code-block:: python

    import sys

    def example():
        try:
            raise KeyError("WOW SUCH ERROR")
        except KeyError:
            first = sys.exc_info()
        
        second = sys.exc_info()
        return first, second
    
    first, second = example()
    assert first == second

It works as a charm in Python2 but raises ``AssertionError`` in Python3. So it is not possible to
keep tracebacks in the same way in both Python2 and Python3. Sad story.

So if we will rewrite given example with PEP3134

.. code-block:: python

    import sys
    import pep3134
    
    def example():
        error = -1
        try:
            pep3134.raise_(KeyError("WOW SUCH ERROR"))
        except KeyError as err:
            error = err
            first = sys.exc_info()
            assert error.__traceback__ is first[2]
    
        second = sys.exc_info()
        assert error.__traceback__ is not second[2]  # works in Python 2 only
    
    example()


This is the only pitfall. Causes, as I mentioned, work well.



PEP3134 library
---------------

This library gives you 3 functions you can use. Only 3 so no need to have full documentation on
any external source.



``pep3134.raise_``
------------------

Works with the same signature as ``raise`` clause in both Python 2 and Python 3. Just a reminder:

.. code-block:: python

    raise exc_type, [exc_value, [exc_traceback]]

Raises exceptions on the same problems.



``pep3134.reraise``
-------------------

Works in the same way as ``raise`` clause without any arguments does in Python 2.



``pep3134.raise_from``
----------------------

Works absolutely in the same way as ``raise ... from ...`` clause does in Python 3.



.. |Build Status| image:: https://travis-ci.org/9seconds/pep3134.svg?branch=master
    :target: https://travis-ci.org/9seconds/pep3134

.. |Code Coverage| image:: https://coveralls.io/repos/9seconds/pep3134/badge.png?branch=master 
    :target: https://coveralls.io/r/9seconds/pep3134?branch=master

.. |Static Analysis| image:: https://landscape.io/github/9seconds/pep3134/master/landscape.png
    :target: https://landscape.io/github/9seconds/pep3134/master

.. |PyPI Package| image:: https://badge.fury.io/py/pep3134.svg
    :target: http://badge.fury.io/py/pep3134