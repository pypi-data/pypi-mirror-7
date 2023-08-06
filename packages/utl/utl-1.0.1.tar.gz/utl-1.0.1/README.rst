utl
===

This is a simply one-function utility. The purpose is to print available tests without executing them.
It should be used with standard `*python's unit tests* <https://docs.python.org/3.4/library/unittest.html>`_.

**utl** stands for **u**-nit **t**-est **l**-ister.

.. image:: https://pypip.in/version/utl/badge.svg
    :target: https://pypi.python.org/pypi/utl
    :alt: Latest PyPI version

Usage
-----

You can see it in action on `this asciicast <https://asciinema.org/a/11852>`_.


Note:
^^^^^

If you run *UTL* with Django project, pass *env. var.* like this:

    $ DJANGO_SETTINGS_MODULE=mysite.settings; utl <dir-to-scan-for-tests>

see details `Django doc <https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings>`_.


Installation
------------

As other python packages::

     pip install utl

Links:
------

* source on `Bitbucket <https://bitbucket.org/xliiv/utl>`_


Licence
-------

`Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0) <http://creativecommons.org/licenses/by-sa/3.0>`_


Authors
-------

Many thanks to `Vaultah  <http://stackoverflow.com/users/2301450/vaultah>`_
because he|she cover the main work on `stackoverflow <http://stackoverflow.com/a/24478809/740067>`_

Wrapping Vaultah's work into package was done by `xliiv <tymoteusz.jankowski@gmail.com>`_.

Future features
---------------
- process and pass all possible `unittest.discovery <https://docs.python.org/3.4/library/unittest.html#test-discovery>`_ params
- 'entry point' could be in package notation, eg.:
    foo.bar.baz
- show some sort of statistics
