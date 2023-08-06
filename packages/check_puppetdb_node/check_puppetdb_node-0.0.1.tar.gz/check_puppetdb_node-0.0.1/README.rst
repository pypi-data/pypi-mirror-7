##############
check_puppetdb_node
##############

check_puppetdb_node is a Nagios / Icinga plugin that allows you to check the
agent/run status by querying PuppetDB. This is more robust and reliable
than parsing the report YAML that the agent might store on disk.

This plugin requires:
    * `pypuppetdb`_

.. _pypuppetdb: https://github.com/nedap/pypuppetdb


Installation
============

You can install this package from source or from PyPi.

.. code-block:: bash

   $ pip install check_puppetdb_node

.. code-block:: bash

   $ git clone https://github.com/daenney/check_puppetdb_node
   $ pip install .

If you wish to hack on this, clone the repository as above but instead run:

.. code-block:: bash

   $ pip install -e .


Usage
=====

Once you have check_puppetdb_node installed simply call the script with the
`--help` argument for more information

Contributing
============

We welcome contributions to this library. However, there are a few ground
rules contributors should be aware of.

License
-------
This project is licensed under the Apache v2.0 License. As such, your
contributions, once accepted, are automatically covered by this license.

Copyright (c) 2013-2014 Daniele Sluijters

Commit messages
---------------
Write decent commit messages. Don't use swear words and refrain from
uninformative commit messages as 'fixed typo'.

The preferred format of a commit message:

::

    docs/quickstart: Fixed a typo in the Nodes section.

    If needed, elaborate further on this commit. Feel free to write a
    complete blog post here if that helps us understand what this is
    all about.

    Fixes #4 and resolves #2.

If you'd like a more elaborate guide on how to write and format your commit
messages have a look at this post by `Tim Pope`_.

.. _Tim Pope: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

Tests
-----

This project does not have a test-suite but it will check for PEP-8 style
violations. This is done using py.test and the pytest-pep8 plugin.
