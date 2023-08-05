Pyrepo
======

.. image:: https://travis-ci.org/dghubble/pyrepo.png
    :target: https://travis-ci.org/dghubble/pyrepo

Pyrepo is a repository abstraction package which provides a Python API for fetching and managing a variety of repositories.

Install
-------

Install Pyrepo via `pip <https://pip.pypa.io/en/latest/>`_

.. code-block:: bash

    $ pip install pyrepo


Usage
-----

.. code-block:: pycon

    from pyrepo import Repository, git_command
    repo = Repository("github.com/dghubble/pyrepo", git_command, "https://github.com/dghubble/pyrepo.git")
    repo.clone()
    repo.update()

Documentation
-------------

Documentation is available `here <http://pyrepo.readthedocs.org/en/latest/>`_.


Contributing
------------

To get the source from Github

.. code-block:: bash

    $ git clone git@github.com:dghubble/pyrepo.git
    $ cd pyrepo
    $ python setup.py develop


Testing
-------

.. code-block:: bash

    $ pip install nose
    $ cd pyrepo
    $ nosetests
    ....
    ----------------------------------------------------------------------
    Ran 4 tests in 0.147s

    OK


Questions, Comments, Contact
----------------------------

If you'd like to contact me, you can Tweet to `@dghubble <https://twitter.com/dghubble>`_ or email dghubble@gmail.com.


License
-------

`MIT License <LICENSE>`_















