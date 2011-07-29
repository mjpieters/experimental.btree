Introduction
============

This library provides experimental code to speed up BTree difference and
intersection functions, as used by the ZCatalog.

It's been extracted out from
`experimental.catalogqueryplan <https://github.com/Jarn/experimental.catalogqueryplan>`_
now that the query plan implementation has been moved to ZCatalog itself.

Testing
=======

To test, import the monkey patch in other tests, like CMFPlone::

 import experimental.btree

and run the test.

Development
===========

Development of this project takes place at:
https://github.com/Jarn/experimental.btree
