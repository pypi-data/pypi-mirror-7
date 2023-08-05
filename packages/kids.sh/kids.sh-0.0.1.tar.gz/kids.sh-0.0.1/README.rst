=======
kids.sh
=======

.. image:: https://pypip.in/v/kids.sh/badge.png
    :target: https://pypi.python.org/pypi/kids.sh

.. image:: https://secure.travis-ci.org/0k/kids.sh.png?branch=master
    :target: http://travis-ci.org/0k/kids.sh


``kids.sh`` is a Python library providing helpers when calling shell
commands thanks to python. It's part of 'Kids' (for Keep It Dead Simple)
library.

It is, for now, a very humble package.


Features
--------

using ``kids.sh``:

- Call ``wrap()`` when you want to call a system command and you don't
  have to bother about subprocess and other stuff. You get the standard
  output of the command as the return string.

These assumptions are in the code:

- You don't want to deal with precise subprocess things, don't really need to
  care about security (because system command you launch are hard-written).
- You don't need asynchronous code.


Requirements
------------

This code is tested and work with python 2.7.6 and 3.2 and 3.4
