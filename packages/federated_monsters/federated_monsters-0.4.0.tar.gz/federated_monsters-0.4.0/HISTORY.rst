.. :changelog:

History
-------

0.4.0 (2014-07-15)
==================

* Fix issue with database not working in tests

    - Note: Do not run BerkeleyDB.close! It will make the database unreadable for some weird-ass reason

* Ran files through ``isort``
* Fix loop in ``federated_monsters.box.Box.run()`` so that it exits cleanly on ``KeyboardInterrupt``
* Add to the ``usage`` section
* Add ``federated_monsters.box.Client`` class to make chat handling easier
* Use ``federated_monsters.box.Client`` throughout ``federated_monsters.box``
* Add code to implement chat, but not going to add it in until some implementation details are fixed
* Add ``federated_monsters.crypto`` so monsters can be encrypted before upload

    - Prevent server owners form jacking all the monsters

* Add tests for ``federated_monsters.crypto``
* Fix ``setup.py`` so requirements aren't just for Python 3
* Change return type of ``federated_monsters.crypto.gen_key()`` to ``collections.namedtuple``
* Add support for encryption to ``federated_monsters.box.Box``
* Add tests for ``federated_monsters.crypto`` and encrypted uploads

0.3.1 (2014-07-08)
==================

* Update ``.travis.yml`` to finally get it to build

    - Had to remove builds for all Python versions except 2.7 and 3.2
    - thx ubuntu

* Move requirements from ``requirements.txt`` to ``setup.py``
* Update ``README.rst`` to fix badges
* Change doc settings so building on Read The Docs works

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