=================
Tornado Testlayer
=================

A testlayer for Tornado that can be used with zope.testrunner


See _`tornado_testing/layer.rst` for more information.



Development
===========

Run bootstrap and buildout to create the development environment::

    python bootstrap.py
    ./bin/buildout -N


The tests can then be run using the zope testrunner::

    bin/test
