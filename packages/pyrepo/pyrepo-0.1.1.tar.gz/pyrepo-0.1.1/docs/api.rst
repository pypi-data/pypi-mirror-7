API Documentation
==================

.. module:: pyrepo

This documentation covers the interfaces exposed by Pyrepo.

Repositories
-------------

.. autoclass:: Repository
    :members:

.. autoclass:: RepoImporter
    :members:
    :private-members:

.. autoexception:: ImportPathError

Commands
---------

.. currentmodule:: pyrepo.commands

.. autoclass:: Command
    :members:

.. autodata:: git_command
.. autodata:: default_commands

Hosts
------

.. currentmodule:: pyrepo.hosts

.. autoclass:: Host
    :members:

.. autodata:: github_host
.. autodata:: bitbucket_host
.. autodata:: default_hosts




