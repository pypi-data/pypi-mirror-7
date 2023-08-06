prtdep
=======

CRUX linux ports dependencies helper.
Help resolving dependencies for CURX ports.
It calculates dependencies for specified list of ports root paths.
It can list dependencies for list of packages, list packages that
depend on specified list of packages. For specified packages it
can print list of packages that can freely be removed after them
to have system without orphans.

Usage
=====

As library

.. code:: python

    from prtdep import prtdep
    prtdep = prtdep.Prtdep('/usr/ports')
    prtdep.calc_deps()
    ...

For a complete list of functionality see source code.

As script::

    python prtdep.py --help

As installed console script::
    
    prtdep --help

Installation
============

from source::

    python setup.py install

or from PyPI::

    pip install prtdep

Documentation
=============

this README.rst, code itself, docstrings

prtdep can be found on github.com at:

https://github.com/darko-poljak/prtdep
