jsonrpc-requests: a compact JSON-RPC client library backed by `requests  <http://python-requests.org>`_
=======================================================================================================

This is a compact (~90 SLOC) and simple JSON-RPC client implementation written while debugging a picky server.

Main Features
-------------

* Python 2.7 & 3.4 compatible
* Exposes requests options
* Supports nested namespaces (eg. `app.users.getUsers()`)
* 100% test coverage

TODO
----

* Batch requests (http://www.jsonrpc.org/specification#batch)

Usage
-----
.. code-block:: python

    from jsonrpc_requests import Server
    server = Server('http://localhost:8080')
    server.foo(1, 2)
    server.foo(bar=1, baz=2)
    server.foo.bar(baz=1, qux=2)

A notification:

.. code-block:: python

    from jsonrpc_requests import Server
    server.foo(bar=1, _notification=True)

Pass through arguments to requests (see also `requests  documentation <http://docs.python-requests.org/en/latest/>`_)

.. code-block:: python

    from jsonrpc_requests import Server
    server = Server('http://localhost:8080', auth=('user', 'pass'), headers={'x-test2': 'true'})

Pass through requests exceptions

.. code-block:: python

    from jsonrpc_requests import Server, TransportError
    server = Server('http://unknown-host')
    try:
        server.foo()
    except TransportError as transport_error:
        print(transport_error.args[1]) # this will hold a `requests.exceptions.RequestException` instance


Tests
-----
Install the Python tox package and run ``tox``, it'll test this package with Python 2.7 and 3.4.

