m2websocket
===========

Makes handling websockets with `Mongrel2 <http://mongrel2.org/>`__ and
Python easy.

This module was lovingly crafted for `First
Opinion <http://firstopinionapp.com>`__.

Example
-------

Typical websocket *hello world* type example, creating an echo server:

.. code:: python

    from m2websocket import Connection

    conn = Connection("tcp://localhost:port", "tcp://localhost:port")

    while True:
        req = conn.recv_frame()
        conn.reply_websocket(req, req.body, req.opcode)

Yup, that's all there is to it, much easier than `this
example <https://github.com/zedshaw/mongrel2/blob/master/examples/ws/python/echo.py>`__.

You can see a working example of the echo server (with a working
mongrel2 conf file and python script) by looking in the ``example/``
directory in the Github repo.

Install it
----------

Prerequisites
~~~~~~~~~~~~~

You'll need to install the mongrel2 python library from the `mongrel2
source <https://github.com/zedshaw/mongrel2/tree/master/examples/python>`__.
Once you've cloned the source or downloaded that folder, you can install
it using ``setup.py``

::

    $ cd /path/to/mongrel2/src/examples/python
    $ python setup.py install

Then, you can install this module using pip:

::

    pip install m2websocket

Or:

::

    pip install git+https://github.com/firstopinion/m2websocket#egg=m2websocket

License
-------

MIT
