.. _home:

rexpro
======

rexpro is an experimental RexPro socket interface for python


.. image:: https://app.wercker.com/status/6a2160385debe13745f2ff3eec734dac/m/master
   :alt: Build Status
   :align: center
   :target: https://app.wercker.com/project/bykey/6a2160385debe13745f2ff3eec734dac



.. _features:

Features
--------

 - Straightforward syntax
 - Connection Pooling Support
 - Gevent Compatible - see ``rexpro.connectors.rgevent``
 - Eventlet Compatible - see ``rexpro.connectors.reventlet``
 - Tested against Celery
    - Only Gevent has been tested (must use ``-P gevent`` argument)
    - Testing needed against default prefork method, and eventlet


.. _links:

Links
-----

* Documentation: http://rexpro.readthedocs.org/
* Official Repository: https://github.com/platinummonkey/rexpro.git
* Package: https://pypi.python.org/pypi/rexpro/

rexpro is known to support Python 2.7. Python 3.x is not compatible due to the use of gevent.


.. _download:

Download
--------

PyPI: https://pypi.python.org/pypi/rexpro/

.. code-block:: sh

    $ pip install rexpro

Source: https://github.com/platinummonkey/rexpro-python.git

.. code-block:: sh

    $ git clone git://github.com/platinummonkey/rexpro-python.git
    $ python setup.py install


Contents
--------

.. toctree::
   :maxdepth: 2

   Home <self>
   quickstart
   internals/index
   changelog
   contribute



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

