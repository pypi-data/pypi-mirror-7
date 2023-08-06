.. :protocol:

Protocol
--------

In order to transfer data, a custom protocol associated with the box servers has been created. In order to make it easy to develop new implementations of the game and server, this protocol will be openly documented here.

Basic Overview
==============

When a client wishes to connect to a server, the following steps are taken.

 1. The client seeks to establish a connection with the server, usually on port 8888
 2. Once the connection is established, the server indicates that the connection has been successful. If not, the client will time out.
 3. Upon receiving this signal, the client will send any commands it wishes one at a time, waiting for the server's response each time.
 4. Once it has finished sending all of its commands, the client will disconnect the socket and the server will close the thread.
 
 An example session could go along these lines:

 .. code-block:: console

    Hello, and welcome to 192.168.1.6
    $ /echo Hello, world!
    Hello, world!
    $ /uploadmonster [JSON-serialized monster]
    OK

Status Codes
============

The status codes numbering scheme is the same as the one used by HTTP.

* 1XX: Informational
* 2XX: Success
* 3XX: Redirection
* 4XX: Client Error
* 5XX: Server Error

While no applications for the 3XX codes has yet been decided, they are reserved for future use.

The return format is as follows::

    NUMBER STATUS_CODE [Additional data]

So, for example::

    200 OK Hello world

Code List
~~~~~~~~~

===  ======================  ==========================================
Status Code                  Explanation
---------------------------  ------------------------------------------
100  CONNECTED               A connection to the server has been made
101  RESPONSE_REQUIRED       A response from the client is required
200  OK                      The request has succeeded
400  BAD_REQUEST             The request is not in a valid format
401  BAD_HASH                The hash supplied is invalid
402  BAD_MONSTER             The monster uploaded is not valid
403  BAD_COMMAND             The command requested is unknown
404  NOT_FOUND               The box has no monster matching request
500  FAIL                    The server was unable to comply
===  ======================  ==========================================