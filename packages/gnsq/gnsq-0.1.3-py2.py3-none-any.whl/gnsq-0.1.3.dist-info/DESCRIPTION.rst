===============================
gnsq
===============================

.. image:: https://badge.fury.io/py/gnsq.svg
    :target: http://badge.fury.io/py/gnsq

.. image:: https://travis-ci.org/wtolson/gnsq.svg?branch=master
        :target: https://travis-ci.org/wtolson/gnsq

.. image:: https://pypip.in/d/gnsq/badge.png
        :target: https://pypi.python.org/pypi/gnsq


A `gevent`_ based `NSQ`_ driver for Python.

Features include:

* Free software: BSD license
* Documentation: http://gnsq.readthedocs.org.
* Battle tested on billions and billions of messages `</sagan>`.
* Based on `gevent`_ for fast concurrent networking.
* Fast and flexible signals with :doc:`Blinker <signals>`.

Installation
------------

At the command line::

    $ easy_install gnsq

Or even better, if you have virtualenvwrapper installed::

    $ mkvirtualenv gnsq
    $ pip install gnsq

Usage
-----

To use gnsq in a project::

    import gnsq
    reader = gnsq.Reader('topic', 'channel', 'localhost:4150')

    @reader.on_message.connect
    def handler(reader, message):
        do_work(message.body)

    reader.start()


.. _gevent: http://gevent.org/
.. _NSQ: http://nsq.io/




History
-------

0.1.3 (2014-07-08)
~~~~~~~~~~~~~~~~~~

* Block as expected on start, even if already started.
* Raise runtime error if starting the reader without a message handler.
* Add on_close signal to the reader.
* Allow upgrading to tls+snappy or tls+deflate.

0.1.2 (2014-07-08)
~~~~~~~~~~~~~~~~~~

* Flush delfate buffer for each message.

0.1.1 (2014-07-07)
~~~~~~~~~~~~~~~~~~

* Fix packaging stream submodule.
* Send queued messages before closing socket.
* Continue to read from socket on EAGAIN


0.1.0 (2014-07-07)
~~~~~~~~~~~~~~~~~~

* First release on PyPI.


