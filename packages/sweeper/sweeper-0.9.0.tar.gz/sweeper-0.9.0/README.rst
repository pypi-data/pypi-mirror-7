sweeper
=======

Find duplicate files and perform action.

Usage
=====

Print duplicates

.. code:: python

    from sweeper import Sweeper
    swp = Sweeper(['images1', 'images2'])
    dups = swp.file_dups()
    print(dups)

Remove duplicate files

.. code:: python

    from sweeper import Sweeper
    swp = Sweeper(['images1', 'images2'])
    swp.rm()

Perform custom action

.. code:: python

    from sweeper import Sweeper
    swp = Sweeper(['images'])
    for f, h, dups in swp:
        print('encountered {} which duplicates with already found duplicate files {} with hash {}'.format(f, dups, h))

As script::

    python -m sweeper/sweeper --help

As installed console script::
    
    sweeper --help

Installation
============

from source::

    python setup.py install

or from PyPI::

    pip install sweeper

Documentation
=============

this README.rst, code itself, docstrings

sweeper can be found on github.com at:

https://github.com/darko-poljak/sweeper

Tested With
===========

Python2.7, Python3

