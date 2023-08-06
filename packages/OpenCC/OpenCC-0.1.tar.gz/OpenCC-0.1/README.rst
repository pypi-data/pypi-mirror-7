OpenCC for Python
=================

An OpenCC_ converter for Python.

.. _OpenCC: https://github.com/BYVoid/OpenCC

Installation
------------

You should install OpenCC (0.4.3) library first.

Install the python library with pip::

    $ pip install OpenCC


Features
--------

1. Compatible with CPython and PyPy (c-types)
2. Cython implementation (TODO)


Usage
-----

This library has only one method::

    >>> import opencc
    >>> opencc.convert('乾坤一擲')
    >>> opencc.convert('乾坤一掷', config='zhs2zht.ini')

Config
------

Convert method accepts an additional config parameter. Available configs::


    zhs2zhtw_p.ini
    zhs2zhtw_v.ini
    zhs2zhtw_vp.ini
    zht2zhtw_p.ini
    zht2zhtw_v.ini
    zht2zhtw_vp.ini
    zhtw2zhs.ini
    zhtw2zht.ini
    zhtw2zhcn_s.ini
    zhtw2zhcn_t.ini
    zhs2zht.ini
    zht2zhs.ini
