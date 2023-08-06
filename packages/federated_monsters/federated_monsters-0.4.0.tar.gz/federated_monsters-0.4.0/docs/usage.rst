========
Usage
========

To use Federated Monsters in a project::

	import federated_monsters

Box
---

Running a box is as simple as

.. code-block:: python

    from federated_monsters.box import Box
    b = Box(port=8888, db_fn="example_database_file.db")
    b.run()

This loop can be exited cleanly by hitting :kbd:`Control-c`

Client
------

As yet, there is no official client module. However, you can connect to a box using many methods, including telnet.

However, it can be done from Python.

.. code-block:: python

    from federated_monsters import client

    # connect to a local box
    conn = client.gen_conn("localhost")
    # wait for a response and print the output
    client.wait_for_response(conn, out=True)

    # send an /echo command
    client.send_msg(conn, "/echo Hello, world!")
    client.wait_for_response(conn, out=True)
