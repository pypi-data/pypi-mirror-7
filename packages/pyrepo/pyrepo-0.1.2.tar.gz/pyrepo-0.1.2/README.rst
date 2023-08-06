Pyrepo
======

.. image:: https://pypip.in/version/pyrepo/badge.png
    :target: https://pypi.python.org/pypi/pyrepo/
    :alt: Latest Version

.. image:: https://travis-ci.org/dghubble/pyrepo.png
    :target: https://travis-ci.org/dghubble/pyrepo
    :alt: Continuous Integration Testing

.. image:: https://pypip.in/download/pyrepo/badge.png
    :target: https://pypi.python.org/pypi/pyrepo/
    :alt: Downloads

.. image:: https://pypip.in/license/pyrepo/badge.png
    :target: https://pypi.python.org/pypi/pyrepo/
    :alt: License

Pyrepo is a repository abstraction package which provides a Python API for fetching and managing a variety of repositories.

Install
-------

Install Pyrepo via `pip <https://pip.pypa.io/en/latest/>`_

.. code-block:: bash

    $ pip install pyrepo

Usage
-----

.. code-block:: pycon

    >>> import os
    >>> from pyrepo import Repository, git_command
    >>> home = os.path.expanduser('~')
    >>> repo = Repository(command=git_command, 
                          url='https://github.com/dghubble/pyrepo.git')
    >>> repo2 = Repository(import_path="github.com/dghubble/pyrepo")
    >>> repo.clone()
    >>> repo.update()

Documentation
-------------

Documentation is available `here <http://pyrepo.readthedocs.org/en/latest/>`_.


Contributing
------------

To get the source from Github

.. code-block:: bash

    $ git clone git@github.com:dghubble/pyrepo.git
    $ cd pyrepo
    $ pip install -r requirements.txt
    $ python setup.py develop

If you want to remove the development install

.. code-block:: bash

    $ cd pyrepo
    $ python setup.py develop --uninstall


Testing
-------

.. code-block:: bash

    $ pip install nose
    $ nosetests
    ............
    ----------------------------------------------------------------------
    Ran 14 tests in 0.707s

    OK


Questions, Comments, Contact
----------------------------

If you'd like to contact me, feel free to Tweet to `@dghubble <https://twitter.com/dghubble>`_ or email dghubble@gmail.com.


License
-------

`MIT License <LICENSE>`_
