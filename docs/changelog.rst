.. _changelog:

ChangeLog
=========

Changes to the library are recorded here.

v0.1.6
------

  * Reconnect handling
  * Testing against Celery
    * must use ``-P gevent`` flag, ``eventlet`` is known to immediately hang forever


v0.1.5
------

  * Hotfix for connection pooling context manager


v0.1.4
------

  * Connection Pooling and Green Thread Friendly sockets using the ``gevent`` library.
    * Using gevent.socket directly, no monkey patching.


v0.1.3
------

  * Hotfix for new setup.py ``install_requires``


v0.1.2
------

  * Authentication Fixed
  * Coverage Testing
  * Fixed broken tests.