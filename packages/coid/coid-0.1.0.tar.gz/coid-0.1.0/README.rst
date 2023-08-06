====
coid
====

.. image:: https://travis-ci.org/bninja/coid.png
   :target: https://travis-ci.org/bninja/coid
   
.. image:: https://coveralls.io/repos/bninja/coid/badge.png?branch=master
   :target: https://coveralls.io/r/bninja/coid?branch=master

Simple codecs for uuiids. Can be useful when you represent ids differently
between domains.

Get it:

.. code:: bash

   $ pip install coid

use it:

.. code:: python

   import uuid
   import coid
   
   id = uuid.uuid4()
    
   id_codec = coid.Id(prefix='BLA-', encoding='base58')
   assert id == id_codec.decode(id_codec.encode(id))
