mongo-memoize
=============

.. image:: https://badge.fury.io/py/mongo-memoize.png
    :target: http://badge.fury.io/py/mongo-memoize

.. image:: https://travis-ci.org/ikuyamada/mongo-memoize.png?branch=master
    :target: https://travis-ci.org/ikuyamada/mongo-memoize

A Python decorator library for instantly caching function results in MongoDB.

Basic Usage
-----------

.. code-block:: python

    from mongo_memoize import memoize

    @memoize()
    def func():
        ...

Customization
-------------

You can specify custom *serializer* and *key_generator*. *serializer* is used to serialize function results in order to convert them into formats that can be stored in MongoDB. *key_generator* generates a cache key from the function arguments. *PickleSerializer* and *PickleMD5KeyGenerator* are used by default.

.. code-block:: python

    from mongo_memoize import memoize, NoopSerializer, PickleMD5KeyGenerator

    @memoize(serializer=NoopSerializer(), key_generator=PickleMD5KeyGenerator())
    def func():
        ...

Using Capped Collection
-----------------------

*Capped collection* is a MongoDB feature which allows to limit the maximum size of the collection. By setting `capped=True`, a capped collection is created automatically.

.. code-block:: python

    from mongo_memoize import memoize

    @memoize(capped=True, capped_size=100000000)
    def func():
        ...

Documentation
-------------

http://mongo-memoize.readthedocs.org/
