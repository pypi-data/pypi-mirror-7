Decoratori
==========

-----

Cine
====

blog.ionelmc.ro
===============

github.com/ionelmc
==================

-----

Decoratori
==========

* Cine nu a scris un decorator ?

Presenter Notes
---------------

* Din prima :)

-----

Arată cunoscut ?
================

.. sourcecode:: pycon

    >>> from functools import wraps
    >>> def log_errors(func):
    ...     @wraps(func)
    ...     def log_errors_wrapper(*args, **kwargs):
    ...         try:
    ...             return func(*args, **kwargs)
    ...         except Exception as exc:
    ...             print("Raised %r for %s/%s" % (exc, args, kwargs))
    ...             raise
    ...     return log_errors_wrapper

    >>> @log_errors
    ... def broken_function():
    ...     raise RuntimeError()

    >>> from pytest import raises
    >>> raises(RuntimeError, broken_function)
    Raised RuntimeError() for ()/{}
    ...

-----

O mică paranteză
================

* Odată ca niciodată ...
* Că de n-ar fi `bad practice`
* Nu s-ar povesti ....

.. sourcecode:: python

    def log_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, exc:
                print("Raised %r for %s/%s" % (exc, args, kwargs))
                raise exc
        return wrapper


Presenter Notes
---------------

* ``__name__`` e diferit (``@wraps`` lipsa)
* except ``as``
* reraising
* ``wrapper`` name

-----

Aiurea
======

* Mult cod repetitiv

.. image:: 92374175_31fc8fd839_z.jpg
    :alt: source: https://www.flickr.com/photos/michelyn/92374175/in/photostream/

-----

Problemuțe
==========

Există 2 tipuri de funcții, decise la compilare:

* Funcția cea de toate zilele ...
* Funcția generator, dracul împielițat (are ``yield``) - nu poate avea ``return valoare``, doar ``return`` singur.

Așadar, `funcția generator` intoarce un generator.

* Dacă excepția este aruncată după ce a început iterarea atunci decoratorul nostru nu o poate prinde.
* Trebuie sa consumam generatorul (``for i in ...: yield i``)

----

Generatorul
===========

.. sourcecode:: pycon

    >>> @log_errors
    ... def broken_generator():
    ...     yield 1
    ...     raise RuntimeError()

    >>> _=raises(RuntimeError, lambda: list(broken_generator()))

Dooh ! Nu se intampla nimic ...

-----

Bun, mergem la doctor cu decoratorul
====================================

* Otrava prescrisă: condiții și repetiții

.. sourcecode:: pycon

    >>> from inspect import isgeneratorfunction
    >>> def log_errors(func):
    ...     if isgeneratorfunction(func):
    ...         @wraps(func)
    ...         def log_errors_wrapper(*args, **kwargs):
    ...             try:
    ...                 for item in func(*args, **kwargs):
    ...                     yield item
    ...             except Exception as exc:
    ...                 print("Raised %r for %s/%s" % (exc, args, kwargs))
    ...                 raise
    ...     else:
    ...         @wraps(func)
    ...         def log_errors_wrapper(*args, **kwargs):
    ...             try:
    ...                 return func(*args, **kwargs)
    ...             except Exception as exc:
    ...                 print("Raised %r for %s/%s" % (exc, args, kwargs))
    ...                 raise
    ...     return log_errors_wrapper

Presenter notes
---------------

* O mica perversitate, in Python 3 poti avea ``yield`` **si** ``return value``, dar functia ramane functie generator !

-----

Merge ...
=========

.. sourcecode:: pycon

    >>> @log_errors
    ... def broken_generator():
    ...     yield 1
    ...     raise RuntimeError()

    >>> raises(RuntimeError, list, broken_generator())
    Raised RuntimeError() for ()/{}
    ...

-----

Medicamentul, greu de înghițit
==============================

* Trebuie 2 functii - fiindcă funcția generator (are ``yield``) nu poate avea ``return`` cu valoare
* Nu merge cu corutine ...

-----

Corutine ?
==========

.. image:: 15bike2.jpg

-----

Corutina
========

::

    def

The alternative, use ``aspectlib``
==================================

.. sourcecode:: pycon

    >>> from aspectlib import Aspect
    >>> @Aspect
    ... def log_errors(*args, **kwargs):
    ...     try:
    ...         yield
    ...     except Exception as exc:
    ...         print("Raised %r for %s/%s" % (exc, args, kwargs))
    ...         raise

Works as expected with generators:

.. sourcecode:: pycon

    >>> @log_errors
    ... def broken_generator():
    ...     yield 1
    ...     raise RuntimeError()
    >>> raises(RuntimeError, lambda: list(broken_generator()))
    Raised RuntimeError() for ()/{}
    ...

    >>> @log_errors
    ... def broken_function():
    ...     raise RuntimeError()
    >>> raises(RuntimeError, broken_function)
    Raised RuntimeError() for ()/{}
    ...

-----

``aspectlib``
=============

* **This presentation**:

    https://github.com/ionelmc/python-aspectlib/tree/master/docs/presentations

* ``aspectlib`` **does many more things, check it out**:

    http://python-aspectlib.readthedocs.org/en/latest/
