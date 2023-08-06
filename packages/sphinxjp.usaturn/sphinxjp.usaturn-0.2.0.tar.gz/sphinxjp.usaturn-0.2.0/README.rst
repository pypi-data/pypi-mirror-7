================
sphinxjp.usaturn
================

`sphinxjp.usaturn` is sphinx extension to add `usaturn` admonition.
This extension enable you to add wonderful admonition notaiton.

Example::

  .. usaturn:: Hello world!


This is memorial package for `SphinxCon JP 2014`_ . Let's enjoy Sphinx!

.. _SphinxCon JP 2014: http://sphinx-users.jp/event/20141026_sphinxconjp/index.html

See more examples are in http://packages.python.org/sphinxjp.usaturn/ .

Install
=======

Use pip::

   $ pip install sphinxjp.usaturn

And configure your `conf.py`::

   # Enabled extensions
   extensions = ['sphinxjp.usaturn']


Directive
=========

**.. usaturn::**

   This directive insert a `usaturn` admonition into the document.

   Example::

     .. usaturn:: Hello world!

License
=======
Apache License 2.0
