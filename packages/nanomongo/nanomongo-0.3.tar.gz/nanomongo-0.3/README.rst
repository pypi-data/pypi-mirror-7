=========
nanomongo
=========

If you like using ``pymongo`` native api but often find yourself subclassing
``dict`` to add some extra logic and while you're at it, why not add some
field validations right? And index definitions, and ``pymongo.Collection``
wrappers, and ... (you get the idea).

.. image:: https://travis-ci.org/eguven/nanomongo.png
        :target: https://travis-ci.org/eguven/nanomongo

Features
--------

- single format ``Field`` definitions with type checking and a few common
  options such as ``required``, ``default``, ``auto_update``

- ``pymongo``-identical index definitions

- optional ``dot_notation``

- assignment and deletion (delta) tracking for ``'$set'`` and ``'$unset'``
  and atomic updates; you either insert or update

- ``'$addToSet'`` on ``Document``

- *upcoming* ``'$push'`` ``'$pull'`` funtionality


**note**: nanomongo is in alpha stage and in development, `documentation
<https://nanomongo.readthedocs.org>`_ is in progress as well::


    # rough example
    import pymongo
    from nanomongo import Field, BaseDocument, Index

    client = pymongo.MongoClient()

    class MyDoc(BaseDocument, dot_notation=True, client=client, db='dbname'):
        foo = Field(str)
        bar = Field(int, required=False)

        __indexes__ = [
            Index('foo'),
            Index([('bar', 1), ('foo', -1)], unique=True),
        ]

    doc = MyDoc(foo='L33t')
    doc.bar = 42
    doc.insert()

    Doc.find_one({'foo': 'L33t'})


nanomongo is written for Python3 and I intend to support both pymongo & motor
transparently under the hood.

Contributions and insight are welcome!

:Author: Eren Güven (GitHub_, Twitter_)
:License: Apache Software License

.. _GitHub: https://github.com/eguven
.. _Twitter: https://twitter.com/cyberfart
