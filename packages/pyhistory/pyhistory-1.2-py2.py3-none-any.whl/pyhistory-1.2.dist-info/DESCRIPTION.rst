===============================
Python History
===============================

.. image:: https://badge.fury.io/py/pyhistory.png
    :target: http://badge.fury.io/py/pyhistory

.. image:: https://travis-ci.org/beregond/pyhistory.png?branch=master
        :target: https://travis-ci.org/beregond/pyhistory

.. image:: https://pypip.in/d/pyhistory/badge.png
        :target: https://pypi.python.org/pypi/pyhistory


Package to help maintaining HISTORY file for Python project.

* Free software: BSD license
* Documentation: http://pyhistory.readthedocs.org.

Note
----

This package is created to help maintaining history file in environment of high
concurrency (literally: each pull request on GitHub had conflicts in
HISTORY.rst file because it was updated before creating PR). Take into account
it may NOT fit into your environment and/or workflow since it was cutted for
specific case, but it's good if so. :)

Features
--------

(All commands can start either with `pyhistory` or `pyhi`.)

* Add history entry:

.. code-block:: bash

    $ pyhi add 'New feature'
    $ pyhi add Something

* List history entries:

.. code-block:: bash

    $ pyhi list

    * New feature
    * Something

* Update your history file with entries for given release:

.. code-block:: bash

    $ pyhi update 0.4.2

* Delete selected entries:

.. code-block:: bash

    $ pyhi delete

    1. New feature
    2. Something
    3. Another one
    4. Wrong one

    (Delete by choosing entries numbers.)

    $ pyhi delete 2 4
    $ pyhi list

    * New feature
    * Another one

* Clear all history:

.. code-block:: bash

    $ pyhi clear




History
-------

1.2 (2014-07-22)
++++++++++++++++

* Added delete command.

1.1 (2014-07-15)
++++++++++++++++

* Added timestamp to generated files, so now entries are properly ordered.
* Pyhistory traverses directory tree to find proper place for history directory.

1.0.3 (2014-06-23)
++++++++++++++++++

* Added squash command (alias to update).

1.0.2 (2014-06-22)
++++++++++++++++++

* Further bug fixing of start detecting.

1.0.1 (2014-06-20)
++++++++++++++++++

* Fixed error raised by `clear` when history dir is absent.
* Fixed `update` - command will now try to find file start.

1.0 (2014-06-20)
++++++++++++++++

* First release on PyPI.


