===============================
pyrpo
===============================


`GitHub`_ |
`PyPi`_ |
`Warehouse`_ |
`ReadTheDocs`_ |
`Travis-CI`_


.. image:: https://badge.fury.io/py/pyrpo.png
   :target: http://badge.fury.io/py/pyrpo
    
.. image:: https://travis-ci.org/westurner/pyrpo.png?branch=master
        :target: https://travis-ci.org/westurner/pyrpo

.. image:: https://pypip.in/d/pyrpo/badge.png
       :target: https://pypi.python.org/pypi/pyrpo

.. _GitHub: https://github.com/westurner/pyrpo
.. _PyPi: https://pypi.python.org/pypi/pyrpo
.. _Warehouse: https://warehouse.python.org/project/pyrpo
.. _ReadTheDocs:  https://pyrpo.readthedocs.org/en/latest
.. _Travis-CI:  https://travis-ci.org/westurner/pyrpo

pyrpo: a shell command wrapper for hg, git, bzr, svn

Features
==========

* Wrap and parse shell commands (largely as a reference)
* Walk for repository directories
* Generate reports for one or more repositories
* Call ``hg status``, ``git status``, etc. 
* Generate mercurial ``.hgsubs``
* Generate git ``.gitsubmodule``
* Generate pip ``requirements.txt``
* Generate shell script (to rebuild environment)

  * TODO: replicate branches/tags/revisions

* Functional `namedtuples`_, `iterators`_ ``yield`` -ing `generators`_
* `optparse`_ argument parsing (``-h``, ``--help``)
* `cookiecutter-pypackage`_ project templating  


.. _namedtuples: https://docs.python.org/2/library/collections.html#collections.namedtuple 
.. _iterators: https://docs.python.org/2/howto/functional.html#iterators
.. _generators: https://docs.python.org/2/howto/functional.html#generators    
.. _optparse: https://docs.python.org/2/library/optparse.html 
.. _cookiecutter-pypackage: https://github.com/audreyr/cookiecutter-pypackage 



Installing
============
Install from `PyPi`_::

    pip install pyrpo

Install from `GitHub`_ as editable (add a ``pyrpo.pth`` in ``site-packages``)::

    pip install -e git+https://github.com/westurner/pyrpo#egg=pyrpo


Usage
=========

Print help::

    pyrpo --help

Scan for files::

    # Scan and print a shell report
    pyrpo -s . -r sh
    pyrpo

Generate a TortoiseHG ``thg-reporegistry.xml`` file::

    pyrpo -s . --thg

Generate a pip report::

    pyrpo -r pip

Generate a status report::

    pyrpo -r status

Generate an `.hgsubs` file::

    pyrpo -r hgsub

Generate a ``.gitsubmodule`` file::

    pyrpo -r gitsubmodule

Generate an origin report::

    pyrpo -r origin

Generate a string report::

    pyrpo -r str



License
========
`BSD Software License
<https://github.com/westurner/pyrpo/blob/master/LICENSE>`_
