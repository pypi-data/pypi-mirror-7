hat-trie
========

HAT-Trie structure for Python (2.x and 3.x).

This package is a Python wrapper for `hat-trie`_ C library.

.. image:: https://travis-ci.org/kmike/hat-trie.png?branch=master
    :target: https://travis-ci.org/kmike/hat-trie

.. _hat-trie: https://github.com/dcjones/hat-trie

Installation
============

::

    pip install hat-trie

Usage
=====

Create a new trie::

    >>> from hat_trie import Trie
    >>> trie = Trie()

``trie`` variable is a dict-like object that support unicode
keys and can have any Python object as a value. For keys that share prefixes
it usually uses less memory than Python dict.

There is also ``hat_trie.IntTrie`` which only supports positive
integers as values. It can be more efficient when you don't need
arbitrary objects as values. For example, if you need to store float
values then storing them in an array (either numpy or stdlib's ``array.array`)
and using IntTrie values as indices could be more memory efficient
than storing Python float objects directly in ``hat_trie.Trie``.

Currently implemented methods are:

* __getitem__()
* __setitem__()
* __contains__()
* __len__()
* get()
* setdefault()
* keys()
* iterkeys()

Other methods are not implemented - contributions are welcome!

Performance
===========

Performance is measured for ``hat_trie.Trie`` against Python's dict with
100k unique unicode words (English and Russian) as keys and '1' numbers
as values.

Benchmark results for Python 3.3 (intel i5 1.8GHz,
"1.000M ops/sec" == "1 000 000 operations per second")::

    dict __getitem__ (hits)      6.874M ops/sec
    trie __getitem__ (hits)      3.754M ops/sec
    dict __contains__ (hits)     7.035M ops/sec
    trie __contains__ (hits)     3.772M ops/sec
    dict __contains__ (misses)   5.356M ops/sec
    trie __contains__ (misses)   3.364M ops/sec
    dict __len__                 785958.286 ops/sec
    trie __len__                 574164.704 ops/sec
    dict __setitem__ (updates)   6.830M ops/sec
    trie __setitem__ (updates)   3.472M ops/sec
    dict __setitem__ (inserts)   6.774M ops/sec
    trie __setitem__ (inserts)   2.460M ops/sec
    dict setdefault (updates)    3.522M ops/sec
    trie setdefault (updates)    2.680M ops/sec
    dict setdefault (inserts)    4.062M ops/sec
    trie setdefault (inserts)    1.866M ops/sec
    dict keys()                  189.564 ops/sec
    trie keys()                  16.067 ops/sec


HAT-Trie is about 1.5x faster that `datrie`_ on all supported operations;
it also supports fast inserts unlike datrie. On the other hand,
datrie has more features (e.g. better iteration support and richer API);
datrie is also more memory efficient.

If you need a memory efficient data structure and don't need inserts
then marisa-trie_ or DAWG_ should work better.

.. _datrie: https://github.com/kmike/datrie
.. _marisa-trie: https://github.com/kmike/marisa-trie
.. _DAWG: https://github.com/kmike/DAWG

Contributing
============

Development happens at github:

* https://github.com/kmike/hat-trie

Feel free to submit ideas, bugs, pull requests or regular patches.

Please don't commit changes to generated C files; I will rebuild them myself.

Running tests and benchmarks
----------------------------

Make sure `tox`_ is installed and run

::
    # ./update_c.sh
    $ tox

from the source checkout. You will need Cython_ to do that.

Tests should pass under python 2.6, 2.7, 3.2, 3.3 and 3.4.

::

    $ tox -c bench.ini

runs benchmarks.

.. _Cython: http://cython.org
.. _tox: http://tox.testrun.org

Authors & Contributors
----------------------

* Mikhail Korobov <kmike84@gmail.com>
* Brandon Forehand <b4hand@users.sf.net>
* https://github.com/yflau
* Michael Heilman <https://github.com/mheilman/>

This module wraps `hat-trie`_ C library by Daniel Jones & contributors.

License
=======

Licensed under MIT License.
