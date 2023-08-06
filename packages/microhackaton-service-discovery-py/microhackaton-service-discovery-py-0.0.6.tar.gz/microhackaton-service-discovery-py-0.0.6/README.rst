service-discovery-py
====================

Python library to interact with other microservices at http://microhackaton.github.io/2014/

Installation
++++++++++++

You can get it from https://pypi.python.org/pypi/microhackaton-service-discovery-py

.. code-block:: bash

  $ pip install microhackaton-service-discovery-py

Usage
+++++

.. code-block:: python

  from service_discovery import ServiceDiscovery

  sd = ServiceDiscovery('/pl/pl/microhackaton', 'zookeeper.microhackathon.pl:2181')

How to register your service?
-----------------------------
.. code-block:: python

  instance_id = sd.register('something-collector', '12.34.56.78', 8080)

How to find instances of other service?
---------------------------------------

.. code-block:: python

  urls_as_list = sd.get_instances('blog-collector')

How to find random service instance?
-------------------------------------

.. code-block:: python

  url_as_str = sd.get_instance('blog-collector')
