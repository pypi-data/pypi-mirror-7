Subset of ``set`` designed to conveniently hold sets of integers. It creates
them from, and displays them as, integer spans (e.g. ``1-3,14,29,92-97``). When
iterating, ``pop()``-ing an item, or converting to a list, ``intspan`` behaves as
if it were an ordered collection.

The main draw is that this provides a convenient way
to specify ranges--for example, ranges of rows to be processed in a spreadsheet.

Usage
=====

::

    from intspan import intspan

    s = intspan('1-3,14,29,92-97')
    s.discard('2,13,92')
    print s
    print repr(s)
    print list(s)

yields::

    1,3,14,29,93-97
    intspan('1,3,14,29,93-97')
    [1, 3, 14, 29, 93, 94, 95, 96, 97]

While::

    for n in intspan('1-3,5'):
        print n                 # Python 2

yields::

    1
    2
    3
    5

Most set operations such as intersection, union, and so on are available just
as they are in Python's ``set``. In addition, if you wish to extract the
contiguous ranges::

    for r in intspan('1-3,5,7-9,10,21-22,23,24').ranges():
        print r                 # Python 2

yields::

    (1, 3)
    (5, 5)
    (7, 10)
    (21, 24)

There is a corresponding constructor::

    print intspan.from_ranges([ (4,6), (10,12) ])

Gives::

    4-6,10-12

Performance
===========

``intspan`` piggybacks Python's ``set``, so it stores every integer individually.
Unlike Perl's ``Set::IntSpan`` it is not
optimized for long contiguous runs. For sets of several hundred or thousand
members, you will probably never notice the difference.

On the other hand, if you're doing lots of processing of
large sets (e.g. with 100,000 or more elements), or doing lots of set operations
on them (e.g. union, intersection), a data structure based on
lists of ranges, `run length encoding
<http://en.wikipedia.org/wiki/Run-length_encoding>`_, or `Judy arrays
<http://en.wikipedia.org/wiki/Judy_array>`_ might perform / scale
better.

Alternatives
============

There are several modules you might want to consider as
alternatives or supplements. AFAIK, none of them provide the convenient
integer span specification that ``intspan`` does, but they have other virtues:

 *  `cowboy <http://pypi.python.org/pypi/cowboy>`_ provides
    generalized ranges and multi-ranges. Bonus points
    for the package tagline:
    "It works on ranges."

 *  `rangeset <http://pypi.python.org/pypi/rangeset>`_ is a generalized range set
    module. It also supports infinite ranges.

 *  `judy <http://pypi.python.org/pypi/judy>`_ a Python wrapper around Judy arrays
    that are implemented in C. No docs or tests to speak of.

Notes
=====

 *  Version 1.0 immediately follows 0.73. Bumped to institute a 
    cleaner "semantic versioning"
    scheme. Upgraded from "beta" to "production" status. 

 *  Version 0.73 updates testing to include the latest Python 3.4

 *  Version 0.7 fixed parsing of spans including negative numbers, and
    added the ``ranges()`` method. As of 0.71, the ``from_ranges()``
    constructor appeared.

 *  Though inspired by Perl's `Set::IntSpan <http://search.cpan.org/~swmcd/Set-IntSpan-1.16/IntSpan.pm>`_,
    that's where the similarity stops.
    ``intspan`` supports only finite sets, and it
    follows the methods and conventions of Python's ``set``.

 *  ``intspan`` methods and operations such as ``add()`` ``discard()``, and
    ``>=`` take integer span strings, lists, and sets as arguments, changing
    facilities that used to take only one item into onces that take multiples,
    inlcuding arguments that are technically string specifications rather than
    proper ``intspan`` objects.

 *  String representation and ``ranges()`` method
    based on Jeff Mercado's concise answer to `this
    StackOverflow question <http://codereview.stackexchange.com/questions/5196/grouping-consecutive-numbers-into-ranges-in-python-3-2>`_.
    Thank you, Jeff!

 *  Automated multi-version testing managed with the wonderful
    `pytest <http://pypi.python.org/pypi/pytest>`_,
    `pytest-cov <http://pypi.python.org/pypi/pytest>`_,
    and `tox <http://pypi.python.org/pypi/tox>`_.
    Successfully packaged for, and tested against, all late-model verions of
    Python: 2.6, 2.7, 3.2, 3.3, and 3.4, as well as PyPy 2.2.1 (based on 2.7.3).
    Test line coverage ~100%.

 *  The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
    `@jeunice on Twitter <http://twitter.com/jeunice>`_
    welcomes your comments and suggestions.

Installation
============

To install the latest version::

    pip install -U intspan

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade intspan

(You may need to prefix these with "sudo " to authorize installation.)
