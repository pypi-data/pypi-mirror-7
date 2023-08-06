Safe
====

Is your password safe? **Safe** will check the password strength for you.

.. image:: https://travis-ci.org/lepture/safe.png?branch=master
   :target: https://travis-ci.org/lepture/safe

How it works
------------

**Safe** will check if the password has a simple pattern, for instance:

1. password is in the order on your QWERT keyboards.
2. password is simple alphabet step by step, such as: abcd, 1357

**Safe** will check if the password is a common used password.
Many thanks to Mark Burnett for the great work on `10000 Top Passwords <https://xato.net/passwords/more-top-worst-passwords/>`_.

**Safe** will check if the password has mixed number, alphabet, marks.

Installation
------------

Install Safe with pip::

    $ pip install Safe

If pip is not available, try easy_install::

    $ easy_install Safe

Usage
-----

It's very simple to check the strength of a password::

    >>> import safe
    >>> safe.safety(1)
    terrible
    >>> safe.safety('password')
    simpile
    >>> safe.safety('is.safe')
    medium
    >>> safe.safety('x*V-92Ba')
    strong
    >>> strength = safe.safety('x*V-92Ba')
    >>> bool(strength)
    True
    >>> s.level
    20
    >>> s.message
    'good password'
