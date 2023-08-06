===============================
Federated Monsters
===============================

.. image:: https://badge.fury.io/py/federated_monsters.svg
    :target: http://badge.fury.io/py/federated_monsters

.. image:: https://travis-ci.org/colatkinson/federated_monsters.svg?branch=master
        :target: https://travis-ci.org/colatkinson/federated_monsters

.. image:: https://pypip.in/d/federated_monsters/badge.svg
        :target: https://pypi.python.org/pypi/federated_monsters


Federated Monsters is a game that seeks to follow the format of games like Pokemon, but to instead use a federated server format to store and trade creatures

* Free software: GPLv3 license
* Documentation: http://federated_monsters.readthedocs.org.

Features
--------

* TODO



History
-------

0.3.0 (2014-07-06)
==================

* Fix Python 2 compatibility issues
* Begin work on communication protocol
* Update tests for new protocol
* Add support for storage in Oracle Berkeley DB
* Add ``/uploadmonster`` command
* Create simple client
* Fix weird import errors with tests

    - Required adding try-except clause to all imports

* Add generic database class
* Move opening of database file to separate function, and put it in ``Box.run()``

    - Allows for a quick switcheroo of database types for testing

* Initial protocol documentation
* Add ``/downloadmonster`` command
* Make ``Box`` strip whitespace from sent text
* Add hash authentication
* Add support for user response to server
* Update HISTORY to use code instead of italic formatting

0.2.0 (2014-07-04)
==================

* Add tests for ``box`` and ``monster``
* Create `box` module to contain server code
* Add Sphinx-compatible docstrings to all code
* Create framework for ``box`` to parse commands
* Add ``export_monster`` method to ``Monster`` to make export easier

0.1.0 (2014-07-02)
==================

* Initial release

