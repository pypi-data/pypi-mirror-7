.. -*- coding: utf-8 -*-

=============
 CwClientLib
=============

Summary
-------

A Python library to easily build CubicWeb_ clients:

* execute RQL_ queries remotely (using rqlcontroller_),
* access instances that requires authentication (using signedrequest_).

Requirements
------------

client side:

- requests_ (>= 2.0)

server side:

- CubicWeb (>= 3.18.3) with the cubes rqlcontroller_ and signedrequest_


Using signed requests
---------------------

Once the cube signedrequest_ is added, in the WebUI:

#. View a ``CWUser`` and click the action ``add an AuthToken``
#. Give an identifier to the token and make it enabled
#. Use the token identifier and the token in your source code

Using Kerberos
--------------

Just make sure `Python-Kerberos`_ and `Requests-Kerberos`_ are installed.

Examples
--------

Simple read only query:

.. code-block:: python

   import cwproxy

   client = cwproxy.CWProxy('http://www.cubicweb.org/')
   query = 'Any X WHERE X is Ticket, X concerns P, P name "cwclientlib"'
   resp = client.rql(query)
   data = resp.json()

Creating an entity, authenticating with signedrequest_:

.. code-block:: python

   import cwproxy

   auth = cwproxy.SignedRequestAuth('my token', '6ed44d82172211e49d9777269ec78bae')
   client = cwproxy.CWProxy('https://www.cubicweb.org/', auth)
   queries = [('INSERT CWUser U: U login %(l)s, U upassword %(p)s',
               {'l': 'Babar', 'p': 'cubicweb rulez & 42'}), ]
   resp = client.rqlio(query)
   data = resp.json()


Using ``builders`` helpers, authenticating with kerberos:

.. code-block:: python

   import cwproxy, builders
   from requests_kerberos import HTTPKerberosAuth, OPTIONAL

   auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
   client = cwproxy.CWProxy('https://www.cubicweb.org/', auth)
   queries = [builders.create_entity('CWUser', login='Babar', password='secret'),
              builders.build_trinfo('__r0', 'disable', 'not yet activated'),
	     ]
   resp = client.rqlio(queries)
   data = resp.json()

.. _CubicWeb: http://www.cubicweb.org/
.. _RQL: http://docs.cubicweb.org/annexes/rql/language
.. _rqlcontroller: http://www.cubicweb.org/project/cubicweb-rqlcontroller/
.. _signedrequest: http://www.cubicweb.org/project/cubicweb-signedrequest/
.. _requests: http://docs.python-requests.org/en/latest/
.. _`Python-Kerberos`: https://pypi.python.org/pypi/kerberos
.. _`Requests-Kerberos`: https://github.com/requests/requests-kerberos.git
