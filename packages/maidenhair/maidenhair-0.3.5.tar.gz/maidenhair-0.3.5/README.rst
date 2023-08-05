maidenhair
=============
.. image:: https://secure.travis-ci.org/lambdalisue/maidenhair.png?branch=master
    :target: http://travis-ci.org/lambdalisue/maidenhair
    :alt: Build status

.. image:: https://coveralls.io/repos/lambdalisue/maidenhair/badge.png?branch=master
    :target: https://coveralls.io/r/lambdalisue/maidenhair/
    :alt: Coverage

.. image:: https://pypip.in/d/maidenhair/badge.png
    :target: https://pypi.python.org/pypi/maidenhair/
    :alt: Downloads

.. image:: https://pypip.in/v/maidenhair/badge.png
    :target: https://pypi.python.org/pypi/maidenhair/
    :alt: Latest version

.. image:: https://pypip.in/wheel/maidenhair/badge.png
    :target: https://pypi.python.org/pypi/maidenhair/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/maidenhair/badge.png
    :target: https://pypi.python.org/pypi/maidenhair/
    :alt: Egg Status

.. image:: https://pypip.in/license/maidenhair/badge.png
    :target: https://pypi.python.org/pypi/maidenhair/
    :alt: License

A plugin based data load and manimupulation library.

Installation
------------
Use pip_ like::

    $ pip install maidenhair

.. _pip:  https://pypi.python.org/pypi/pip


Usage
---------
Assume that there are three kinds of samples and each samples have 5 indipendent
experimental results.
All filenames are written as the following format::

    sample-type<type number>.<experiment number>.txt

And files are saved in `data` directory like::

    +- data
        |
        +- sample-type1.001.txt
        +- sample-type1.002.txt
        +- sample-type1.003.txt
        +- sample-type1.004.txt
        +- sample-type1.005.txt
        +- sample-type2.001.txt
        +- sample-type2.002.txt
        +- sample-type2.003.txt
        +- sample-type2.004.txt
        +- sample-type2.005.txt
        +- sample-type3.001.txt
        +- sample-type3.002.txt
        +- sample-type3.003.txt
        +- sample-type3.004.txt
        +- sample-type3.005.txt

Then, the code for plotting the data will be::

    >>> import matplotlib.pyplot as plt
    >>> import maidenhair
    >>> import maidenhair.statistics
    >>> dataset = []
    >>> dataset += maidenhair.load('data/sample-type1.*.txt', unite=True)
    >>> dataset += maidenhair.load('data/sample-type2.*.txt', unite=True)
    >>> dataset += maidenhair.load('data/sample-type3.*.txt', unite=True)
    >>> nameset = ['Type1', 'Type2', 'Type3']
    >>> for name, (x, y) in zip(nameset, dataset):
    ...     xa = maidenhair.statistics.average(x)
    ...     ya = maidenhair.statistics.average(y)
    ...     ye = maidenhair.statistics.confidential_interval(y)
    ...     plt.errorbar(xa, ya, yerr=ye, label=name)
    ...
    >>> plt.show()

