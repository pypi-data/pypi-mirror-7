sprockets.clients.memcached
===========================
Memcached client wrapper that is configured via environment variables.

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------
``sprockets.clients.memcached`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets.clients.memcached>`_
and can be installed via ``pip`` or ``easy_install``:

.. code:: bash

  pip install sprockets.clients.memcached

Documentation
-------------
https://sprocketsclientsmemcached.readthedocs.org

Requirements
------------
-  `python-memcached <https://pypi.python.org/pypi/python-memcached>`_ (Python 2)
-  `python3-memcached <https://pypi.python.org/pypi/python3-memcached>`_ (Python 3)

Example
-------
The following example sets the environment variables for connecting to
memcached on ``192.168.1.2`` and ``192.168.1.3`` and subsequently issuing a few
memcached commands:

.. code:: python

    import os

    from sprockets.clients import memcached

    os.environ['MEMCACHED_SERVERS'] = '192.168.1.2:11211,192.168.1.3:11211'


    client = memcached.Client()
    client.set('foo', 'bar')
    print(client.get('foo'))


Version History
---------------
Available at https://sprocketsclientsmemcached.readthedocs.org/en/latest/history.html

.. |Version| image:: https://badge.fury.io/py/sprockets.clients.memcached.svg?
   :target: http://badge.fury.io/py/sprockets.clients.memcached

.. |Status| image:: https://travis-ci.org/sprockets/sprockets.clients.memcached.svg?branch=master
   :target: https://travis-ci.org/sprockets/sprockets.clients.memcached

.. |Coverage| image:: https://img.shields.io/coveralls/sprockets/sprockets.clients.memcached.svg?
   :target: https://coveralls.io/r/sprockets/sprockets.clients.memcached

.. |Downloads| image:: https://pypip.in/d/sprockets.clients.memcached/badge.svg?
   :target: https://pypi.python.org/pypi/sprockets.clients.memcached

.. |License| image:: https://pypip.in/license/sprockets.clients.memcached/badge.svg?
   :target: https://sprocketsclientsmemcached.readthedocs.org