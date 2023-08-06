service-discovery-py
====================

Python library to interact with other miocroservices at http://microhackaton.github.io/2014/

Installation
++++++++++++

```bash
$ pip install microhackaton-service-discovery-py
```

Usage
+++++

```python
from service_discovery import ServiceDiscovery

sd = ServiceDiscovery('/pl/pl/microhackaton', 'zookeeper.microhackathon.pl:2181')
```

How to register your service?
-----------------------------

```python
instance_id = sd.register('something-collector', '12.34.56.78', 8080)
```

How to find instances of other service?
---------------------------------------

```python
urls_as_list = sd.get_instances('blog-collector')
```

How to find random service instance?
-------------------------------------

```python
url_as_str = sd.get_instances('blog-collector')
```
