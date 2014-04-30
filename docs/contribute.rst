.. _contribute:

Contributing
============

License
-------

``rexpro`` is distributed under the `Apache 2.0 License <http://www.apache.org/licenses/LICENSE-2.0.html>`_.


Issues
------

Issues should be opened through `GitHub Issues <http://github.com/platinummonkey/rexpro-python/issues/>`_; whenever
possible, a pull request should be included.


Pull Requests
-------------

All pull requests should pass the test suite, which can be launched simply with:

.. code-block:: sh

    $ make test

.. note::

    Running test requires `nosetests`, `coverage`, `six`, `gevent`, `redis` and `celery`.
    As well an available titan server.

In order to test coverage, please use:

.. code-block:: sh

    $ pip install coverage
    $ coverage erase; ./run_coverage.sh


Test Server
-----------

``rexpro`` was designed for `Titan <http://thinkaurelius.github.io/titan/>`_, other graph databases that utilize
`Blueprints <https://github.com/tinkerpop/blueprints/wiki>`_ may be compatible, but further testing would be needed.

Currently Titan 0.4.4 is known to work and can be downloaded:
`Titan <http://s3.thinkaurelius.com/downloads/titan/titan-server-0.4.2.zip>`_.
