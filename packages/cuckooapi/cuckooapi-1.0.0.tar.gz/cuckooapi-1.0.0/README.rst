cuckooapi
=========

Client for Cuckoo's REST API.

Installation |Version| |Coverage| |TravisCI|
--------------------------------------------

.. code-block:: bash

   $ pip install cuckooapi


Usage example
-------------

.. code-block:: python

   >>> from cuckooapi import CuckooAPI
   >>> api=CuckooAPI('http://cuckoohost:8090')
   >>> response=api.cuckoo_status.get()
   >>> response.data
   {u'hostname': u'cuckoohost',
    u'machines': {u'available': 18, u'total': 18},
    u'tasks': {u'completed': 76,
     u'pending': 0,
     u'reported': 48268,
     u'running': 0,
     u'total': 48636},
    u'version': u'1.0-dev'}
   >>> response.data['tasks']['pending']
   0
   >>> response.data['tasks']['running']
   0

Endpoint Reference
------------------

https://github.com/cuckoobox/cuckoo/blob/master/docs/book/src/usage/api.rst

.. |TravisCI| image:: https://travis-ci.org/nilp0inter/cuckooapi.svg
    :target: https://travis-ci.org/nilp0inter/cuckooapi

.. |Version| image:: https://pypip.in/version/cuckooapi/badge.png
    :target: https://pypi.python.org/pypi/cuckooapi/
    :alt: Latest Version

.. |Coverage| image:: https://coveralls.io/repos/nilp0inter/cuckooapi/badge.png
    :target: https://coveralls.io/r/nilp0inter/cuckooapi
